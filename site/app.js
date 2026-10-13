// België in cijfers — grafieken, tabbladen, zoeken en delen.
// De cijfers zelf staan al in de HTML; dit script maakt de pagina interactief.
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const BASIS = (document.currentScript && document.currentScript.src.replace(/app\.js.*$/, "")) || "./";
  const css = (el, naam) => getComputedStyle(el).getPropertyValue(naam).trim();

  function maak(tag, attrs, ouder, tekst) {
    const el = document.createElementNS(NS, tag);
    for (const k in attrs) el.setAttribute(k, attrs[k]);
    if (tekst !== undefined) el.textContent = tekst;
    if (ouder) ouder.appendChild(el);
    return el;
  }

  const nf = (d) => new Intl.NumberFormat("nl-BE", { minimumFractionDigits: d, maximumFractionDigits: d });
  function fmt(x, ind) {
    const s = nf(ind.decimalen).format(x).replace(/^-/, "−");
    const e = ind.eenheid.trim();
    if (e === "€") return "€ " + s;
    if (e === "mln €") return "€ " + s + " mln";
    if (e === "% bbp") return s + "%";
    return s + ind.eenheid;
  }
  function kort(x) {
    const abs = Math.abs(x);
    const o = abs >= 1e6 ? { notation: "compact", maximumFractionDigits: 1 } : abs >= 10000 ? { notation: "compact", maximumFractionDigits: 0 } : { maximumFractionDigits: 1 };
    return new Intl.NumberFormat("nl-BE", o).format(x).replace(/^-/, "−");
  }
  function ticks(min, max, n) {
    if (min === max) { min -= 1; max += 1; }
    const ruw = (max - min) / n, macht = Math.pow(10, Math.floor(Math.log10(ruw)));
    const stap = [1, 2, 2.5, 5, 10].map((f) => f * macht).find((s) => (max - min) / s <= n) || 10 * macht;
    const uit = [];
    for (let v = Math.floor(min / stap) * stap; v <= Math.ceil(max / stap) * stap + stap / 2; v += stap) uit.push(+v.toFixed(10));
    return uit;
  }
  function meetTekst(svg, teksten, klasse) {
    const g = maak("g", {}, svg);
    let m = 0;
    teksten.forEach((t) => { const n = maak("text", klasse ? { class: klasse } : {}, g, t); m = Math.max(m, n.getComputedTextLength()); });
    g.remove();
    return m;
  }

  // ---------- tooltip ----------
  function maakTip(doos) {
    const tip = document.createElement("div");
    tip.className = "tip";
    doos.appendChild(tip);
    return {
      toon(x, y, titel, regels) {
        tip.textContent = "";
        const t = document.createElement("div"); t.className = "t"; t.textContent = titel; tip.appendChild(t);
        regels.forEach((r) => {
          const d = document.createElement("div"); d.className = "r";
          if (r.kleur) { const s = document.createElement("span"); s.className = "sw"; s.style.background = r.kleur; d.appendChild(s); }
          d.appendChild(document.createTextNode(r.tekst));
          tip.appendChild(d);
        });
        tip.style.opacity = 1;
        const bw = doos.clientWidth;
        let l = x + 14; if (l + tip.offsetWidth > bw) l = x - tip.offsetWidth - 14;
        tip.style.left = Math.max(0, l) + "px";
        tip.style.top = Math.max(0, y - tip.offsetHeight - 8) + "px";
      },
      verberg() { tip.style.opacity = 0; },
    };
  }

  function legende(doos, items) {
    const l = document.createElement("div");
    l.className = "legende";
    items.forEach((it) => {
      const s = document.createElement("span");
      const i = document.createElement("i");
      if (it.vorm) i.className = it.vorm;
      i.style.setProperty("--k", it.kleur);
      s.appendChild(i);
      s.appendChild(document.createTextNode(it.naam));
      l.appendChild(s);
    });
    doos.appendChild(l);
  }

  const naam = (data, g) => (data.landnamen[g] && data.landnamen[g].nl) || g;
  const kortNaam = (data, g) => (g === "EU27_2020" ? "EU" : naam(data, g));

  // ---------- lijn: België, EU en buren door de jaren ----------
  function lijn(doos, ind, data, kl) {
    const B = doos.clientWidth, H = 220, mt = 12, mb = 22;
    const geos = ["BE", "EU27_2020", "NL", "DE", "FR", "LU"].filter((g) => ind.reeksen[g] && ind.reeksen[g].length);
    const stijl = { BE: { k: kl.thema, d: 3 }, EU27_2020: { k: kl.eu, d: 2, s: "5 4" } };
    const anders = { k: kl.ander, d: 1.4 };
    const alle = geos.flatMap((g) => ind.reeksen[g]);
    const j0 = Math.min(...alle.map((r) => r[0])), j1 = Math.max(...alle.map((r) => r[0]));
    const vals = alle.map((r) => r[1]).concat(ind.norm ? [ind.norm.waarde] : []);
    const tk = ticks(Math.min(...vals), Math.max(...vals), 4);
    const svg = maak("svg", { viewBox: `0 0 ${B} ${H}` }, doos);
    const ml = meetTekst(svg, tk.map(kort)) + 10;
    const eindLabels = ["BE", "EU27_2020"].filter((g) => ind.reeksen[g]).map((g) => ({ g, r: ind.reeksen[g][ind.reeksen[g].length - 1] }));
    const mr = Math.min(B * 0.32, meetTekst(svg, eindLabels.map((e) => kortNaam(data, e.g) + " " + fmt(e.r[1], ind)), "sterk") + 12);
    const x = (j) => ml + ((j - j0) / Math.max(1, j1 - j0)) * (B - ml - mr);
    const y = (v) => mt + (1 - (v - tk[0]) / (tk[tk.length - 1] - tk[0])) * (H - mt - mb);
    tk.forEach((t) => {
      maak("line", { x1: ml, x2: B - mr, y1: y(t), y2: y(t), stroke: t === 0 ? kl.eu : kl.raster, "stroke-width": t === 0 ? 1 : 1 }, svg);
      maak("text", { x: ml - 8, y: y(t), "text-anchor": "end", "dominant-baseline": "middle" }, svg, kort(t));
    });
    const stap = Math.max(1, Math.ceil((j1 - j0) / Math.max(2, Math.floor((B - ml - mr) / 56))));
    for (let j = j0; j <= j1; j += stap) if (j1 - j >= stap * 0.6 || j === j0) maak("text", { x: x(j), y: H - 4, "text-anchor": j === j0 ? "start" : "middle" }, svg, j);
    maak("text", { x: x(j1), y: H - 4, "text-anchor": "end" }, svg, j1);
    if (ind.norm) {
      maak("line", { x1: ml, x2: B - mr, y1: y(ind.norm.waarde), y2: y(ind.norm.waarde), stroke: kl.norm, "stroke-dasharray": "3 4", "stroke-width": 1.5 }, svg);
    }
    [...geos].reverse().forEach((g) => {
      const s = stijl[g] || anders;
      const d = ind.reeksen[g].map((r, i) => (i ? "L" : "M") + x(r[0]).toFixed(1) + "," + y(r[1]).toFixed(1)).join("");
      maak("path", { d, fill: "none", stroke: s.k, "stroke-width": s.d, "stroke-linejoin": "round", "stroke-linecap": "round", "stroke-dasharray": s.s || "" }, svg);
    });
    // eindlabels uit elkaar houden
    const pos = eindLabels.map((e) => ({ ...e, y: y(e.r[1]) })).sort((a, b) => a.y - b.y);
    if (pos.length === 2 && pos[1].y - pos[0].y < 15) { const m = (pos[0].y + pos[1].y) / 2; pos[0].y = m - 8; pos[1].y = m + 8; }
    pos.forEach((p) => {
      maak("circle", { cx: x(p.r[0]), cy: y(p.r[1]), r: p.g === "BE" ? 4.5 : 3.5, fill: (stijl[p.g] || anders).k }, svg);
      maak("text", { x: x(j1) + 8, y: p.y, "dominant-baseline": "middle", class: p.g === "BE" ? "sterk" : "" }, svg, kortNaam(data, p.g) + " " + fmt(p.r[1], ind));
    });
    const items = geos.map((g) => ({ naam: naam(data, g), kleur: (stijl[g] || anders).k, vorm: g === "EU27_2020" ? "stip" : "" }));
    if (ind.norm) items.push({ naam: ind.norm.label.nl, kleur: kl.norm, vorm: "stip" });
    legende(doos, items);
    // hover
    const tip = maakTip(doos);
    const regel = maak("line", { y1: mt, y2: H - mb, stroke: kl.eu, opacity: 0 }, svg);
    const vang = maak("rect", { x: ml, y: 0, width: Math.max(0, B - ml - mr), height: H - mb, fill: "transparent" }, svg);
    vang.addEventListener("pointermove", (ev) => {
      const rr = svg.getBoundingClientRect(), s = rr.width / B;
      const j = Math.round(j0 + (((ev.clientX - rr.left) / s - ml) / (B - ml - mr)) * (j1 - j0));
      const rijen = geos.map((g) => [g, ind.reeksen[g].find((w) => w[0] === j)]).filter((p) => p[1]);
      if (!rijen.length) return;
      regel.setAttribute("x1", x(j)); regel.setAttribute("x2", x(j)); regel.setAttribute("opacity", .5);
      tip.toon(x(j) * s, 40, String(j), rijen.map(([g, w]) => ({ kleur: (stijl[g] || anders).k, tekst: naam(data, g) + ": " + fmt(w[1], ind) + (/[pj]/.test(w[2]) ? " (voorlopig)" : "") })));
    });
    vang.addEventListener("pointerleave", () => { tip.verberg(); regel.setAttribute("opacity", 0); });
  }

  // ---------- kolommen: België per jaar, met het EU-gemiddelde als streepje ----------
  function kolommen(doos, ind, data, kl) {
    const be = ind.reeksen.BE || [];
    if (!be.length) return;
    const eu = Object.fromEntries((ind.reeksen.EU27_2020 || []).map((r) => [r[0], r[1]]));
    const reeks = be.slice(-16);
    const B = doos.clientWidth, H = 220, mt = 20, mb = 22;
    const vals = reeks.map((r) => r[1]).concat(reeks.map((r) => eu[r[0]]).filter((v) => v !== undefined), [0]).concat(ind.norm ? [ind.norm.waarde] : []);
    const tk = ticks(Math.min(...vals), Math.max(...vals), 4);
    const svg = maak("svg", { viewBox: `0 0 ${B} ${H}` }, doos);
    const ml = meetTekst(svg, tk.map(kort)) + 10, mr = 4;
    const bw = (B - ml - mr) / reeks.length, kolom = Math.min(30, bw * 0.68);
    const y = (v) => mt + (1 - (v - tk[0]) / (tk[tk.length - 1] - tk[0])) * (H - mt - mb);
    tk.forEach((t) => {
      maak("line", { x1: ml, x2: B - mr, y1: y(t), y2: y(t), stroke: t === 0 ? kl.eu : kl.raster }, svg);
      maak("text", { x: ml - 8, y: y(t), "text-anchor": "end", "dominant-baseline": "middle" }, svg, kort(t));
    });
    if (ind.norm) maak("line", { x1: ml, x2: B - mr, y1: y(ind.norm.waarde), y2: y(ind.norm.waarde), stroke: kl.norm, "stroke-dasharray": "3 4", "stroke-width": 1.5 }, svg);
    const elk = Math.max(1, Math.ceil(reeks.length / Math.floor((B - ml) / 44)));
    reeks.forEach((r, i) => {
      const cx = ml + bw * i + bw / 2;
      const top = y(Math.max(0, r[1])), h = Math.max(1.5, Math.abs(y(r[1]) - y(0)));
      const lopend = /[j]/.test(r[2]);
      const kolomEl = maak("rect", { x: cx - kolom / 2, y: top, width: kolom, height: h, rx: Math.min(4, kolom / 2), fill: kl.thema, opacity: lopend ? 0.45 : (r[1] < 0 ? 0.7 : 1) }, svg);
      kolomEl.dataset.i = i;
      if (eu[r[0]] !== undefined) maak("line", { x1: cx - kolom / 2 - 3, x2: cx + kolom / 2 + 3, y1: y(eu[r[0]]), y2: y(eu[r[0]]), stroke: kl.eu, "stroke-width": 2.5, "stroke-linecap": "round" }, svg);
      if ((reeks.length - 1 - i) % elk === 0) maak("text", { x: cx, y: H - 4, "text-anchor": "middle" }, svg, r[0]);
    });
    const l = reeks[reeks.length - 1], lx = ml + bw * (reeks.length - 1) + bw / 2;
    maak("text", { x: Math.min(lx, B - 4), y: l[1] >= 0 ? y(l[1]) - 6 : y(l[1]) + 14, "text-anchor": lx > B - 40 ? "end" : "middle", class: "sterk" }, svg, fmt(l[1], ind));
    const items = [{ naam: "België", kleur: kl.thema, vorm: "blok" }];
    if (Object.keys(eu).length) items.push({ naam: "EU-gemiddelde", kleur: kl.eu });
    if (ind.norm) items.push({ naam: ind.norm.label.nl, kleur: kl.norm, vorm: "stip" });
    if (reeks.some((r) => /j/.test(r[2]))) items.push({ naam: "lopend jaar (nog niet volledig)", kleur: kl.thema, vorm: "blok licht" });
    legende(doos, items);
    const tip = maakTip(doos);
    const vang = maak("rect", { x: ml, y: 0, width: B - ml - mr, height: H - mb, fill: "transparent" }, svg);
    vang.addEventListener("pointermove", (ev) => {
      const rr = svg.getBoundingClientRect(), s = rr.width / B;
      const i = Math.max(0, Math.min(reeks.length - 1, Math.floor(((ev.clientX - rr.left) / s - ml) / bw)));
      const r = reeks[i];
      const regels = [{ kleur: kl.thema, tekst: "België: " + fmt(r[1], ind) + (/[pj]/.test(r[2]) ? " (voorlopig)" : "") }];
      if (eu[r[0]] !== undefined) regels.push({ kleur: kl.eu, tekst: "EU-gemiddelde: " + fmt(eu[r[0]], ind) });
      tip.toon((ml + bw * i + bw / 2) * s, y(Math.max(0, r[1])) * s, String(r[0]), regels);
    });
    vang.addEventListener("pointerleave", () => tip.verberg());
  }

  // ---------- liggende staven: één jaar, meerdere landen of gewesten ----------
  function staven(doos, ind, data, kl, geos, titelJaar) {
    // kies het recentste jaar waarin België en de meeste anderen een cijfer hebben
    const jaren = {};
    geos.forEach((g) => (ind.reeksen[g] || []).forEach((r) => { jaren[r[0]] = (jaren[r[0]] || 0) + 1; }));
    const kandidaten = Object.keys(jaren).map(Number).filter((j) => (ind.reeksen.BE || []).some((r) => r[0] === j) && jaren[j] >= Math.min(3, geos.length)).sort((a, b) => b - a);
    const jaar = kandidaten[0];
    if (!jaar) return;
    const rijen = geos.map((g) => ({ g, w: (ind.reeksen[g] || []).find((r) => r[0] === jaar) })).filter((r) => r.w).sort((a, b) => b.w[1] - a.w[1]);
    const rh = 34, H = rijen.length * rh + 8, B = doos.clientWidth;
    const svg = maak("svg", { viewBox: `0 0 ${B} ${H}` }, doos);
    const ml = meetTekst(svg, rijen.map((r) => naam(data, r.g)), "sterk") + 14;
    const mr = meetTekst(svg, rijen.map((r) => fmt(r.w[1], ind)), "sterk") + 10;
    const vals = rijen.map((r) => r.w[1]).concat([0]).concat(ind.norm ? [ind.norm.waarde] : []);
    const lo = Math.min(...vals), hi = Math.max(...vals);
    const x = (v) => ml + ((v - lo) / (hi - lo || 1)) * (B - ml - mr);
    rijen.forEach((r, i) => {
      const yy = 4 + i * rh, kleur = r.g === "BE" ? kl.thema : r.g === "EU27_2020" ? kl.eu : kl.ander;
      const x0 = x(Math.min(0, r.w[1])), x1 = x(Math.max(0, r.w[1]));
      maak("text", { x: ml - 10, y: yy + rh / 2 - 2, "text-anchor": "end", "dominant-baseline": "middle", class: r.g === "BE" ? "sterk" : "" }, svg, naam(data, r.g));
      maak("rect", { x: x0, y: yy + 5, width: Math.max(2, x1 - x0), height: rh - 16, rx: 4, fill: kleur }, svg);
      maak("text", { x: x1 + 6, y: yy + rh / 2 - 2, "dominant-baseline": "middle", class: r.g === "BE" ? "sterk" : "" }, svg, fmt(r.w[1], ind));
    });
    if (lo < 0) maak("line", { x1: x(0), x2: x(0), y1: 0, y2: H, stroke: kl.eu }, svg);
    if (ind.norm) maak("line", { x1: x(ind.norm.waarde), x2: x(ind.norm.waarde), y1: 0, y2: H, stroke: kl.norm, "stroke-dasharray": "3 4", "stroke-width": 1.5 }, svg);
    const items = [{ naam: titelJaar + " " + jaar, kleur: "transparent" }];
    if (ind.norm) items.push({ naam: ind.norm.label.nl, kleur: kl.norm, vorm: "stip" });
    legende(doos, items);
  }

  // ---------- kaarten tekenen ----------
  // Zet CSS-kleuren (ook color-mix) om naar een gewone rgb-waarde die SVG begrijpt.
  function kleuren(kaart) {
    const proef = document.createElement("span");
    kaart.appendChild(proef);
    const los = (v) => { proef.style.color = v; return getComputedStyle(proef).color; };
    const k = {
      thema: los("var(--t-licht, var(--t))"),
      eu: los("var(--eu)"), ander: los("var(--ander)"), raster: los("var(--raster)"), norm: los("var(--norm)"),
    };
    proef.remove();
    return k;
  }

  function teken(doos, ind, data) {
    doos.textContent = "";
    if (!doos.clientWidth) return;
    const kaart = doos.closest(".kaart");
    const tab = (kaart.querySelector(".tabs [aria-selected=true]") || {}).dataset;
    const kl = kleuren(kaart);
    const keuze = (tab && tab.tab) || "jaren";
    if (keuze === "buren") return staven(doos, ind, data, kl, ["BE", "EU27_2020", "NL", "DE", "FR", "LU"], "België en de buren in");
    if (keuze === "gewesten") return staven(doos, ind, data, kl, ["BE2", "BE3", "BE1", "BE", "EU27_2020"], "Per gewest in");
    if (doos.dataset.weergave === "kolommen") return kolommen(doos, ind, data, kl);
    return lijn(doos, ind, data, kl);
  }

  function grafieken(data) {
    const per = Object.fromEntries(data.indicatoren.map((i) => [i.id, i]));
    const dozen = [...document.querySelectorAll("[data-grafiek]")];
    const alles = () => dozen.forEach((d) => per[d.dataset.grafiek] && teken(d, per[d.dataset.grafiek], data));
    alles();
    document.querySelectorAll(".tabs").forEach((tabs) => {
      tabs.addEventListener("click", (ev) => {
        const knop = ev.target.closest("button"); if (!knop) return;
        tabs.querySelectorAll("button").forEach((b) => b.setAttribute("aria-selected", b === knop ? "true" : "false"));
        const doos = tabs.closest(".kaart").querySelector("[data-grafiek]");
        teken(doos, per[doos.dataset.grafiek], data);
      });
    });
    let wacht, breedte = innerWidth;
    addEventListener("resize", () => { if (innerWidth === breedte) return; breedte = innerWidth; clearTimeout(wacht); wacht = setTimeout(alles, 150); });
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", alles);
  }

  if (document.querySelector("[data-grafiek]")) {
    fetch(BASIS + "data/dashboard.json").then((r) => r.json()).then(grafieken).catch(() => {
      document.querySelectorAll("[data-grafiek]").forEach((d) => { d.textContent = "De grafiek kon niet geladen worden."; d.style.minHeight = "0"; });
    });
  }

  // ---------- zoeken ----------
  const veld = document.getElementById("zoekveld");
  const indexEl = document.getElementById("zoekindex");
  if (veld && indexEl) {
    const index = JSON.parse(indexEl.textContent);
    const lijst = document.getElementById("zoekresultaten");
    const norm = (s) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
    let actief = -1;
    function toon() {
      const q = norm(veld.value.trim());
      lijst.textContent = "";
      actief = -1;
      if (!q) { lijst.hidden = true; return; }
      const woorden = q.split(/\s+/);
      const hits = index.map((it) => {
        const hooi = norm(`${it.v} ${it.t} ${it.th} ${it.z}`);
        const score = woorden.reduce((s, w) => s + (hooi.includes(w) ? (norm(it.t).includes(w) ? 3 : 1) : -99), 0);
        return { it, score };
      }).filter((h) => h.score > 0).sort((a, b) => b.score - a.score).slice(0, 8);
      if (!hits.length) {
        const li = document.createElement("li"); li.className = "geen";
        li.textContent = "Nog geen cijfer gevonden. Probeer een ander woord, of kies hieronder een thema.";
        lijst.appendChild(li);
      }
      hits.forEach(({ it }) => {
        const li = document.createElement("li"), a = document.createElement("a");
        a.href = it.u; a.textContent = it.v;
        const s = document.createElement("small"); s.textContent = it.th + " · " + it.t;
        a.appendChild(s); li.appendChild(a); lijst.appendChild(li);
      });
      lijst.hidden = false;
    }
    veld.addEventListener("input", toon);
    veld.addEventListener("keydown", (ev) => {
      const links = [...lijst.querySelectorAll("a")];
      if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
        ev.preventDefault();
        actief = (actief + (ev.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
        links.forEach((a, i) => a.setAttribute("aria-selected", i === actief ? "true" : "false"));
      } else if (ev.key === "Enter" && links.length) {
        location.href = links[Math.max(0, actief)].href;
      } else if (ev.key === "Escape") { veld.value = ""; toon(); }
    });
    document.addEventListener("click", (ev) => { if (!ev.target.closest(".zoek")) lijst.hidden = true; });
    if (location.hash === "#zoek") veld.focus();
  }

  // ---------- delen ----------
  function melding(tekst) {
    const m = document.createElement("div"); m.className = "melding"; m.textContent = tekst; m.setAttribute("role", "status");
    document.body.appendChild(m); setTimeout(() => m.remove(), 2200);
  }
  document.addEventListener("click", (ev) => {
    const knop = ev.target.closest("[data-deel]"); if (!knop) return;
    const url = location.href.split("#")[0] + "#" + knop.dataset.deel;
    const titel = knop.closest(".kaart").querySelector("h3").textContent;
    if (navigator.share) navigator.share({ title: titel, url }).catch(() => {});
    else if (navigator.clipboard) navigator.clipboard.writeText(url).then(() => melding("Link gekopieerd"));
  });
})();
