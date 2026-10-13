"""Promomateriaal voor sociale media: een carrousel (PDF + PNG's, 1080×1350) en screenshots van de site.

Alle getallen komen uit site/data/dashboard.json en worden opgemaakt met dezelfde functies als de site.
Gebruik: python -m pipeline.promo [map]   (vereist Playwright en een lokale webserver niet: we openen bestanden)
"""
from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

from . import build_site as bs
from .build_site import SITE, SITE_URL, THEMA_KLEUR, eur, getal, kort_met_eenheid, laatste, pct, waarde_in

FONTS = (SITE / "fonts").resolve().as_uri()
DOMEIN = SITE_URL.replace("https://", "").rstrip("/")


def dia(inhoud: str, bron: str, nummer: int, totaal: int, kleur: str = "#2357a6") -> str:
    return f"""<!doctype html><html lang="nl"><head><meta charset="utf-8"><style>
@font-face {{ font-family: Plex; src: url("{FONTS}/plex-sans.woff2"); font-weight: 100 700; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 1080px; height: 1350px; overflow: hidden; background: #f6f7f9; color: #1a1f24; font-family: Plex, sans-serif; position: relative; }}
.raster {{ position: absolute; inset: 0; background-image: linear-gradient(rgba(20,30,45,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(20,30,45,.05) 1px, transparent 1px); background-size: 54px 54px; }}
.gloed {{ position: absolute; width: 760px; height: 760px; border-radius: 50%; filter: blur(110px); opacity: .32; background: #fdda24; right: -260px; top: -340px; }}
.gloed2 {{ position: absolute; width: 620px; height: 620px; border-radius: 50%; filter: blur(120px); opacity: .14; background: #ef3340; right: -320px; top: 260px; }}
.binnen {{ position: absolute; inset: 0; padding: 84px 84px 64px; display: flex; flex-direction: column; }}
.merk {{ display: flex; align-items: center; gap: 18px; }}
.vlag {{ display: flex; gap: 4px; height: 48px; }} .vlag i {{ width: 10px; border-radius: 3px; }}
.vlag i:nth-child(1) {{ background: #1f1f1f; }} .vlag i:nth-child(2) {{ background: #fdda24; }} .vlag i:nth-child(3) {{ background: #ef3340; }}
.merk b {{ display: block; font-size: 24px; font-weight: 500; color: #5b636b; }} .merk span {{ font-size: 30px; font-weight: 600; }}
.label {{ margin-top: 92px; font-size: 32px; font-weight: 600; color: var(--k); }}
h1 {{ font-size: 76px; line-height: 1.04; letter-spacing: -.035em; font-weight: 650; margin-top: 18px; }}
h1.groot {{ font-size: 104px; margin-top: 110px; }}
.sub {{ font-size: 36px; line-height: 1.38; color: #4a525a; margin-top: 30px; max-width: 880px; }}
.getal {{ font-size: 190px; font-weight: 650; letter-spacing: -.05em; line-height: 1; margin-top: 54px; color: var(--k); }}
.inhoud {{ margin-top: 56px; }}
.balk {{ display: flex; height: 64px; border-radius: 14px; overflow: hidden; gap: 4px; }}
.balk i {{ display: block; height: 100%; }}
.rij {{ display: grid; grid-template-columns: 34px 1fr auto; gap: 18px; align-items: baseline; font-size: 38px; padding: 22px 0; border-bottom: 2px solid #e1e4e8; }}
.rij .stip {{ width: 26px; height: 26px; border-radius: 7px; align-self: center; }}
.rij b {{ font-weight: 650; font-variant-numeric: tabular-nums; }}
.rij small {{ grid-column: 2 / 4; font-size: 27px; color: #6b737b; margin-top: -6px; }}
.gw {{ display: grid; grid-template-columns: 250px 1fr 150px; gap: 22px; align-items: center; font-size: 38px; margin: 18px 0; }}
.gw i {{ display: block; height: 34px; border-radius: 10px; background: var(--k); }}
.gw b {{ text-align: right; font-variant-numeric: tabular-nums; }}
.kop2 {{ font-size: 30px; font-weight: 600; color: #5b636b; margin: 46px 0 6px; }}
.kolommen {{ display: flex; align-items: flex-end; gap: 14px; height: 380px; margin-top: 30px; }}
.kolommen div {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%; gap: 10px; }}
.kolommen i {{ display: block; width: 100%; border-radius: 8px 8px 0 0; background: var(--k); }}
.kolommen span {{ font-size: 24px; color: #6b737b; }}
.voet {{ margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; font-size: 24px; color: #5b636b; gap: 30px; }}
.voet .bron {{ max-width: 720px; line-height: 1.35; }}
.voet .url {{ font-weight: 600; color: #1a1f24; font-size: 28px; white-space: nowrap; }}
.pagina {{ position: absolute; top: 96px; right: 84px; font-size: 24px; color: #80888f; }}
.kern {{ display: grid; grid-template-columns: repeat(3, 1fr); margin-top: 80px; border: 2px solid #e1e4e8; border-radius: 22px; background: rgba(255,255,255,.75); overflow: hidden; }}
.kern div {{ padding: 30px 28px; border-right: 2px solid #e1e4e8; display: flex; flex-direction: column; gap: 8px; }}
.kern div:last-child {{ border-right: 0; }}
.kern b {{ font-size: 50px; letter-spacing: -.03em; }} .kern span {{ font-size: 24px; color: #6b737b; }}
.rij.klein {{ font-size: 31px; padding: 9px 0; }}
.invoer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 32px; padding: 30px 36px; border: 3px solid #1a1f24; border-radius: 22px; background: #fff; font-size: 34px; color: #5b636b; }}
.invoer b {{ font-size: 60px; color: #1a1f24; letter-spacing: -.02em; }}
.maker {{ display: inline-flex; align-items: center; gap: 18px; font-size: 25px; line-height: 1.3; }}
.maker b {{ color: #1a1f24; font-size: 29px; }}
.maker img {{ width: 84px; height: 84px; border-radius: 50%; object-fit: cover; }}
.stapel {{ position: relative; align-self: center; width: 560px; margin-top: 84px; flex-shrink: 0; }}
.stapel > i {{ position: absolute; inset: 0; border-radius: 18px; background: #fff; border: 2px solid #dfe3e7; box-shadow: 0 10px 30px rgba(20,30,45,.08); }}
.stapel > i:nth-of-type(1) {{ transform: translate(34px, -22px) rotate(3deg); opacity: .55; }}
.stapel > i:nth-of-type(2) {{ transform: translate(17px, -11px) rotate(1.5deg); opacity: .8; }}
.voorbeeld {{ position: absolute; top: -50px; left: -60px; z-index: 2; background: #fdda24; color: #1a1f24; font-size: 22px; font-weight: 600; padding: 8px 16px; border-radius: 10px; transform: rotate(-3deg); box-shadow: 0 6px 16px rgba(20,30,45,.12); }}
.scherm {{ position: relative; border-radius: 18px; overflow: hidden; border: 2px solid #dfe3e7; box-shadow: 0 24px 60px rgba(20,30,45,.16); background: #fff; }}
.cta-midden {{ align-self: center; margin-top: 40px; font-size: 38px; padding: 22px 40px; }}
.scherm-balk {{ display: flex; align-items: center; gap: 9px; height: 46px; padding: 0 20px; background: #eef0f3; border-bottom: 2px solid #dfe3e7; }}
.scherm-balk i {{ width: 13px; height: 13px; border-radius: 50%; background: #c9ced4; }}
.scherm-balk span {{ margin-left: 18px; font-size: 20px; color: #6b737b; }}
.scherm img {{ display: block; width: 100%; }}
.cta {{ display: inline-block; margin-top: 70px; padding: 28px 44px; border-radius: 18px; background: #1a1f24; color: #fff; font-size: 40px; font-weight: 600; }}
</style></head><body style="--k:{kleur}"><div class="raster"></div><div class="gloed"></div><div class="gloed2"></div>
<div class="binnen">
  <div class="merk"><div class="vlag"><i></i><i></i><i></i></div><div><b>State of the Union</b><span>België in cijfers</span></div></div>
  <div class="pagina">{nummer}/{totaal}</div>
  {inhoud}
  <div class="voet"><span class="bron">{bron}</span><span class="url">{DOMEIN}</span></div>
</div></body></html>"""


TOTAAL = 10


def rekenvoorbeeld(maandloon: float) -> dict:
    """Rekent met dezelfde rekenmodule als de site (site/rekenmodule.js), via Node."""
    import subprocess
    code = (f"const R=require('{(SITE / 'rekenmodule.js').as_posix()}');"
            f"const P=require('{(SITE / 'data' / 'fiscaal-2026.json').as_posix()}');"
            f"const u=R.bereken({{maandloon:{maandloon},vakantiegeld:true,eindejaarspremie:true,eindejaarsMaanden:1,kinderen:0,"
            f"gemeentePct:P.gemeentebelasting.voorbeeld_percentage}},P);console.log(JSON.stringify(u));")
    return json.loads(subprocess.run(["node", "-e", code], capture_output=True, text=True, check=True).stdout)


def dias(d: dict, scherm: Path | None = None) -> list[tuple[str, str]]:
    bs.zet_taal("nl")
    p = {i["id"]: i for i in d["indicatoren"]}
    teller = iter(range(1, 100))
    volgende = lambda: next(teller)
    uit = []

    # 1. opening, met drie kerncijfers
    kern = '<div class="kern">' + "".join(
        f'<div><b>{kort_met_eenheid(laatste(p[i], "BE")[1], p[i])}</b><span>{escape(p[i]["titel"]["nl"])}, {laatste(p[i], "BE")[0]}</span></div>'
        for i in ("schuld_per_inwoner", "rente_per_dag", "werkzaamheidsgraad")) + "</div>"
    uit.append(("01-opening", dia(
        '<h1 class="groot">Hoe gaat het<br>met België?</h1>'
        '<p class="sub">De belangrijkste officiële cijfers over ons land op één plek. In gewone taal, met bij elk cijfer de bron, en elke dag automatisch bijgewerkt.</p>'
        '<p class="sub">In het Nederlands, Frans, Duits en Engels.</p>'
        + kern,
        "Eurostat · Nationale Bank · Federaal Planbureau · RIZIV · Europese Commissie", volgende(), TOTAAL)))

    # 2. belastingen: waar komen ze vandaan
    ink = d["inkomsten"]
    j = str(ink["jaar"])
    kl = {"LAB": "#2a78d6", "C": "#eda100", "CAP": "#1baf7a"}
    deel = {f["code"]: ink["aandelen"][f["code"]]["BE"][j] for f in ink["functies"]}
    voet = {f["code"]: ink["impliciete_voet"][f["code"]] for f in ink["functies"]}
    balk = "".join(f'<i style="width:{deel[c]:.2f}%;background:{kl[c]}"></i>' for c in deel)
    rijen = "".join(
        f'<div class="rij"><span class="stip" style="background:{kl[f["code"]]}"></span><span>{escape(f["nl"])}</span><b>{eur(deel[f["code"]], 1)}</b>'
        f'<small>gemiddeld belast aan {pct(voet[f["code"]]["BE"][j], 1)} (EU: {pct(voet[f["code"]]["EU27_2020"][j], 1)})</small></div>'
        for f in ink["functies"])
    uit.append(("02-belastingen", dia(
        f'<p class="label">Belastingen</p><h1>Van elke 100 euro belastingen komt {eur(deel["LAB"], 1)} uit arbeid.</h1>'
        f'<div class="inhoud"><div class="balk">{balk}</div>{rijen}</div>',
        f"Europese Commissie, Data on Taxation Trends ({j}); alle belastingen en sociale bijdragen samen", volgende(), TOTAAL, THEMA_KLEUR["overheidsfinancien"])))

    # 3. uitgaven
    u = d["uitgaven"]
    ju = str(u["jaar"])
    top = sorted(u["functies"], key=lambda f: -(u["aandelen"][f["code"]]["BE"].get(ju) or 0))[:5]
    kleuren = bs.UITGAVEN_KLEUREN
    if not any(f["code"] == "GF02" for f in top):  # defensie altijd tonen, ook buiten de top vijf
        top.append(next(f for f in u["functies"] if f["code"] == "GF02"))
    rijen = "".join(f'<div class="rij"><span class="stip" style="background:{kleuren[i % len(kleuren)]}"></span><span>{escape(f["nl"])}</span><b>{eur(u["aandelen"][f["code"]]["BE"][ju], 1)}</b></div>'
                    for i, f in enumerate(top))
    uit.append(("03-uitgaven", dia(
        f'<p class="label">Uitgaven</p><h1>En waar gaan die 100 euro naartoe?</h1>'
        f'<div class="inhoud">{rijen}<p class="sub" style="font-size:30px">De vijf grootste posten van alle Belgische overheden samen, en defensie, in {ju}.</p></div>',
        f"Eurostat, gov_10a_exp (COFOG), {ju}", volgende(), TOTAAL, THEMA_KLEUR["overheidsfinancien"])))

    # 3b. rekenmodule: vul je brutoloon in
    loon = 3500
    rk = rekenvoorbeeld(loon)
    # concrete posten: pensioenen, zorg, onderwijs, rente, veiligheid, defensie (aandeel in alle overheidsuitgaven)
    namen = {f["code"]: f["nl"] for f in u["functies"] + u["details"]}
    posten = [("GF1002", "Pensioenen en ouderenzorg"), ("GF07", namen["GF07"]), ("GF09", namen["GF09"]),
              ("GF0107", "Rente op de staatsschuld"), ("GF03", namen["GF03"]), ("GF02", namen["GF02"])]
    waarheen = "".join(
        f'<div class="rij klein"><span class="stip" style="background:{kleuren[i % len(kleuren)]}"></span><span>{escape(naam)}</span><b>{eur(rk["totaal"] * u["aandelen"][code]["BE"][ju] / 100)}</b></div>'
        for i, (code, naam) in enumerate(posten))
    rest = rk["totaal"] * (1 - sum(u["aandelen"][code]["BE"][ju] for code, _ in posten) / 100)
    waarheen += f'<div class="rij klein" style="color:#6b737b"><span class="stip" style="background:#c9ced4"></span><span>Al de rest (andere uitkeringen, economie …)</span><b>{eur(rest)}</b></div>'
    gem = json.loads((SITE / "data" / "fiscaal-2026.json").read_text(encoding="utf-8"))["gemeentebelasting"]["voorbeeld_percentage"]
    uit.append(("rekenmodule", dia(
        f'<p class="label">Rekenmodule</p><h1 style="font-size:56px">Vul je brutoloon in en zie waar je bijdrage naartoe gaat.</h1>'
        f'<div class="invoer"><span>Brutoloon per maand</span><b>{eur(loon)}</b></div>'
        f'<p class="sub" style="font-size:30px;margin-top:28px">Je betaalt <b style="color:#1a1f24">{pct(rk["druk"] * 100, 1)}</b> aan sociale bijdragen en belastingen: '
        f'{eur(rk["totaal"])} per jaar. Verdeeld zoals alle overheidsuitgaven gaat dat naar:</p>'
        f'<div class="inhoud" style="margin-top:20px">{waarheen}</div>',
        f"Voorbeeld: bediende, alleenstaand, met vakantiegeld en eindejaarspremie, gemeentebelasting {pct(gem, 0)}. Tarieven 2026.",
        volgende(), TOTAAL, THEMA_KLEUR["overheidsfinancien"])))

    # 4. gewesten
    def gw(ind_id: str) -> tuple[str, int]:
        ind = p[ind_id]
        jaren = set.intersection(*[{r[0] for r in ind["reeksen"][g]} for g in bs.GEWEST_CODES])
        jr = max(jaren)
        vals = [(g, waarde_in(ind, g, jr)) for g in bs.GEWEST_CODES]
        hi = max(v for _, v in vals)
        namen = {"BE1": "Brussel", "BE2": "Vlaanderen", "BE3": "Wallonië"}
        return "".join(f'<div class="gw"><span>{namen[g]}</span><i style="width:{v / hi * 100:.0f}%"></i><b>{kort_met_eenheid(v, ind)}</b></div>' for g, v in vals), jr
    werk, jw = gw("werkzaamheidsgraad")
    arm, ja = gw("armoede_uitsluiting")
    uit.append(("04-gewesten", dia(
        f'<p class="label">Per gewest</p><h1>Eén land, drie heel verschillende gewesten.</h1>'
        f'<p class="kop2">Hoeveel 20- tot 64-jarigen werken er? ({jw})</p>{werk}'
        f'<p class="kop2">Hoeveel mensen lopen risico op armoede? ({ja})</p>{arm}',
        f'Eurostat, {p["werkzaamheidsgraad"]["bron"].get("regionaal_dataset")} en {p["armoede_uitsluiting"]["bron"].get("regionaal_dataset")}', volgende(), TOTAAL, "#3a434c")))

    # 5. langdurig zieken
    inv = p["invaliditeit"]["reeksen"]["BE"]
    reeks = inv[-11:]
    hi = max(r[1] for r in reeks)
    kol = "".join(f'<div><i style="height:{r[1] / hi * 100:.1f}%;opacity:{0.55 if "p" in r[2] else 1}"></i><span>{str(r[0])[2:] if i % 2 else r[0]}</span></div>' for i, r in enumerate(reeks))
    eerste, laatst = reeks[0], reeks[-1]
    uit.append(("05-langdurig-ziek", dia(
        f'<p class="label">Werk</p><div class="getal">{getal(laatst[1], 0)}</div>'
        f'<h1 style="font-size:58px">werknemers en werklozen zijn langdurig ziek (invaliditeit, {laatst[0]}).</h1>'
        f'<p class="sub" style="font-size:32px">In {eerste[0]} waren dat er {getal(eerste[1], 0)}.</p>'
        f'<div class="kolommen">{kol}</div>',
        f"RIZIV, statistieken invaliditeit (op 31 december; {laatst[0]} is voorlopig)", volgende(), TOTAAL, THEMA_KLEUR["werk"])))

    # 6. gevangenissen
    gev = p["gevangenis_bezetting"]["reeksen"]["BE"][-1]
    uit.append(("06-gevangenissen", dia(
        f'<p class="label">Justitie</p><div class="getal">{pct(gev[1], 0)}</div>'
        f'<h1 style="font-size:64px">Zo vol zitten de Belgische gevangenissen ({gev[0]}).</h1>'
        f'<p class="sub">Boven de honderd zijn er meer gedetineerden dan plaatsen.</p>',
        f"Eurostat, crim_pris_cap: aantal gedetineerden gedeeld door de officiële capaciteit", volgende(), TOTAAL, THEMA_KLEUR["veiligheid_justitie"])))

    # 7. gezondheid
    le, hly = laatste(p["levensverwachting"], "BE"), laatste(p["gezonde_levensjaren"], "BE")
    uit.append(("07-gezondheid", dia(
        f'<p class="label">Gezondheid</p><h1>We worden gemiddeld {kort_met_eenheid(le[1], p["levensverwachting"])} oud.</h1>'
        f'<div class="getal" style="font-size:150px">{kort_met_eenheid(hly[1], p["gezonde_levensjaren"])}</div>'
        f'<h1 style="font-size:58px">daarvan leven we zonder beperkingen door onze gezondheid.</h1>',
        f'Eurostat, {p["levensverwachting"]["bron"]["dataset"]} en {p["gezonde_levensjaren"]["bron"]["dataset"]} ({hly[0]})', volgende(), TOTAAL, THEMA_KLEUR["gezondheid"])))

    # 8. rente: wat kostte de schuld terwijl je deze carrousel bekeek?
    rj, rente_jaar, rvl = p["rentelasten_eur"]["reeksen"]["BE"][-1]  # miljoen euro per jaar
    per_minuut = rente_jaar * 1e6 / (365 * 24 * 60)
    uit.append(("rente", dia(
        '<p class="label">Schuld</p><h1 style="font-size:60px">Sinds je deze carrousel opende, betaalde de Belgische overheid al ongeveer</h1>'
        f'<div class="getal">{eur(round(per_minuut, -2))}</div>'
        '<h1 style="font-size:60px">aan rente op haar schuld.</h1>'
        f'<p class="sub" style="font-size:32px">Dat is {getal(rente_jaar / 365, 1)} miljoen euro per dag.</p>',
        f"Aannames: je bekijkt de carrousel in één minuut; de rentelasten van {rj}{' (voorlopig)' if 'p' in rvl else ''}, "
        f"{getal(rente_jaar / 1000, 1)} miljard euro, gelijk gespreid over het jaar. Alle overheden samen. Bron: Eurostat, gov_10a_main (D41PAY).",
        volgende(), TOTAAL, THEMA_KLEUR["overheidsfinancien"])))

    # 9. afsluiter
    n_cijfers = sum(1 for i in d["indicatoren"] if not i.get("verborgen"))
    if scherm:
        inhoud = ('<h1 class="groot" style="font-size:80px;margin-top:56px">Zoek het zelf op.</h1>'
                  '<p class="sub" style="font-size:34px;margin-top:20px">Elk cijfer met een link naar de bron. Geen mening, geen reclame, geen cookies.</p>'
                  f'<div class="stapel"><span class="voorbeeld">Eén voorbeeld van de {n_cijfers} cijfers op de site</span>'
                  f'<i></i><i></i><div class="scherm"><img src="{scherm.resolve().as_uri()}" alt=""></div></div>'
                  f'<span class="cta cta-midden">👉 {DOMEIN}</span>')
    else:
        inhoud = ('<h1 class="groot" style="font-size:88px">Zoek het zelf op.</h1>'
                  '<p class="sub">Elk cijfer met een link naar de bron. Een rekenmodule voor je eigen belastingen. Vlaanderen, Wallonië en Brussel naast elkaar. Geen mening, geen reclame, geen cookies.</p>'
                  f'<span class="cta">{DOMEIN}</span>')
    uit.append(("08-afsluiter", dia(
        inhoud,
        f'<span class="maker"><img src="{(SITE / "img" / "jonathan-maes@2x.jpg").resolve().as_uri()}" alt=""><span>Een onafhankelijk project van<br><b>Jonathan Maes</b></span></span>',
        volgende(), TOTAAL)))
    return uit


def main() -> None:
    from playwright.sync_api import sync_playwright
    doel = Path(sys.argv[1] if len(sys.argv) > 1 else "promo")
    doel.mkdir(parents=True, exist_ok=True)
    d = json.loads((SITE / "data" / "dashboard.json").read_text(encoding="utf-8"))
    pngs = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        scherm = doel / "_scherm.png"
        # een kaart van de site, ingezoomd: bbp per inwoner, België en de buren (via een lokale webserver, want de grafieken laden JSON)
        import functools, http.server, threading
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE)))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        site = b.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=2)
        site.goto(f"http://127.0.0.1:{srv.server_address[1]}/thema/economie.html")
        site.add_style_tag(content="#bbp_per_inwoner .uitleg, #bbp_per_inwoner .zinnen, #bbp_per_inwoner .technisch, #bbp_per_inwoner .deel { display: none !important; } #bbp_per_inwoner { align-self: start; }")
        site.locator("#bbp_per_inwoner .tabs button").nth(1).click()
        site.wait_for_timeout(800)
        site.locator("#bbp_per_inwoner").screenshot(path=str(scherm))
        site.close()
        srv.shutdown()
        lijst = dias(d, scherm)
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        assert len(lijst) == TOTAAL
        for nr, (naam, inhoud) in enumerate(lijst, 1):
            naam = f"{nr:02d}-" + naam.split("-", 1)[-1] if naam[:2].isdigit() else f"{nr:02d}-{naam}"
            html = doel / f"{naam}.html"
            html.write_text(inhoud, encoding="utf-8")
            pg.goto(html.resolve().as_uri())
            pg.wait_for_timeout(200)
            png = doel / f"{naam}.png"
            pg.screenshot(path=str(png))
            pngs.append(png)
            html.unlink()
        b.close()
    scherm.unlink()
    # carrousel als PDF (LinkedIn "document"), één dia per pagina
    from PIL import Image
    beelden = [Image.open(x).convert("RGB") for x in pngs]
    beelden[0].save(doel / "carrousel-state-of-the-union.pdf", save_all=True, append_images=beelden[1:], resolution=144)
    print(f"{len(pngs)} dia's en een PDF in {doel}")


if __name__ == "__main__":
    main()
