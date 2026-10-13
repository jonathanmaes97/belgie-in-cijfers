"""Fase 0: test welke bronnen buiten Eurostat bereikbaar zijn en wat ze teruggeven.

Schrijft reports/bronnen.md. Dit is een verkenning: de URL's hieronder zijn
kandidaten die we nog moeten bevestigen. Niets hiervan komt al op de site.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import requests

WORTEL = Path(__file__).resolve().parent.parent
RAPPORT = WORTEL / "reports" / "bronnen.md"

KANDIDATEN = [
    ("Statbel", "Open data overzicht", "https://statbel.fgov.be/nl/open-data"),
    ("Statbel", "Bevolking per gemeente (open data)", "https://statbel.fgov.be/nl/open-data/bevolking-naar-woonplaats-nationaliteit-burgerlijke-staat-leeftijd-en-geslacht-10"),
    ("Nationale Bank", "NBB.Stat SDMX-dataflows", "https://stat.nbb.be/restsdmx/sdmx.ashx/GetDataStructure/ALL"),
    ("Nationale Bank", "NBB data-API (nieuw)", "https://nsidisseminate-stat.nbb.be/rest/dataflow/all/all/latest"),
    ("Infrabel", "Open data catalogus: stiptheid", "https://opendata.infrabel.be/api/explore/v2.1/catalog/datasets?where=search(%22punctuality%22)&limit=20"),
    ("iRail", "Stations (NMBS, via iRail)", "https://api.irail.be/stations/?format=json&lang=nl"),
    ("data.gov.be", "Federale open-data catalogus", "https://data.gov.be/api/3/action/package_search?q=statbel&rows=5"),
    ("Sciensano", "Epistat open data", "https://epistat.sciensano.be/"),
    ("Federaal Planbureau", "Indicatoren duurzame ontwikkeling", "https://indicators.be/nl/"),
    ("Statistiek Vlaanderen", "Werkzaamheidsgraad", "https://www.vlaanderen.be/statistiek-vlaanderen/arbeid/werkzaamheidsgraad"),
    ("IWEPS", "Indicateurs Wallonie", "https://www.iweps.be/"),
    ("BISA (Brussel)", "Statistieken Brussel", "https://bisa.brussels/"),
    ("De Kamer", "Kamerleden", "https://www.dekamer.be/kvvcr/showpage.cfm?section=/depute&language=nl&cfm=/site/wwwcfm/depute/cvlist54.cfm"),
    ("Belgium.be", "Federale regering", "https://www.belgium.be/nl/over_belgie/overheid/federale_overheid/federale_regering"),
]


def main() -> None:
    sessie = requests.Session()
    sessie.headers["User-Agent"] = "belgie-in-cijfers (bronverkenning; github.com/jonathanmaes97/belgie-in-cijfers)"
    regels = [
        "# Verkenning van bronnen (fase 0)\n",
        f"Laatste test: {datetime.now(timezone.utc).replace(microsecond=0).isoformat()}\n",
        "Automatisch gegenereerd door `pipeline/probe_sources.py`. ✅ = antwoordt met data, ⚠️ = antwoordt maar mogelijk geen bruikbare data, ❌ = niet bereikbaar.\n",
        "| Instelling | Wat | Status | Type | Eerste tekens van het antwoord |",
        "|---|---|---|---|---|",
    ]
    for instelling, wat, url in KANDIDATEN:
        try:
            r = sessie.get(url, timeout=30)
            soort = r.headers.get("Content-Type", "?").split(";")[0]
            begin = " ".join(r.text[:160].split()).replace("|", "/")
            data_achtig = any(s in soort for s in ("json", "xml", "csv"))
            teken = "✅" if r.ok and data_achtig else ("⚠️" if r.ok else "❌")
            regels.append(f"| {instelling} | [{wat}]({url}) | {teken} HTTP {r.status_code} | {soort} | `{begin}` |")
        except requests.RequestException as e:
            regels.append(f"| {instelling} | [{wat}]({url}) | ❌ | — | {type(e).__name__} |")
        time.sleep(1)
    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text("\n".join(regels) + "\n", encoding="utf-8")
    print(RAPPORT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
