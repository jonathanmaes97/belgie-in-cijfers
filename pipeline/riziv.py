"""Aantal werknemers en werklozen in invaliditeit (langer dan een jaar arbeidsongeschikt), van het RIZIV.

Het RIZIV publiceert elk jaar een PDF "Statistieken over de invaliditeit" met in tabel 1 het aantal
invaliden op 31 december, voor de laatste vijf jaar. Wij lezen enkel de regel "Algemeen totaal" van tabel 1
en controleren dat de som van arbeiders en bedienden klopt. Recentere PDF's overschrijven oudere jaren
(het RIZIV stelt cijfers soms nog bij); jaren met (*) zijn volgens het RIZIV voorlopig.

Bron: https://www.inami.fgov.be/nl/statistieken/statistieken-uitkeringen
"""
from __future__ import annotations

import io
import re
from datetime import date

import requests

from .eurostat import BronFout, Resultaat, Waarneming

PDF = "https://www.inami.fgov.be/SiteCollectionDocuments/stat_du{jaar}_1_invaliditeit.pdf"
PAGINA = "https://www.inami.fgov.be/nl/statistieken/statistieken-uitkeringen"
UA = {"User-Agent": "belgie-in-cijfers (open data dashboard; github.com/jonathanmaes97/belgie-in-cijfers)"}
EERSTE_PDF = 2015


GETAL = r"\d{1,3}(?:\.\d{3})+|\d+"


def lees_tabel1(tekst: str) -> dict[int, tuple[int, bool]]:
    """Geeft {jaar: (aantal, voorlopig)} uit de tekst van pagina 1 (tabel 1).

    De opmaak verschilt per jaar (alles op één regel of elk getal apart), dus we werken op de tekst met
    samengevoegde witruimte: eerst vijf jaartallen, dan drie keer "Totaal" met vijf getallen
    (arbeiders, bedienden, algemeen totaal; het laatste heet soms "Algemeen totaal").
    """
    plat = " ".join(tekst.split())
    begin = plat.find("Arbeiders")
    kop = re.search(r"((?:20\d\d(?:\s*\(\*\))?\s*){5})", plat[:begin] if begin > 0 else plat)
    if not kop or begin < 0:
        raise BronFout("RIZIV: jaartallen of 'Arbeiders' van tabel 1 niet gevonden.")
    jaren = [int(m.group(1)) for m in re.finditer(r"(20\d\d)", kop.group(1))]
    voorlopig = [bool(m.group(2)) for m in re.finditer(r"(20\d\d)(\s*\(\*\))?", kop.group(1))]
    rijen = [[int(x.replace(".", "")) for x in re.findall(GETAL, m.group(1))]
             for m in re.finditer(rf"(?:Algemeen totaal|Totaal) ((?:(?:{GETAL}) ){{4}}(?:{GETAL}))(?=\s|$)", plat[begin:])]
    if len(rijen) < 3:
        raise BronFout("RIZIV: de drie totalen van tabel 1 niet gevonden.")
    arb, bed, alg = rijen[0], rijen[1], rijen[2]
    for j, a, b, c in zip(jaren, alg, arb, bed):
        if b + c != a:
            raise BronFout(f"RIZIV {j}: arbeiders ({b}) + bedienden ({c}) is niet het totaal ({a}).")
    return {j: (a, v) for j, a, v in zip(jaren, alg, voorlopig)}


def haal_op(bron: dict | None = None) -> Resultaat:
    from pypdf import PdfReader
    s = requests.Session()
    s.headers.update(UA)
    reeks: dict[int, tuple[int, bool]] = {}
    urls = []
    fout = None
    for jaar in range(EERSTE_PDF, date.today().year + 1):
        url = PDF.format(jaar=jaar)
        try:
            r = s.get(url, timeout=90)
        except requests.RequestException:
            continue
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            continue
        try:
            tekst = PdfReader(io.BytesIO(r.content)).pages[0].extract_text() or ""
            reeks.update(lees_tabel1(tekst))  # latere PDF's overschrijven oudere jaren
            urls.append(url)
            fout = None
        except Exception as e:  # een oudere PDF die niet leesbaar is, laten we vallen; de recentste moet lukken
            fout = f"RIZIV-PDF {jaar} onleesbaar: {type(e).__name__}: {e}"
    if fout:
        raise BronFout(fout)
    if len(reeks) < 5:
        raise BronFout("RIZIV: te weinig jaren gevonden in de PDF's.")
    w = [Waarneming("BE", j, float(a), "p" if v else "") for j, (a, v) in sorted(reeks.items())]
    return Resultaat(waarnemingen=w, bijgewerkt_bron=None, url=urls[-1])
