"""Bouwt site/index.html op uit site/data/dashboard.json.

De kerncijfers staan rechtstreeks in de HTML, zodat ze ook zonder JavaScript
zichtbaar zijn (en in previews op sociale media). JavaScript tekent enkel de grafieken.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from html import escape
from pathlib import Path

WORTEL = Path(__file__).resolve().parent.parent
SITE = WORTEL / "site"
REPO_URL = "https://github.com/jonathanmaes97/belgie-in-cijfers"

KERNCIJFERS = ["schuld_per_inwoner", "rente_per_dag", "bbp_groei", "werkzaamheidsgraad", "inflatie", "levensverwachting"]
MAANDEN = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
VLAGGEN = {"p": "voorlopig", "e": "geschat", "b": "breuk in reeks", "d": "definitie wijkt af", "u": "onbetrouwbaar"}


def getal(x: float, decimalen: int) -> str:
    s = f"{abs(x):,.{decimalen}f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    return ("−" if x < 0 else "") + s


def met_eenheid(x: float, ind: dict) -> str:
    e = ind["eenheid"]
    if e.strip() == "€":
        return "€ " + getal(x, ind["decimalen"])
    if e.strip() == "mln €":
        return "€ " + getal(x, ind["decimalen"]) + " mln"
    return getal(x, ind["decimalen"]) + e


def datum(iso: str | None) -> str:
    if not iso:
        return "onbekend"
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d.day} {MAANDEN[d.month - 1]} {d.year}"


def laatste(ind: dict, geo: str):
    reeks = ind["reeksen"].get(geo) or []
    return reeks[-1] if reeks else None


def waarde_in(ind: dict, geo: str, jaar: int):
    for j, w, s in ind["reeksen"].get(geo) or []:
        if j == jaar:
            return w, s
    return None


def vlag_tekst(status: str) -> str:
    return ", ".join(VLAGGEN.get(c, c) for c in status if c in VLAGGEN)


def bronregel(ind: dict) -> str:
    b = ind["bron"]
    csv = f'<a href="data/csv/{ind["id"]}.csv">CSV</a>'
    if b["instelling"] == "Berekend":
        return f'Berekend uit {", ".join(escape(v) for v in b["invoer"].values())} · {csv}'
    return (f'Bron: <a href="{escape(b["url"])}" rel="noopener">{escape(b["instelling"])} · {escape(b["dataset"])}</a>'
            f' · opgehaald {datum(ind.get("opgehaald"))} · {csv}')


def tegel(ind: dict, data: dict, klein: bool = False) -> str:
    namen = data["landnamen"]
    be = laatste(ind, "BE")
    kop = f'<h3 class="tegel-titel">{escape(ind["titel"]["nl"])}</h3>'
    if not be:
        melding = escape(ind.get("melding") or "Nog niet opgehaald.")
        return f'<article class="tegel leeg" id="{ind["id"]}">{kop}<p class="geen-data">Nog geen cijfers beschikbaar. <span>{melding}</span></p><p class="bron">{bronregel(ind)}</p></article>'
    jaar, waarde, status = be
    vlag = vlag_tekst(status)
    meta = f'<span>België, {jaar}</span>' + (f' <span class="vlag">{escape(vlag)}</span>' if vlag else "")

    vergelijk = []
    eu = waarde_in(ind, "EU27_2020", jaar)
    if eu:
        vergelijk.append(f'EU-27: <b>{met_eenheid(eu[0], ind)}</b>')
    if ind.get("norm"):
        vergelijk.append(f'{escape(ind["norm"]["label"]["nl"])}')
    regio, regio_jaar = [], None
    for code, kort in (("BE2", "Vlaanderen"), ("BE3", "Wallonië"), ("BE1", "Brussel")):
        r = laatste(ind, code)
        if r:
            regio.append(f'{kort} <b>{met_eenheid(r[1], ind)}</b>')
            regio_jaar = regio_jaar or r[0]
    regio_html = ('<p class="regio">' + " · ".join(regio) + f' <span class="jaar">({regio_jaar})</span></p>') if regio else ""

    details = ""
    if not klein:
        b = ind["bron"]
        extra = []
        if b["instelling"] == "Berekend":
            extra.append(f'<dt>Formule</dt><dd><code>{escape(b["formule"])}</code></dd>')
        else:
            for u in b.get("api_urls", []):
                extra.append(f'<dt>Exacte bevraging</dt><dd><a href="{escape(u)}" rel="noopener">API-link</a></dd>')
            if b.get("bijgewerkt_bron"):
                extra.append(f'<dt>Bijgewerkt door bron</dt><dd>{datum(b["bijgewerkt_bron"])}</dd>')
        if ind.get("norm"):
            extra.append(f'<dt>Norm</dt><dd>{escape(ind["norm"]["label"]["nl"])} ({escape(ind["norm"]["bron"])})</dd>')
        if not ind["ok"] and ind.get("melding"):
            extra.append(f'<dt>Laatste update mislukt</dt><dd>{escape(ind["melding"])}. We tonen de laatst geldige cijfers.</dd>')
        details = f'<details><summary>Definitie en bron</summary><p>{escape(ind["definitie"]["nl"])}</p><dl>{"".join(extra)}</dl></details>'

    titel_esc = escape(ind["titel"]["nl"])
    grafiek = "" if klein else f'<div class="grafiek" data-grafiek="{ind["id"]}" role="img" aria-label="Verloop van {titel_esc}"></div>'
    vergelijk_html = '<p class="vergelijk">' + " · ".join(vergelijk) + "</p>" if vergelijk else ""
    klasse = "tegel klein" if klein else "tegel"
    anker = ("k-" if klein else "") + ind["id"]
    return (f'<article class="{klasse}" id="{anker}">{kop}'
            f'<p class="waarde">{met_eenheid(waarde, ind)}</p><p class="meta">{meta}</p>'
            f'{vergelijk_html}{regio_html}{grafiek}{details}<p class="bron">{bronregel(ind)}</p></article>')


def bouw() -> None:
    data = json.loads((SITE / "data" / "dashboard.json").read_text(encoding="utf-8"))
    per_id = {i["id"]: i for i in data["indicatoren"]}

    # CSV-bestanden meekopiëren zodat elke download op de site werkt
    csv_map = SITE / "data" / "csv"
    csv_map.mkdir(parents=True, exist_ok=True)
    for f in (WORTEL / "data" / "clean").glob("*.csv"):
        shutil.copy(f, csv_map / f.name)

    kern = "".join(tegel(per_id[i], data, klein=True) for i in KERNCIJFERS if i in per_id)
    nav, secties = [], []
    for thema in data["themas"]:
        inds = [i for i in data["indicatoren"] if i["thema"] == thema["id"] and not i["verborgen"]]
        if not inds:
            continue
        nav.append(f'<a href="#{thema["id"]}">{escape(thema["nl"])}</a>')
        secties.append(f'<section id="{thema["id"]}"><h2>{escape(thema["nl"])}</h2><div class="raster">{"".join(tegel(i, data) for i in inds)}</div></section>')

    html = SJABLOON.format(
        bijgewerkt=datum(data["gegenereerd"]), kern=kern, nav="".join(nav), secties="".join(secties), repo=REPO_URL,
    )
    (SITE / "index.html").write_text(html, encoding="utf-8")


SJABLOON = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>België in cijfers</title>
<meta name="description" content="Open, onafhankelijk dashboard met de officiële kerncijfers van België. Elk cijfer met bron.">
<meta property="og:title" content="België in cijfers">
<meta property="og:description" content="De officiële kerncijfers van België op één plek. Elk cijfer met bron, automatisch bijgewerkt.">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="kop">
  <div class="binnen">
    <p class="merk"><a href="./">België in cijfers</a></p>
    <nav aria-label="Thema's">{nav}</nav>
  </div>
</header>
<main class="binnen">
  <section class="intro">
    <h1>De officiële kerncijfers van België, op één plek</h1>
    <p>Elk cijfer komt rechtstreeks van een officiële bron en staat er met bronvermelding bij. De site werkt zichzelf dagelijks bij. Laatste update: <b>{bijgewerkt}</b>.</p>
  </section>
  <section aria-labelledby="kern-titel">
    <h2 id="kern-titel" class="visueel-verborgen">Kerncijfers</h2>
    <div class="kern">{kern}</div>
  </section>
  {secties}
  <section id="binnenkort" class="binnenkort">
    <h2>In ontwikkeling</h2>
    <ul>
      <li><b>Loonsimulator:</b> geef je brutoloon in en zie hoeveel belastingen en bijdragen je betaalt.</li>
      <li><b>Wie is bevoegd?</b> Stel je vraag en zie welk bestuursniveau en welke minister bevoegd is.</li>
      <li><b>Meer cijfers:</b> stiptheid van de treinen, wachttijden in de zorg, cijfers per gewest en per gemeente.</li>
    </ul>
  </section>
</main>
<footer class="voet">
  <div class="binnen">
    <p><b>België in cijfers</b> is een onafhankelijk, open project. Alle code en data staan publiek op <a href="{repo}">GitHub</a>, zodat iedereen elk cijfer kan narekenen.</p>
    <p>Cijfers worden door de bronnen soms bijgesteld. Zie de <a href="{repo}/blob/main/data/changelog.json">lijst met herzieningen</a> en de <a href="{repo}/blob/main/reports/status.md">status van elke bron</a>.</p>
    <p>Fout gezien? <a href="{repo}/issues/new">Meld het</a>.</p>
  </div>
</footer>
<script src="app.js" defer></script>
</body>
</html>
"""

if __name__ == "__main__":
    bouw()
