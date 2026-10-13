import json
from pathlib import Path

import pytest
import yaml

from pipeline import eurostat
from pipeline.build_site import getal, kort_met_eenheid, met_eenheid, zinnen
from pipeline.infrabel import jaar_uit_maanden
from pipeline.eurostat import BronFout
from pipeline.run import afleiden, bereken, herzieningen, valideer

FIX = Path(__file__).parent / "fixtures"
WORTEL = Path(__file__).parent.parent


def test_ontleed_echt_eurostat_antwoord():
    res = eurostat.ontleed(json.loads((FIX / "gov_10dd_edpt1_BE_GD.json").read_text()))
    assert len(res.waarnemingen) == 16
    assert res.waarnemingen[0].geo == "BE" and res.waarnemingen[0].jaar == 2010 and res.waarnemingen[0].waarde == 100.3
    assert res.waarnemingen[-1].jaar == 2025 and res.waarnemingen[-1].waarde == 107.9


def test_ontleed_meerdere_landen_en_vlaggen():
    antwoord = {
        "id": ["freq", "geo", "time"], "size": [1, 2, 2],
        "dimension": {
            "freq": {"category": {"index": {"A": 0}}},
            "geo": {"category": {"index": {"BE": 0, "NL": 1}}},
            "time": {"category": {"index": {"2024": 0, "2025": 1}}},
        },
        "value": {"0": 1.0, "1": 2.0, "2": 3.0, "3": 4.0},
        "status": {"1": "p"},
    }
    w = eurostat.ontleed(antwoord).waarnemingen
    assert [(x.geo, x.jaar, x.waarde, x.status) for x in w] == [
        ("BE", 2024, 1.0, ""), ("BE", 2025, 2.0, "p"), ("NL", 2024, 3.0, ""), ("NL", 2025, 4.0, "")]


def test_onvolledige_filter_geeft_duidelijke_fout():
    antwoord = {
        "id": ["unit", "geo", "time"], "size": [2, 1, 1],
        "dimension": {
            "unit": {"category": {"index": {"PC": 0, "NR": 1}}},
            "geo": {"category": {"index": {"BE": 0}}},
            "time": {"category": {"index": {"2025": 0}}},
        },
        "value": {"0": 1.0},
    }
    with pytest.raises(BronFout, match="unit"):
        eurostat.ontleed(antwoord)


def test_url_bevat_alle_landen_en_filters():
    url = eurostat.bouw_url("tec00115", {"unit": "CLV_PCH_PRE"}, ["BE", "EU27_2020"], 2005)
    assert "geo=BE" in url and "geo=EU27_2020" in url and "unit=CLV_PCH_PRE" in url and "sinceTimePeriod=2005" in url


def test_formule_veilig():
    assert bereken("schuld * 1000000 / inwoners", {"schuld": 692460.8, "inwoners": 11883495}) == pytest.approx(58270.80, abs=0.01)
    with pytest.raises(ValueError):
        bereken("__import__('os')", {})


def test_afleiden_alleen_gemeenschappelijke_jaren():
    data = {
        "a": [{"geo": "BE", "jaar": 2024, "waarde": 10.0, "status": ""}, {"geo": "BE", "jaar": 2025, "waarde": 20.0, "status": "p"}],
        "b": [{"geo": "BE", "jaar": 2025, "waarde": 4.0, "status": ""}],
    }
    uit = afleiden({"afgeleid": {"formule": "x / y", "invoer": {"x": "a", "y": "b"}}}, data)
    assert uit == [{"geo": "BE", "jaar": 2025, "waarde": 5.0, "status": "p"}]


def test_validatie_eist_belgie():
    with pytest.raises(BronFout):
        valideer([{"geo": "NL", "jaar": 2025, "waarde": 1.0, "status": ""}], ["BE", "NL"])


def test_herzieningen_gedetecteerd():
    oud = [{"geo": "BE", "jaar": 2025, "waarde": 107.9, "status": "p"}]
    nieuw = [{"geo": "BE", "jaar": 2025, "waarde": 108.1, "status": ""}]
    assert herzieningen("x", oud, nieuw)[0]["nieuw"] == 108.1
    assert herzieningen("x", oud, oud) == []


def test_belgische_getalnotatie():
    assert getal(58271.3, 0) == "58.271"
    assert getal(-5.2, 1) == "−5,2"
    assert kort_met_eenheid(39.1, {"eenheid": " mln €", "decimalen": 1}) == "€ 39,1 mln"
    assert met_eenheid(107.9, {"eenheid": "% bbp", "decimalen": 1}) == "107,9% van het bbp"


def test_zinnen_vergelijken_neutraal():
    ind = {"decimalen": 1, "eenheid": "%", "bron": {},
           "reeksen": {"BE": [[2015, 67.2, ""], [2025, 72.8, ""]], "EU27_2020": [[2025, 76.1, ""]]}}
    z = zinnen(ind)
    assert z[0] == "Dat is lager dan het EU-gemiddelde (76,1%)."
    assert z[1] == "In 2015 was dit 67,2%."


def test_infrabel_jaarcijfer_uit_maanden_met_controle():
    recs = [{"maand": f"2024-{m:02d}", "reg": 90, "tel": 100} for m in range(1, 13)]
    recs[-1].update({"reg_ytd": 1080, "tel_ytd": 1200})
    recs += [{"maand": "2025-01", "reg": 80, "tel": 100}]
    w = jaar_uit_maanden(recs, "maand", "reg", "tel")
    assert [(x.jaar, x.waarde, x.status) for x in w] == [(2024, 90.0, ""), (2025, 80.0, "j")]
    recs[11]["reg_ytd"] = 1000
    with pytest.raises(BronFout):
        jaar_uit_maanden(recs, "maand", "reg", "tel")


def test_catalogus_is_consistent():
    cat = yaml.safe_load((WORTEL / "config" / "indicatoren.yaml").read_text(encoding="utf-8"))
    themas = {t["id"] for t in cat["themas"]}
    ids = [i["id"] for i in cat["indicatoren"]]
    assert len(ids) == len(set(ids)), "dubbele id's"
    for ind in cat["indicatoren"]:
        assert ind["thema"] in themas, ind["id"]
        assert ind["titel"]["nl"] and ind["definitie"]["nl"], ind["id"]
        assert ("bron" in ind) != ("afgeleid" in ind), f"{ind['id']}: precies één van bron/afgeleid"
        if "afgeleid" in ind:
            for bron_id in ind["afgeleid"]["invoer"].values():
                assert bron_id in ids, f"{ind['id']} verwijst naar onbekende {bron_id}"


def _maak_inflatie_xlsx():
    import io
    from datetime import datetime
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "NL"
    ws.append(["Indexcijfer der consumptieprijzen"])
    ws.append([None, "Nationale consumptieprijsindex", None, "Gezondheidsindex", None, "Afgevlakte gezondheidsindex", "Spilindex"])
    ws.append([None, "Index (2025=100)", "Groeivoet (%)", "Index (2025=100)", "Groeivoet (%)"])
    ws.append(["Jaarcijfers"])
    ws.append([2026, 103.69, 3.69, 103.31, 3.30])
    ws.append(["Maandcijfers"])
    rijen = [("2026-05", 103.26, 4.08, 100.19, 100.28), ("2026-06", 102.95, 3.4, 100.37, 100.28),
             ("2026-07", 103.6, 3.56, 100.77, 102.29), ("2026-11", 106.1, 5.39, 102.35, 102.29)]
    for m, cpi, gr, afg, spil in rijen:
        ws.append([datetime.strptime(m, "%Y-%m"), cpi, gr, None, None, afg, spil])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_planbureau_inflatie_en_spilindex():
    from datetime import date
    from pipeline.planbureau import lees_inflatie
    uit = lees_inflatie(_maak_inflatie_xlsx(), date(2026, 10, 6))
    assert uit["jaren"][0]["inflatie"] == 3.69
    assert [m["vooruitzicht"] for m in uit["maanden"]] == [False, False, False, True]
    assert [o["maand"] for o in uit["overschrijdingen"]] == ["2026-06", "2026-11"]
    assert uit["laatste_gemeten"] == "2026-07"
