"""Ophalen van open data van Infrabel (Opendatasoft API, licentie CC0).

Catalogus: https://opendata.infrabel.be/
"""
from __future__ import annotations

from collections import defaultdict

import requests

from .eurostat import BronFout, Resultaat, Waarneming

API = "https://opendata.infrabel.be/api/explore/v2.1/catalog/datasets/{dataset}/exports/json"
PAGINA = "https://opendata.infrabel.be/explore/dataset/{dataset}/"


def pagina_url(dataset: str) -> str:
    return PAGINA.format(dataset=dataset)


def jaar_uit_maanden(records: list[dict], maandveld: str, teller: str, noemer: str) -> list[Waarneming]:
    """Telt maandcijfers op tot een jaarcijfer: 100 × som(teller) / som(noemer).

    Een jaar met minder dan 12 maanden krijgt de vlag "j" (lopend jaar).
    Als de bron ook cumulatieve jaartotalen geeft (teller_ytd / noemer_ytd),
    controleren we dat onze optelling daar exact mee overeenkomt.
    """
    som_t: dict[int, float] = defaultdict(float)
    som_n: dict[int, float] = defaultdict(float)
    maanden: dict[int, set] = defaultdict(set)
    laatste: dict[int, dict] = {}
    for r in records:
        m = str(r.get(maandveld) or "")
        if len(m) < 7 or r.get(teller) is None or r.get(noemer) is None:
            continue
        jaar, maand = int(m[:4]), int(m[5:7])
        if maand in maanden[jaar]:
            raise BronFout(f"Maand {m} komt twee keer voor.")
        maanden[jaar].add(maand)
        som_t[jaar] += float(r[teller])
        som_n[jaar] += float(r[noemer])
        if jaar not in laatste or m > str(laatste[jaar][maandveld]):
            laatste[jaar] = r

    uit = []
    for jaar in sorted(som_n):
        if som_n[jaar] <= 0:
            continue
        ytd_t, ytd_n = laatste[jaar].get(f"{teller}_ytd"), laatste[jaar].get(f"{noemer}_ytd")
        if ytd_t is not None and ytd_n is not None and (round(float(ytd_t)) != round(som_t[jaar]) or round(float(ytd_n)) != round(som_n[jaar])):
            raise BronFout(f"Optelling {jaar} ({som_t[jaar]:.0f}/{som_n[jaar]:.0f}) wijkt af van het jaartotaal van de bron ({ytd_t}/{ytd_n}).")
        status = "" if len(maanden[jaar]) == 12 else "j"
        uit.append(Waarneming("BE", jaar, round(100 * som_t[jaar] / som_n[jaar], 4), status))
    return uit


def haal_op(bron: dict, sessie: requests.Session | None = None) -> Resultaat:
    sessie = sessie or requests.Session()
    url = API.format(dataset=bron["dataset"])
    velden = [bron["maandveld"], bron["teller"], bron["noemer"], f"{bron['teller']}_ytd", f"{bron['noemer']}_ytd"]
    try:
        r = sessie.get(url, params={"select": ",".join(velden)}, timeout=60,
                       headers={"User-Agent": "belgie-in-cijfers (open data dashboard; github.com/jonathanmaes97/belgie-in-cijfers)"})
    except requests.RequestException as e:
        raise BronFout(f"netwerkfout: {e}")
    if r.status_code == 400 and "_ytd" in r.text:
        # dataset zonder cumulatieve velden: zonder controle ophalen
        r = sessie.get(url, params={"select": ",".join(velden[:3])}, timeout=60)
    if not r.ok:
        raise BronFout(f"HTTP {r.status_code}: {r.text[:200]}")
    records = r.json()
    if not isinstance(records, list) or not records:
        raise BronFout("Infrabel gaf geen records terug.")
    waarnemingen = jaar_uit_maanden(records, bron["maandveld"], bron["teller"], bron["noemer"])
    laatste_maand = max(str(x.get(bron["maandveld"])) for x in records)
    res = Resultaat(waarnemingen=waarnemingen, bijgewerkt_bron=None, url=r.url)
    res.labels = {"laatste_maand": laatste_maand}
    return res
