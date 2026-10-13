// België in cijfers — tekent de grafieken. De cijfers zelf staan al in de HTML.
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const css = (naam) => getComputedStyle(document.documentElement).getPropertyValue(naam).trim();

  function maak(tag, attrs, ouder) {
    const el = document.createElementNS(NS, tag);
    for (const k in attrs) el.setAttribute(k, attrs[k]);
    if (ouder) ouder.appendChild(el);
    return el;
  }

  function formatteer(x, ind) {
    const s = new Intl.NumberFormat("nl-BE", { minimumFractionDigits: ind.decimalen, maximumFractionDigits: ind.decimalen }).format(x);
    const e = ind.eenheid.trim();
    if (e === "€") return "€ " + s;
    if (e === "mln €") return "€ " + s + " mln";
    return s + ind.eenheid;
  }

  function mooieTicks(min, max, n) {
    const bereik = max - min || Math.abs(max) || 1;
    const ruw = bereik / n;
    const macht = Math.pow(10, Math.floor(Math.log10(ruw)));
    const stap = [1, 2, 2.5, 5, 10].map((f) => f * macht).find((s) => bereik / s <= n) || 10 * macht;
    const start = Math.floor(min / stap) * stap, einde = Math.ceil(max / stap) * stap;
    const uit = [];
    for (let v = start; v <= einde + stap / 2; v += stap) uit.push(+v.toFixed(10));
    return uit;
  }

  function teken(doos, ind, data) {
    doos.textContent = "";
    const B = doos.clientWidth;
    if (!B) return;
    const H = 170, ml = 44, mr = 8, mt = 8, mb = 20;
    const namen = data.landnamen;
    const volgorde = ["BE", "EU27_2020", "NL", "DE", "FR", "LU"].filter((g) => ind.reeksen[g] && ind.reeksen[g].length);
    if (!volgorde.length) return;
    const stijl = {
      BE: { kleur: css("--accent"), dikte: 2.5 },
      EU27_2020: { kleur: css("--vergelijk"), dikte: 1.5, streep: "5 4" },
    };
    const anders = { kleur: css("--overig"), dikte: 1.2 };

    const alle = volgorde.flatMap((g) => ind.reeksen[g]);
    const jaren = alle.map((r) => r[0]);
    const waarden = alle.map((r) => r[1]);
    if (ind.norm) waarden.push(ind.norm.waarde);
    const j0 = Math.min(...jaren), j1 = Math.max(...jaren);
    const ticks = mooieTicks(Math.min(...waarden), Math.max(...waarden), 4);
    const y0 = ticks[0], y1 = ticks[ticks.length - 1];
    const x = (j) => ml + ((j - j0) / Math.max(1, j1 - j0)) * (B - ml - mr);
    const y = (v) => mt + (1 - (v - y0) / (y1 - y0 || 1)) * (H - mt - mb);

    const svg = maak("svg", { viewBox: `0 0 ${B} ${H}`, width: "100%" }, doos);
    const kort = (v) => new Intl.NumberFormat("nl-BE", { notation: Math.abs(v) >= 10000 ? "compact" : "standard", maximumFractionDigits: 1 }).format(v);
    ticks.forEach((t) => {
      maak("line", { x1: ml, x2: B - mr, y1: y(t), y2: y(t), stroke: css(t === 0 ? "--vergelijk" : "--raster") }, svg);
      const tx = maak("text", { x: ml - 6, y: y(t), "text-anchor": "end", "dominant-baseline": "middle" }, svg);
      tx.textContent = kort(t);
    });
    const stap = j1 - j0 > 12 ? 5 : j1 - j0 > 6 ? 3 : 1;
    for (let j = j0; j <= j1; j++) {
      if ((j - j0) % stap && j !== j1) continue;
      if (j !== j1 && j1 - j < stap / 2 + 1 && j !== j0) continue;
      const tx = maak("text", { x: x(j), y: H - 4, "text-anchor": j === j1 ? "end" : j === j0 ? "start" : "middle" }, svg);
      tx.textContent = j;
    }
    if (ind.norm) {
      maak("line", { x1: ml, x2: B - mr, y1: y(ind.norm.waarde), y2: y(ind.norm.waarde), stroke: css("--waarschuwing"), "stroke-dasharray": "2 3" }, svg);
    }
    [...volgorde].reverse().forEach((g) => {
      const s = stijl[g] || anders;
      const d = ind.reeksen[g].map((r, i) => (i ? "L" : "M") + x(r[0]).toFixed(1) + "," + y(r[1]).toFixed(1)).join("");
      maak("path", { d, fill: "none", stroke: s.kleur, "stroke-width": s.dikte, "stroke-linejoin": "round", "stroke-linecap": "round", "stroke-dasharray": s.streep || "" }, svg);
    });

    // legende
    const leg = document.createElement("div");
    leg.className = "legende";
    volgorde.forEach((g) => {
      const s = stijl[g] || anders;
      const sp = document.createElement("span");
      if (s.streep) sp.className = "stip";
      sp.style.setProperty("--kleur", s.kleur);
      sp.textContent = (namen[g] && namen[g].nl) || g;
      leg.appendChild(sp);
    });
    if (ind.norm) {
      const sp = document.createElement("span");
      sp.className = "stip";
      sp.style.setProperty("--kleur", css("--waarschuwing"));
      sp.textContent = ind.norm.label.nl;
      leg.appendChild(sp);
    }
    doos.appendChild(leg);

    // tooltip
    const tip = document.createElement("div");
    tip.className = "tip";
    doos.appendChild(tip);
    const regel = maak("line", { y1: mt, y2: H - mb, stroke: css("--vergelijk"), opacity: 0 }, svg);
    const vang = maak("rect", { x: ml, y: 0, width: Math.max(0, B - ml - mr), height: H - mb, fill: "transparent" }, svg);
    vang.addEventListener("pointermove", (ev) => {
      const r = svg.getBoundingClientRect();
      const px = (ev.clientX - r.left) * (B / r.width);
      const j = Math.round(j0 + ((px - ml) / (B - ml - mr)) * (j1 - j0));
      const rijen = volgorde.map((g) => [g, ind.reeksen[g].find((w) => w[0] === j)]).filter((p) => p[1]);
      if (!rijen.length) return;
      regel.setAttribute("x1", x(j)); regel.setAttribute("x2", x(j)); regel.setAttribute("opacity", 1);
      tip.textContent = "";
      const t = document.createElement("div"); t.className = "t"; t.textContent = j; tip.appendChild(t);
      rijen.forEach(([g, w]) => {
        const rij = document.createElement("div");
        const sw = document.createElement("span"); sw.className = "sw"; sw.style.background = (stijl[g] || anders).kleur;
        rij.appendChild(sw);
        rij.appendChild(document.createTextNode(((namen[g] && namen[g].nl) || g) + ": " + formatteer(w[1], ind) + (w[2].includes("p") ? " (voorlopig)" : "")));
        tip.appendChild(rij);
      });
      tip.style.opacity = 1;
      const schaal = r.width / B;
      let links = x(j) * schaal + 12;
      if (links + tip.offsetWidth > doos.clientWidth) links = x(j) * schaal - tip.offsetWidth - 12;
      tip.style.left = Math.max(0, links) + "px";
      tip.style.top = "0px";
    });
    vang.addEventListener("pointerleave", () => { tip.style.opacity = 0; regel.setAttribute("opacity", 0); });
  }

  fetch("data/dashboard.json")
    .then((r) => r.json())
    .then((data) => {
      const per = Object.fromEntries(data.indicatoren.map((i) => [i.id, i]));
      const dozen = [...document.querySelectorAll("[data-grafiek]")];
      const alles = () => dozen.forEach((d) => per[d.dataset.grafiek] && teken(d, per[d.dataset.grafiek], data));
      alles();
      let wacht;
      window.addEventListener("resize", () => { clearTimeout(wacht); wacht = setTimeout(alles, 150); });
      matchMedia("(prefers-color-scheme: dark)").addEventListener("change", alles);
    })
    .catch(() => {});
})();
