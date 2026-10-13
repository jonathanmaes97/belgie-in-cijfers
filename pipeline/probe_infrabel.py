"""Verkenning: welke datasets over stiptheid biedt Infrabel aan, en met welke velden?

Schrijft reports/infrabel.md. Draait in GitHub Actions (Infrabel staat geen
automatische lezers toe buiten gewone API-aanroepen).
"""
from __future__ import annotations

from pathlib import Path

import requests

WORTEL = Path(__file__).resolve().parent.parent
API = "https://opendata.infrabel.be/api/explore/v2.1"


def main() -> None:
    s = requests.Session()
    s.headers["User-Agent"] = "belgie-in-cijfers (bronverkenning; github.com/jonathanmaes97/belgie-in-cijfers)"
    regels = ["# Infrabel: datasets over stiptheid\n"]
    for zoek in ("punctuality", "stiptheid", "ponctualite", "retard"):
        r = s.get(f"{API}/catalog/datasets", params={"where": f'search("{zoek}")', "limit": 20}, timeout=30)
        if not r.ok:
            regels.append(f"Zoekterm `{zoek}`: HTTP {r.status_code}\n")
            continue
        for ds in r.json().get("results", []):
            ds_id = ds["dataset_id"]
            if any(f"`{ds_id}`" in rg for rg in regels):
                continue
            meta = ds.get("metas", {}).get("default", {})
            regels.append(f"## `{ds_id}`\n")
            regels.append(f"- Titel: {meta.get('title')}")
            regels.append(f"- Laatst gewijzigd: {meta.get('modified')} · records: {meta.get('records_count')}")
            regels.append(f"- Licentie: {meta.get('license')}")
            besch = " ".join(str(meta.get("description") or "").split())[:400]
            regels.append(f"- Beschrijving: {besch}")
            regels.append("- Velden: " + ", ".join(f"`{f['name']}` ({f['type']})" for f in ds.get("fields", [])))
            v = s.get(f"{API}/catalog/datasets/{ds_id}/records", params={"limit": 3, "order_by": ""}, timeout=30)
            if v.ok:
                regels.append("- Voorbeeld: `" + str(v.json().get("results", [])[:3])[:700].replace("`", "'") + "`")
            regels.append("")
    pad = WORTEL / "reports" / "infrabel.md"
    pad.write_text("\n".join(regels) + "\n", encoding="utf-8")
    print(pad.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
