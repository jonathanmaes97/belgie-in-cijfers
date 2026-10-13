"""Ophalen en ontleden van Eurostat-data (JSON-stat 2.0 via de dissemination API).

Documentatie API: https://wikis.ec.europa.eu/display/EUROSTATHELP/API+Statistics+-+data+query
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from urllib.parse import urlencode

import requests

API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
DATABROWSER = "https://ec.europa.eu/eurostat/databrowser/view/{dataset}/default/table?lang=en"

# Eurostat beperkt het aantal aanvragen; we wachten tussen elke aanvraag.
WACHTTIJD_SEC = 2.0
_laatste_aanvraag = 0.0


class BronFout(Exception):
    """Een bron gaf geen bruikbaar antwoord. De boodschap legt uit waarom."""


@dataclass
class Waarneming:
    geo: str
    jaar: int
    waarde: float
    status: str = ""  # Eurostat-vlag, bv. "p" = voorlopig, "e" = geschat, "b" = breuk in reeks


@dataclass
class Resultaat:
    waarnemingen: list[Waarneming]
    bijgewerkt_bron: str | None  # datum waarop Eurostat de dataset bijwerkte
    url: str
    labels: dict = field(default_factory=dict)


def bouw_url(dataset: str, filters: dict, landen: list[str], vanaf_jaar: int) -> str:
    params: list[tuple[str, str]] = [("lang", "EN"), ("sinceTimePeriod", str(vanaf_jaar))]
    for sleutel, waarde in filters.items():
        for w in (waarde if isinstance(waarde, list) else [waarde]):
            params.append((sleutel, str(w)))
    for land in landen:
        params.append(("geo", land))
    return API + dataset + "?" + urlencode(params)


def databrowser_url(dataset: str) -> str:
    return DATABROWSER.format(dataset=dataset)


def ontleed(antwoord: dict) -> Resultaat:
    """Zet een JSON-stat-antwoord om naar een lijst waarnemingen per land en jaar.

    Alle dimensies behalve `geo` en `time` moeten na filtering precies één waarde
    hebben. Anders is de filter in de catalogus onvolledig, en dan stoppen we met
    een duidelijke foutmelding in plaats van stilletjes de verkeerde reeks te tonen.
    """
    if "error" in antwoord:
        raise BronFout(f"Eurostat gaf een fout: {antwoord['error']}")
    ids: list[str] = antwoord["id"]
    groottes: list[int] = antwoord["size"]
    dims = antwoord["dimension"]

    te_veel = []
    for dim, grootte in zip(ids, groottes):
        if dim in ("geo", "time"):
            continue
        if grootte != 1:
            codes = list(dims[dim]["category"]["index"].keys())
            te_veel.append(f"'{dim}' heeft {grootte} waarden {codes[:15]}")
    if te_veel:
        raise BronFout("Dimensie " + "; ".join(te_veel) + "; voeg een filter toe in de catalogus.")

    def codes_per_index(dim: str) -> list[str]:
        index = dims[dim]["category"]["index"]
        lijst = [""] * len(index)
        for code, i in index.items():
            lijst[i] = code
        return lijst

    geo_codes = codes_per_index("geo")
    tijd_codes = codes_per_index("time")
    pos_geo, pos_tijd = ids.index("geo"), ids.index("time")

    # stappen (strides) per dimensie in de platte waardenlijst
    stappen = [1] * len(groottes)
    for i in range(len(groottes) - 2, -1, -1):
        stappen[i] = stappen[i + 1] * groottes[i + 1]

    waarden = antwoord.get("value", {})
    vlaggen = antwoord.get("status", {})
    if isinstance(waarden, list):  # JSON-stat laat ook een lijst toe
        waarden = {str(i): v for i, v in enumerate(waarden) if v is not None}

    uit: list[Waarneming] = []
    for sleutel, waarde in waarden.items():
        if waarde is None:
            continue
        plat = int(sleutel)
        i_geo = (plat // stappen[pos_geo]) % groottes[pos_geo]
        i_tijd = (plat // stappen[pos_tijd]) % groottes[pos_tijd]
        tijd = tijd_codes[i_tijd]
        if not tijd[:4].isdigit():
            continue
        uit.append(Waarneming(geo_codes[i_geo], int(tijd[:4]), float(waarde), str(vlaggen.get(sleutel, ""))))

    uit.sort(key=lambda w: (w.geo, w.jaar))
    return Resultaat(waarnemingen=uit, bijgewerkt_bron=antwoord.get("updated"), url="", labels={})


def haal_op(dataset: str, filters: dict, landen: list[str], vanaf_jaar: int, sessie: requests.Session | None = None) -> Resultaat:
    """Haalt één reeks op bij Eurostat, met wachttijd en beperkte herhaalpogingen."""
    global _laatste_aanvraag
    sessie = sessie or requests.Session()
    url = bouw_url(dataset, filters, landen, vanaf_jaar)
    laatste_fout = ""
    for poging in range(4):
        wacht = WACHTTIJD_SEC - (time.monotonic() - _laatste_aanvraag)
        if wacht > 0:
            time.sleep(wacht)
        _laatste_aanvraag = time.monotonic()
        try:
            r = sessie.get(url, timeout=60, headers={"User-Agent": "belgie-in-cijfers (open data dashboard; github.com/jonathanmaes97/belgie-in-cijfers)"})
        except requests.RequestException as e:
            laatste_fout = f"netwerkfout: {e}"
            time.sleep(5 * (poging + 1))
            continue
        if r.status_code == 429 or r.status_code >= 500:
            laatste_fout = f"HTTP {r.status_code}"
            time.sleep(int(r.headers.get("Retry-After", 10 * (poging + 1))))
            continue
        try:
            data = r.json()
        except ValueError:
            raise BronFout(f"HTTP {r.status_code}, geen JSON: {r.text[:200]}")
        if r.status_code != 200:
            raise BronFout(f"HTTP {r.status_code}: {data.get('error', data)}")
        resultaat = ontleed(data)
        resultaat.url = url
        return resultaat
    raise BronFout(f"Geen antwoord na 4 pogingen ({laatste_fout})")
