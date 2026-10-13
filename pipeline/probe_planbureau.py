"""Verkenning: waar publiceren het Federaal Planbureau en Statbel hun inflatievooruitzichten,
spilindex en indexcijfers in een machineleesbare vorm (CSV, Excel, API)?

Schrijft reports/planbureau.md. Niets hiervan komt al op de site.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin

import requests

WORTEL = Path(__file__).resolve().parent.parent
STARTPAGINAS = [
    "https://www.plan.be/nl",
    "https://www.plan.be/nl/inflatievooruitzichten",
    "https://www.plan.be/nl/publicaties",
    "https://www.plan.be/databases",
    "https://statbel.fgov.be/nl/themas/consumptieprijsindex",
    "https://statbel.fgov.be/nl/open-data?category=All&keys=consumptieprijsindex",
]
INTERESSANT = re.compile(r"inflat|spilindex|indexcijfer|consumptieprijs|prijsindex|gezondheidsindex|forecast|vooruitzicht|databas|open-data", re.I)
BESTAND = re.compile(r"\.(xlsx?|csv|txt|zip|json)(\?|$)", re.I)


def main() -> None:
    s = requests.Session()
    s.headers["User-Agent"] = "belgie-in-cijfers (bronverkenning; github.com/jonathanmaes97/belgie-in-cijfers)"
    regels = ["# Planbureau en Statbel: inflatie, spilindex, indexcijfers\n"]
    gezien = set()
    te_bezoeken = list(STARTPAGINAS)
    bezocht = 0
    while te_bezoeken and bezocht < 25:
        url = te_bezoeken.pop(0)
        if url in gezien:
            continue
        gezien.add(url)
        bezocht += 1
        try:
            r = s.get(url, timeout=30)
        except requests.RequestException as e:
            regels.append(f"## {url}\n- fout: {type(e).__name__}\n")
            continue
        regels.append(f"## {url}\n- HTTP {r.status_code}, {r.headers.get('Content-Type', '?')}")
        if not r.ok or "html" not in r.headers.get("Content-Type", ""):
            continue
        links = set()
        for href, tekst in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S):
            volledig = urljoin(url, href)
            tekst = " ".join(re.sub("<[^>]+>", " ", tekst).split())[:90]
            if BESTAND.search(volledig) or INTERESSANT.search(volledig + " " + tekst):
                links.add((volledig, tekst))
        for volledig, tekst in sorted(links)[:40]:
            soort = "BESTAND" if BESTAND.search(volledig) else "pagina"
            regels.append(f"  - [{soort}] {tekst or '(geen tekst)'} → {volledig}")
            if soort == "pagina" and INTERESSANT.search(volledig) and ("plan.be" in volledig or "statbel" in volledig):
                te_bezoeken.append(volledig)
        regels.append("")
    pad = WORTEL / "reports" / "planbureau.md"
    pad.write_text("\n".join(regels) + "\n", encoding="utf-8")
    print(pad.read_text(encoding="utf-8")[:4000])


if __name__ == "__main__":
    main()
