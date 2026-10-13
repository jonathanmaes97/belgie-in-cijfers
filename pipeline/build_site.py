"""Bouwt de website op uit site/data/dashboard.json, in vier talen.

Pagina's per taal (Nederlands in de hoofdmap, de andere talen in /fr/, /de/ en /en/):
  index.html            startpagina: zoeken, kerncijfers, thema's kiezen
  thema/<thema>.html    één pagina per thema met uitleg en alle cijfers
  gewesten.html         Vlaanderen, Wallonië en Brussel naast elkaar
  rekenmodule.html      hoeveel belastingen betaal ik?

Vaste teksten staan in config/vertalingen/ui.yaml, vertalingen van de inhoud
(titels, vragen, uitleg) in config/vertalingen/<taal>.yaml. Ontbreekt een
vertaling, dan valt de site terug op het Nederlands. Getallen worden nooit
vertaald of overgetikt: ze komen altijd uit de data.

Zinnen zoals "Dat is hoger dan het EU-gemiddelde" worden hier uit de data
berekend. Ze vergelijken enkel (hoger, lager, gelijk) en oordelen niet.
"""
from __future__ import annotations

import copy
import json
import shutil
from datetime import datetime
from html import escape
from pathlib import Path

import yaml

WORTEL = Path(__file__).resolve().parent.parent
SITE = WORTEL / "site"
REPO_URL = "https://github.com/jonathanmaes97/belgie-in-cijfers"
_SITE = yaml.safe_load((WORTEL / "config" / "site.yaml").read_text(encoding="utf-8"))
SITE_URL = (_SITE.get("domein") or _SITE["github_pages"]).rstrip("/") + "/"
GOATCOUNTER = _SITE.get("goatcounter")  # None = geen bezoekersstatistieken
# voorwaarden voor hergebruik per instelling (None = enkel de website, voorwaarden niet automatisch nagekeken)
VOORWAARDEN = {
    "Eurostat": ("https://ec.europa.eu/eurostat/help/copyright-notice", True),
    "Nationale Bank van België": ("https://www.nbb.be/en/disclaimer-and-legal-information/copyright-and-use-information", True),
    "Infrabel": ("https://opendata.infrabel.be/pages/license/", True),
    "Federaal Planbureau": ("https://www.plan.be", False),
    "RIZIV": ("https://www.inami.fgov.be/nl/statistieken/statistieken-uitkeringen", False),
    "Europese Commissie": ("https://commission.europa.eu/legal-notice_en", True),
    "Koninklijke Commissie voor Geschiedenis": ("https://www.commissionroyalehistoire.be/belelite/nl/gov/governmentsoverview/fed", False),
}
MERK = "State of the Union"
MAKER = "Jonathan Maes"
CONTACT = "sotu@jonathanmaes.be"            # voor vragen over de site
CONTACT_PERSOONLIJK = "hallo@jonathanmaes.be"  # algemeen adres van de maker
LINKEDIN_URL = "https://www.linkedin.com/in/maesjonathan/"
GEWEST_CODES = ["BE2", "BE3", "BE1"]
# Thema's waar federale regeringen als laag zinvol zijn (onderwijs is volledig een bevoegdheid van de gemeenschappen).
THEMAS_MET_REGERINGEN = {"veiligheid_justitie", "economie", "overheidsfinancien", "werk", "gezondheid", "wonen_armoede", "klimaat_energie", "mobiliteit", "demografie"}
KERNCIJFERS = ["schuld_per_inwoner", "rente_per_dag", "belastingwig", "werkzaamheidsgraad", "inflatie", "bbp_groei"]

UI = yaml.safe_load((WORTEL / "config" / "vertalingen" / "ui.yaml").read_text(encoding="utf-8"))
TALEN = list(UI["talen"])  # nl eerst: dat is de brontaal
TAAL = "nl"
PER_ID: dict = {}
NAMEN: dict = {}  # namen van instellingen in de huidige taal  # alle indicatoren (ook verborgen), om bij afgeleide cijfers naar de echte bronnen te linken


def zet_taal(taal: str) -> None:
    global TAAL
    TAAL = taal


def map_van(taal: str) -> str:
    """Submap van een taal ten opzichte van de site ('' voor Nederlands)."""
    return "" if taal == "nl" else f"{taal}/"


def T(sleutel: str, **kw) -> str:
    """Vaste tekst in de huidige taal."""
    s = UI["t"][sleutel]
    s = s.get(TAAL) or s["nl"]
    return s.format(**kw) if kw else s


def tx(waarde) -> str:
    """Tekst in de huidige taal uit een veld {nl: ..., fr: ...}, met terugval op Nederlands."""
    if isinstance(waarde, dict):
        return waarde.get(TAAL) or waarde.get("nl") or ""
    return waarde or ""


def ondertitel() -> str:
    return T("ondertitel")


def landnaam(data: dict, geo: str) -> str:
    return tx(data["landnamen"].get(geo, {})) or geo


# Kleur per thema: alleen om thema's te herkennen, nooit om te oordelen.
THEMA_KLEUR = {
    "economie": "#2357a6", "overheidsfinancien": "#6b3fa0", "werk": "#0b7a6e", "gezondheid": "#b03a5e",
    "onderwijs": "#8f5f00", "wonen_armoede": "#9a4a24", "klimaat_energie": "#2e7d32", "mobiliteit": "#c0461a",
    "veiligheid_justitie": "#7a3e65", "demografie": "#4f5f70",
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
    "kaart": '<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
    "reken": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8"/><path d="M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01M16 15h.01M8 18h.01M12 18h4"/>',
    "justitie": '<path d="M12 4v16M7 20h10"/><path d="M5 8h14"/><path d="M5 8l-3 6a3 3 0 0 0 6 0z"/><path d="M19 8l-3 6a3 3 0 0 0 6 0z"/><circle cx="12" cy="4" r="1"/>',
    "profiel": '<rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="9" cy="10.5" r="2.2"/><path d="M5.8 16.5c.6-1.8 1.8-2.7 3.2-2.7s2.6.9 3.2 2.7"/><path d="M14.5 9.5h3.5M14.5 13h3.5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>',
    "taal": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/>',
}


def icoon(naam: str) -> str:
    return _I.format(ICONEN.get(naam, ""))


# ---------------------------------------------------------------- opmaak van getallen

NB = " "  # harde spatie: getal en eenheid blijven samen op één regel
# duizendtal-teken en decimaalteken per taal
SCHEIDING = {"nl": (".", ","), "de": (".", ","), "fr": (" ", ","), "en": (",", ".")}
# eenheid in de catalogus → (vóór het getal, erna voluit, erna kort)
EENHEDEN = {
    "nl": {"per 100.000": ("", " per 100.000", " per 100.000"),
           "cent/kWh": ("", " cent per kWh", " cent/kWh"), "€/kWh": ("€ ", " per kWh", "/kWh"), "€/l": ("€ ", " per liter", "/l"),
           "%": ("", "%", "%"), "% bbp": ("", "% van het bbp", "%"), "€": ("€ ", "", ""), "mln €": ("€ ", " miljoen", " mln"),
           "jaar": ("", " jaar", " jaar"), "ton": ("", " ton", " ton"), "per 1.000": ("", " per 1.000", " per 1.000"),
           "per miljoen": ("", " per miljoen", " per miljoen"), "GWh": ("", " GWh", " GWh")},
    "fr": {"per 100.000": ("", " pour 100\u202f000", " pour 100\u202f000"),
           "cent/kWh": ("", " centimes par kWh", " c/kWh"), "€/kWh": ("", " € par kWh", " €/kWh"), "€/l": ("", " € par litre", " €/l"),
           "%": ("", " %", " %"), "% bbp": ("", " % du PIB", " %"), "€": ("", " €", " €"), "mln €": ("", " millions d'euros", " M€"),
           "jaar": ("", " ans", " ans"), "ton": ("", " tonnes", " t"), "per 1.000": ("", " pour 1 000", " pour 1 000"),
           "per miljoen": ("", " par million", " par million"), "GWh": ("", " GWh", " GWh")},
    "de": {"per 100.000": ("", " je 100.000", " je 100.000"),
           "cent/kWh": ("", " Cent pro kWh", " ct/kWh"), "€/kWh": ("", " € pro kWh", " €/kWh"), "€/l": ("", " € pro Liter", " €/l"),
           "%": ("", " %", " %"), "% bbp": ("", " % des BIP", " %"), "€": ("", " €", " €"), "mln €": ("", " Mio. €", " Mio. €"),
           "jaar": ("", " Jahre", " Jahre"), "ton": ("", " Tonnen", " t"), "per 1.000": ("", " je 1.000", " je 1.000"),
           "per miljoen": ("", " je Million", " je Million"), "GWh": ("", " GWh", " GWh")},
    "en": {"per 100.000": ("", " per 100,000", " per 100,000"),
           "cent/kWh": ("", " cents per kWh", "c/kWh"), "€/kWh": ("€", " per kWh", "/kWh"), "€/l": ("€", " per litre", "/l"),
           "%": ("", "%", "%"), "% bbp": ("", "% of GDP", "%"), "€": ("€", "", ""), "mln €": ("€", " million", "m"),
           "jaar": ("", " years", " years"), "ton": ("", " tonnes", " t"), "per 1.000": ("", " per 1,000", " per 1,000"),
           "per miljoen": ("", " per million", " per million"), "GWh": ("", " GWh", " GWh")},
}


def _eenheid(e: str) -> tuple[str, str, str]:
    e = e.strip()
    if not e:
        return ("", "", "")
    v = EENHEDEN[TAAL].get(e)
    if v is None:  # onbekende eenheid: toon ze zoals in de catalogus
        return ("", " " + e, " " + e)
    return tuple(s.replace(" ", NB) for s in v)


def getal(x: float, decimalen: int) -> str:
    duizend, decimaal = SCHEIDING[TAAL]
    s = f"{abs(x):,.{decimalen}f}".replace(",", "\x00").replace(".", decimaal).replace("\x00", duizend)
    return ("−" if x < 0 and round(abs(x), decimalen) != 0 else "") + s


def met_eenheid(x: float, ind: dict) -> str:
    voor, na, _ = _eenheid(ind["eenheid"])
    return voor + getal(x, ind["decimalen"]) + na


def kort_met_eenheid(x: float, ind: dict) -> str:
    """Kortere vorm voor grote cijfers op tegels."""
    voor, _, na = _eenheid(ind["eenheid"])
    return voor + getal(x, ind["decimalen"]) + na


def eur(x: float, decimalen: int = 0) -> str:
    voor, na, _ = _eenheid("€")
    return voor + getal(x, decimalen) + na


def pct(x: float, decimalen: int = 1) -> str:
    return getal(x, decimalen) + _eenheid("%")[1]


def datum(iso: str | None) -> str:
    if not iso:
        return T("onbekend")
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    maand = UI["maanden"][TAAL][d.month - 1]
    if TAAL == "de":
        return f"{d.day}. {maand} {d.year}"
    if TAAL == "fr" and d.day == 1:
        return f"1er {maand} {d.year}"
    return f"{d.day} {maand} {d.year}"


def maand_tekst(periode: str | None) -> str:
    if not periode or len(periode) < 7:
        return ""
    return f"{UI['maanden'][TAAL][int(periode[5:7]) - 1]} {periode[:4]}"


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
    return ", ".join(UI["vlaggen"][c][TAAL] for c in status if c in UI["vlaggen"])


def zinnen(ind: dict) -> list[str]:
    """Neutrale, uit de data berekende zinnen die het cijfer in context plaatsen."""
    be = laatste(ind, "BE")
    if not be:
        return []
    jaar, waarde, status = be
    uit = []
    eu = waarde_in(ind, "EU27_2020", jaar)
    if eu is not None:
        d = ind["decimalen"]
        soort = "gelijk" if round(waarde, d) == round(eu, d) else ("hoger" if waarde > eu else "lager")
        uit.append(T(f"zin_{soort}", eu=kort_met_eenheid(eu, ind)))
    reeks = ind["reeksen"]["BE"]
    vroeger = next((r for r in reeks if r[0] == jaar - 10), None) or (reeks[0] if len(reeks) > 3 and reeks[0][0] < jaar else None)
    if vroeger:
        uit.append(T("zin_vroeger", jaar=vroeger[0], waarde=kort_met_eenheid(vroeger[1], ind)))
    if "j" in status and ind["bron"].get("laatste_periode"):
        uit.append(T("zin_lopend", jaar=jaar, maand=maand_tekst(ind["bron"]["laatste_periode"])))
    return uit


# ---------------------------------------------------------------- vertalingen van de inhoud

def lees_vertaling(taal: str) -> dict:
    pad = WORTEL / "config" / "vertalingen" / f"{taal}.yaml"
    return yaml.safe_load(pad.read_text(encoding="utf-8")) if pad.exists() else {}


def vertaal(data: dict, taal: str) -> dict:
    """Kopie van de data waarin de teksten in `taal` zijn toegevoegd.

    Velden van de vorm {nl: ...} krijgen een sleutel `taal` (lees ze met tx()). Velden die gewone tekst zijn
    (thema's, begrippen, uitgaven) worden in de kopie vervangen. Getallen blijven onaangeroerd.
    """
    d = copy.deepcopy(data)
    if taal == "nl":
        return d
    v = lees_vertaling(taal)
    for t in d["themas"]:
        for k, w in (v.get("themas", {}).get(t["id"]) or {}).items():
            t[k] = w
    for b, w in (v.get("begrippen") or {}).items():
        if b in d["begrippen"]:
            d["begrippen"][b].update(w)
    for g, naam in (v.get("landnamen") or {}).items():
        d["landnamen"].setdefault(g, {})[taal] = naam
    for ind in d["indicatoren"]:
        w = (v.get("indicatoren") or {}).get(ind["id"]) or {}
        for k in ("titel", "vraag", "definitie", "uitleg", "wafel_tekst"):
            if w.get(k) and isinstance(ind.get(k), dict):
                ind[k][taal] = w[k]
        if w.get("norm") and ind.get("norm"):
            ind["norm"]["label"][taal] = w["norm"]
        if w.get("zoekwoorden"):
            ind["zoekwoorden"] = list(ind.get("zoekwoorden") or []) + list(w["zoekwoorden"])
    if d.get("uitgaven"):
        for f in d["uitgaven"]["functies"] + d["uitgaven"]["details"]:
            f.update((v.get("uitgaven") or {}).get(f["code"]) or {})
    if d.get("inkomsten"):
        for f in d["inkomsten"]["functies"]:
            f.update((v.get("inkomsten") or {}).get(f["code"]) or {})
    for blok in ("snel", "olie"):
        for r in (d.get(blok) or {}).get("reeksen", []):
            w = (v.get("snel") or {}).get(r["id"]) or {}
            for k in ("titel", "vraag", "uitleg"):
                if w.get(k):
                    r[k][taal] = w[k]
            if w.get("vergelijk") and r.get("vergelijk"):
                r["vergelijk"]["naam"][taal] = w["vergelijk"]
            if w.get("bron") and r["bron"].get("naam"):
                r["bron"]["naam"][taal] = w["bron"]
    d["_instellingen"] = v.get("instellingen") or {}
    d["_niet_meegerekend"] = v.get("niet_meegerekend")
    return d


# ---------------------------------------------------------------- beelden zonder JavaScript

def wafel(ind: dict, kleur: str) -> str:
    be = laatste(ind, "BE")
    if not be or not ind.get("wafel_tekst"):
        return ""
    n = max(0, min(100, round(be[1])))
    vakjes = []
    for i in range(100):
        x, y = (i % 10) * 11, (i // 10) * 11
        vakjes.append(f'<rect x="{x}" y="{y}" width="9" height="9" rx="2" class="{"vol" if i < n else "leeg"}"/>')
    tekst = escape(tx(ind["wafel_tekst"]))
    return (f'<figure class="beeld wafel"><svg viewBox="0 0 109 109" role="img" aria-label="{escape(T("wafel_aria", n=n))}">{"".join(vakjes)}</svg>'
            f'<figcaption><b>{T("wafel_kop", n=n)}</b> {tekst}.</figcaption></figure>')


def doel(ind: dict) -> str:
    be, norm = laatste(ind, "BE"), ind.get("norm")
    if not be or not norm:
        return ""
    jaar, w, _ = be
    eu = waarde_in(ind, "EU27_2020", jaar)
    lo, hi = 50.0, 100.0
    pos = lambda v: max(0.0, min(100.0, (v - lo) / (hi - lo) * 100))
    afstand = norm["waarde"] - w
    zin = T("doel_nog", n=getal(afstand, ind["decimalen"])) if afstand > 0 else T("doel_bereikt")
    eu_html = (f'<span class="markering eu" style="left:{pos(eu):.1f}%"><span>{T("eu_kort")} {pct(eu, ind["decimalen"])}</span></span>'
               if eu is not None else "")
    return (f'<figure class="beeld doel"><div class="balk" role="img" aria-label="{T("land")} {pct(w, ind["decimalen"])}, {T("doel").lower()} {pct(norm["waarde"], 0)}">'
            f'<div class="vulling" style="width:{pos(w):.1f}%"></div>'
            f'<span class="markering norm" style="left:{pos(norm["waarde"]):.1f}%"><span>{T("doel")} {pct(norm["waarde"], 0)}</span></span>{eu_html}</div>'
            f'<div class="schaal"><span>{pct(lo, 0)}</span><span>{pct(hi, 0)}</span></div>'
            f'<figcaption>{zin}</figcaption></figure>')


# ---------------------------------------------------------------- onderdelen

def bronnen_van(ind: dict) -> list[dict]:
    """De echte bronnen achter een cijfer; bij een afgeleid cijfer die van de invoer."""
    b = ind["bron"]
    if b["instelling"] != "Berekend":
        return [b]
    uit = []
    for i in b["invoer"].values():
        for x in bronnen_van(PER_ID[i]) if i in PER_ID else []:
            if all((x["instelling"], x.get("dataset")) != (y["instelling"], y.get("dataset")) for y in uit):
                uit.append(x)
    return uit


def bronlink(b: dict) -> str:
    return f'<a href="{escape(b["url"])}" rel="noopener">{escape(NAMEN.get(b["instelling"], b["instelling"]))} · {escape(b["dataset"])}</a>'


def bronregel(ind: dict, bpad: str) -> str:
    b = ind["bron"]
    if b["instelling"] == "Berekend":
        bron = T("berekend_uit") + " " + f' {T("en_woord")} '.join(bronlink(x) for x in bronnen_van(ind))
    else:
        bron = bronlink(b)
    return (f'<footer class="bron">{icoon("bron")}<span>{T("bron")}: {bron} · {T("opgehaald")} {datum(ind.get("opgehaald"))}</span>'
            f'<button type="button" class="deel js" data-deel="{ind["id"]}" aria-label="{T("deel_aria")}">{icoon("deel")}<span>{T("deel")}</span></button></footer>')


def technisch(ind: dict, bpad: str = "") -> str:
    b = ind["bron"]
    rijen = [f'<dt>{T("definitie")}</dt><dd>{escape(tx(ind["definitie"]))}</dd>']
    if b["instelling"] == "Berekend":
        rijen.append(f'<dt>{T("berekening")}</dt><dd><code>{escape(b["formule"])}</code> {T("met")} {", ".join(escape(v) for v in b["invoer"].values())}</dd>')
        for x in [PER_ID[i]["bron"] for i in b["invoer"].values() if i in PER_ID and PER_ID[i]["bron"]["instelling"] != "Berekend"]:
            for u in x.get("api_urls", []):
                rijen.append(f'<dt>{T("exacte_bevraging")}</dt><dd>{escape(x["dataset"])}: <a href="{escape(u)}" rel="noopener">{T("open_ruwe_data")}</a></dd>')
    else:
        rijen.append(f'<dt>{T("dataset")}</dt><dd>{escape(b["instelling"])} · <code>{escape(b["dataset"])}</code></dd>')
        for u in b.get("api_urls", []):
            rijen.append(f'<dt>{T("exacte_bevraging")}</dt><dd><a href="{escape(u)}" rel="noopener">{T("open_ruwe_data")}</a></dd>')
        if b.get("bijgewerkt_bron"):
            rijen.append(f'<dt>{T("bijgewerkt_bron")}</dt><dd>{datum(b["bijgewerkt_bron"])}</dd>')
    if ind.get("norm"):
        rijen.append(f'<dt>{T("norm_of_doel")}</dt><dd>{escape(tx(ind["norm"]["label"]))} ({escape(ind["norm"]["bron"])})</dd>')
    if not ind["ok"] and ind.get("melding"):
        rijen.append(f'<dt>{T("laatste_update")}</dt><dd>{T("mislukt", melding=escape(ind["melding"]))}</dd>')
    rijen.append(f'<dt>{T("csv_kopie")}</dt><dd><a href="{bpad}data/csv/{ind["id"]}.csv" download>{ind["id"]}.csv</a> ({T("csv_noot")})</dd>')
    return f'<details class="technisch"><summary>{T("definitie_en_bron")}</summary><dl>{"".join(rijen)}</dl></details>'


def kaart(ind: dict, bpad: str) -> str:
    kleur = THEMA_KLEUR.get(ind["thema"], "#4f5f70")
    be = laatste(ind, "BE")
    kop = f'<header><p class="label">{escape(tx(ind["titel"]))}</p><h3>{escape(tx(ind["vraag"]))}</h3></header>'
    if not be:
        return (f'<article class="kaart leeg" id="{ind["id"]}">{kop}<p class="geen-data">{T("geen_cijfers")}</p>'
                f'{technisch(ind, bpad)}{bronregel(ind, bpad)}</article>')
    jaar, waarde, status = be
    vlag = vlag_tekst(status)
    meta = f'{T("land")}, {jaar}' + (f' <span class="vlag">{escape(vlag)}</span>' if vlag else "")
    zin_html = "".join(f"<li>{z}</li>" for z in zinnen(ind))
    beeld = wafel(ind, kleur) if ind.get("beeld") == "wafel" else doel(ind) if ind.get("beeld") == "doel" else ""
    uitleg = f'<p class="uitleg">{icoon("info")}<span>{escape(tx(ind["uitleg"]))}</span></p>' if ind.get("uitleg") else ""
    landen = [g for g in ind["reeksen"] if not g.startswith("BE") or g == "BE"]
    heeft_buren = len([g for g in landen if g != "BE"]) >= 2
    heeft_regio = any(g in ind["reeksen"] for g in GEWEST_CODES)
    tabs = [("jaren", T("tab_jaren"))]
    if heeft_buren:
        tabs.append(("buren", T("tab_buren")))
    if heeft_regio:
        tabs.append(("gewesten", T("tab_gewesten")))
    tab_html = ""
    if len(tabs) > 1:
        knoppen = "".join(f'<button type="button" role="tab" data-tab="{t}" aria-selected="{"true" if i == 0 else "false"}">{escape(n)}</button>' for i, (t, n) in enumerate(tabs))
        tab_html = f'<div class="tabs js" role="tablist" aria-label="{T("kies_weergave")}">{knoppen}</div>'
    grafiek = (f'<div class="grafiek" data-grafiek="{ind["id"]}" data-weergave="{escape(ind["weergave"])}" role="img" '
               f'aria-label="{escape(T("grafiek_aria", titel=tx(ind["titel"])))}"></div>')
    return (f'<article class="kaart" id="{ind["id"]}">{kop}'
            f'<div class="kern"><p class="waarde">{kort_met_eenheid(waarde, ind)}</p><p class="meta">{meta}</p></div>'
            f'<ul class="zinnen">{zin_html}</ul>{uitleg}{beeld}{tab_html}{grafiek}{technisch(ind, bpad)}{bronregel(ind, bpad)}</article>')


def sparkline(ind: dict, b: int = 120, h: int = 34) -> str:
    """Kleine verloopgrafiek (laatste tien jaar België) als SVG, zonder JavaScript."""
    reeks = (ind["reeksen"].get("BE") or [])[-11:]
    if len(reeks) < 3:
        return ""
    xs = [r[0] for r in reeks]
    ys = [r[1] for r in reeks]
    lo, hi = min(ys), max(ys)
    span = (hi - lo) or 1
    pts = [((x - xs[0]) / (xs[-1] - xs[0]) * (b - 6) + 3, h - 4 - (y - lo) / span * (h - 8)) for x, y in zip(xs, ys)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    lx, ly = pts[-1]
    return (f'<svg class="spark" viewBox="0 0 {b} {h}" aria-hidden="true"><path d="{d}" pathLength="1"/>'
            f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3"/></svg>')


def telwaarde(waarde: float, ind: dict) -> str:
    """Attributen zodat JavaScript het getal kan laten optellen tot de echte waarde."""
    voor, _, na = _eenheid(ind["eenheid"])
    return f'data-tel="{waarde}" data-dec="{ind["decimalen"]}" data-voor="{escape(voor)}" data-na="{escape(na)}"'


def tick(ind: dict, pad: str) -> str:
    be = laatste(ind, "BE")
    if not be:
        return ""
    jaar, waarde, status = be
    eu = waarde_in(ind, "EU27_2020", jaar)
    sub = (f'{T("eu_kort")} {kort_met_eenheid(eu, ind)}' if eu is not None
           else (UI["vlaggen"]["j"][TAAL] if "j" in status else (UI["vlaggen"]["p"][TAAL] if "p" in status else "")))
    thema = ind["thema"]
    return (f'<a class="tick" href="{pad}thema/{thema}.html#{ind["id"]}" style="--t:{THEMA_KLEUR.get(thema)}">'
            f'<span class="tick-label">{escape(tx(ind["titel"]))}</span>'
            f'<span class="tick-waarde" {telwaarde(waarde, ind)}>{kort_met_eenheid(waarde, ind)}</span>'
            f'{sparkline(ind)}'
            f'<span class="tick-sub">{T("land")} {jaar}{" · " + sub if sub else ""}</span></a>')


def themabalk(themas: list[dict], actief: str | None, pad: str) -> str:
    huidig = ' aria-current="page"' if actief == "gewesten" else ""
    links = [f'<a href="{pad}gewesten.html" class="gewesten-link" style="--t:#1a1f24"{huidig}>{icoon("kaart")}<span>{T("gewesten_kort")}</span></a>']
    for t in themas:
        huidig = ' aria-current="page"' if t["id"] == actief else ""
        links.append(f'<a href="{pad}thema/{t["id"]}.html" style="--t:{THEMA_KLEUR.get(t["id"])}"{huidig}>{icoon(t["icoon"])}<span>{escape(t["nl"])}</span></a>')
    knoppen = (f'<button type="button" class="schuif-knop links" aria-hidden="true" tabindex="-1">{icoon("terug")}</button>'
               f'<button type="button" class="schuif-knop rechts" aria-hidden="true" tabindex="-1">{icoon("pijl")}</button>')
    return f'<nav class="themabalk" aria-label="{escape(T("themas_aria"))}"><div class="binnen">{"".join(links)}</div>{knoppen}</nav>'


def taalkeuze(url: str, bpad: str) -> str:
    """Links naar dezelfde pagina in de andere talen."""
    links = []
    for t in TALEN:
        info = UI["talen"][t]
        huidig = ' aria-current="true"' if t == TAAL else ""
        links.append(f'<a href="{bpad}{map_van(t)}{url}" hreflang="{t}" lang="{t}" title="{escape(info["naam"])}"{huidig}>{info["kort"]}</a>')
    return f'<nav class="talen" aria-label="{T("taal_aria")}">{"".join(links)}</nav>'


def js_teksten(data: dict) -> str:
    """Teksten en notaties die app.js en reken.js nodig hebben, voor de huidige taal."""
    eenheden = {k: [v[0].replace(" ", NB), v[2].replace(" ", NB)] for k, v in EENHEDEN[TAAL].items()}
    ui = {
        "taal": TAAL, "locale": UI["talen"][TAAL]["locale"],
        "t": {k: v.get(TAAL) or v["nl"] for k, v in UI["js"].items()},
        "maanden": UI["maanden_kort"][TAAL],
        "land": T("land"), "geenTreffer": T("zoek_geen"), "eu": landnaam(data, "EU27_2020"), "euKort": T("eu_kort"),
        "landnamen": {g: landnaam(data, g) for g in data["landnamen"]},
        "eenheden": eenheden,
        "normen": {i["id"]: tx(i["norm"]["label"]) for i in data["indicatoren"] if i.get("norm")},
        "uitgaven": {f["code"]: f["nl"] for f in (data.get("uitgaven") or {}).get("functies", [])},
    }
    return json.dumps(ui, ensure_ascii=False).replace("</", "<\\/")


def pagina(titel: str, beschrijving: str, inhoud: str, pad: str, data: dict, actief: str | None, og: str, url: str) -> str:
    """Zet de inhoud in het sjabloon. `pad` leidt naar de hoofdmap van de taal, `url` is de pagina binnen die map."""
    bpad = pad + ("" if TAAL == "nl" else "../")  # naar de hoofdmap van de site (voor css, js, data)
    og_naam = og if TAAL == "nl" else f"{og}-{TAAL}"
    alternatieven = "".join(f'<link rel="alternate" hreflang="{t}" href="{SITE_URL}{map_van(t)}{url}">' for t in TALEN)
    alternatieven += f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{url}">'
    linkedin = f' <a class="li-knop" href="{LINKEDIN_URL}" rel="noopener" aria-label="{MAKER} op LinkedIn">{icoon("profiel")}<span>LinkedIn</span></a>' if LINKEDIN_URL else ""
    return SJABLOON.format(
        taal=TAAL, titel=escape(titel), beschrijving=escape(beschrijving), inhoud=inhoud, pad=pad, bpad=bpad,
        themabalk=themabalk(data["themas"], actief, pad), zoek=icoon("zoek"), reken=icoon("reken"),
        og=f"{SITE_URL}og/{og_naam}.png", url=SITE_URL + map_van(TAAL) + url, merk=MERK, ondertitel=ondertitel(),
        alternatieven=alternatieven, taalkeuze=taalkeuze(url, bpad), og_locale=UI["talen"][TAAL]["locale"].replace("-", "_"),
        naar_inhoud=T("naar_inhoud"), kop_reken=T("kop_reken"), zoek_aria=T("zoek_cijfer"), zoek_tekst=T("zoek"),
        voet_project=T("voet_project", datum=datum(data["gegenereerd"])), voet_code=T("voet_code", repo=REPO_URL),
        voet_maker=T("voet_maker", maker=MAKER, linkedin=linkedin), voet_contact=T("voet_contact", mail=CONTACT, repo=REPO_URL),
        voet_vibe=T("voet_vibe"), over_link=T("over_link"),
        statistiek=(f'<script data-goatcounter="{escape(GOATCOUNTER)}" async src="https://gc.zgo.at/count.js"></script>' if GOATCOUNTER else ""), voet_onafhankelijk=T("voet_onafhankelijk"), ui=js_teksten(data),
    )


# ---------------------------------------------------------------- pagina's

def startpagina(data: dict, per_id: dict) -> str:
    pad = ""
    ticks = "".join(tick(per_id[i], pad) for i in KERNCIJFERS if i in per_id)
    kaarten = []
    for t in data["themas"]:
        inds = [i for i in data["indicatoren"] if i["thema"] == t["id"] and not i["verborgen"]]
        k = per_id.get(t.get("kop"))
        kop = ""
        if k and laatste(k, "BE"):
            j, w, _ = laatste(k, "BE")
            titel = tx(k["titel"])
            # kleine beginletter, behalve in het Duits (zelfstandige naamwoorden) en bij afkortingen zoals "GDP"
            if TAAL != "de" and titel[1:2].islower():
                titel = titel[:1].lower() + titel[1:]
            kop = f'<span class="tk-cijfer"><b>{kort_met_eenheid(w, k)}</b><span>{escape(titel)}, {j}</span></span>'
        kaarten.append(
            f'<a class="themavlak" href="thema/{t["id"]}.html" style="--t:{THEMA_KLEUR.get(t["id"])}">'
            f'<span class="tv-kop">{icoon(t["icoon"])}<span class="tv-naam">{escape(t["nl"])}</span></span>'
            f'<span class="tv-vraag">{escape(t["vraag"])}</span>{kop}'
            f'<span class="tv-meer">{T("n_cijfers", n=len(inds))} {icoon("pijl")}</span></a>')
    kaarten.append(
        f'<a class="themavlak gewestvlak" href="gewesten.html" style="--t:#3a434c">'
        f'<span class="tv-kop">{icoon("kaart")}<span class="tv-naam">{T("gewestvlak_naam")}</span></span>'
        f'<span class="tv-vraag">{T("gewestvlak_vraag")}</span>'
        f'<span class="tv-meer">{T("gewestvlak_meer")} {icoon("pijl")}</span></a>')

    # rekenvoorbeeld rente: jaarlijkse rentelasten gelijk verdeeld over het jaar
    teller = ""
    r = per_id.get("rentelasten_eur")
    if r and laatste(r, "BE"):
        rj, rw, rs = laatste(r, "BE")
        per_sec = rw * 1_000_000 / (365 * 24 * 3600)
        bedrag = getal(rw / 1000, 1) + {"nl": " miljard euro", "fr": " milliards d'euros", "de": " Milliarden Euro", "en": " billion euros"}[TAAL]
        teller = (f'<div class="teller"><p>{T("teller", bedrag=f"<b id=renteteller data-per-seconde={per_sec:.4f}>{eur(0)}</b>")}</p>'
                  f'<small>{T("teller_noot", jaar=rj, voorlopig=T("voorlopig_komma") if "p" in rs else "", bedrag=bedrag)}</small></div>')

    themanaam = {t["id"]: t["nl"] for t in data["themas"]}
    zoekindex = [{"v": tx(i["vraag"]), "t": tx(i["titel"]), "th": themanaam[i["thema"]],
                  "z": " ".join(i.get("zoekwoorden", [])), "u": f'thema/{i["thema"]}.html#{i["id"]}'}
                 for i in data["indicatoren"] if not i["verborgen"]]
    zoekindex += [{"v": t["vraag"], "t": t["nl"], "th": T("thema"), "z": "", "u": f'thema/{t["id"]}.html'} for t in data["themas"]]
    zoekindex.append({"v": T("rk_titel"), "t": T("rk_kruimel"), "th": T("rk_kruimel"),
                      "z": "loon brutoloon netto belasting rekenen simulator schijven belastingdruk vakantiegeld eindejaarspremie "
                           "salaire brut impôt calcul salaire Gehalt Steuer brutto Rechner salary tax gross calculator", "u": "rekenmodule.html"})
    zoekindex.append({"v": T("zoek_index_uitgaven"), "t": T("uit_label"), "th": themanaam.get("overheidsfinancien", ""),
                      "z": "belastinggeld uitgaven pensioenen defensie onderwijs zorg begroting dépenses pensions défense "
                           "Ausgaben Renten Verteidigung spending pensions defence", "u": "thema/overheidsfinancien.html#belastinggeld"})
    zoekindex.append({"v": T("zoek_index_inkomsten"), "t": T("ink_label"), "th": themanaam.get("overheidsfinancien", ""),
                      "z": "belastingen arbeid consumptie kapitaal vermogen btw vennootschapsbelasting lasten op arbeid impliciete belastingvoet "
                           "impôts travail capital consommation Steuern Arbeit Kapital Konsum taxes labour capital consumption", "u": "thema/overheidsfinancien.html#belastingen-per-soort"})
    zoekindex.append({"v": T("zoek_index_vz"), "t": T("vz_label"), "th": themanaam.get("economie", ""),
                      "z": "index indexering spilindex inflatie vooruitzicht planbureau loon uitkering indexation indice-pivot prévision "
                           "Indexierung Schwellenindex Prognose indexation pivot forecast", "u": "thema/economie.html#inflatie-en-index"})
    for o in (data.get("olie") or {}).get("reeksen", []):
        zoekindex.append({"v": tx(o["vraag"]), "t": tx(o["titel"]), "th": themanaam.get("klimaat_energie", ""),
                          "z": "mazout stookolie gasolie verwarming fioul mazout de chauffage Heizöl heating oil", "u": f'thema/klimaat_energie.html#{o["id"]}'})
    zoekindex.append({"v": T("zoek_index_gewesten"), "t": T("gw_kruimel"), "th": T("gewesten_kort"),
                      "z": "vlaanderen wallonie brussel gewest regio deelstaat flandre bruxelles région Flandern Brüssel Region "
                           "flanders wallonia brussels region", "u": "gewesten.html"})
    vertrouwen = "".join(f'<li>{icoon(ic)}<b>{T(f"vertrouwen_{n}_titel")}</b><span>{T(f"vertrouwen_{n}")}</span></li>'
                         for n, ic in ((1, "bron"), (2, "klok"), (3, "code")))
    inhoud = f'''
<section class="held">
  <div class="held-achter" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="binnen">
    <p class="bovenregel"><b>{MERK}</b><span>{ondertitel()}</span><span class="editie">{T("editie", datum=datum(data["gegenereerd"]))}</span></p>
    <h1>{T("held_titel")}</h1>
    <p class="held-sub">{T("held_sub")}</p>
    <div class="zoek js" id="zoek">
      <label for="zoekveld" class="visueel-verborgen">{T("zoek_cijfer")}</label>
      {icoon("zoek")}
      <input id="zoekveld" type="search" placeholder="{escape(T("zoek_placeholder"))}" autocomplete="off">
      <ul id="zoekresultaten" role="listbox" hidden></ul>
    </div>
  </div>
  <div class="binnen"><div class="ticks">{ticks}</div>{teller}</div>
</section>
<div class="binnen">
  <div class="tegels">
  {gewestentegel(data, per_id)}
  <a class="reken-tegel" href="rekenmodule.html" style="--t:{THEMA_KLEUR["overheidsfinancien"]}"><span class="tk-icoon">{icoon("reken")}</span><span><b>{T("reken_tegel_titel")}</b><span>{T("reken_tegel_tekst")}</span></span>{icoon("pijl")}</a>
  </div>
  <section aria-labelledby="thema-titel" class="blok">
    <div class="blok-kop"><h2 id="thema-titel">{T("kies_thema")}</h2><a href="gewesten.html" class="blok-link">{T("vergelijk_link")} {icoon("pijl")}</a></div>
    <div class="thema-raster">{"".join(kaarten)}</div>
  </section>
  {snelblok(data)}
  <section aria-labelledby="hoe-titel" class="blok hoe">
    <h2 id="hoe-titel">{T("vertrouwen_titel")}</h2>
    <ol>{vertrouwen}</ol>
  </section>
</div>
<script type="application/json" id="zoekindex">{json.dumps(zoekindex, ensure_ascii=False).replace("</", "<\\/")}</script>
'''
    return pagina(f"{MERK}: {ondertitel()}", T("start_beschrijving"), inhoud, pad, data, None, "index", "")


def gewestentegel(data: dict, per_id: dict) -> str:
    """Opvallende tegel naar de vergelijking per gewest, met een klein voorbeeld (werkzaamheidsgraad)."""
    ind = per_id.get("werkzaamheidsgraad")
    voorbeeld = ""
    if ind:
        jaren = set.intersection(*[{r[0] for r in ind["reeksen"].get(g, [])} for g in GEWEST_CODES])
        if jaren:
            jaar = max(jaren)
            w = [(g, waarde_in(ind, g, jaar)) for g in GEWEST_CODES]
            hi = max(v for _, v in w)
            rijen = "".join(f'<span class="gt-rij"><span>{escape(landnaam(data, g))}</span><i style="width:{v / hi * 100:.0f}%"></i><b>{kort_met_eenheid(v, ind)}</b></span>' for g, v in w)
            voorbeeld = f'<span class="gt-voorbeeld"><small>{escape(T("gw_tegel_voorbeeld", titel=tx(ind["titel"]), jaar=jaar))}</small>{rijen}</span>'
    return (f'<a class="reken-tegel gewest-tegel" href="gewesten.html" style="--t:#3a434c"><span class="tk-icoon">{icoon("kaart")}</span>'
            f'<span><b>{T("gw_tegel_titel")}</b><span>{T("gw_tegel_tekst")}</span>{voorbeeld}</span>{icoon("pijl")}</a>')


def vooruitzichtenblok(data: dict) -> str:
    """Inflatievooruitzichten, spilindex en consensus van instellingen (Federaal Planbureau)."""
    vz = data.get("vooruitzichten")
    if not vz or not vz.get("inflatie"):
        return ""
    inf, con = vz["inflatie"], vz.get("consensus")
    nu = data["gegenereerd"][:7]
    jaren = "".join(
        f'<div><span class="vz-label">{T("vz_inflatie", jaar=j["jaar"])}</span><span class="vz-waarde">{pct(j["inflatie"], 1)}</span>'
        f'<span class="vz-sub">{T("vz_verwacht") if j["jaar"] >= int(nu[:4]) else T("vz_gemiddelde")}</span></div>'
        for j in inf["jaren"] if j.get("inflatie") is not None)
    komend = [o for o in inf["overschrijdingen"] if o["maand"] >= nu]
    voorbij = [o for o in inf["overschrijdingen"] if o["maand"] < nu and not o["vooruitzicht"]]
    spil = ""
    if komend:
        o = komend[0]
        daarna = T("vz_daarna", lijst=", ".join(maand_tekst(x["maand"]) for x in komend[1:])) if len(komend) > 1 else ""
        spil = (f'<div><span class="vz-label">{T("vz_volgende")}</span>'
                f'<span class="vz-waarde">{maand_tekst(o["maand"])}</span>'
                f'<span class="vz-sub">{T("vz_verwachting") if o["vooruitzicht"] else T("vz_gemeten")}{daarna}</span></div>')
    elif voorbij:
        spil = (f'<div><span class="vz-label">{T("vz_laatste")}</span>'
                f'<span class="vz-waarde">{maand_tekst(voorbij[-1]["maand"])}</span><span class="vz-sub">{T("vz_gemeten")}</span></div>')
    tabel = ""
    if con and con.get("instellingen"):
        j1, j2 = con["jaren"]
        cel = lambda v: "—" if v is None else getal(v, 1)
        namen = data.get("_instellingen") or {}
        rijen = "".join(
            f'<tr{" class=eigen" if i["naam"].startswith("Federaal Planbureau") else ""}><th scope="row">{escape(namen.get(i["naam"], i["naam"]))}</th>'
            f'<td>{cel(i["groei"][0])}</td><td>{cel(i["groei"][1])}</td><td>{cel(i["inflatie"][0])}</td><td>{cel(i["inflatie"][1])}</td>'
            f'<td>{cel(i["saldo"][0])}</td><td>{cel(i["saldo"][1])}</td><td class="upd">{maand_tekst(i["update"]) if i.get("update") else ""}</td></tr>'
            for i in con["instellingen"])
        tabel = (f'<details class="consensus"><summary>{T("vz_andere")}</summary>'
                 f'<p>{T("vz_andere_uitleg")}</p>'
                 f'<div class="consensus-doos"><table><thead><tr><th scope="col">{T("vz_instelling")}</th><th scope="col" colspan="2">{T("vz_groei")}</th>'
                 f'<th scope="col" colspan="2">{T("vz_inflatie_kol")}</th><th scope="col" colspan="2">{T("vz_saldo")}</th><th scope="col">{T("vz_bijgewerkt")}</th></tr>'
                 f'<tr class="sub"><th></th><th>{j1}</th><th>{j2}</th><th>{j1}</th><th>{j2}</th><th>{j1}</th><th>{j2}</th><th></th></tr></thead>'
                 f'<tbody>{rijen}</tbody></table></div>'
                 f'<p class="bron-klein">{T("bron")}: <a href="{escape(con["pagina"])}" rel="noopener">{T("vz_bron_consensus")}</a> · '
                 f'<a href="{escape(con["bron"])}">Excel</a> · {T("versie_van", datum=datum(con["gepubliceerd"]))}</p></details>')
    return f'''
<section class="vz kaart" id="inflatie-en-index">
  <header><p class="label">{T("vz_label")}</p><h3>{T("vz_titel")}</h3></header>
  <div class="vz-kern">{jaren}{spil}</div>
  <p class="uitleg">{icoon("info")}<span>{T("vz_uitleg")}</span></p>
  <div class="grafiek vz-grafiek" data-vz="inflatie" role="img" aria-label="{T("vz_grafiek_aria")}"></div>
  {tabel}
  <footer class="bron">{icoon("bron")}<span>{T("bron")}: <a href="{escape(inf["pagina"])}" rel="noopener">{T("vz_bron_inflatie")}</a> · {T("versie_van", datum=datum(inf["gepubliceerd"]))} · {T("laatste_gemeten", maand=maand_tekst(inf.get("laatste_gemeten")))} · <a href="{escape(inf["bron"])}">Excel</a></span></footer>
</section>'''


UITGAVEN_KLEUREN = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]


def uitgavenblok(data: dict, per_id: dict) -> str:
    """Waar gaat ons belastinggeld naartoe? Overheidsuitgaven per functie (Eurostat COFOG)."""
    u = data.get("uitgaven")
    if not u:
        return ""
    jaar = str(u["jaar"])
    aandeel = lambda code, geo="BE": (u["aandelen"].get(code, {}).get(geo, {}) or {}).get(jaar)
    bev = waarde_in(per_id["bevolking"], "BE", int(jaar)) if "bevolking" in per_id else None
    functies = sorted(u["functies"], key=lambda f: -(aandeel(f["code"]) or 0))
    kleur = {f["code"]: (UITGAVEN_KLEUREN[i] if i < len(UITGAVEN_KLEUREN) else "#9aa0a6") for i, f in enumerate(functies)}
    balk = "".join(f'<i style="width:{aandeel(f["code"]) or 0:.2f}%;background:{kleur[f["code"]]}" title="{escape(f["nl"])}: {pct(aandeel(f["code"]) or 0, 1)}"></i>' for f in functies)
    rijen = []
    for f in functies:
        a, eu = aandeel(f["code"]), aandeel(f["code"], "EU27_2020")
        mio = (u["miljoen_euro"].get(f["code"]) or {}).get(jaar)
        per_inw = eur(mio * 1e6 / bev) if mio and bev else "—"
        detail = ""
        for d in u["details"]:
            if d["deel_van"] == f["code"] and aandeel(d["code"]) is not None:
                dm = (u["miljoen_euro"].get(d["code"]) or {}).get(jaar)
                deu = aandeel(d["code"], "EU27_2020")
                detail += (f'<tr class="detail"><th scope="row">{escape(d["nl"])}{officieel(d)}</th><td>{eur(aandeel(d["code"]), 1)}</td>'
                           f'<td>{eur(dm * 1e6 / bev) if dm and bev else "—"}</td><td>{pct(deu, 1) if deu is not None else "—"}</td></tr>')
        rijen.append(f'<tr><th scope="row"><span class="stip" style="background:{kleur[f["code"]]}"></span>{escape(f["nl"])}<small>{escape(f["uitleg"])}</small>{officieel(f)}</th>'
                     f'<td>{eur(a, 1) if a is not None else "—"}</td><td>{per_inw}</td><td>{pct(eu, 1) if eu is not None else "—"}</td></tr>{detail}')
    filters = "; ".join(f'{k} = {v}' for k, v in (u["bron"].get("filters") or {}).items())
    zo_vind = f'<p class="bron-klein zo-vind">{T("uit_zo_vind", ds=f"<a href={chr(34)}{escape(u["bron"]["url"])}{chr(34)} rel=noopener><code>{escape(u["bron"]["dataset"])}</code></a>", filters=escape(filters))}</p>' if filters else ""
    totaal_mio = sum(((u["miljoen_euro"].get(f["code"]) or {}).get(jaar) or 0) for f in u["functies"])
    totaal_zin = T("uit_totaal", bedrag=eur(totaal_mio * 1e6 / bev)) if bev and totaal_mio else ""
    b = u["bron"]
    return f'''
<section class="vz kaart uitgaven" id="belastinggeld">
  <header><p class="label">{T("uit_label")}</p><h3>{T("uit_titel")}</h3></header>
  <p class="intro-klein">{T("uit_intro", jaar=jaar)}{totaal_zin}</p>
  <button type="button" class="controle-knop js" aria-pressed="false" data-controle>{icoon("bron")}<span>{T("uit_toon_controle")}</span></button>
  <div class="honderd" role="img" aria-label="{T("uit_aria")}">{balk}</div>
  <div class="uitgaven-doos"><table>
    <thead><tr><th scope="col">{T("uit_domein")}</th><th scope="col">{T("uit_per_100")}</th><th scope="col">{T("uit_per_inwoner")}</th><th scope="col">{escape(landnaam(data, "EU27_2020"))}</th></tr></thead>
    <tbody>{"".join(rijen)}</tbody>
  </table></div>
  <p class="uitleg">{icoon("info")}<span>{T("uit_uitleg")}</span></p>
  {zo_vind}
  <p class="bron-klein">{T("uit_per_inwoner_noot", jaar=jaar)}</p>
  <footer class="bron">{icoon("bron")}<span>{T("bron")}: <a href="{escape(b["url"])}" rel="noopener">Eurostat · {escape(b["dataset"])}</a> (COFOG) · {T("opgehaald")} {datum(u.get("opgehaald"))}</span></footer>
</section>'''


def eu_voet(v) -> str:
    return f'<small>{T("ink_voet_eu", waarde=pct(v, 1))}</small>' if v is not None else ""


INKOMSTEN_KLEUREN = {"LAB": "#2a78d6", "C": "#eda100", "CAP": "#1baf7a"}


def inkomstenblok(data: dict, per_id: dict) -> str:
    """Waar komen onze belastingen vandaan? Arbeid, consumptie en kapitaal (Europese Commissie, Taxation Trends)."""
    u = data.get("inkomsten")
    if not u:
        return ""
    jaar = str(u["jaar"])
    deel = lambda code, geo="BE": (u["aandelen"].get(code, {}).get(geo) or {}).get(jaar)
    voet = lambda code, geo="BE": (u["impliciete_voet"].get(code, {}).get(geo) or {}).get(jaar)
    bev = waarde_in(per_id["bevolking"], "BE", int(jaar)) if "bevolking" in per_id else None
    balk = "".join(f'<i style="width:{deel(f["code"]) or 0:.2f}%;background:{INKOMSTEN_KLEUREN[f["code"]]}" title="{escape(f["nl"])}: {pct(deel(f["code"]) or 0, 1)}"></i>'
                   for f in u["functies"])
    rijen = []
    for f in u["functies"]:
        c = f["code"]
        mio = (u["miljoen_euro"].get(c) or {}).get(jaar)
        v, veu = voet(c), voet(c, "EU27_2020")
        controle = (f'<small class="cofog">{escape(c)} “{escape(f.get("officieel", ""))}” · <a href="{escape(f["api_url"])}" rel="noopener">{T("uit_controleer")}</a>'
                    f' · <a href="{escape(f["itr_url"])}" rel="noopener">{T("ink_voet").lower()}</a></small>')
        rijen.append(
            f'<tr><th scope="row"><span class="stip" style="background:{INKOMSTEN_KLEUREN[c]}"></span>{escape(f["nl"])}<small>{escape(f["uitleg"])}</small>{controle}</th>'
            f'<td>{eur(deel(c), 1) if deel(c) is not None else "—"}</td>'
            f'<td>{eur(mio * 1e6 / bev) if mio and bev else "—"}</td>'
            f'<td>{pct(deel(c, "EU27_2020"), 1) if deel(c, "EU27_2020") is not None else "—"}</td>'
            f'<td><b>{pct(v, 1) if v is not None else "—"}</b>{eu_voet(veu)}</td></tr>')
    b = u["bron"]
    return f'''
<section class="vz kaart uitgaven inkomsten" id="belastingen-per-soort">
  <header><p class="label">{T("ink_label")}</p><h3>{T("ink_titel")}</h3></header>
  <p class="intro-klein">{T("ink_intro", jaar=jaar)}</p>
  <button type="button" class="controle-knop js" aria-pressed="false" data-controle>{icoon("bron")}<span>{T("ink_toon_controle")}</span></button>
  <div class="honderd" role="img" aria-label="{T("ink_aria")}">{balk}</div>
  <div class="uitgaven-doos"><table>
    <thead><tr><th scope="col">{T("ink_soort")}</th><th scope="col">{T("uit_per_100")}</th><th scope="col">{T("uit_per_inwoner")}</th><th scope="col">{escape(landnaam(data, "EU27_2020"))}</th><th scope="col">{T("ink_voet")}</th></tr></thead>
    <tbody>{"".join(rijen)}</tbody>
  </table></div>
  <p class="uitleg">{icoon("info")}<span>{T("ink_uitleg")}</span></p>
  <p class="bron-klein">{T("ink_per_inwoner_noot", jaar=jaar)}</p>
  <footer class="bron">{icoon("bron")}<span>{T("bron")}: <a href="{escape(b["pagina"])}" rel="noopener">{T("ink_bron")}</a> · <a href="{escape(b["url"])}" rel="noopener">REDISSTAT</a> · {T("opgehaald")} {datum(u.get("opgehaald"))}</span></footer>
</section>'''


def officieel(f: dict) -> str:
    """Code en officiële Eurostat-naam van een uitgavenfunctie, met een link naar de exacte bevraging."""
    if not f.get("officieel"):
        return f'<small class="cofog">COFOG {escape(f["code"])}</small>'
    link = f' · <a href="{escape(f["api_url"])}" rel="noopener">{T("uit_controleer")}</a>' if f.get("api_url") else ""
    return f'<small class="cofog">COFOG {escape(f["code"])} “{escape(f["officieel"])}” {T("uit_officieel")}{link}</small>'


def periode_tekst(p: str) -> str:
    if "-Q" in p:
        return T("kwartaal", n=p[-1], jaar=p[:4])
    if len(p) == 10:  # weekcijfer: volledige datum
        return datum(p)
    return maand_tekst(p) if len(p) >= 7 else p


def mini_spark(punten: list, b: int = 160, h: int = 40) -> str:
    ys = [p[1] for p in punten]
    if len(ys) < 3:
        return ""
    lo, hi = min(ys), max(ys)
    span = (hi - lo) or 1
    pts = [(i / (len(ys) - 1) * (b - 6) + 3, h - 4 - (y - lo) / span * (h - 8)) for i, y in enumerate(ys)]
    nul = f'<line x1="0" x2="{b}" y1="{h - 4 - (0 - lo) / span * (h - 8):.1f}" y2="{h - 4 - (0 - lo) / span * (h - 8):.1f}" class="nul"/>' if lo < 0 < hi else ""
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<svg class="spark" viewBox="0 0 {b} {h}" aria-hidden="true">{nul}<path d="{d}" pathLength="1"/><circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3"/></svg>'


def snelkaart(r: dict) -> str:
    """Eén kaartje met een maand-, kwartaal- of weekcijfer."""
    p = r["punten"]
    laatst, vorig = p[-1], p[-2] if len(p) > 1 else None
    stap = 4 if "-Q" in laatst[0] else 52 if len(laatst[0]) == 10 else 12
    jaar_eerder = p[-1 - stap] if len(p) > stap else None
    fmt = lambda v: kort_met_eenheid(v, r)
    verschil = lambda a, b: (("+" if a - b > 0 else "−" if a - b < 0 else "±")
                             + (getal(abs(a - b), r["decimalen"]) + T("procentpunt") if r["eenheid"] == "%"
                                else kort_met_eenheid(abs(a - b), r)))
    regels = []
    if vorig:
        regels.append(T("tegenover", verschil=verschil(laatst[1], vorig[1]), periode=periode_tekst(vorig[0])))
    if jaar_eerder:
        regels.append(T("jaar_eerder", waarde=fmt(jaar_eerder[1])))
    if r.get("vergelijk"):
        v = {x[0]: x[1] for x in r["vergelijk"]["punten"]}
        if laatst[0] in v:
            regels.append(f'{escape(tx(r["vergelijk"]["naam"]))}: {fmt(v[laatst[0]])}')
    return (
        f'<article class="snel-kaart" id="{escape(r["id"])}"><p class="sk-vraag">{escape(tx(r["vraag"]))}</p>'
        f'<p class="sk-titel">{escape(tx(r["titel"]))}</p>'
        f'<p class="sk-waarde">{fmt(laatst[1])}</p><p class="sk-periode">{periode_tekst(laatst[0])}</p>'
        f'{mini_spark(p[-2 * stap:])}<ul>{"".join(f"<li>{x}</li>" for x in regels)}</ul>'
        f'<details><summary>{T("wat_is_dit")}</summary><p>{escape(tx(r["uitleg"]))}</p></details>'
        f'<p class="sk-bron">{T("bron")}: <a href="{escape(r["bron"]["url"])}" rel="noopener">{escape(tx(r["bron"].get("naam")) or T("nationale_bank"))}</a> · <a href="{escape(r["api_url"])}" rel="noopener">{T("ruwe_data")}</a></p></article>')


def mazoutkaarten(data: dict) -> str:
    """Weekprijs van mazout (Europese Commissie): als laatste kaart op de pagina Klimaat en energie."""
    reeksen = (data.get("olie") or {}).get("reeksen") or []
    return "".join(snelkaart(r).replace('class="snel-kaart"', 'class="kaart snel-kaart week-kaart"', 1) for r in reeksen)


def snelblok(data: dict) -> str:
    """De laatste maanden: maand- en kwartaalcijfers van de Nationale Bank."""
    snel = data.get("snel")
    if not snel:
        return ""
    kaarten = [snelkaart(r) for r in snel["reeksen"]]
    return (f'<section class="blok snel" aria-labelledby="snel-titel"><div class="blok-kop"><h2 id="snel-titel">{T("snel_titel")}</h2>'
            f'<span class="blok-noot">{T("snel_noot", datum=datum(snel.get("opgehaald")))}</span></div>'
            f'<div class="snel-raster">{"".join(kaarten)}</div></section>')


def regeringschakelaar() -> str:
    return ('<div class="regeringen js"><label class="schakelaar"><input type="checkbox" id="toon-regeringen">'
            f'<span class="schuif" aria-hidden="true"></span>{T("reg_schakelaar")}</label>'
            f'<p>{T("reg_uitleg")}</p></div>')


def themapagina(data: dict, thema: dict, vorige: dict, volgende: dict) -> str:
    pad = "../"
    bpad = pad + ("" if TAAL == "nl" else "../")
    per_id = {i["id"]: i for i in data["indicatoren"]}
    inds = [i for i in data["indicatoren"] if i["thema"] == thema["id"] and not i["verborgen"]]
    snel = "".join(f'<li><a href="#{i["id"]}">{escape(tx(i["vraag"]))}</a></li>' for i in inds)
    begrippen = "".join(f'<div><dt>{escape(data["begrippen"][b]["term"])}</dt><dd>{escape(data["begrippen"][b]["uitleg"])}</dd></div>'
                        for b in thema.get("begrippen", []) if b in data["begrippen"])
    schakelaar = regeringschakelaar() if thema["id"] in THEMAS_MET_REGERINGEN else ""
    inhoud = f'''
<section class="themakop" style="--t:{THEMA_KLEUR.get(thema["id"])}">
  <div class="binnen">
    <p class="kruimel"><a href="../">{MERK}</a> / {escape(thema["nl"])}</p>
    <div class="themakop-titel"><span class="tk-icoon groot">{icoon(thema["icoon"])}</span><h1>{escape(thema["vraag"])}</h1></div>
    <p class="intro">{escape(thema["intro"])}</p>
    <div class="themakop-onder">
      <aside class="bevoegd"><h2>{T("wie_beslist")}</h2><p>{escape(thema["bevoegd"])}</p></aside>
      <nav class="snel" aria-label="{T("op_deze_pagina")}"><h2>{T("op_deze_pagina")}</h2><ul>{snel}</ul></nav>
    </div>
  </div>
</section>
<div class="binnen" style="--t:{THEMA_KLEUR.get(thema["id"])}">
  {schakelaar}
  {vooruitzichtenblok(data) if thema["id"] == "economie" else ""}
  {inkomstenblok(data, per_id) if thema["id"] == "overheidsfinancien" else ""}
  {uitgavenblok(data, per_id) if thema["id"] == "overheidsfinancien" else ""}
  <div class="kaart-raster">{"".join(kaart(i, bpad) for i in inds)}{mazoutkaarten(data) if thema["id"] == "klimaat_energie" else ""}</div>
  {f'<section class="begrippen"><h2>{T("begrippen_titel")}</h2><dl>{begrippen}</dl></section>' if begrippen else ""}
  <nav class="buren-nav" aria-label="{escape(T("andere_themas"))}">
    <a href="{vorige["id"]}.html">{icoon("terug")}<span><small>{T("vorig_thema")}</small>{escape(vorige["nl"])}</span></a>
    <a href="{volgende["id"]}.html"><span><small>{T("volgend_thema")}</small>{escape(volgende["nl"])}</span>{icoon("pijl")}</a>
  </nav>
</div>
'''
    return pagina(f'{thema["nl"]} · {MERK}', thema["vraag"] + " " + thema["intro"][:140], inhoud, pad,
                  data, thema["id"], f'thema-{thema["id"]}', f'thema/{thema["id"]}.html')


def gewestenpagina(data: dict) -> str:
    """Vergelijkt Vlaanderen, Wallonië en Brussel voor elk cijfer waarvoor gewestcijfers bestaan."""
    pad = ""
    rijen = []
    for ind in data["indicatoren"]:
        if ind["verborgen"] or not any(g in ind["reeksen"] for g in GEWEST_CODES):
            continue
        # recentste jaar waarin alle drie de gewesten een cijfer hebben
        jaren = set.intersection(*[{r[0] for r in ind["reeksen"].get(g, [])} for g in GEWEST_CODES])
        if not jaren:
            continue
        jaar = max(jaren)
        waarden = [waarde_in(ind, g, jaar) for g in GEWEST_CODES]
        be, eu = waarde_in(ind, "BE", jaar), waarde_in(ind, "EU27_2020", jaar)
        alle = waarden + [v for v in (be, eu) if v is not None]
        hi = max(alle) if max(alle) > 0 else 1
        cellen = "".join(
            f'<td><span class="gw-waarde">{kort_met_eenheid(w, ind)}</span><span class="gw-balk"><i style="width:{max(2, w / hi * 100):.1f}%"></i></span></td>'
            for w in waarden)
        thema = ind["thema"]
        rijen.append(
            f'<tr style="--t:{THEMA_KLEUR.get(thema)}"><th scope="row"><a href="thema/{thema}.html#{ind["id"]}">{escape(tx(ind["vraag"]))}</a>'
            f'<small>{escape(tx(ind["titel"]))} · {jaar} · {T("bron").lower()}: {escape(ind["bron"].get("instelling", ""))}</small></th>{cellen}'
            f'<td class="gw-be">{kort_met_eenheid(be, ind) if be is not None else "—"}</td>'
            f'<td class="gw-be">{kort_met_eenheid(eu, ind) if eu is not None else "—"}</td></tr>')
    koppen = "".join(f'<th scope="col">{escape(landnaam(data, g))}</th>' for g in GEWEST_CODES + ["BE"])
    inhoud = f'''
<section class="themakop" style="--t:#1a1f24">
  <div class="binnen">
    <p class="kruimel"><a href="./">{MERK}</a> / {T("gw_kruimel")}</p>
    <div class="themakop-titel"><span class="tk-icoon groot">{icoon("kaart")}</span><h1>{T("gw_titel")}</h1></div>
    <p class="intro">{T("gw_intro")}</p>
    <div class="themakop-onder">
      <aside class="bevoegd"><h2>{T("gw_goed_titel")}</h2><p>{T("gw_goed")}</p></aside>
      <aside class="bevoegd"><h2>{T("gw_lees_titel")}</h2><p>{T("gw_lees")}</p></aside>
    </div>
  </div>
</section>
<div class="binnen">
  <div class="gw-tabel-doos"><table class="gw-tabel">
    <thead><tr><th scope="col">{T("gw_cijfer")}</th>{koppen}<th scope="col">{T("eu_kort")}</th></tr></thead>
    <tbody>{"".join(rijen)}</tbody>
  </table></div>
  <p class="voetnoot">{T("gw_voetnoot")}</p>
</div>
'''
    return pagina(f'{T("gw_kruimel")} · {MERK}', T("gw_beschrijving"), inhoud, pad, data, "gewesten", "gewesten", "gewesten.html")


def rekenpagina(data: dict) -> str:
    """Rekenmodule: van brutoloon naar belastingdruk (bedienden, inkomstenjaar 2026)."""
    P = yaml.safe_load((WORTEL / "config" / "fiscaal" / "2026.yaml").read_text(encoding="utf-8"))
    bronnen = []
    for sleutel, v in P.items():
        if isinstance(v, dict):
            for k, b in v.items():
                if k.startswith("bron") and isinstance(b, dict):
                    bronnen.append(f'<li><a href="{escape(b["url"])}" rel="noopener">{escape(b["naam"])}</a></li>')
    niet_lijst = data.get("_niet_meegerekend") or P["niet_meegerekend"]
    niet = "".join(f"<li>{escape(x)}</li>" for x in niet_lijst)
    kinderen = "".join(f'<option value="{k}">{k}</option>' for k in range(0, 7))
    kleur = THEMA_KLEUR["overheidsfinancien"]
    bpad = "" if TAAL == "nl" else "../"
    euro_voor, euro_na, _ = _eenheid("€")
    euro_veld = lambda veld: (f'<span class="invoer-euro"><b>€</b>{veld}</span>' if euro_voor else f'<span class="invoer-euro na">{veld}<b>€</b></span>')
    inhoud = f'''
<section class="themakop" style="--t:{kleur}">
  <div class="binnen">
    <p class="kruimel"><a href="./">{MERK}</a> / {T("rk_kruimel")}</p>
    <div class="themakop-titel"><span class="tk-icoon groot">{icoon("reken")}</span><h1>{T("rk_titel")}</h1></div>
    <p class="intro">{T("rk_intro", jaar=P["inkomstenjaar"])}</p>
  </div>
</section>
<div class="binnen reken" style="--t:{kleur}">
  <noscript><p class="geen-data">{T("rk_noscript")}</p></noscript>
  <form class="reken-invoer kaart" id="reken-form" autocomplete="off">
    <h2>{T("rk_situatie")}</h2>
    <label class="veld"><span>{T("rk_maandloon")}</span>{euro_veld('<input id="maandloon" type="number" inputmode="decimal" min="0" step="50" value="3500">')}</label>
    <label class="vink"><input id="vakantiegeld" type="checkbox" checked><span>{T("rk_vakantiegeld")} <small>{T("rk_vakantiegeld_noot", pct=getal(P["dubbel_vakantiegeld"]["percentage_maandloon"], 0))}</small></span></label>
    <label class="vink"><input id="eindejaarspremie" type="checkbox" checked><span>{T("rk_ejp")}</span></label>
    <label class="veld klein"><span>{T("rk_ejp_maanden")}</span><input id="ejp-maanden" type="number" min="0" max="3" step="0.25" value="1"></label>
    <label class="veld"><span>{T("rk_kinderen")}</span><select id="kinderen">{kinderen}</select></label>
    <div id="kind-extra" hidden>
      <label class="veld klein"><span>{T("rk_jonger3")}</span><input id="jonger3" type="number" min="0" max="6" step="1" value="0"></label>
      <label class="vink"><input id="alleenstaand" type="checkbox"><span>{T("rk_alleenstaand")}</span></label>
    </div>
    <label class="veld"><span>{T("rk_gemeente")} <small>{T("rk_gemeente_noot")}</small></span><span class="invoer-euro na"><input id="gemeente" type="number" min="0" max="12" step="0.1" value="{P["gemeentebelasting"]["voorbeeld_percentage"]}"><b>%</b></span></label>
  </form>
  <div class="reken-uitkomst" aria-live="polite">
    <section class="kaart">
      <p class="reken-kop">{T("rk_kop")}</p>
      <div class="reken-balk" id="r-balk" role="img" aria-label="{T("rk_balk_aria")}"></div>
      <ul class="reken-legende" id="r-legende"></ul>
      <div class="reken-cijfers">
        <div><span>{T("rk_bruto_jaar")}</span><b id="r-bruto">…</b></div>
        <div><span>{T("rk_netto_jaar")}</span><b id="r-netto">…</b></div>
        <div><span>{T("rk_netto_maand")}</span><b id="r-nettomaand">…</b><small id="r-nettomaand-noot"></small></div>
        <div><span>{T("rk_marginaal")}</span><b id="r-marg">…</b></div>
      </div>
      <p class="klein-grijs" id="r-zonder"></p>
      <p class="klein-grijs">{T("rk_loonbrief")}</p>
    </section>
    <section class="kaart">
      <h2>{T("rk_berekend")}</h2>
      <table class="reken-tabel"><tbody id="r-stappen"></tbody></table>
      <h3>{T("rk_schijven")}</h3>
      <p class="klein-grijs">{T("rk_schijven_uitleg")}</p>
      <table class="reken-tabel"><tbody id="r-schijven"></tbody></table>
    </section>
    <section class="kaart">
      <h2>{T("rk_waarheen")}</h2>
      <p class="klein-grijs">{T("rk_waarheen_uitleg")}</p>
      <ul class="waarheen" id="r-waarheen"></ul>
    </section>
    <section class="kaart">
      <h2>{T("rk_niet")}</h2>
      <p class="klein-grijs">{T("rk_niet_uitleg")}</p>
      <ul class="lijst">{niet}</ul>
      <h3>{T("rk_bronnen")}</h3>
      <ul class="lijst bronnen">{"".join(dict.fromkeys(bronnen))}</ul>
      <p class="klein-grijs">{T("rk_officieel")}</p>
    </section>
  </div>
</div>
<script src="{bpad}rekenmodule.js"></script>
<script src="{bpad}reken.js"></script>
'''
    return pagina(f'{T("rk_titel")} · {MERK}', T("rk_beschrijving"), inhoud, "", data, "reken", "thema-overheidsfinancien", "rekenmodule.html")


def overpagina(data: dict) -> str:
    """Over deze site: waarom, hoe, neutraliteit, bronnen, privacy, AI en de maker."""
    namen = data.get("_instellingen") or {}
    bronnen = []
    for naam, (url, voorwaarden) in VOORWAARDEN.items():
        label = T("over_voorwaarden") if voorwaarden else "website"
        bronnen.append(f'<li><b>{escape(namen.get(naam, naam))}</b> · <a href="{escape(url)}" rel="noopener">{label}</a></li>')
    privacy = T("over_privacy") + (" " + T("over_statistiek") if GOATCOUNTER else "")
    linkedin = f'<a class="li-knop" href="{LINKEDIN_URL}" rel="noopener">{icoon("profiel")}<span>LinkedIn</span></a>' if LINKEDIN_URL else ""
    bpad = "" if TAAL == "nl" else "../"
    blok = lambda titel, tekst: f'<section class="over-blok"><h2>{titel}</h2><p>{tekst}</p></section>'
    inhoud = f'''
<section class="themakop" style="--t:#3a434c">
  <div class="binnen">
    <p class="kruimel"><a href="./">{MERK}</a> / {T("over_titel")}</p>
    <div class="themakop-titel"><span class="tk-icoon groot">{icoon("info")}</span><h1>{T("over_titel")}</h1></div>
    <p class="intro">{T("over_intro")}</p>
  </div>
</section>
<div class="binnen over">
  {blok(T("over_hoe_titel"), T("over_hoe"))}
  {blok(T("over_neutraal_titel"), T("over_neutraal"))}
  <section class="over-blok"><h2>{T("over_bronnen_titel")}</h2><p>{T("over_bronnen")}</p><ul class="lijst">{"".join(bronnen)}</ul></section>
  {blok(T("over_privacy_titel"), privacy)}
  {blok(T("over_ai_titel"), T("over_ai"))}
  <section class="over-blok over-mij">
    <img src="{bpad}img/jonathan-maes.jpg" srcset="{bpad}img/jonathan-maes.jpg 1x, {bpad}img/jonathan-maes@2x.jpg 2x" width="120" height="120" alt="{MAKER}" loading="lazy">
    <div><h2>{T("over_mij_titel")}</h2><p>{T("over_mij")}</p>
    <p class="knoppen">{linkedin}<a class="li-knop" href="mailto:{CONTACT_PERSOONLIJK}">{icoon("mail")}<span>{CONTACT_PERSOONLIJK}</span></a></p></div>
  </section>
  <section class="over-blok"><h2>{T("over_fout_titel")}</h2><p>{T("voet_contact", mail=CONTACT, repo=REPO_URL)}</p></section>
</div>
'''
    return pagina(f'{T("over_titel")} · {MERK}', T("over_beschrijving"), inhoud, "", data, None, "index", "over.html")


def bouw_taal(basis: dict, taal: str) -> None:
    zet_taal(taal)
    data = vertaal(basis, taal)
    per_id = {i["id"]: i for i in data["indicatoren"]}
    PER_ID.clear()
    PER_ID.update(per_id)
    NAMEN.clear()
    NAMEN.update(data.get("_instellingen") or {})
    doel_map = SITE / map_van(taal)
    (doel_map / "thema").mkdir(parents=True, exist_ok=True)
    (doel_map / "index.html").write_text(startpagina(data, per_id), encoding="utf-8")
    (doel_map / "gewesten.html").write_text(gewestenpagina(data), encoding="utf-8")
    (doel_map / "rekenmodule.html").write_text(rekenpagina(data), encoding="utf-8")
    (doel_map / "over.html").write_text(overpagina(data), encoding="utf-8")
    themas = data["themas"]
    for n, t in enumerate(themas):
        html = themapagina(data, t, themas[n - 1], themas[(n + 1) % len(themas)])
        (doel_map / "thema" / f'{t["id"]}.html').write_text(html, encoding="utf-8")


def bouw() -> None:
    basis = json.loads((SITE / "data" / "dashboard.json").read_text(encoding="utf-8"))

    csv_map = SITE / "data" / "csv"
    csv_map.mkdir(parents=True, exist_ok=True)
    for f in (WORTEL / "data" / "clean").glob("*.csv"):
        shutil.copy(f, csv_map / f.name)

    # parameters voor de rekenmodule (met bronnen) naar de site kopiëren
    for f in (WORTEL / "config" / "fiscaal").glob("*.yaml"):
        (SITE / "data" / f"fiscaal-{f.stem}.json").write_text(
            json.dumps(yaml.safe_load(f.read_text(encoding="utf-8")), ensure_ascii=False, indent=1), encoding="utf-8")

    try:
        for taal in TALEN:
            bouw_taal(basis, taal)
        bouw_extra(basis)
    finally:
        zet_taal("nl")


def bouw_extra(basis: dict) -> None:
    """robots.txt, sitemap.xml, 404-pagina en webmanifest."""
    paginas = ["", "gewesten.html", "rekenmodule.html", "over.html"] + [f'thema/{t["id"]}.html' for t in basis["themas"]]
    dag = basis["gegenereerd"][:10]
    regels = []
    for url in paginas:
        alt = "".join(f'<xhtml:link rel="alternate" hreflang="{t}" href="{SITE_URL}{map_van(t)}{url}"/>' for t in TALEN)
        for t in TALEN:
            regels.append(f"<url><loc>{SITE_URL}{map_van(t)}{url}</loc><lastmod>{dag}</lastmod>{alt}</url>")
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(regels) + "\n</urlset>\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    (SITE / "site.webmanifest").write_text(json.dumps({
        "name": f"{MERK}: België in cijfers", "short_name": "België in cijfers", "start_url": "./", "display": "standalone",
        "background_color": "#f6f7f9", "theme_color": "#f6f7f9",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    # 404: GitHub Pages toont deze pagina bij een onbekend adres; absolute paden, want de map is onbekend
    zet_taal("nl")
    data = vertaal(basis, "nl")
    teksten = {t: (UI["t"]["n404_titel"][t], UI["t"]["n404_tekst"][t]) for t in TALEN}
    blokken = "".join(f'<section class="blok" lang="{t}"><h2>{escape(a)}</h2><p>{escape(b)}</p><p><a href="{SITE_URL}{map_van(t)}">{SITE_URL}{map_van(t)}</a></p></section>'
                      for t, (a, b) in teksten.items())
    from urllib.parse import urlparse
    wortel = urlparse(SITE_URL).path or "/"  # bv. /belgie-in-cijfers/ of / bij een eigen domein
    html = pagina(f"404 · {MERK}", teksten["nl"][1], f'<div class="binnen" style="padding:48px 0">{blokken}</div>', wortel, data, None, "index", "")
    (SITE / "404.html").write_text(html.replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"'), encoding="utf-8")


SJABLOON = """<!doctype html>
<html lang="{taal}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
<meta name="description" content="{beschrijving}">
<link rel="canonical" href="{url}">
{alternatieven}
<meta property="og:type" content="website">
<meta property="og:locale" content="{og_locale}">
<meta property="og:site_name" content="{merk}: {ondertitel}">
<meta property="og:title" content="{titel}">
<meta property="og:description" content="{beschrijving}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{titel}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og}">
<link rel="icon" href="{bpad}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{bpad}favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{bpad}apple-touch-icon.png">
<link rel="manifest" href="{bpad}site.webmanifest">
<meta name="theme-color" content="#0f1317">
<link rel="preload" href="{bpad}fonts/plex-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{bpad}style.css">
<script>document.documentElement.classList.add("met-js")</script>
</head>
<body>
<script type="application/json" id="ui">{ui}</script>
<a class="overslaan" href="#inhoud">{naar_inhoud}</a>
<header class="kop">
  <div class="binnen">
    <a class="merk" href="{pad}"><span class="merk-blok" aria-hidden="true"><i></i><i></i><i></i></span><span class="merk-tekst"><b>{merk}</b><span>{ondertitel}</span></span></a>
    <nav class="kop-links"><a class="kop-zoek" href="{pad}rekenmodule.html">{reken}<span>{kop_reken}</span></a><a class="kop-zoek" href="{pad}#zoek" aria-label="{zoek_aria}">{zoek}<span>{zoek_tekst}</span></a>{taalkeuze}</nav>
  </div>
</header>
{themabalk}
<main id="inhoud">
{inhoud}
</main>
<footer class="voet">
  <div class="binnen voet-raster">
    <div>
      <p class="voet-merk"><span class="merk-blok" aria-hidden="true"><i></i><i></i><i></i></span><b>{merk}: {ondertitel}</b></p>
      <p>{voet_project}</p>
      <p>{voet_code}</p>
      <p class="klein">{voet_onafhankelijk}</p>
    </div>
    <div>
      <p>{voet_maker}</p>
      <p>{voet_contact}</p>
      <p><a href="{pad}over.html">{over_link}</a></p>
      <p class="vibe">{voet_vibe}</p>
    </div>
  </div>
</footer>
<script src="{bpad}app.js" defer></script>
{statistiek}
</body>
</html>
"""

if __name__ == "__main__":
    bouw()
