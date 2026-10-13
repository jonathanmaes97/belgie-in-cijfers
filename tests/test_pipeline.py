import json
from pathlib import Path

import pytest
import yaml

from pipeline import eurostat
from pipeline.build_site import getal, met_eenheid
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
    assert met_eenheid(39.1, {"eenheid": " mln €", "decimalen": 1}) == "€ 39,1 mln"


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
