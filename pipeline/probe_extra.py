"""Verkenning voor nieuwe onderdelen: PISA, energieprijzen, mazout en de BBSZ.

Draait enkel bij een handmatige start van de workflow. Schrijft reports/extra.md.
"""
from __future__ import annotations

import io
import re
from pathlib import Path

import requests

from .probe_fiscaal import tekst

WORTEL = Path(__file__).resolve().parent.parent
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{ds}?geo=BE&lastTimePeriod=2&lang=EN"
DATASETS = ["sdg_04_40", "nrg_pc_204", "nrg_pc_202", "educ_outc_pisa"]
OLIE = "https://energy.ec.europa.eu/document/download/906e60ca-8b6a-44e7-8589-652854d2fd3f_en?filename=Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx"
BBSZ = [
    "https://www.socialsecurity.be/employer/instructions/dmfa/nl/latest/instructions/special_contributions/other_specialcontributions/specialsocialsecuritycontribution.html",
    "https://www.ejustice.just.fgov.be/eli/wet/1994/03/30/1994000287/justel",
]


def eurostat(s: requests.Session, uit: list[str]) -> None:
    for ds in DATASETS:
        r = s.get(EUROSTAT.format(ds=ds), timeout=60)
        uit.append(f"## Eurostat {ds}\n- HTTP {r.status_code}")
        if r.status_code != 200:
            uit.append(f"```\n{r.text[:500]}\n```")
            continue
        j = r.json()
        uit.append(f"- titel: {j.get('label')}\n- bijgewerkt: {j.get('updated')}")
        for dim in j["id"]:
            cat = j["dimension"][dim]["category"]
            labels = cat.get("label", {})
            waarden = ", ".join(f"{k} ({labels.get(k, '')})" for k in list(cat["index"])[:60])
            uit.append(f"- **{dim}**: {waarden}")
        waarden = list(j.get("value", {}).items())[:12]
        uit.append(f"- eerste waarden: {waarden}\n")


def olie(s: requests.Session, uit: list[str]) -> None:
    import openpyxl
    r = s.get(OLIE, timeout=120)
    uit.append(f"## Weekly Oil Bulletin, historiek\n- HTTP {r.status_code}, {len(r.content)} bytes, {r.headers.get('Content-Type')}")
    if r.status_code != 200:
        return
    wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True, data_only=True)
    for ws in wb.worksheets:
        uit.append(f"### blad {ws.title!r} ({ws.max_row} rijen × {ws.max_column} kolommen)")
        for i, rij in enumerate(ws.iter_rows(values_only=True)):
            if i >= 8:
                break
            uit.append("    " + " | ".join("" if v is None else str(v)[:40] for v in rij[:40]))


def bbsz(s: requests.Session, uit: list[str]) -> None:
    for url in BBSZ:
        r = s.get(url, timeout=60)
        t = tekst(r.text)
        uit.append(f"## BBSZ: {url}\n- HTTP {r.status_code}, {len(t)} tekens")
        if "ejustice" in url:
            for m in re.finditer(r"Art\.\s*10[6-9]\b", t):
                uit.append(f"```\n{t[m.start():m.start() + 6000]}\n```")
                break
        else:
            i = t.lower().find("bijzondere bijdrage")
            uit.append(f"```\n{t[max(0, i):][:15000]}\n```")


def main() -> None:
    s = requests.Session()
    s.headers["User-Agent"] = "belgie-in-cijfers (bronverkenning; github.com/jonathanmaes97/belgie-in-cijfers)"
    uit = ["# Verkenning: PISA, energieprijzen, mazout, BBSZ\n"]
    for stap in (eurostat, olie, bbsz):
        try:
            stap(s, uit)
        except Exception as e:  # een verkenning mag nooit de publicatie tegenhouden
            uit.append(f"## {stap.__name__}: FOUT {type(e).__name__}: {e}\n")
    (WORTEL / "reports" / "extra.md").write_text("\n".join(uit) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
