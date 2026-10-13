"""Officiële maximumprijzen van benzine en diesel, van de FOD Economie.

De FOD Economie legt volgens de programmaovereenkomst met de sector maximumprijzen vast voor aardolieproducten.
Twee PDF's van de Algemene Directie Energie:
- de geldende lijst ("Officiële maximumprijzen"), met de prijs die vanaf een bepaalde dag geldt;
- per maand de gemiddelde maximumprijzen ("Pmax-gemiddelden-MM-JJJJ.pdf").

Wij lezen de prijs inclusief btw van Benzine 95 RON E10 en Diesel B7 (de gewone brandstoffen aan de pomp).
Controle: de prijs met btw moet gelijk zijn aan de prijs zonder btw maal 1,21 (op afronding na).
Maanden die we al hebben, worden niet opnieuw opgehaald, behalve de laatste twee.

Bron: https://economie.fgov.be/nl/themas/energie/energieprijzen/maximumprijzen
"""
from __future__ import annotations

import io
import json
import re
from datetime import date
from pathlib import Path

import requests

from .eurostat import BronFout

PAGINA = "https://economie.fgov.be/nl/themas/energie/energieprijzen/maximumprijzen/officieel-tarief-van-de"
BASIS = "https://economie.fgov.be/sites/default/files/Files/Energy/prices/"
LIJST = BASIS + "Officiele-Maximumtarieven-aardolieproducten.pdf"
MAAND = BASIS + "Pmax-gemiddelden-{m:02d}-{j}.pdf"
UA = {"User-Agent": "belgie-in-cijfers (open data dashboard; github.com/jonathanmaes97/belgie-in-cijfers)"}
EERSTE_MAAND = (2023, 1)
VORIG = Path(__file__).resolve().parent.parent / "data" / "clean" / "brandstof.json"

PRODUCTEN = {  # id: naam zoals in de PDF's
    "benzine": "Benzine 95 RON E10",
    "diesel": "Diesel B7",
}
G = r"(\d+,\d+)"


def _getal(s: str) -> float:
    return float(s.replace(",", "."))


def _controle(naam: str, excl: float, incl: float) -> None:
    if abs(excl * 1.21 - incl) > 0.002:
        raise BronFout(f"FOD Economie, {naam}: {excl} zonder btw past niet bij {incl} met btw.")


def lees_lijst(tekst: str) -> dict:
    """De geldende lijst: {'geldig_vanaf': 'JJJJ-MM-DD', 'lijst': '2026/198', product-id: prijs incl. btw}."""
    plat = " ".join(tekst.split())
    m = re.search(r"geldig vanaf\s*:\s*(\d{2})/(\d{2})/(\d{4})", plat)
    nr = re.search(r"Lijst nr\s*:\s*(\S+)", plat)
    if not m:
        raise BronFout("FOD Economie: datum 'geldig vanaf' niet gevonden in de lijst met maximumprijzen.")
    uit = {"geldig_vanaf": f"{m.group(3)}-{m.group(2)}-{m.group(1)}", "lijst": nr.group(1) if nr else ""}
    for pid, naam in PRODUCTEN.items():
        r = re.search(re.escape(naam) + rf" aan de pomp l {G}(?: \([-+]?\d+,\d+\))? 21 {G}", plat)
        if not r:
            raise BronFout(f"FOD Economie: '{naam} aan de pomp' niet gevonden in de lijst met maximumprijzen.")
        excl, incl = _getal(r.group(1)), _getal(r.group(2))
        _controle(naam, excl, incl)
        uit[pid] = incl
    return uit


def lees_maand(tekst: str) -> dict[str, float]:
    """Een maand-PDF: {product-id: gemiddelde maximumprijs incl. btw}."""
    uit = {}
    for pid, naam in PRODUCTEN.items():
        r = re.search(rf"^{re.escape(naam)} {G} {G}\s*$", tekst, flags=re.M)
        if not r:
            raise BronFout(f"FOD Economie: '{naam}' niet gevonden in de maandgemiddelden.")
        excl, incl = _getal(r.group(1)), _getal(r.group(2))
        _controle(naam, excl, incl)
        uit[pid] = incl
    return uit


def _pdf_tekst(inhoud: bytes) -> str:
    from pypdf import PdfReader
    return (PdfReader(io.BytesIO(inhoud)).pages[0].extract_text() or "")


def _maanden(tot: date):
    j, m = EERSTE_MAAND
    while (j, m) < (tot.year, tot.month):
        yield j, m
        j, m = (j + 1, 1) if m == 12 else (j, m + 1)


def haal_op() -> dict:
    s = requests.Session()
    s.headers.update(UA)
    try:
        r = s.get(LIJST, timeout=90)
    except requests.RequestException as e:
        raise BronFout(f"netwerkfout: {e}")
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise BronFout(f"HTTP {r.status_code} voor de lijst met maximumprijzen.")
    nu = lees_lijst(_pdf_tekst(r.content))

    # maandgemiddelden: wat we al hebben, hergebruiken (behalve de laatste twee maanden)
    oud: dict[str, dict[str, float]] = {}
    if VORIG.exists():
        for reeks in json.loads(VORIG.read_text(encoding="utf-8")).get("reeksen", []):
            for p in reeks["punten"]:
                oud.setdefault(p[0], {})[reeks["id"]] = p[1]
    alle = list(_maanden(date.today()))
    maanden: dict[str, dict[str, float]] = {}
    for j, m in alle:
        sleutel = f"{j}-{m:02d}"
        if sleutel in oud and len(oud[sleutel]) == len(PRODUCTEN) and (j, m) not in alle[-2:]:
            maanden[sleutel] = oud[sleutel]
            continue
        try:
            q = s.get(MAAND.format(m=m, j=j), timeout=90)
        except requests.RequestException:
            continue
        if q.status_code == 200 and q.content.startswith(b"%PDF"):
            maanden[sleutel] = lees_maand(_pdf_tekst(q.content))
        elif sleutel in oud and len(oud[sleutel]) == len(PRODUCTEN):
            maanden[sleutel] = oud[sleutel]
    if len(maanden) < 3:
        raise BronFout("FOD Economie: te weinig maandgemiddelden gevonden.")

    teksten = {
        "benzine": ("Maximumprijs benzine", "Wat kost een liter benzine?",
                    "De officiële maximumprijs voor Benzine 95 RON E10 aan de pomp, met btw, zoals de FOD Economie die vastlegt. "
                    "Tankstations mogen niet meer vragen, wel minder. Het grote cijfer is de prijs die nu geldt; de grafiek toont het gemiddelde per maand."),
        "diesel": ("Maximumprijs diesel", "Wat kost een liter diesel?",
                   "De officiële maximumprijs voor Diesel B7 aan de pomp, met btw, zoals de FOD Economie die vastlegt. "
                   "Tankstations mogen niet meer vragen, wel minder. Het grote cijfer is de prijs die nu geldt; de grafiek toont het gemiddelde per maand."),
    }
    reeksen = []
    for pid in PRODUCTEN:
        titel, vraag, uitleg = teksten[pid]
        reeksen.append({
            "id": pid, "titel": {"nl": titel}, "vraag": {"nl": vraag}, "uitleg": {"nl": uitleg},
            "eenheid": "€/l", "decimalen": 3,
            "punten": [[k, v[pid], ""] for k, v in sorted(maanden.items()) if pid in v],
            "nu": {"waarde": nu[pid], "geldig_vanaf": nu["geldig_vanaf"], "lijst": nu["lijst"]},
            "api_url": LIJST,
            "bron": {"instelling": "FOD Economie", "naam": {"nl": "FOD Economie (maximumprijzen)"}, "url": PAGINA, "dataset": "Officiële maximumprijzen aardolieproducten"},
        })
    return {"reeksen": reeksen}
