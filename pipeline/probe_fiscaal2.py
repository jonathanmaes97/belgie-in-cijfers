"""Gerichte verkenning: volledige tekst van pagina's met parameters voor de rekenmodule.

Volgt links op basis van de linktekst (niet de URL) en bewaart de volledige tekst vanaf de
gezochte titel. Schrijft reports/fiscaal2.md.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin

import requests

from .probe_fiscaal import tekst

WORTEL = Path(__file__).resolve().parent.parent
RSZ_START = "https://www.socialsecurity.be/employer/instructions/dmfa/nl/latest/instructions/deductions/workers_deductions/socialbonus.html"
GEZOCHT = {
    "Werknemersbijdragen": re.compile(r"^werknemersbijdragen$|^de werknemersbijdrage", re.I),
    "Werkbonus": re.compile(r"^werkbonus$", re.I),
    "Dubbel vakantiegeld": re.compile(r"inhouding op het dubbel vakantiegeld", re.I),
    "Bijzondere bijdrage": re.compile(r"bijzondere bijdrage voor de sociale zekerheid", re.I),
}
EXTRA = [
    "https://financien.belgium.be/nl/particulieren/belastingaangifte/persoonlijke-situatie/personen-ten-laste/kinderen",
    "https://financien.belgium.be/nl/particulieren/belastingaangifte/aanslagbiljet/gemeentebelasting",
]


def main() -> None:
    s = requests.Session()
    s.headers["User-Agent"] = "belgie-in-cijfers (bronverkenning; github.com/jonathanmaes97/belgie-in-cijfers)"
    uit = ["# Rekenmodule: volledige teksten\n"]
    r = s.get(RSZ_START, timeout=40)
    links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S)
    for label, patroon in GEZOCHT.items():
        for href, linktekst in links:
            t = " ".join(re.sub("<[^>]+>", " ", linktekst).split())
            if patroon.search(t):
                url = urljoin(RSZ_START, href)
                p = s.get(url, timeout=40)
                inhoud = tekst(p.text)
                i = inhoud.rfind(t)
                uit.append(f"## {label}: {url}\n- HTTP {p.status_code}\n```\n{inhoud[max(0, i):][:12000]}\n```\n")
                break
        else:
            uit.append(f"## {label}: geen link gevonden\n")
    for url in EXTRA:
        p = s.get(url, timeout=40)
        inhoud = tekst(p.text)
        i = inhoud.find("Bedragen van de verhoging")
        uit.append(f"## {url}\n- HTTP {p.status_code}\n")
        for href in re.findall(r'href="([^"]+)"', p.text):
            if re.search(r"\.(pdf|xlsx?|csv)", href, re.I):
                v = urljoin(url, href)
                h = s.head(v, timeout=30, allow_redirects=True)
                uit.append(f"- BESTAND {v} → HTTP {h.status_code} {h.headers.get('Content-Type')}")
        uit.append(f"```\n{inhoud[max(0, i):][:4000]}\n```\n")
    (WORTEL / "reports" / "fiscaal2.md").write_text("\n".join(uit) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
