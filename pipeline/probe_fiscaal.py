"""Verkenning: officiële fiscale parameters bij FOD Financiën (belastingschijven, belastingvrije som,
beroepskosten, gemeentebelasting) en sociale bijdragen bij de RSZ.

Schrijft reports/fiscaal.md met de leesbare tekst van de relevante pagina's en alle downloadlinks.
"""
from __future__ import annotations

import re
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

import requests

WORTEL = Path(__file__).resolve().parent.parent
START = [
    "https://financien.belgium.be/nl/particulieren/belastingaangifte/belastingtarieven-inkomsten",
    "https://financien.belgium.be/nl/particulieren/belastingaangifte/belastingtarieven-inkomsten/belastingtarieven",
    "https://financien.belgium.be/nl/particulieren/belastingaangifte/belastingtarieven-inkomsten/belastingvrije-som",
    "https://financien.belgium.be/nl/particulieren/belastingaangifte/belastingtarieven-inkomsten/gemeentebelasting",
    "https://financien.belgium.be/nl/particulieren/belastingaangifte/aangifte/beroepskosten",
    "https://www.socialsecurity.be/employer/instructions/dmfa/nl/latest/instructions/socialsecuritycontributions/contributions.html",
    "https://www.socialsecurity.be/employer/instructions/dmfa/nl/latest/instructions/deductions/workers_deductions/socialbonus.html",
]
RELEVANT = re.compile(r"belastingtarie|belastingvrije|beroepskosten|gemeentebelasting|aanvullende|opcentiem|werkbonus|bijzondere bijdrage|socialsecuritycontributions|socialbonus|indexering|geindexeerd|geïndexeerd", re.I)


def tekst(html: str) -> str:
    html = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</tr>|</h\d>", "\n", html)
    html = re.sub(r"(?i)</td>|</th>", " | ", html)
    t = unescape(re.sub(r"<[^>]+>", " ", html))
    regels = [" ".join(r.split()) for r in t.splitlines()]
    return "\n".join(r for r in regels if r)


def main() -> None:
    s = requests.Session()
    s.headers["User-Agent"] = "belgie-in-cijfers (bronverkenning; github.com/jonathanmaes97/belgie-in-cijfers)"
    uit = ["# Fiscale en sociale parameters: officiële pagina's\n"]
    rij, gezien = list(START), set()
    while rij and len(gezien) < 18:
        url = rij.pop(0)
        if url in gezien:
            continue
        gezien.add(url)
        try:
            r = s.get(url, timeout=40)
        except requests.RequestException as e:
            uit.append(f"## {url}\n- fout {type(e).__name__}\n")
            continue
        uit.append(f"## {url}\n- HTTP {r.status_code}, {r.headers.get('Content-Type')}\n")
        if not r.ok or "html" not in r.headers.get("Content-Type", ""):
            continue
        for href in re.findall(r'href="([^"]+)"', r.text):
            v = urljoin(url, href).split("#")[0]
            if re.search(r"\.(pdf|xlsx?|csv)$", v, re.I):
                uit.append(f"- BESTAND: {v}")
            elif RELEVANT.search(v) and v not in gezien and ("financien.belgium.be/nl/particulieren" in v or "socialsecurity.be" in v):
                rij.append(v)
        uit.append("```")
        uit.append(tekst(r.text)[:6000])
        uit.append("```\n")
    (WORTEL / "reports" / "fiscaal.md").write_text("\n".join(uit) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
