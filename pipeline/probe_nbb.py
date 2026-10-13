"""Verkenning: welke datasets biedt de Nationale Bank (NBB.Stat, SDMX-API) en hoe zien ze eruit?

Schrijft reports/nbb.md: alle dataflows (id + naam), en voor dataflows met interessante
trefwoorden een staal van de data in SDMX-CSV.
"""
from __future__ import annotations

import re
from pathlib import Path

import requests

WORTEL = Path(__file__).resolve().parent.parent
API = "https://nsidisseminate-stat.nbb.be/rest"
TREFWOORDEN = re.compile(r"consum|vertrouw|confidence|barometer|conjunct|business survey|faillis|bankrupt|unemploy|werklo|"
                         r"quarterly national|kwartaal|flash|gdp|bbp|hicp|inflation|employment|werkgelegen", re.I)


def main() -> None:
    s = requests.Session()
    s.headers["User-Agent"] = "belgie-in-cijfers (bronverkenning; github.com/jonathanmaes97/belgie-in-cijfers)"
    regels = ["# Nationale Bank (NBB.Stat): beschikbare datasets\n"]
    r = s.get(f"{API}/dataflow/all/all/latest", timeout=60, headers={"Accept": "application/vnd.sdmx.structure+json;version=1.0"})
    regels.append(f"Dataflow-lijst: HTTP {r.status_code}, {r.headers.get('Content-Type')}\n")
    flows = []
    try:
        data = r.json()
        for f in data["data"]["dataflows"]:
            naam = f.get("names", {}).get("en") or f.get("name") or ""
            flows.append((f["agencyID"], f["id"], f.get("version", "latest"), naam))
    except Exception:
        for agency, fid, versie, naam in re.findall(r'<structure:Dataflow[^>]*agencyID="([^"]+)"[^>]*id="([^"]+)"[^>]*version="([^"]+)".*?<common:Name xml:lang="en">([^<]*)', r.text, re.S):
            flows.append((agency, fid, versie, naam))
    regels.append(f"Aantal dataflows: {len(flows)}\n")
    regels.append("| agency | id | versie | naam |\n|---|---|---|---|")
    for a, i, v, n in flows:
        regels.append(f"| {a} | `{i}` | {v} | {n} |")
    regels.append("\n## Stalen van interessante datasets\n")
    gekozen = [f for f in flows if TREFWOORDEN.search(f[3] + " " + f[1])][:25]
    for a, i, v, n in gekozen:
        u = f"{API}/data/{a},{i},{v}/all?lastNObservations=3&format=csvfilewithlabels"
        try:
            d = s.get(u, timeout=60)
            regels.append(f"### `{i}`: {n}\n- {u}\n- HTTP {d.status_code}, {d.headers.get('Content-Type')}\n```")
            regels += d.text.splitlines()[:12]
            regels.append("```\n")
        except requests.RequestException as e:
            regels.append(f"### `{i}`: fout {type(e).__name__}\n")
    (WORTEL / "reports" / "nbb.md").write_text("\n".join(regels) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
