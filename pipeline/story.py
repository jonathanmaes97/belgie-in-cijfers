"""Instagram-story (1080×1920): een statisch beeld en een korte animatie (MP4).

Alle getallen komen uit site/data/dashboard.json, opgemaakt met dezelfde functies als de site.
De animatie wordt beeld per beeld gerenderd (Playwright) en met ffmpeg tot een MP4 samengevoegd.
Gebruik: python -m pipeline.story [map]
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

from . import build_site as bs
from .build_site import SITE, THEMA_KLEUR, getal, laatste, pct
from .promo import DOMEIN, FONTS

FPS = 30
DUUR = 16.0  # seconden


def cijfers(d: dict) -> list[dict]:
    bs.zet_taal("nl")
    p = {i["id"]: i for i in d["indicatoren"]}
    gev = p["gevangenis_bezetting"]["reeksen"]["BE"][-1]
    inv = p["invaliditeit"]["reeksen"]["BE"][-1]
    ink = d["inkomsten"]
    arbeid = ink["aandelen"]["LAB"]["BE"][str(ink["jaar"])]
    return [
        {"waarde": pct(gev[1], 0), "num": gev[1], "dec": 0, "suf": "%",
         "tekst": f"zo vol zitten de Belgische gevangenissen ({gev[0]})", "bron": "Eurostat", "kleur": THEMA_KLEUR["veiligheid_justitie"]},
        {"waarde": getal(inv[1], 0), "num": inv[1], "dec": 0, "suf": "",
         "tekst": f"werknemers en werklozen zijn langdurig ziek (invaliditeit, {inv[0]})", "bron": "RIZIV", "kleur": THEMA_KLEUR["werk"]},
        {"waarde": "€ " + getal(arbeid, 1), "num": arbeid, "dec": 1, "pre": "€ ", "suf": "",
         "tekst": f"van elke 100 euro belastingen komt uit arbeid ({ink['jaar']})", "bron": "Europese Commissie", "kleur": THEMA_KLEUR["overheidsfinancien"]},
    ]


def pagina(c: list[dict], statisch: bool) -> str:
    kaarten = "".join(
        f'<div class="kaart" id="k{i}" style="--k:{x["kleur"]}"><b data-eind="{escape(x["waarde"])}">{escape(x["waarde"])}</b>'
        f'<span>{escape(x["tekst"])}</span><small>Bron: {escape(x["bron"])}</small></div>' for i, x in enumerate(c))
    return f"""<!doctype html><html lang="nl"><head><meta charset="utf-8"><style>
@font-face {{ font-family: Plex; src: url("{FONTS}/plex-sans.woff2"); font-weight: 100 700; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 1080px; height: 1920px; overflow: hidden; background: #f6f7f9; color: #1a1f24; font-family: Plex, sans-serif; position: relative; }}
.raster {{ position: absolute; inset: 0; background-image: linear-gradient(rgba(20,30,45,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(20,30,45,.05) 1px, transparent 1px); background-size: 54px 54px; }}
.gloed {{ position: absolute; width: 900px; height: 900px; border-radius: 50%; filter: blur(120px); opacity: .32; background: #fdda24; right: -320px; top: -300px; }}
.gloed2 {{ position: absolute; width: 760px; height: 760px; border-radius: 50%; filter: blur(130px); opacity: .14; background: #ef3340; left: -360px; bottom: 120px; }}
.laag {{ position: absolute; inset: 0; padding: 260px 90px 360px; display: flex; flex-direction: column; }}
.merk {{ display: flex; align-items: center; gap: 20px; }}
.vlag {{ display: flex; gap: 5px; height: 58px; }} .vlag i {{ width: 12px; border-radius: 3px; }}
.vlag i:nth-child(1) {{ background: #1f1f1f; }} .vlag i:nth-child(2) {{ background: #fdda24; }} .vlag i:nth-child(3) {{ background: #ef3340; }}
.merk b {{ display: block; font-size: 28px; font-weight: 500; color: #5b636b; }} .merk span {{ font-size: 36px; font-weight: 600; }}
h1 {{ font-size: 96px; line-height: 1.03; letter-spacing: -.035em; font-weight: 650; }}
.sub {{ font-size: 44px; line-height: 1.35; color: #4a525a; }}
.stempel {{ display: inline-block; margin-top: 40px; padding: 14px 30px; border: 6px solid #ef3340; color: #ef3340; border-radius: 14px; font-size: 64px; font-weight: 700; letter-spacing: .08em; transform: rotate(-6deg); }}
.kaart {{ background: rgba(255,255,255,.82); border: 2px solid #e1e4e8; border-left: 14px solid var(--k); border-radius: 26px; padding: 40px 44px; display: flex; flex-direction: column; gap: 10px; }}
.kaart b {{ font-size: 120px; letter-spacing: -.045em; line-height: 1; font-weight: 650; color: var(--k); font-variant-numeric: tabular-nums; }}
.kaart span {{ font-size: 40px; line-height: 1.25; }}
.kaart small {{ font-size: 26px; color: #6b737b; }}
.url {{ display: inline-block; padding: 30px 46px; border-radius: 20px; background: #1a1f24; color: #fff; font-size: 54px; font-weight: 600; }}
.klein {{ font-size: 34px; color: #5b636b; line-height: 1.4; }}
/* statische versie */
.statisch .laag {{ padding-top: 220px; }}
.statisch .kaarten {{ display: flex; flex-direction: column; gap: 22px; margin-top: 50px; margin-bottom: 50px; }}
.statisch .kaart {{ padding: 26px 38px; gap: 6px; }} .statisch .kaart b {{ font-size: 84px; }} .statisch .kaart span {{ font-size: 33px; }} .statisch .kaart small {{ font-size: 24px; }}
/* animatie: elke scène is een laag */
.anim .laag {{ opacity: 0; }}
.anim .kaart {{ margin-top: 70px; }}
</style></head><body class="{"statisch" if statisch else "anim"}"><div class="raster"></div><div class="gloed"></div><div class="gloed2"></div>
{statische_inhoud(kaarten) if statisch else animatie_inhoud(c)}
</body></html>"""


MERK = '<div class="merk"><div class="vlag"><i></i><i></i><i></i></div><div><b>State of the Union</b><span>België in cijfers</span></div></div>'


def statische_inhoud(kaarten: str) -> str:
    return f"""<div class="laag">{MERK}
<h1 style="font-size:78px;margin-top:60px">De State of the Union in de Kamer? Uitgesteld.</h1>
<p class="sub" style="margin-top:24px">Hier is er alvast eentje, met officiële cijfers.</p>
<div class="kaarten">{kaarten}</div>
<div style="margin-top:auto"><span class="url">{DOMEIN}</span></div></div>"""


def animatie_inhoud(c: list[dict]) -> str:
    scenes = [f"""<div class="laag" id="s0" style="justify-content:center">{MERK}
<h1 style="margin-top:80px">De State of the Union in de Kamer?</h1><div><span class="stempel" id="stempel">UITGESTELD</span></div></div>""",
              f"""<div class="laag" id="s1" style="justify-content:center">{MERK}
<h1 style="margin-top:80px">Hier is er alvast eentje.</h1><p class="sub" style="margin-top:30px">Met officiële cijfers. Elk met een link naar de bron.</p></div>"""]
    for i, x in enumerate(c):
        scenes.append(f"""<div class="laag" id="s{i + 2}" style="justify-content:center">{MERK}
<div class="kaart" style="--k:{x["kleur"]}"><b id="n{i}">{escape(x["waarde"])}</b><span>{escape(x["tekst"])}</span><small>Bron: {escape(x["bron"])}</small></div></div>""")
    scenes.append(f"""<div class="laag" id="s{len(c) + 2}" style="justify-content:center">{MERK}
<h1 style="margin-top:80px;font-size:88px">Zoek het zelf op.</h1>
<p class="sub" style="margin-top:30px">Werk, gezondheid, onderwijs, klimaat, veiligheid en de gewesten naast elkaar. Elke dag bijgewerkt, in vier talen.</p>
<div style="margin-top:60px"><span class="url">{DOMEIN}</span></div></div>""")
    data = json.dumps([{k: x.get(k, "") for k in ("num", "dec", "pre", "suf", "waarde")} for x in c])
    return "".join(scenes) + f"""<script>
const C = {data}, N = {len(c) + 3};
// begin en einde (s) van elke scène
const T = [[0, 3], [3, 5.4], [5.4, 7.9], [7.9, 10.4], [10.4, 12.9], [12.9, {DUUR}]];
const fmt = (v, x) => (x.pre || "") + v.toLocaleString("nl-BE", {{minimumFractionDigits: x.dec, maximumFractionDigits: x.dec}}) + (x.suf || "");
const ease = (u) => 1 - Math.pow(1 - Math.min(Math.max(u, 0), 1), 3);
window.render = (t) => {{
  for (let i = 0; i < N; i++) {{
    const [a, b] = T[i], el = document.getElementById("s" + i), laatste = i === N - 1;
    const inn = ease((t - a) / .45), uit = laatste ? 0 : ease((t - (b - .35)) / .35);
    el.style.opacity = Math.min(inn, 1 - uit);
    el.style.transform = `translateY(${{(1 - inn) * 40 - uit * 40}}px)`;
  }}
  const s = document.getElementById("stempel"), u = ease((t - 1.1) / .25);
  s.style.opacity = u; s.style.transform = `rotate(-6deg) scale(${{1.8 - .8 * u}})`;
  C.forEach((x, i) => {{
    const a = T[i + 2][0] + .25, u = ease((t - a) / 1.3);
    document.getElementById("n" + i).textContent = u >= 1 ? x.waarde : fmt(x.num * u, x);
  }});
}};
</script>"""


def main() -> None:
    from playwright.sync_api import sync_playwright
    doel = Path(sys.argv[1] if len(sys.argv) > 1 else "promo")
    doel.mkdir(parents=True, exist_ok=True)
    d = json.loads((SITE / "data" / "dashboard.json").read_text(encoding="utf-8"))
    c = cijfers(d)
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for statisch, naam in ((True, "story-statisch"), (False, "story-animatie")):
            html = Path(tmp) / f"{naam}.html"
            html.write_text(pagina(c, statisch), encoding="utf-8")
            pg.goto(html.resolve().as_uri())
            pg.wait_for_timeout(300)
            if statisch:
                pg.screenshot(path=str(doel / "story-statisch.png"))
                continue
            beelden = Path(tmp) / "beelden"
            beelden.mkdir()
            for f in range(int(DUUR * FPS)):
                pg.evaluate(f"render({f / FPS})")
                pg.screenshot(path=str(beelden / f"{f:04d}.png"))
            pg.evaluate("render(14.5)")
            pg.screenshot(path=str(doel / "story-einde.png"))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(beelden / "%04d.png"),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart",
                            str(doel / "story-animatie.mp4")], check=True)
        b.close()
    print(f"Story (statisch + animatie) in {doel}")


if __name__ == "__main__":
    main()
