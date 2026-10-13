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
    "https://financien.belgium.be/nl/particulieren/belastingaangifte/inkomsten",
    "https://financien.belgium.be/nl/particulieren/belastingaangifte/persoonlijke-situatie/personen-ten-laste",
]
# alleen pagina's onder deze paden volgen (schijven, beroepskosten, belastingvrije som, kinderen ten laste)
VOLG = re.compile(r"/belastingaangifte/(inkomsten|persoonlijke-situatie)/", re.I)
RELEVANT = re.compile(r"tarie|belastingvrije|beroepskosten|gemeentebelasting|aanvullende|opcentiem|werkbonus|bijzondere-bijdrage|socialbonus|indexering|geindexeerd|belastingaangifte|berekening|particulieren/belasting", re.I)


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
    while rij and len(gezien) < 30:
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
            elif VOLG.search(v) and v not in gezien and "financien.belgium.be/nl/particulieren" in v:
                rij.append(v)
        uit.append("```")
        t = tekst(r.text)
        if "socialsecurity.be" in url:
            i = t.find("Werkbonus")
            t = t[i:] if i >= 0 else t
        uit.append(t[:9000])
        uit.append("```\n")
    # lijst gemeentebelasting
    import io
    import openpyxl
    for u in ("https://financien.belgium.be/sites/default/files/media/documents/tarieven-gemeentebelasting-2026.xlsx",):
        r = s.get(u, timeout=60)
        uit.append(f"## {u}\n- HTTP {r.status_code}, {len(r.content)} bytes\n```")
        if r.ok:
            wb = openpyxl.load_workbook(io.BytesIO(r.content), data_only=True, read_only=True)
            for ws in wb.worksheets:
                uit.append(f"[blad {ws.title}]")
                for i, rij in enumerate(ws.iter_rows(values_only=True)):
                    if i < 15 or i % 100 == 0:
                        uit.append(f"{i + 1}: " + " | ".join("" if c is None else str(c)[:30] for c in rij[:10]))
        uit.append("```")
    (WORTEL / "reports" / "fiscaal.md").write_text("\n".join(uit) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
