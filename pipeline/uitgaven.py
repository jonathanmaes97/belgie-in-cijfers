"""Overheidsuitgaven per functie (COFOG), voor "Waar gaat ons belastinggeld naartoe?".

Bron: Eurostat gov_10a_exp, alle overheden samen (S13), totale uitgaven (TE).
- aandeel van elke functie in de totale overheidsuitgaven (PC_TOT), voor België, de EU en de buren
- bedrag in miljoen euro (MIO_EUR) voor België, om per inwoner te kunnen rekenen
"""
from __future__ import annotations

from . import eurostat

FUNCTIES = [
    ("GF10", {"nl": "Sociale bescherming", "uitleg": "pensioenen, uitkeringen, kinderbijslag, steun bij ziekte en werkloosheid"}),
    ("GF07", {"nl": "Gezondheidszorg", "uitleg": "ziekenhuizen, terugbetaling van dokters en geneesmiddelen"}),
    ("GF04", {"nl": "Economische zaken", "uitleg": "verkeer en vervoer, energie, landbouw, steun aan bedrijven"}),
    ("GF01", {"nl": "Algemeen bestuur", "uitleg": "werking van de overheid, rente op de staatsschuld, ontwikkelingshulp"}),
    ("GF09", {"nl": "Onderwijs", "uitleg": "scholen, hogescholen en universiteiten"}),
    ("GF03", {"nl": "Veiligheid en justitie", "uitleg": "politie, brandweer, rechtbanken, gevangenissen"}),
    ("GF08", {"nl": "Cultuur, sport en religie", "uitleg": "cultuur, sport, media, erediensten"}),
    ("GF06", {"nl": "Huisvesting en voorzieningen", "uitleg": "sociale huisvesting, water, straatverlichting"}),
    ("GF05", {"nl": "Milieu", "uitleg": "afval, waterzuivering, natuurbehoud"}),
    ("GF02", {"nl": "Defensie", "uitleg": "leger en militaire uitgaven"}),
]
DETAILS = [
    ("GF1002", {"nl": "waarvan pensioenen en ouderenzorg", "deel_van": "GF10"}),
    ("GF0107", {"nl": "waarvan rente op de staatsschuld", "deel_van": "GF01"}),
]
LANDEN = ["BE", "EU27_2020", "NL", "DE", "FR", "LU"]


def haal_op(vanaf_jaar: int = 2015) -> dict:
    basis = {"unit": "PC_TOT", "sector": "S13", "na_item": "TE"}
    aandelen: dict[str, dict[str, dict[int, float]]] = {}
    euro: dict[str, dict[int, float]] = {}
    urls: dict[str, str] = {}
    officieel: dict[str, str] = {}
    for code, _ in FUNCTIES + DETAILS:
        res = eurostat.haal_op("gov_10a_exp", {**basis, "cofog99": code}, LANDEN, vanaf_jaar)
        urls[code] = res.url
        officieel[code] = (res.labels.get("cofog99") or {}).get("label", "")
        keuzes = {d: f'{l["code"]} ({l["label"]})' for d, l in res.labels.items() if d not in ("cofog99", "freq")}
        for w in res.waarnemingen:
            aandelen.setdefault(code, {}).setdefault(w.geo, {})[w.jaar] = w.waarde
        res2 = eurostat.haal_op("gov_10a_exp", {**basis, "unit": "MIO_EUR", "cofog99": code}, ["BE"], vanaf_jaar)
        for w in res2.waarnemingen:
            euro.setdefault(code, {})[w.jaar] = w.waarde
    if not aandelen.get("GF10", {}).get("BE"):
        raise eurostat.BronFout("Geen uitgaven per functie voor België.")
    # recentste jaar waarin alle tien functies voor België gekend zijn
    jaren = set.intersection(*(set(aandelen[c]["BE"]) for c, _ in FUNCTIES if aandelen.get(c, {}).get("BE")))
    jaar = max(jaren)
    return {
        "jaar": jaar,
        # per functie: onze eenvoudige naam, de officiële Eurostat-naam (Engels) en de exacte bevraging
        "functies": [{"code": c, **meta, "officieel": officieel.get(c, ""), "api_url": urls[c]} for c, meta in FUNCTIES],
        "details": [{"code": c, **meta, "officieel": officieel.get(c, ""), "api_url": urls[c]} for c, meta in DETAILS],
        "aandelen": {c: {g: {str(j): v for j, v in r.items()} for g, r in per_geo.items()} for c, per_geo in aandelen.items()},
        "miljoen_euro": {c: {str(j): v for j, v in r.items()} for c, r in euro.items()},
        "bron": {"instelling": "Eurostat", "dataset": "gov_10a_exp", "url": eurostat.databrowser_url("gov_10a_exp"), "api_urls": list(urls.values()),
                 "filters": keuzes},  # officiële namen van de gekozen filters, zoals Eurostat ze teruggeeft
    }
