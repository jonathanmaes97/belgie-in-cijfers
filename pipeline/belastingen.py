"""Waar komen de belastingen vandaan? Belastingen op arbeid, consumptie en kapitaal.

Bron: Europese Commissie, DG Belastingen en Douane (TAXUD), "Data on Taxation Trends", via de REDISSTAT-databank.
Die werkt met dezelfde API als Eurostat.
- TAX_EC_FUNC: belastinginkomsten per economische functie (arbeid, consumptie, kapitaal), in % van alle
  belastingen en sociale bijdragen, en in miljoen euro
- TAX_ITR en TAX_ITR_CAPITAL: impliciete belastingvoeten (hoeveel belasting er gemiddeld op een euro
  inkomen uit arbeid, op consumptie of op kapitaal wordt betaald)
"""
from __future__ import annotations

from . import eurostat

API = "https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination/statistics/1.0/data/"
DATABROWSER = "https://webgate.ec.europa.eu/taxation_customs/redisstat/databrowser/explore/all/DATA_ON_TAX?lang=en&display=card&sort=category"
PAGINA = "https://taxation-customs.ec.europa.eu/taxation/economic-analysis/data-taxation-trends_en"
LANDEN = ["BE", "EU27_2020", "NL", "DE", "FR", "LU"]

FUNCTIES = [
    ("LAB", {"nl": "Arbeid", "uitleg": "personenbelasting op lonen en uitkeringen, sociale bijdragen van werknemers en werkgevers"},
     ("TAX_ITR", {"ITR": "L"})),
    ("C", {"nl": "Consumptie", "uitleg": "btw, accijnzen op brandstof, tabak en alcohol, andere taksen op wat we kopen"},
     ("TAX_ITR", {"ITR": "C"})),
    ("CAP", {"nl": "Kapitaal", "uitleg": "vennootschapsbelasting, belasting op rente, dividenden en huur, op winst van zelfstandigen, onroerende voorheffing en erfbelasting"},
     ("TAX_ITR_CAPITAL", {"ITR_CAPITAL": "ITR_C"})),
]


def _reeks(dataset: str, filters: dict, landen: list[str], vanaf: int) -> tuple[dict, str, dict]:
    res = eurostat.haal_op(dataset, filters, landen, vanaf, api=API)
    uit: dict[str, dict[str, float]] = {}
    for w in res.waarnemingen:
        uit.setdefault(w.geo, {})[str(w.jaar)] = w.waarde
    return uit, res.url, res.labels


def haal_op(vanaf_jaar: int = 2010) -> dict:
    aandelen, euro, voeten, urls, officieel = {}, {}, {}, {}, {}
    for code, _, (ds_itr, f_itr) in FUNCTIES:
        aandelen[code], urls[code], lab = _reeks("TAX_EC_FUNC", {"EF": code, "UNIT": "PC_TOT"}, LANDEN, vanaf_jaar)
        officieel[code] = next((l["label"] for d, l in lab.items() if d.upper() == "EF"), "")
        euro[code] = _reeks("TAX_EC_FUNC", {"EF": code, "UNIT": "MIO_EUR"}, ["BE"], vanaf_jaar)[0].get("BE", {})
        voeten[code], urls[f"{code}_ITR"], _ = _reeks(ds_itr, {**f_itr, "UNIT": "PC_TOT"}, LANDEN, vanaf_jaar)
    be = [set(aandelen[c].get("BE", {})) for c, _, _ in FUNCTIES]
    jaren = set.intersection(*be) if all(be) else set()
    if not jaren:
        raise eurostat.BronFout("Geen belastingen per economische functie voor België.")
    jaar = max(jaren, key=int)
    som = sum(aandelen[c]["BE"][jaar] for c, _, _ in FUNCTIES)
    if abs(som - 100) > 1.5:  # de drie functies samen horen alle belastingen te zijn
        raise eurostat.BronFout(f"Arbeid, consumptie en kapitaal samen zijn {som:.1f}% in plaats van 100%.")
    return {
        "jaar": int(jaar),
        "functies": [{"code": c, **meta, "officieel": officieel.get(c, ""), "api_url": urls[c], "itr_url": urls[f"{c}_ITR"]}
                     for c, meta, _ in FUNCTIES],
        "aandelen": aandelen, "miljoen_euro": euro, "impliciete_voet": voeten,
        "bron": {"instelling": "Europese Commissie", "naam": "Europese Commissie, DG Belastingen en Douane (Data on Taxation Trends)",
                 "dataset": "TAX_EC_FUNC, TAX_ITR, TAX_ITR_CAPITAL", "url": DATABROWSER, "pagina": PAGINA},
    }
