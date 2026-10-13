"""Hoofdscript van de datapipeline.

Gebruik:  python -m pipeline.run            (alles ophalen en de site opbouwen)
          python -m pipeline.run --offline  (geen netwerk; site opbouwen uit bestaande data)

Stappen:
1. Elke indicator uit config/indicatoren.yaml ophalen bij de bron.
2. Valideren. Mislukt een indicator, dan blijft de laatste geldige versie staan
   en tonen we op de site vanaf wanneer die dateert. Andere indicatoren gaan gewoon door.
3. Herzieningen (gewijzigde cijfers voor een jaar dat al bestond) in de changelog zetten.
4. Afgeleide indicatoren berekenen met hun formule.
5. data/clean/*.csv, site/data/dashboard.json en reports/status.md schrijven.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import operator
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import eurostat, infrabel, planbureau, uitgaven
from .eurostat import BronFout

WORTEL = Path(__file__).resolve().parent.parent
CATALOGUS = WORTEL / "config" / "indicatoren.yaml"
SCHOON = WORTEL / "data" / "clean"
CHANGELOG = WORTEL / "data" / "changelog.json"
SITE_DATA = WORTEL / "site" / "data" / "dashboard.json"
STATUS = WORTEL / "reports" / "status.md"

EXTRA = [("vooruitzichten", planbureau.haal_op), ("uitgaven", uitgaven.haal_op)]

# Een herziening wordt pas gemeld vanaf dit verschil (afrondingsruis negeren).
HERZIENING_DREMPEL = 0.05


def nu() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ---------------------------------------------------------------- opslag

def lees_csv(pad: Path) -> list[dict]:
    if not pad.exists():
        return []
    with pad.open(newline="", encoding="utf-8") as f:
        return [{"geo": r["geo"], "jaar": int(r["jaar"]), "waarde": float(r["waarde"]), "status": r.get("status", "")} for r in csv.DictReader(f)]


def schrijf_csv(pad: Path, rijen: list[dict]) -> None:
    pad.parent.mkdir(parents=True, exist_ok=True)
    with pad.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["geo", "jaar", "waarde", "status"])
        w.writeheader()
        for r in sorted(rijen, key=lambda r: (r["geo"], r["jaar"])):
            w.writerow({**r, "waarde": repr(r["waarde"]) if isinstance(r["waarde"], float) else r["waarde"]})


def lees_meta(id_: str) -> dict:
    pad = SCHOON / f"{id_}.meta.json"
    return json.loads(pad.read_text(encoding="utf-8")) if pad.exists() else {}


def schrijf_meta(id_: str, meta: dict) -> None:
    (SCHOON / f"{id_}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- validatie

def valideer(rijen: list[dict], landen: list[str]) -> None:
    if not rijen:
        raise BronFout("Bron gaf geen enkele waarde terug.")
    huidig_jaar = datetime.now(timezone.utc).year
    for r in rijen:
        if not (1950 <= r["jaar"] <= huidig_jaar + 1):
            raise BronFout(f"Onwaarschijnlijk jaar {r['jaar']} voor {r['geo']}.")
        if r["waarde"] != r["waarde"]:  # NaN
            raise BronFout(f"Ongeldige waarde voor {r['geo']} {r['jaar']}.")
    if "BE" in landen and not any(r["geo"] == "BE" for r in rijen):
        raise BronFout("Geen cijfers voor België in het antwoord.")


def herzieningen(id_: str, oud: list[dict], nieuw: list[dict]) -> list[dict]:
    oud_idx = {(r["geo"], r["jaar"]): r["waarde"] for r in oud}
    uit = []
    for r in nieuw:
        vorig = oud_idx.get((r["geo"], r["jaar"]))
        if vorig is not None and abs(vorig - r["waarde"]) >= HERZIENING_DREMPEL:
            uit.append({"indicator": id_, "geo": r["geo"], "jaar": r["jaar"], "oud": vorig, "nieuw": r["waarde"]})
    return uit


# ---------------------------------------------------------------- afgeleide indicatoren

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def bereken(formule: str, waarden: dict[str, float]) -> float:
    """Rekent een eenvoudige formule uit (enkel + - * / , getallen en namen)."""
    def ev(knoop):
        if isinstance(knoop, ast.Expression):
            return ev(knoop.body)
        if isinstance(knoop, ast.BinOp) and type(knoop.op) in _OPS:
            return _OPS[type(knoop.op)](ev(knoop.left), ev(knoop.right))
        if isinstance(knoop, ast.Constant) and isinstance(knoop.value, (int, float)):
            return float(knoop.value)
        if isinstance(knoop, ast.Name) and knoop.id in waarden:
            return waarden[knoop.id]
        raise ValueError(f"Niet toegelaten in formule: {ast.dump(knoop)}")
    return ev(ast.parse(formule, mode="eval"))


def afleiden(ind: dict, data: dict[str, list[dict]]) -> list[dict]:
    invoer: dict[str, str] = ind["afgeleid"]["invoer"]
    reeksen = {}
    for naam, bron_id in invoer.items():
        if not data.get(bron_id):
            raise BronFout(f"Invoer '{bron_id}' ontbreekt.")
        reeksen[naam] = {(r["geo"], r["jaar"]): r for r in data[bron_id]}
    sleutels = set.intersection(*(set(r.keys()) for r in reeksen.values()))
    uit = []
    for geo, jaar in sorted(sleutels):
        waarden = {naam: reeksen[naam][(geo, jaar)]["waarde"] for naam in reeksen}
        vlaggen = "".join(sorted({reeksen[n][(geo, jaar)]["status"] for n in reeksen} - {""}))
        uit.append({"geo": geo, "jaar": jaar, "waarde": round(bereken(ind["afgeleid"]["formule"], waarden), 6), "status": vlaggen})
    return uit


# ---------------------------------------------------------------- hoofdlus

def haal_indicator(ind: dict, cat: dict, oud: list[dict] | None = None) -> tuple[list[dict], dict]:
    bron = ind["bron"]
    landen = ind.get("landen", cat["standaard_landen"])
    if bron["instelling"] == "Infrabel":
        res = infrabel.haal_op(bron)
        rijen = [{"geo": w.geo, "jaar": w.jaar, "waarde": w.waarde, "status": w.status} for w in res.waarnemingen]
        valideer(rijen, ["BE"])
        return rijen, {"api_urls": [res.url], "bijgewerkt_bron": None, "laatste_periode": res.labels.get("laatste_maand")}
    if bron["instelling"] != "Eurostat":
        raise BronFout(f"Bron {bron['instelling']} wordt nog niet ondersteund.")
    res = eurostat.haal_op(bron["dataset"], bron["filters"], landen, cat["vanaf_jaar"])
    rijen = [{"geo": w.geo, "jaar": w.jaar, "waarde": w.waarde, "status": w.status} for w in res.waarnemingen]
    urls = [res.url]
    bijgewerkt = res.bijgewerkt_bron
    melding_regio = ""
    if ind.get("regionaal"):
        reg = ind["regionaal"]
        try:
            r2 = eurostat.haal_op(reg["dataset"], reg["filters"], reg["landen"], cat["vanaf_jaar"])
            if not r2.waarnemingen:
                raise BronFout("geen cijfers per gewest in het antwoord")
            rijen += [{"geo": w.geo, "jaar": w.jaar, "waarde": w.waarde, "status": w.status} for w in r2.waarnemingen]
            urls.append(r2.url)
        except BronFout as e:
            # vorige gewestcijfers behouden en de fout melden
            melding_regio = f"gewesten: {e}"
            print(f"  ! regionale reeks mislukt: {e}", file=sys.stderr)
            rijen += [r for r in (oud or []) if r["geo"] in reg["landen"]]
    valideer(rijen, landen)
    meta = {"api_urls": urls, "bijgewerkt_bron": bijgewerkt, "melding_regio": melding_regio}
    return rijen, meta


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--offline", action="store_true", help="niets ophalen, enkel de site opbouwen uit bestaande data")
    p.add_argument("--alleen", nargs="*", help="enkel deze indicator-id's ophalen")
    args = p.parse_args(argv)

    cat = yaml.safe_load(CATALOGUS.read_text(encoding="utf-8"))
    tijd = nu()
    data: dict[str, list[dict]] = {}
    status: dict[str, dict] = {}
    nieuwe_herzieningen: list[dict] = []

    for ind in cat["indicatoren"]:
        id_ = ind["id"]
        if "afgeleid" in ind:
            continue
        pad = SCHOON / f"{id_}.csv"
        oud = lees_csv(pad)
        meta = lees_meta(id_)
        if args.offline or (args.alleen and id_ not in args.alleen):
            data[id_] = oud
            status[id_] = {"ok": bool(oud), "melding": "niet opgehaald (offline)" if not oud else "", **meta}
            continue
        print(f"→ {id_}")
        try:
            rijen, extra = haal_indicator(ind, cat, oud)
            nieuwe_herzieningen += herzieningen(id_, oud, rijen)
            schrijf_csv(pad, rijen)
            meta = {**meta, **extra, "opgehaald": tijd, "laatste_poging": tijd, "melding": ""}
            schrijf_meta(id_, meta)
            data[id_] = rijen
            status[id_] = {"ok": True, **meta}
        except BronFout as e:
            print(f"  ✗ {e}", file=sys.stderr)
            meta = {**meta, "laatste_poging": tijd, "melding": str(e)}
            schrijf_meta(id_, meta)
            data[id_] = oud
            status[id_] = {"ok": False, **meta}

    for ind in cat["indicatoren"]:
        if "afgeleid" not in ind:
            continue
        id_ = ind["id"]
        try:
            rijen = afleiden(ind, data)
            valideer(rijen, ["BE"])
            schrijf_csv(SCHOON / f"{id_}.csv", rijen)
            bronnen = {n: status.get(b, {}).get("opgehaald") for n, b in ind["afgeleid"]["invoer"].items()}
            meta = {"opgehaald": min((t for t in bronnen.values() if t), default=None), "melding": ""}
            schrijf_meta(id_, meta)
            data[id_] = rijen
            status[id_] = {"ok": True, **meta}
        except (BronFout, ValueError) as e:
            data[id_] = lees_csv(SCHOON / f"{id_}.csv")
            status[id_] = {"ok": False, **lees_meta(id_), "melding": str(e)}

    # aparte bronnen die geen jaarreeks per land zijn (Planbureau, uitgaven per functie, ...)
    for naam, ophalen in EXTRA:
        pad = SCHOON / f"{naam}.json"
        sleutel = f"_{naam}"
        if args.offline:
            status[sleutel] = {"ok": pad.exists(), "melding": ""}
            continue
        print(f"→ {naam}")
        try:
            inhoud = ophalen()
            inhoud["opgehaald"] = tijd
            pad.write_text(json.dumps(inhoud, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            status[sleutel] = {"ok": True, "opgehaald": tijd, "melding": ""}
        except (BronFout, KeyError, ValueError) as e:
            print(f"  ✗ {e}", file=sys.stderr)
            status[sleutel] = {"ok": False, "melding": str(e)}

    if nieuwe_herzieningen:
        log = json.loads(CHANGELOG.read_text(encoding="utf-8")) if CHANGELOG.exists() else []
        log.insert(0, {"datum": tijd, "herzieningen": nieuwe_herzieningen})
        CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
        CHANGELOG.write_text(json.dumps(log[:200], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    schrijf_site_data(cat, data, status, tijd)
    schrijf_status(cat, status, tijd)

    from .build_site import bouw
    bouw()

    mislukt = [i for i, s in status.items() if not s["ok"] and not i.startswith("_")]
    print(f"\nKlaar: {len(status) - len(mislukt)} gelukt, {len(mislukt)} mislukt.")
    return 0


def schrijf_site_data(cat: dict, data: dict, status: dict, tijd: str) -> None:
    indicatoren = []
    for ind in cat["indicatoren"]:
        id_ = ind["id"]
        rijen = data.get(id_, [])
        reeksen: dict[str, list] = {}
        for r in sorted(rijen, key=lambda r: r["jaar"]):
            reeksen.setdefault(r["geo"], []).append([r["jaar"], r["waarde"], r["status"]])
        st = status.get(id_, {})
        if "afgeleid" in ind:
            bron = {"instelling": "Berekend", "formule": ind["afgeleid"]["formule"], "invoer": ind["afgeleid"]["invoer"]}
        else:
            b = ind["bron"]
            pagina = infrabel.pagina_url(b["dataset"]) if b["instelling"] == "Infrabel" else eurostat.databrowser_url(b["dataset"])
            bron = {"instelling": b["instelling"], "dataset": b["dataset"], "filters": b.get("filters", {}),
                    "url": pagina, "api_urls": st.get("api_urls", []),
                    "bijgewerkt_bron": st.get("bijgewerkt_bron"), "laatste_periode": st.get("laatste_periode")}
            if ind.get("regionaal"):
                bron["regionaal_dataset"] = ind["regionaal"]["dataset"]
                bron["regionaal_url"] = eurostat.databrowser_url(ind["regionaal"]["dataset"])
        indicatoren.append({
            "id": id_, "thema": ind["thema"], "titel": ind["titel"], "vraag": ind.get("vraag", ind["titel"]),
            "definitie": ind["definitie"], "uitleg": ind.get("uitleg"), "weergave": ind.get("weergave", "lijn"),
            "beeld": ind.get("beeld"), "wafel_tekst": ind.get("wafel_tekst"), "zoekwoorden": ind.get("zoekwoorden", []),
            "eenheid": ind["eenheid"], "decimalen": ind["decimalen"], "verborgen": ind.get("verborgen", False),
            "norm": ind.get("norm"), "bron": bron, "opgehaald": st.get("opgehaald"),
            "ok": st.get("ok", False), "melding": st.get("melding", ""), "reeksen": reeksen,
        })
    extra = {}
    for naam, _ in EXTRA:
        pad = SCHOON / f"{naam}.json"
        extra[naam] = json.loads(pad.read_text(encoding="utf-8")) if pad.exists() else None
    reg = yaml.safe_load((WORTEL / "config" / "regeringen.yaml").read_text(encoding="utf-8"))
    regeringen = {"bron": reg["bron"], "federaal": [{**r, "van": str(r["van"]), "tot": str(r["tot"]) if r["tot"] else None} for r in reg["federaal"]]}
    uit = {"gegenereerd": tijd, "themas": cat["themas"], "begrippen": cat.get("begrippen", {}),
           "landnamen": cat["landnamen"], "regeringen": regeringen, **extra, "indicatoren": indicatoren}
    SITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    SITE_DATA.write_text(json.dumps(uit, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def schrijf_status(cat: dict, status: dict, tijd: str) -> None:
    regels = [f"# Status van de datapipeline\n", f"Laatste run: {tijd}\n", "| Indicator | Status | Opgehaald | Melding |", "|---|---|---|---|"]
    for ind in cat["indicatoren"]:
        s = status.get(ind["id"], {})
        regels.append(f"| {ind['id']} | {'✅' if s.get('ok') else '❌'} | {s.get('opgehaald') or '—'} | {(s.get('melding', '') + ' ' + s.get('melding_regio', '')).strip().replace('|', '/')} |")
    for naam, _ in EXTRA:
        v = status.get(f"_{naam}", {})
        regels.append(f"| {naam} | {'✅' if v.get('ok') else '❌'} | {v.get('opgehaald') or '—'} | {v.get('melding', '')} |")
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text("\n".join(regels) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
