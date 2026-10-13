"""Maakt de preview-afbeeldingen (1200×630) die LinkedIn, X en andere sites tonen bij een gedeelde link.

Draait na de pipeline, in GitHub Actions. Elke afbeelding toont actuele cijfers uit
site/data/dashboard.json, met de bron erbij.

Gebruik: python -m pipeline.og   (vereist: pip install playwright && playwright install chromium)
"""
from __future__ import annotations

import json
from html import escape

from .build_site import MERK, ONDERTITEL, SITE, SITE_URL, THEMA_KLEUR, GEWESTEN, datum, kort_met_eenheid, laatste, maand_tekst, waarde_in

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
    sub = f"België {jaar}" + (f" · EU {kort_met_eenheid(eu, ind)}" if eu is not None else "")
    if "j" in status and ind["bron"].get("laatste_periode"):
        sub += f" · t.e.m. {maand_tekst(ind['bron']['laatste_periode'])}"
    return blok(ind["titel"]["nl"], kort_met_eenheid(w, ind), sub, THEMA_KLEUR.get(ind["thema"], "#888"))


def html(titel: str, blokken: list[str], bronnen: set[str], bijgewerkt: str, accent: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Plex; src: url("{FONTS}/plex-sans.woff2"); font-weight: 100 700; }}
@font-face {{ font-family: PlexMono; src: url("{FONTS}/plex-mono.woff2"); font-weight: 500; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 1200px; height: 630px; overflow: hidden; background: #0f1317; color: #eef0f2; font-family: Plex, sans-serif; position: relative; }}
.raster {{ position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.04) 1px, transparent 1px); background-size: 48px 48px; }}
.gloed {{ position: absolute; width: 620px; height: 620px; border-radius: 50%; filter: blur(90px); opacity: .28; background: {accent}; right: -160px; top: -260px; }}
.gloed2 {{ position: absolute; width: 520px; height: 520px; border-radius: 50%; filter: blur(90px); opacity: .18; background: #f5c518; left: -200px; bottom: -320px; }}
.binnen {{ position: absolute; inset: 0; padding: 56px 64px; display: flex; flex-direction: column; }}
.merk {{ display: flex; align-items: center; gap: 16px; }}
.vlag {{ display: flex; gap: 3px; height: 40px; }} .vlag i {{ width: 8px; }}
.vlag i:nth-child(1) {{ background: #1d1d1b; box-shadow: inset 0 0 0 1px rgba(255,255,255,.3); }} .vlag i:nth-child(2) {{ background: #f5c518; }} .vlag i:nth-child(3) {{ background: #e03a3e; }}
.merk b {{ display: block; font: 500 17px PlexMono; letter-spacing: .16em; text-transform: uppercase; color: #f5c518; }}
.merk span {{ font-size: 24px; font-weight: 600; }}
h1 {{ font-size: 64px; line-height: 1.02; font-weight: 650; letter-spacing: -.035em; margin-top: 44px; max-width: 1000px; }}
.cijfers {{ display: flex; margin-top: auto; border-top: 1px solid rgba(255,255,255,.16); }}
.cijfer {{ flex: 1; padding: 22px 24px 0 0; border-right: 1px solid rgba(255,255,255,.16); margin-right: 24px; }}
.cijfer:last-child {{ border-right: 0; margin-right: 0; }}
.l {{ font: 500 15px PlexMono; letter-spacing: .1em; text-transform: uppercase; color: rgba(238,240,242,.6); }}
.w {{ font-size: 52px; font-weight: 650; letter-spacing: -.03em; margin-top: 6px; color: #fff; }}
.s {{ font-size: 18px; color: rgba(238,240,242,.6); margin-top: 2px; }}
.cijfer {{ border-top: 4px solid color-mix(in srgb, var(--t) 60%, white); margin-top: -1px; }}
.voet {{ margin-top: 26px; font-size: 17px; color: rgba(238,240,242,.55); display: flex; justify-content: space-between; }}
</style></head><body><div class="raster"></div><div class="gloed"></div><div class="gloed2"></div>
<div class="binnen">
  <div class="merk"><div class="vlag"><i></i><i></i><i></i></div><div><b>{MERK}</b><span>{ONDERTITEL}</span></div></div>
  <h1>{escape(titel)}</h1>
  <div class="cijfers">{"".join(blokken)}</div>
  <div class="voet"><span>Bron: {escape(", ".join(sorted(bronnen)))} · bijgewerkt {bijgewerkt}</span><span>{SITE_URL.replace("https://", "").rstrip("/")}</span></div>
</div></body></html>"""


def main() -> None:
    from playwright.sync_api import sync_playwright

    data = json.loads((SITE / "data" / "dashboard.json").read_text(encoding="utf-8"))
    per_id = {i["id"]: i for i in data["indicatoren"]}
    bij = datum(data["gegenereerd"])
    bron = lambda inds: {("Eurostat" if i["bron"]["instelling"] == "Berekend" else i["bron"]["instelling"]) for i in inds}

    paginas: dict[str, str] = {}
    kern = [per_id[i] for i in ("schuld_per_inwoner", "werkzaamheidsgraad", "treinstiptheid") if i in per_id and laatste(per_id[i], "BE")]
    paginas["index"] = html("Hoe gaat het met België?", [cijferblok(i) for i in kern], bron(kern), bij, "#2357a6")
    for t in data["themas"]:
        inds = [i for i in data["indicatoren"] if i["thema"] == t["id"] and not i["verborgen"] and laatste(i, "BE")][:3]
        paginas[f'thema-{t["id"]}'] = html(t["vraag"], [cijferblok(i) for i in inds], bron(inds), bij, THEMA_KLEUR.get(t["id"], "#2357a6"))
    w = per_id.get("werkzaamheidsgraad")
    if w:
        blokken = []
        for g, naam in GEWESTEN:
            r = laatste(w, g)
            if r:
                blokken.append(blok(naam, kort_met_eenheid(r[1], w), f"werkzaamheidsgraad {r[0]}", THEMA_KLEUR["werk"]))
        paginas["gewesten"] = html("Hoe verschillen Vlaanderen, Wallonië en Brussel?", blokken, {"Eurostat"}, bij, "#e03a3e")

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
