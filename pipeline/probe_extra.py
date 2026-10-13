"""Verkenning voor nieuwe onderdelen: PISA, energieprijzen, mazout en de BBSZ.

Draait enkel bij een handmatige start van de workflow. Schrijft reports/extra.md.
"""
from __future__ import annotations

import io
import re
from pathlib import Path

import requests

from .probe_fiscaal import tekst

WORTEL = Path(__file__).resolve().parent.parent
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{ds}?geo=BE&lastTimePeriod=1&lang=EN"
DATASETS: list[str] = [  # ronde 3: gezondheid, mobiliteit en onderwerpen uit het politieke debat
    "hlth_hlye", "sdg_03_60", "hlth_cd_apr", "lfsa_igar", "hlth_rs_prs2", "hlth_rs_bds1",
    "tran_hv_psmod", "road_eqs_carhab", "road_eqr_zevpc", "sdg_12_30",
    "une_ltu_a", "lfsi_emp_a", "crim_pris_cap", "ilc_lvho07a", "ilc_mdsd11", "spr_exp_pens", "tps00001",
    "lfsa_ergan", "earn_nt_net", "prc_hicp_aind", "gov_10a_taxag",
]
LICENTIES = [
    "https://opendata.infrabel.be/pages/license/",
    "https://www.plan.be/nl/disclaimer",
    "https://www.plan.be/en/disclaimer",
    "https://www.nbb.be/nl/disclaimer-en-juridische-informatie/copyright-en-gebruik-van-informatie",
    "https://stat.nbb.be/",
]
OLIE = "https://energy.ec.europa.eu/document/download/906e60ca-8b6a-44e7-8589-652854d2fd3f_en?filename=Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx"
BBSZ = [
    "https://www.socialsecurity.be/employer/instructions/dmfa/nl/latest/instructions/special_contributions/other_specialcontributions/specialsocialsecuritycontribution.html",
    "https://www.ejustice.just.fgov.be/eli/wet/1994/03/30/1994000287/justel",
]


def eurostat(s: requests.Session, uit: list[str]) -> None:
    for ds in DATASETS:
        r = s.get(EUROSTAT.format(ds=ds), timeout=60)
        uit.append(f"## Eurostat {ds}\n- HTTP {r.status_code}")
        if r.status_code != 200:
            uit.append(f"```\n{r.text[:500]}\n```")
            continue
        j = r.json()
        uit.append(f"- titel: {j.get('label')}\n- bijgewerkt: {j.get('updated')}")
        for dim in j["id"]:
            cat = j["dimension"][dim]["category"]
            labels = cat.get("label", {})
            waarden = ", ".join(f"{k} ({labels.get(k, '')})" for k in list(cat["index"])[:80])
            uit.append(f"- **{dim}**: {waarden}")
        waarden = list(j.get("value", {}).items())[:12]
        uit.append(f"- eerste waarden: {waarden}\n")


def olie(s: requests.Session, uit: list[str]) -> None:
    return  # eerste ronde gedaan: structuur staat in een eerdere versie van dit rapport


def licenties(s: requests.Session, uit: list[str]) -> None:
    for url in LICENTIES:
        r = s.get(url, timeout=60)
        t = tekst(r.text)
        uit.append(f"## Licentie: {url}\n- HTTP {r.status_code}, {len(t)} tekens")
        for woord in ("licen", "hergebruik", "reuse", "re-use", "reproduc", "copyright", "bronvermelding", "Creative Commons", "CC BY"):
            for m in list(re.finditer(re.escape(woord), t, re.I))[:3]:
                uit.append(f"> …{t[max(0, m.start() - 300):m.start() + 600]}…")


def _bbsz_oud(s, uit):
    import openpyxl
    r = s.get(OLIE, timeout=120)
    uit.append(f"## Weekly Oil Bulletin, historiek\n- HTTP {r.status_code}, {len(r.content)} bytes, {r.headers.get('Content-Type')}")
    if r.status_code != 200:
        return
    wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True, data_only=True)
    for ws in wb.worksheets:
        uit.append(f"### blad {ws.title!r} ({ws.max_row} rijen × {ws.max_column} kolommen)")
        for i, rij in enumerate(ws.iter_rows(values_only=True)):
            if i >= 8:
                break
            uit.append("    " + " | ".join("" if v is None else str(v)[:40] for v in rij[:40]))


def bbsz(s: requests.Session, uit: list[str]) -> None:
    # 1. RSZ-instructie: volledige tekst vanaf de schaal (voorschotten per kwartaal)
    r = s.get(BBSZ[0], timeout=60)
    t = tekst(r.text)
    i = t.find("Bijzondere bijdrage voor de sociale zekerheid\nBehalve")
    uit.append(f"## BBSZ RSZ-instructie\n```\n{t[i:i + 14000]}\n```")
    # 2. Wet van 30 maart 1994 (art. 106-112): de jaarlijkse schaal op het aanslagbiljet
    r = s.get(BBSZ[1], timeout=60)
    uit.append(f"## BBSZ wet: {BBSZ[1]} HTTP {r.status_code}\n```\n{r.text[:3000]}\n```")
    kandidaten = set(re.findall(r'(?:src|href)="([^"]+)"', r.text))
    for k in sorted(kandidaten):
        if any(w in k for w in ("cgi", "loi", "justel", "article", "cn=", "eli")):
            uit.append(f"- link: {k}")
    for url in (
        "https://www.ejustice.just.fgov.be/cgi_loi/loi_a1.pl?language=nl&la=N&cn=1994033032&table_name=wet&&caller=list&fromtab=wet&tri=dd+AS+RANK",
        "https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=nl&la=N&table_name=wet&cn=1994033032",
        "https://www.ejustice.just.fgov.be/eli/wet/1994/03/30/1994000287/justel?lang=nl",
    ):
        try:
            p = s.get(url, timeout=60)
        except requests.RequestException as e:
            uit.append(f"- {url}: {e}")
            continue
        p.encoding = p.apparent_encoding
        tt = tekst(p.text)
        uit.append(f"### {url}\n- HTTP {p.status_code}, {len(tt)} tekens")
        for m in re.finditer(r"Art\.\s*107", tt):
            uit.append(f"```\n{tt[m.start():m.start() + 7000]}\n```")
            break
    return
    for url in BBSZ:
        r = s.get(url, timeout=60)
        t = tekst(r.text)
        uit.append(f"## BBSZ: {url}\n- HTTP {r.status_code}, {len(t)} tekens")
        if "ejustice" in url:
            for m in re.finditer(r"Art\.\s*10[6-9]\b", t):
                uit.append(f"```\n{t[m.start():m.start() + 6000]}\n```")
                break
        else:
            i = t.lower().find("bijzondere bijdrage")
            uit.append(f"```\n{t[max(0, i):][:15000]}\n```")


def riziv(s: requests.Session, uit: list[str]) -> None:
    """Jaarlijkse statistiek invaliditeit (PDF) van het RIZIV: is de opbouw stabiel genoeg om automatisch te lezen?"""
    from pypdf import PdfReader
    for jaar in (2015, 2019, 2025):
        for semester in (1,):
            url = f"https://www.inami.fgov.be/SiteCollectionDocuments/stat_du{jaar}_{semester}_invaliditeit.pdf"
            try:
                r = s.get(url, timeout=90)
            except requests.RequestException as e:
                uit.append(f"- {url}: {e}")
                continue
            uit.append(f"## {url}\n- HTTP {r.status_code}, {len(r.content)} bytes, {r.headers.get('Content-Type')}")
            if r.status_code != 200 or not r.content.startswith(b"%PDF"):
                continue
            pdf = PdfReader(io.BytesIO(r.content))
            uit.append(f"- {len(pdf.pages)} pagina's")
            for i, pg in enumerate(pdf.pages[:8]):
                uit.append(f"### pagina {i + 1}\n```\n{(pg.extract_text() or '')[:3500]}\n```")


def belastingen(s: requests.Session, uit: list[str]) -> None:
    """REDISSTAT (DG TAXUD): alle dataflows en per dataflow de dimensies voor België."""
    basis = "https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination"
    r = s.get(f"{basis}/sdmx/2.1/dataflow/all?format=JSON", timeout=90)
    items = r.json()["link"]["item"]
    uit.append("## Dataflows\n" + "\n".join(f"- {x['extension']['id']}: {x['label']}" for x in items))
    for x in items:
        ds = x["extension"]["id"]
        url = f"{basis}/statistics/1.0/data/{ds}?geo=BE&lastTimePeriod=1&lang=EN"
        try:
            q = s.get(url, timeout=90)
        except requests.RequestException as e:
            uit.append(f"## {ds}: {e}")
            continue
        uit.append(f"## {ds} ({x['label']})\n- {url}\n- HTTP {q.status_code}")
        if q.status_code != 200:
            uit.append(f"```\n{q.text[:300]}\n```")
            continue
        j = q.json()
        for dim in j.get("id", []):
            cat = j["dimension"][dim]["category"]
            lab = cat.get("label", {})
            uit.append(f"- **{dim}**: " + ", ".join(f"{k} ({lab.get(k, '')})" for k in list(cat["index"])[:70]))
        uit.append(f"- eerste waarden: {list(j.get('value', {}).items())[:8]}")


BESTAT = "https://bestat.statbel.fgov.be/bestat/api/views/3a4cfb82-0c67-4f97-94f3-58b2509763ab"
FOD = [
    "https://economie.fgov.be/nl/themas/energie/energieprijzen/maximumprijzen",
    "https://economie.fgov.be/nl/themas/energie/energieprijzen",
    "https://economie.fgov.be/nl/zoeken?search_api_fulltext=maximumprijzen+petroleumproducten",
]


def brandstof(s: requests.Session, uit: list[str]) -> None:
    """Maximumprijzen benzine en diesel: be.STAT (Statbel, bron FOD Economie) en de pagina's van FOD Economie."""
    for pad in ("", "/result/JSON", "/result/CSV", "/result/XLSX"):
        try:
            r = s.get(BESTAT + pad, timeout=60)
            uit.append(f"## be.STAT {pad or '(metadata)'}\n- HTTP {r.status_code}, {r.headers.get('content-type')}\n```\n{r.text[:2500]}\n```")
        except requests.RequestException as e:
            uit.append(f"## be.STAT {pad}: {e}")
    gezien = set()
    for url in FOD:
        try:
            r = s.get(url, timeout=60)
        except requests.RequestException as e:
            uit.append(f"## {url}: {e}")
            continue
        links = sorted(set(re.findall(r'href="([^"]+)"', r.text)))
        relevant = [l for l in links if re.search(r"maximum|petrol|aardolie|brandstof|carbur|\.xlsx|\.csv|\.pdf|officiele-prijs|tarief", l, re.I)]
        uit.append(f"## {url}\n- HTTP {r.status_code}\n" + "\n".join(f"- {l}" for l in relevant[:80]))
        for l in relevant:
            if l.startswith("/"):
                l = "https://economie.fgov.be" + l
            if l in gezien or not l.startswith("https://economie.fgov.be") or len(gezien) > 12:
                continue
            gezien.add(l)
            try:
                q = s.get(l, timeout=60)
            except requests.RequestException:
                continue
            if "html" in (q.headers.get("content-type") or ""):
                t = re.sub(r"<script.*?</script>|<style.*?</style>", "", q.text, flags=re.S)
                tabel = re.findall(r"<table.*?</table>", t, flags=re.S)
                sub = sorted(set(x for x in re.findall(r'href="([^"]+)"', t) if re.search(r"\.xlsx|\.csv|\.pdf|\.xls", x, re.I)))
                uit.append(f"### {l}\n- HTTP {q.status_code}\n- bestanden: {sub[:30]}\n```\n{re.sub(r'<[^>]+>', ' ', tabel[0])[:2000] if tabel else re.sub(r'<[^>]+>', ' ', t)[:1500]}\n```")
            else:
                uit.append(f"### {l}\n- HTTP {q.status_code}, {q.headers.get('content-type')}, {len(q.content)} bytes")


def main() -> None:
    s = requests.Session()
    s.headers["User-Agent"] = "belgie-in-cijfers (bronverkenning; github.com/jonathanmaes97/belgie-in-cijfers)"
    uit = ["# Verkenning: PISA, energieprijzen, mazout, BBSZ\n"]
    for stap in (brandstof,):
        try:
            stap(s, uit)
        except Exception as e:  # een verkenning mag nooit de publicatie tegenhouden
            uit.append(f"## {stap.__name__}: FOUT {type(e).__name__}: {e}\n")
    (WORTEL / "reports" / "brandstof.md").write_text("\n".join(uit) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
