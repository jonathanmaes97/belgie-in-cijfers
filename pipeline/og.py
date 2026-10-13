"""Maakt de preview-afbeeldingen (1200×630) die LinkedIn, X en andere sites tonen bij een gedeelde link.

Draait na de pipeline, in GitHub Actions. Elke afbeelding toont actuele cijfers uit
site/data/dashboard.json, met de bron erbij.

Er komt een set per taal: index.png (Nederlands), index-fr.png, index-de.png, index-en.png, enzovoort.

Gebruik: python -m pipeline.og   (vereist: pip install playwright && playwright install chromium)
"""
from __future__ import annotations

import json
from html import escape

from . import build_site as bs
from .build_site import MERK, SITE, SITE_URL, THEMA_KLEUR, GEWEST_CODES, T, TALEN, datum, kort_met_eenheid, laatste, landnaam, maand_tekst, tx, vertaal, waarde_in, zet_taal

TOT_EN_MET = {"nl": "t.e.m.", "fr": "jusqu'à", "de": "bis", "en": "to"}

FONTS = (SITE / "fonts").resolve().as_uri()


def blok(label: str, waarde: str, sub: str, kleur: str) -> str:
    return (f'<div class="cijfer" style="--t:{kleur}"><div class="l">{escape(label)}</div>'
            f'<div class="w">{escape(waarde)}</div><div class="s">{escape(sub)}</div></div>')


def cijferblok(ind: dict) -> str:
    be = laatste(ind, "BE")
    if not be:
        return ""
    jaar, w, status = be
    eu = waarde_in(ind, "EU27_2020", jaar)
    sub = f'{T("land")} {jaar}' + (f' · {T("eu_kort")} {kort_met_eenheid(eu, ind)}' if eu is not None else "")
    if "j" in status and ind["bron"].get("laatste_periode"):
        sub += f" · {TOT_EN_MET[bs.TAAL]} {maand_tekst(ind['bron']['laatste_periode'])}"
    return blok(tx(ind["titel"]), kort_met_eenheid(w, ind), sub, THEMA_KLEUR.get(ind["thema"], "#888"))


def html(titel: str, blokken: list[str], bronnen: set[str], bijgewerkt: str, accent: str) -> str:
    return f"""<!doctype html><html lang="{bs.TAAL}"><head><meta charset="utf-8"><style>
@font-face {{ font-family: Plex; src: url("{FONTS}/plex-sans.woff2"); font-weight: 100 700; }}
@font-face {{ font-family: PlexMono; src: url("{FONTS}/plex-mono.woff2"); font-weight: 500; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 1200px; height: 630px; overflow: hidden; background: #f6f7f9; color: #1a1f24; font-family: Plex, sans-serif; position: relative; }}
.raster {{ position: absolute; inset: 0; background-image: linear-gradient(rgba(20,30,45,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(20,30,45,.05) 1px, transparent 1px); background-size: 48px 48px; }}
.gloed {{ position: absolute; width: 620px; height: 620px; border-radius: 50%; filter: blur(90px); opacity: .35; background: #fdda24; right: -120px; top: -300px; }}

.gloed2 {{ position: absolute; width: 520px; height: 520px; border-radius: 50%; filter: blur(100px); opacity: .16; background: #ef3340; right: -260px; top: 80px; }}
.binnen {{ position: absolute; inset: 0; padding: 58px 64px 40px; display: flex; flex-direction: column; }}
.merk {{ display: flex; align-items: center; gap: 16px; }}
.vlag {{ display: flex; gap: 3px; height: 40px; }} .vlag i {{ width: 8px; }}
.vlag i {{ border-radius: 3px; }} .vlag i:nth-child(1) {{ background: #1f1f1f; }} .vlag i:nth-child(2) {{ background: #fdda24; }} .vlag i:nth-child(3) {{ background: #ef3340; }}
.merk b {{ display: block; font-size: 19px; font-weight: 500; color: #5b636b; }}
.merk span {{ font-size: 24px; font-weight: 600; }}
h1 {{ font-size: 62px; line-height: 1.02; font-weight: 650; letter-spacing: -.035em; margin-top: 36px; max-width: 1000px; }}
.cijfers {{ display: flex; margin-top: auto; background: rgba(255,255,255,.8); border: 1px solid #e1e4e8; border-radius: 18px; overflow: hidden; }}
.cijfer {{ flex: 1; padding: 22px 26px 22px; border-right: 1px solid #e1e4e8; }}
.cijfer:last-child {{ border-right: 0; }}
.l {{ font-size: 19px; font-weight: 500; color: #5b636b; }}
.w {{ font-size: 52px; font-weight: 650; letter-spacing: -.03em; margin-top: 6px; color: #1a1f24; }}
.s {{ font-size: 18px; color: #80888f; margin-top: 2px; }}
.cijfer {{ box-shadow: inset 0 4px 0 var(--t); }}
.voet {{ margin-top: 22px; font-size: 17px; color: #5b636b; display: flex; justify-content: space-between; }}
</style></head><body><div class="raster"></div><div class="gloed"></div><div class="gloed2"></div>
<div class="binnen">
  <div class="merk"><div class="vlag"><i></i><i></i><i></i></div><div><b>{MERK}</b><span>{T("ondertitel")}</span></div></div>
  <h1>{escape(titel)}</h1>
  <div class="cijfers">{"".join(blokken)}</div>
  <div class="voet"><span>{T("bron")}: {escape(", ".join(sorted(bronnen)))} · {T("vz_bijgewerkt").lower()} {bijgewerkt}</span><span>{SITE_URL.replace("https://", "").rstrip("/")}</span></div>
</div></body></html>"""


def main() -> None:
    from playwright.sync_api import sync_playwright

    basis = json.loads((SITE / "data" / "dashboard.json").read_text(encoding="utf-8"))
    bron = lambda inds: {("Eurostat" if i["bron"]["instelling"] == "Berekend" else i["bron"]["instelling"]) for i in inds}

    paginas: dict[str, str] = {}
    for taal in TALEN:
        zet_taal(taal)
        data = vertaal(basis, taal)
        per_id = {i["id"]: i for i in data["indicatoren"]}
        bij = datum(data["gegenereerd"])
        achter = "" if taal == "nl" else f"-{taal}"
        kern = [per_id[i] for i in ("schuld_per_inwoner", "werkzaamheidsgraad", "treinstiptheid") if i in per_id and laatste(per_id[i], "BE")]
        paginas[f"index{achter}"] = html(T("held_titel").replace("<br>", " "), [cijferblok(i) for i in kern], bron(kern), bij, "#2357a6")
        for t in data["themas"]:
            inds = [i for i in data["indicatoren"] if i["thema"] == t["id"] and not i["verborgen"] and laatste(i, "BE")][:3]
            paginas[f'thema-{t["id"]}{achter}'] = html(t["vraag"], [cijferblok(i) for i in inds], bron(inds), bij, THEMA_KLEUR.get(t["id"], "#2357a6"))
        w = per_id.get("werkzaamheidsgraad")
        if w:
            blokken = []
            for g in GEWEST_CODES:
                r = laatste(w, g)
                if r:
                    blokken.append(blok(landnaam(data, g), kort_met_eenheid(r[1], w), f'{tx(w["titel"])} {r[0]}', THEMA_KLEUR["werk"]))
            paginas[f"gewesten{achter}"] = html(T("gw_titel"), blokken, {"Eurostat"}, bij, "#e03a3e")
    zet_taal("nl")

    uit = SITE / "og"
    uit.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        for naam, inhoud in paginas.items():
            pad = uit / f"{naam}.html"
            pad.write_text(inhoud, encoding="utf-8")
            pg.goto(pad.resolve().as_uri())
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(uit / f"{naam}.png"))
            pad.unlink()
        b.close()
    print(f"{len(paginas)} preview-afbeeldingen gemaakt in {uit}")


if __name__ == "__main__":
    main()
