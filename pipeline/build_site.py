"""Bouwt de website op uit site/data/dashboard.json.

Pagina's:
  site/index.html             startpagina: zoeken, kerncijfers, thema's kiezen
  site/thema/<thema>.html     één pagina per thema met uitleg en alle cijfers

Alle cijfers en vergelijkingszinnen staan rechtstreeks in de HTML (werkt ook
zonder JavaScript en in previews op sociale media). JavaScript tekent enkel de
grafieken, de tabbladen, de zoekfunctie en de deelknop.

Zinnen zoals "Dat is meer dan het EU-gemiddelde" worden hier uit de data
berekend. Ze vergelijken enkel (meer, minder, gelijk) en oordelen niet.
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

KERNCIJFERS = ["schuld_per_inwoner", "rente_per_dag", "werkzaamheidsgraad", "treinstiptheid", "inflatie", "levensverwachting"]
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]
VLAGGEN = {"p": "voorlopig", "e": "geschat", "b": "breuk in reeks", "d": "definitie wijkt af", "u": "onbetrouwbaar", "j": "jaar nog bezig"}

# Kleur per thema: alleen om thema's te herkennen, nooit om te oordelen.
THEMA_KLEUR = {
    "economie": "#2357a6", "overheidsfinancien": "#6b3fa0", "werk": "#0b7a6e", "gezondheid": "#b03a5e",
    "onderwijs": "#8f5f00", "wonen_armoede": "#9a4a24", "klimaat_energie": "#2e7d32", "mobiliteit": "#c0461a",
    "demografie": "#4f5f70",
}

_I = '<svg class="icoon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{}</svg>'
ICONEN = {
    "economie": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "overheid": '<path d="M3 10l9-6 9 6"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8"/><path d="M3 21h18"/>',
    "werk": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7"/><path d="M3 13h18"/>',
    "gezondheid": '<path d="M19.5 12.5c1-1.3 1.5-2.6 1.5-4A4.5 4.5 0 0 0 12 6a4.5 4.5 0 0 0-9 2.5C3 14 12 20 12 20s2.6-1.7 4.8-4"/><path d="M3 12h4l2-3 3 6 2-3h7"/>',
    "onderwijs": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11.2V16c3.5 2.5 8.5 2.5 12 0v-4.8"/><path d="M22 9v6"/>',
    "wonen": '<path d="M3 11l9-7 9 7"/><path d="M5 9.5V20h14V9.5"/><path d="M10 20v-6h4v6"/>',
    "klimaat": '<path d="M5 20c0-9 5.5-15 15-15 0 9.5-6 15-15 15z"/><path d="M5 20l9-9"/>',
    "mobiliteit": '<rect x="5" y="3" width="14" height="14" rx="3"/><path d="M5 10h14"/><path d="M8.5 21l1.5-4M15.5 21l-1.5-4"/><path d="M9 13.5h.01M15 13.5h.01"/>',
    "bevolking": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.3"/><path d="M16 14.2c2.8.2 5 2.6 5 5.8"/>',
    "zoek": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "deel": '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.2 10.8l7.6-4.4M8.2 13.2l7.6 4.4"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
    "pijl": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "terug": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "bron": '<path d="M4 5a2 2 0 0 1 2-2h9l5 5v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M14 3v5h5M8 13h8M8 17h5"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "klok": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "code": '<path d="M8 8l-4 4 4 4M16 8l4 4-4 4M13.5 5l-3 14"/>',
}


def icoon(naam: str) -> str:
    return _I.format(ICONEN.get(naam, ""))


# ---------------------------------------------------------------- opmaak van getallen

def getal(x: float, decimalen: int) -> str:
    s = f"{abs(x):,.{decimalen}f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    return ("−" if x < 0 and round(abs(x), decimalen) != 0 else "") + s


def met_eenheid(x: float, ind: dict) -> str:
    e = ind["eenheid"]
    if e.strip() == "€":
        return "€ " + getal(x, ind["decimalen"])
    if e.strip() == "mln €":
        return "€ " + getal(x, ind["decimalen"]) + " miljoen"
    if e.strip() == "% bbp":
        return getal(x, ind["decimalen"]) + "% van het bbp"
    return getal(x, ind["decimalen"]) + e


def kort_met_eenheid(x: float, ind: dict) -> str:
    """Kortere vorm voor grote cijfers op tegels."""
    e = ind["eenheid"].strip()
    if e == "mln €":
        return "€ " + getal(x, ind["decimalen"]) + " mln"
    if e == "% bbp":
        return getal(x, ind["decimalen"]) + "%"
    return met_eenheid(x, ind)


def datum(iso: str | None) -> str:
    if not iso:
        return "onbekend"
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d.day} {MAANDEN[d.month - 1]} {d.year}"


def maand_tekst(periode: str | None) -> str:
    if not periode or len(periode) < 7:
        return ""
    return f"{MAANDEN[int(periode[5:7]) - 1]} {periode[:4]}"


# ---------------------------------------------------------------- data-hulpjes

def laatste(ind: dict, geo: str):
    reeks = ind["reeksen"].get(geo) or []
    return reeks[-1] if reeks else None


def waarde_in(ind: dict, geo: str, jaar: int):
    for j, w, s in ind["reeksen"].get(geo) or []:
        if j == jaar:
            return w
    return None


def vlag_tekst(status: str) -> str:
    return ", ".join(VLAGGEN[c] for c in status if c in VLAGGEN)


def vergelijk_woord(a: float, b: float, ind: dict) -> str:
    """'hoger dan' / 'lager dan' / 'gelijk aan', op de getoonde precisie."""
    if round(a, ind["decimalen"]) == round(b, ind["decimalen"]):
        return "gelijk aan"
    return "hoger dan" if a > b else "lager dan"


def zinnen(ind: dict) -> list[str]:
    """Neutrale, uit de data berekende zinnen die het cijfer in context plaatsen."""
    be = laatste(ind, "BE")
    if not be:
        return []
    jaar, waarde, status = be
    uit = []
    eu = waarde_in(ind, "EU27_2020", jaar)
    if eu is not None:
        uit.append(f"Dat is {vergelijk_woord(waarde, eu, ind)} het EU-gemiddelde ({kort_met_eenheid(eu, ind)}).")
    reeks = ind["reeksen"]["BE"]
    vroeger = next((r for r in reeks if r[0] == jaar - 10), None) or (reeks[0] if len(reeks) > 3 and reeks[0][0] < jaar else None)
    if vroeger:
        uit.append(f"In {vroeger[0]} was dit {kort_met_eenheid(vroeger[1], ind)}.")
    if "j" in status and ind["bron"].get("laatste_periode"):
        uit.append(f"Cijfer voor {jaar} tot en met {maand_tekst(ind['bron']['laatste_periode'])}.")
    return uit


# ---------------------------------------------------------------- beelden zonder JavaScript

def wafel(ind: dict, kleur: str) -> str:
    be = laatste(ind, "BE")
    if not be or not ind.get("wafel_tekst"):
        return ""
    n = max(0, min(100, round(be[1])))
    vakjes = []
    for i in range(100):
        x, y = (i % 10) * 11, (i // 10) * 11
        vol = i < n
        vakjes.append(f'<rect x="{x}" y="{y}" width="9" height="9" rx="2" class="{"vol" if vol else "leeg"}"/>')
    tekst = escape(ind["wafel_tekst"]["nl"])
    return (f'<figure class="beeld wafel"><svg viewBox="0 0 109 109" role="img" aria-label="{n} op de 100">{"".join(vakjes)}</svg>'
            f'<figcaption><b>Ongeveer {n} op de 100</b> {tekst}.</figcaption></figure>')


def doel(ind: dict) -> str:
    be, norm = laatste(ind, "BE"), ind.get("norm")
    if not be or not norm:
        return ""
    jaar, w, _ = be
    eu = waarde_in(ind, "EU27_2020", jaar)
    lo = 50.0
    hi = 100.0
    pos = lambda v: max(0.0, min(100.0, (v - lo) / (hi - lo) * 100))
    afstand = norm["waarde"] - w
    zin = (f"Nog <b>{getal(afstand, ind['decimalen'])} procentpunt</b> tot het doel." if afstand > 0
           else "Het doel is bereikt.")
    eu_html = f'<span class="markering eu" style="left:{pos(eu):.1f}%"><span>EU {getal(eu, ind["decimalen"])}%</span></span>' if eu is not None else ""
    return (f'<figure class="beeld doel"><div class="balk" role="img" aria-label="België {getal(w, ind["decimalen"])}%, doel {getal(norm["waarde"], 0)}%">'
            f'<div class="vulling" style="width:{pos(w):.1f}%"></div>'
            f'<span class="markering norm" style="left:{pos(norm["waarde"]):.1f}%"><span>Doel {getal(norm["waarde"], 0)}%</span></span>{eu_html}</div>'
            f'<div class="schaal"><span>{getal(lo, 0)}%</span><span>{getal(hi, 0)}%</span></div>'
            f'<figcaption>{zin}</figcaption></figure>')


# ---------------------------------------------------------------- onderdelen

def bronregel(ind: dict, pad: str) -> str:
    b = ind["bron"]
    csv = f'<a href="{pad}data/csv/{ind["id"]}.csv" download>CSV</a>'
    if b["instelling"] == "Berekend":
        bron = "Berekend uit cijfers van Eurostat"
    else:
        bron = f'<a href="{escape(b["url"])}" rel="noopener">{escape(b["instelling"])}</a>'
    return (f'<footer class="bron">{icoon("bron")}<span>Bron: {bron} · opgehaald {datum(ind.get("opgehaald"))} · {csv}</span>'
            f'<button type="button" class="deel js" data-deel="{ind["id"]}" aria-label="Deel dit cijfer">{icoon("deel")}<span>Deel</span></button></footer>')


def technisch(ind: dict) -> str:
    b = ind["bron"]
    rijen = [f'<dt>Definitie</dt><dd>{escape(ind["definitie"]["nl"])}</dd>']
    if b["instelling"] == "Berekend":
        rijen.append(f'<dt>Berekening</dt><dd><code>{escape(b["formule"])}</code> met {", ".join(escape(v) for v in b["invoer"].values())}</dd>')
    else:
        rijen.append(f'<dt>Dataset</dt><dd>{escape(b["instelling"])} · <code>{escape(b["dataset"])}</code></dd>')
        for u in b.get("api_urls", []):
            rijen.append(f'<dt>Exacte bevraging</dt><dd><a href="{escape(u)}" rel="noopener">open de ruwe data</a></dd>')
        if b.get("bijgewerkt_bron"):
            rijen.append(f'<dt>Bijgewerkt door de bron</dt><dd>{datum(b["bijgewerkt_bron"])}</dd>')
    if ind.get("norm"):
        rijen.append(f'<dt>Norm of doel</dt><dd>{escape(ind["norm"]["label"]["nl"])} ({escape(ind["norm"]["bron"])})</dd>')
    if not ind["ok"] and ind.get("melding"):
        rijen.append(f'<dt>Laatste update</dt><dd>Mislukt ({escape(ind["melding"])}). Je ziet de laatste geldige cijfers.</dd>')
    return f'<details class="technisch"><summary>Definitie en bron</summary><dl>{"".join(rijen)}</dl></details>'


def kaart(ind: dict, pad: str) -> str:
    kleur = THEMA_KLEUR.get(ind["thema"], "#4f5f70")
    be = laatste(ind, "BE")
    kop = f'<header><p class="label">{escape(ind["titel"]["nl"])}</p><h3>{escape(ind["vraag"]["nl"])}</h3></header>'
    if not be:
        return (f'<article class="kaart leeg" id="{ind["id"]}">{kop}<p class="geen-data">Nog geen cijfers beschikbaar.</p>'
                f'{technisch(ind)}{bronregel(ind, pad)}</article>')
    jaar, waarde, status = be
    vlag = vlag_tekst(status)
    meta = f'België, {jaar}' + (f' <span class="vlag">{escape(vlag)}</span>' if vlag else "")
    zin_html = "".join(f"<li>{z}</li>" for z in zinnen(ind))
    beeld = wafel(ind, kleur) if ind.get("beeld") == "wafel" else doel(ind) if ind.get("beeld") == "doel" else ""
    uitleg = f'<p class="uitleg">{icoon("info")}<span>{escape(ind["uitleg"]["nl"])}</span></p>' if ind.get("uitleg") else ""
    landen = [g for g in ind["reeksen"] if not g.startswith("BE") or g == "BE"]
    heeft_buren = len([g for g in landen if g != "BE"]) >= 2
    heeft_regio = any(g in ind["reeksen"] for g in ("BE1", "BE2", "BE3"))
    tabs = [("jaren", "Door de jaren")]
    if heeft_buren:
        tabs.append(("buren", "België en de buren"))
    if heeft_regio:
        tabs.append(("gewesten", "Per gewest"))
    tab_html = ""
    if len(tabs) > 1:
        knoppen = "".join(f'<button type="button" role="tab" data-tab="{t}" aria-selected="{"true" if i == 0 else "false"}">{escape(n)}</button>' for i, (t, n) in enumerate(tabs))
        tab_html = f'<div class="tabs js" role="tablist" aria-label="Kies een weergave">{knoppen}</div>'
    grafiek = f'<div class="grafiek" data-grafiek="{ind["id"]}" data-weergave="{escape(ind["weergave"])}" role="img" aria-label="Grafiek: {escape(ind["titel"]["nl"])}"></div>'
    return (f'<article class="kaart" id="{ind["id"]}">{kop}'
            f'<div class="kern"><p class="waarde">{kort_met_eenheid(waarde, ind)}</p><p class="meta">{meta}</p></div>'
            f'<ul class="zinnen">{zin_html}</ul>{uitleg}{beeld}{tab_html}{grafiek}{technisch(ind)}{bronregel(ind, pad)}</article>')


def kerntegel(ind: dict, pad: str) -> str:
    be = laatste(ind, "BE")
    if not be:
        return ""
    jaar, waarde, status = be
    eu = waarde_in(ind, "EU27_2020", jaar)
    sub = f"EU: {kort_met_eenheid(eu, ind)}" if eu is not None else ("lopend jaar" if "j" in status else ("voorlopig" if "p" in status else ""))
    thema = ind["thema"]
    return (f'<a class="kerntegel" href="{pad}thema/{thema}.html#{ind["id"]}" style="--t:{THEMA_KLEUR.get(thema)}">'
            f'<span class="kt-label">{escape(ind["titel"]["nl"])}</span>'
            f'<span class="kt-waarde">{kort_met_eenheid(waarde, ind)}</span>'
            f'<span class="kt-sub">België {jaar}{" · " + sub if sub else ""}</span></a>')


def themabalk(themas: list[dict], actief: str | None, pad: str) -> str:
    links = []
    for t in themas:
        huidig = ' aria-current="page"' if t["id"] == actief else ""
        links.append(f'<a href="{pad}thema/{t["id"]}.html" style="--t:{THEMA_KLEUR.get(t["id"])}"{huidig}>{icoon(t["icoon"])}<span>{escape(t["nl"])}</span></a>')
    return f'<nav class="themabalk" aria-label="Thema\'s"><div class="binnen">{"".join(links)}</div></nav>'


def pagina(titel: str, beschrijving: str, inhoud: str, pad: str, themas: list[dict], actief: str | None, bijgewerkt: str) -> str:
    return SJABLOON.format(
        titel=escape(titel), beschrijving=escape(beschrijving), inhoud=inhoud, pad=pad, repo=REPO_URL,
        themabalk=themabalk(themas, actief, pad), bijgewerkt=bijgewerkt, zoek=icoon("zoek"),
    )


# ---------------------------------------------------------------- pagina's

def startpagina(data: dict, per_id: dict) -> str:
    pad = ""
    kern = "".join(kerntegel(per_id[i], pad) for i in KERNCIJFERS if i in per_id)
    kaarten = []
    for t in data["themas"]:
        inds = [i for i in data["indicatoren"] if i["thema"] == t["id"] and not i["verborgen"]]
        k = per_id.get(t.get("kop"))
        kop = ""
        if k and laatste(k, "BE"):
            j, w, _ = laatste(k, "BE")
            kop = f'<span class="tk-cijfer"><b>{kort_met_eenheid(w, k)}</b> {escape(k["titel"]["nl"].lower())} ({j})</span>'
        kaarten.append(
            f'<a class="themakaart" href="thema/{t["id"]}.html" style="--t:{THEMA_KLEUR.get(t["id"])}">'
            f'<span class="tk-icoon">{icoon(t["icoon"])}</span><span class="tk-naam">{escape(t["nl"])}</span>'
            f'<span class="tk-vraag">{escape(t["vraag"])}</span>{kop}'
            f'<span class="tk-meer">{len(inds)} cijfers {icoon("pijl")}</span></a>')
    zoekindex = [{"v": i["vraag"]["nl"], "t": i["titel"]["nl"], "th": next(t["nl"] for t in data["themas"] if t["id"] == i["thema"]),
                  "z": " ".join(i.get("zoekwoorden", [])), "u": f'thema/{i["thema"]}.html#{i["id"]}'}
                 for i in data["indicatoren"] if not i["verborgen"]]
    zoekindex += [{"v": t["vraag"], "t": t["nl"], "th": "Thema", "z": "", "u": f'thema/{t["id"]}.html'} for t in data["themas"]]
    inhoud = f'''
<section class="held">
  <div class="binnen">
    <h1>Hoe gaat het met België?</h1>
    <p class="held-sub">De belangrijkste cijfers over ons land, in gewone taal. Elk cijfer komt rechtstreeks van een officiële bron, staat er met bron bij en wordt elke dag automatisch bijgewerkt.</p>
    <div class="zoek js" id="zoek">
      <label for="zoekveld" class="visueel-verborgen">Zoek een cijfer</label>
      {icoon("zoek")}
      <input id="zoekveld" type="search" placeholder="Waar ben je benieuwd naar? Bv. treinen, schuld, armoede…" autocomplete="off">
      <ul id="zoekresultaten" role="listbox" hidden></ul>
    </div>
  </div>
</section>
<div class="binnen">
  <section aria-labelledby="kern-titel" class="blok">
    <h2 id="kern-titel">In één oogopslag</h2>
    <div class="kern-raster">{kern}</div>
  </section>
  <section aria-labelledby="thema-titel" class="blok">
    <h2 id="thema-titel">Kies een thema</h2>
    <div class="thema-raster">{"".join(kaarten)}</div>
  </section>
  <section aria-labelledby="hoe-titel" class="blok hoe">
    <h2 id="hoe-titel">Waarom kun je deze cijfers vertrouwen?</h2>
    <ol>
      <li>{icoon("bron")}<b>Officiële bronnen</b><span>Elk cijfer komt van een officiële instelling zoals Eurostat of Infrabel. Bij elk cijfer staat de bron, met een link.</span></li>
      <li>{icoon("klok")}<b>Elke dag bijgewerkt</b><span>Een programma haalt de cijfers elke dag automatisch op. Niemand tikt ze over, en er komt geen AI aan te pas.</span></li>
      <li>{icoon("code")}<b>Iedereen kan het narekenen</b><span>Alle data en berekeningen zijn openbaar. Je kunt elk cijfer downloaden en zelf controleren.</span></li>
    </ol>
  </section>
</div>
<script type="application/json" id="zoekindex">{json.dumps(zoekindex, ensure_ascii=False).replace("</", "<\\/")}</script>
'''
    return pagina("België in cijfers", "De belangrijkste cijfers over België, in gewone taal en met bron.", inhoud, pad,
                  data["themas"], None, datum(data["gegenereerd"]))


def themapagina(data: dict, thema: dict, vorige: dict, volgende: dict) -> str:
    pad = "../"
    inds = [i for i in data["indicatoren"] if i["thema"] == thema["id"] and not i["verborgen"]]
    snel = "".join(f'<li><a href="#{i["id"]}">{escape(i["vraag"]["nl"])}</a></li>' for i in inds)
    begrippen = "".join(f'<div><dt>{escape(data["begrippen"][b]["term"])}</dt><dd>{escape(data["begrippen"][b]["uitleg"])}</dd></div>'
                        for b in thema.get("begrippen", []) if b in data["begrippen"])
    inhoud = f'''
<section class="themakop" style="--t:{THEMA_KLEUR.get(thema["id"])}">
  <div class="binnen">
    <p class="kruimel"><a href="../">Alle thema's</a> / {escape(thema["nl"])}</p>
    <div class="themakop-titel"><span class="tk-icoon groot">{icoon(thema["icoon"])}</span><h1>{escape(thema["vraag"])}</h1></div>
    <p class="intro">{escape(thema["intro"])}</p>
    <div class="themakop-onder">
      <aside class="bevoegd"><h2>Wie beslist hierover?</h2><p>{escape(thema["bevoegd"])}</p></aside>
      <nav class="snel" aria-label="Op deze pagina"><h2>Op deze pagina</h2><ul>{snel}</ul></nav>
    </div>
  </div>
</section>
<div class="binnen" style="--t:{THEMA_KLEUR.get(thema["id"])}">
  <div class="kaart-raster">{"".join(kaart(i, pad) for i in inds)}</div>
  {f'<section class="begrippen"><h2>Moeilijke woorden uitgelegd</h2><dl>{begrippen}</dl></section>' if begrippen else ""}
  <nav class="buren-nav" aria-label="Andere thema's">
    <a href="{vorige["id"]}.html">{icoon("terug")}<span><small>Vorig thema</small>{escape(vorige["nl"])}</span></a>
    <a href="{volgende["id"]}.html"><span><small>Volgend thema</small>{escape(volgende["nl"])}</span>{icoon("pijl")}</a>
  </nav>
</div>
'''
    return pagina(f'{thema["nl"]} · België in cijfers', thema["vraag"] + " " + thema["intro"][:120], inhoud, pad,
                  data["themas"], thema["id"], datum(data["gegenereerd"]))


def bouw() -> None:
    data = json.loads((SITE / "data" / "dashboard.json").read_text(encoding="utf-8"))
    per_id = {i["id"]: i for i in data["indicatoren"]}

    csv_map = SITE / "data" / "csv"
    csv_map.mkdir(parents=True, exist_ok=True)
    for f in (WORTEL / "data" / "clean").glob("*.csv"):
        shutil.copy(f, csv_map / f.name)

    (SITE / "index.html").write_text(startpagina(data, per_id), encoding="utf-8")
    themamap = SITE / "thema"
    themamap.mkdir(exist_ok=True)
    themas = data["themas"]
    for n, t in enumerate(themas):
        html = themapagina(data, t, themas[n - 1], themas[(n + 1) % len(themas)])
        (themamap / f'{t["id"]}.html').write_text(html, encoding="utf-8")


SJABLOON = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
<meta name="description" content="{beschrijving}">
<meta property="og:title" content="{titel}">
<meta property="og:description" content="{beschrijving}">
<meta name="theme-color" content="#16202a">
<link rel="stylesheet" href="{pad}style.css">
<script>document.documentElement.classList.add("met-js")</script>
</head>
<body>
<a class="overslaan" href="#inhoud">Naar de inhoud</a>
<header class="kop">
  <div class="binnen">
    <a class="merk" href="{pad}"><span class="merk-blok" aria-hidden="true"></span>België in cijfers</a>
    <a class="kop-zoek" href="{pad}#zoek" aria-label="Zoek een cijfer">{zoek}<span>Zoek</span></a>
  </div>
</header>
{themabalk}
<main id="inhoud">
{inhoud}
</main>
<footer class="voet">
  <div class="binnen">
    <p><b>België in cijfers</b> is een onafhankelijk en open project. De cijfers worden elke dag automatisch bijgewerkt; laatste update op {bijgewerkt}.</p>
    <p>Alle code en data staan openbaar op <a href="{repo}">GitHub</a>. Bronnen stellen cijfers soms bij: bekijk de <a href="{repo}/blob/main/data/changelog.json">herzieningen</a> en de <a href="{repo}/blob/main/reports/status.md">status van elke bron</a>.</p>
    <p>Fout gezien of een cijfer dat ontbreekt? <a href="{repo}/issues/new">Laat het weten</a>.</p>
  </div>
</footer>
<script src="{pad}app.js" defer></script>
</body>
</html>
"""

if __name__ == "__main__":
    bouw()
