"""Snelle (maand- en kwartaal)cijfers van de Nationale Bank van België via de SDMX-API van NBB.Stat.

Documentatie: https://stat.nbb.be (dataflows BE2:DF_*). Sleutels volgen de dimensievolgorde van
elke dataflow; die volgorde staat in reports/nbb_codes.md.
"""
from __future__ import annotations

import csv
import io

import requests

from .eurostat import BronFout

API = "https://nsidisseminate-stat.nbb.be/rest/data/BE2,{flow},1.0/{sleutel}"
PORTAAL = "https://stat.nbb.be/"
UA = {"User-Agent": "belgie-in-cijfers (open data dashboard; github.com/jonathanmaes97/belgie-in-cijfers)"}

REEKSEN = [
    {
        "id": "consumentenvertrouwen", "flow": "DF_CONSN", "sleutel": "M.CCI.BE", "vergelijk": None,
        "titel": {"nl": "Consumentenvertrouwen"}, "vraag": {"nl": "Hoe optimistisch zijn de gezinnen?"},
        "uitleg": {"nl": "Een maandelijkse enquête bij gezinnen over de economie, werkloosheid, hun eigen financiën en sparen. Nul is neutraal: een negatief cijfer betekent meer pessimisten dan optimisten."},
        "eenheid": "", "decimalen": 0, "begin": "2019-01",
    },
    {
        "id": "conjunctuurbarometer", "flow": "DF_BUSSURVM", "sleutel": "M.SYNC.BE.A999.X", "vergelijk": None,
        "titel": {"nl": "Conjunctuurbarometer"}, "vraag": {"nl": "Hoe zien de bedrijven het?"},
        "uitleg": {"nl": "De barometer van de Nationale Bank vat de maandelijkse enquêtes bij bedrijven samen (industrie, bouw, handel en diensten). Hij wordt vooral gebruikt om de richting te zien: stijgt hij, dan zijn bedrijven positiever."},
        "eenheid": "", "decimalen": 1, "begin": "2019-01",
    },
    {
        "id": "werkloosheid_maand", "flow": "DF_UNEMPLOY_RATE", "sleutel": "M.AA.Z0000.Y.BE.HUR.RATE",
        "vergelijk": {"sleutel": "M.AA.Z0000.Y.B4.HUR.RATE", "naam": {"nl": "EU"}},
        "titel": {"nl": "Werkloosheid deze maand"}, "vraag": {"nl": "Hoeveel mensen zoeken nu werk?"},
        "uitleg": {"nl": "Werkloosheidsgraad volgens de internationale definitie, gezuiverd voor seizoenseffecten, zodat je maanden met elkaar kunt vergelijken."},
        "eenheid": "%", "decimalen": 1, "begin": "2019-01",
    },
    {
        "id": "bbp_kwartaal", "flow": "DF_QNA_DISS", "sleutel": "Q.1.B1GM.VZ.LQ.Y", "vergelijk": None,
        "titel": {"nl": "Groei dit kwartaal"}, "vraag": {"nl": "Groeit de economie nu?"},
        "uitleg": {"nl": "Groei van het bbp (na inflatie) tegenover het vorige kwartaal, gezuiverd voor seizoens- en kalendereffecten. Twee kwartalen krimp na elkaar noemt men vaak een recessie."},
        "eenheid": "%", "decimalen": 1, "begin": "2019-Q1",
    },
]


def _reeks(flow: str, sleutel: str, begin: str) -> list[list]:
    url = API.format(flow=flow, sleutel=sleutel)
    try:
        r = requests.get(url, params={"startPeriod": begin, "format": "csvfile"}, timeout=60, headers=UA)
    except requests.RequestException as e:
        raise BronFout(f"netwerkfout: {e}")
    if not r.ok:
        raise BronFout(f"HTTP {r.status_code} voor {flow}/{sleutel}: {r.text[:150]}")
    punten = []
    for rij in csv.DictReader(io.StringIO(r.text)):
        try:
            punten.append([rij["TIME_PERIOD"], float(rij["OBS_VALUE"]), rij.get("OBS_STATUS", "")])
        except (KeyError, ValueError):
            continue
    if not punten:
        raise BronFout(f"Geen waarden voor {flow}/{sleutel}.")
    punten.sort(key=lambda p: p[0])
    return punten, r.url


def haal_op() -> dict:
    uit = []
    for d in REEKSEN:
        punten, url = _reeks(d["flow"], d["sleutel"], d["begin"])
        item = {k: v for k, v in d.items() if k not in ("vergelijk",)}
        item.update({"punten": punten, "api_url": url, "bron": {"instelling": "Nationale Bank van België", "url": PORTAAL, "dataset": d["flow"]}})
        if d.get("vergelijk"):
            vp, _ = _reeks(d["flow"], d["vergelijk"]["sleutel"], d["begin"])
            item["vergelijk"] = {"naam": d["vergelijk"]["naam"], "punten": vp}
        uit.append(item)
    return {"reeksen": uit}
