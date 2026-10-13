// Pagina "Hoeveel belastingen betaal ik?": leest de invoer, rekent met rekenmodule.js en toont het resultaat.
(function () {
  "use strict";
  const form = document.getElementById("reken-form");
  if (!form || !window.Rekenmodule) return;
  const BASIS = document.currentScript.src.replace(/reken\.js.*$/, "");
  let UI = {};
  try { UI = JSON.parse(document.getElementById("ui").textContent); } catch (e) {}
  const LOC = UI.locale || "nl-BE";
  const T = (k, vars) => String((UI.t && UI.t[k]) || k).replace(/\{(\w+)\}/g, (m, n) => (vars && n in vars ? vars[n] : m));
  const [EV, EN] = (UI.eenheden && UI.eenheden["€"]) || ["€ ", ""];
  const P_TEKEN = (UI.eenheden && UI.eenheden["%"] && UI.eenheden["%"][1]) || "%";
  const nf0 = new Intl.NumberFormat(LOC, { maximumFractionDigits: 0 });
  const nf1 = new Intl.NumberFormat(LOC, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const nf2 = new Intl.NumberFormat(LOC, { maximumFractionDigits: 2 });
  const eur = (x) => EV + nf0.format(Math.round(x)) + EN;
  const pct = (x) => nf1.format(x * 100) + P_TEKEN;
  const $ = (id) => document.getElementById(id);
  let P = null, uitgaven = null;

  function invoer() {
    return {
      maandloon: +$("maandloon").value || 0,
      vakantiegeld: $("vakantiegeld").checked,
      eindejaarspremie: $("eindejaarspremie").checked,
      eindejaarsMaanden: +$("ejp-maanden").value || 0,
      kinderen: +$("kinderen").value || 0,
      jongerDan3: +$("jonger3").value || 0,
      alleenstaandeOuder: $("alleenstaand").checked,
      gemeentePct: +$("gemeente").value || 0,
    };
  }

  function rij(label, bedrag, klasse) {
    const tr = document.createElement("tr");
    if (klasse) tr.className = klasse;
    const th = document.createElement("th"); th.scope = "row"; th.textContent = label;
    const td = document.createElement("td"); td.textContent = bedrag;
    tr.append(th, td);
    return tr;
  }

  function toon() {
    if (!P) return;
    const i = invoer();
    $("kind-extra").hidden = i.kinderen === 0;
    $("ejp-maanden").disabled = !i.eindejaarspremie;
    const u = Rekenmodule.bereken(i, P);
    const marg = Rekenmodule.marginaal(i, P);
    $("r-druk").textContent = pct(u.druk);
    $("r-bruto").textContent = eur(u.bruto);
    $("r-netto").textContent = eur(u.netto);
    $("r-nettomaand").textContent = eur(u.nettoPerMaand);
    $("r-marg").textContent = eur(marg);
    // netto per maand is een gemiddelde: zeg wat erin zit, en toon ook de maand zonder extra's
    const vg = i.vakantiegeld && u.vakantiegeld > 0, ejp = i.eindejaarspremie && u.eindejaarspremie > 0;
    $("r-nettomaand-noot").textContent = T(vg && ejp ? "r_nm_beide" : vg ? "r_nm_vg" : ejp ? "r_nm_ejp" : "r_nm_geen");
    const zonder = Rekenmodule.bereken({ ...i, vakantiegeld: false, eindejaarspremie: false }, P);
    $("r-zonder").textContent = vg || ejp ? T("r_nm_zonder", { bedrag: eur(zonder.nettoPerMaand) }) : "";
    $("r-zonder").hidden = !(vg || ejp);

    // balk: netto | RSZ | personenbelasting | gemeentebelasting
    const delen = [
      ["netto", u.netto, T("r_netto")], ["rsz", u.rsz, T("r_rsz")],
      ["pb", u.personenbelasting, T("r_pb")], ["gem", u.gemeentebelasting, T("r_gem")],
    ];
    const balk = $("r-balk"); balk.textContent = "";
    const leg = $("r-legende"); leg.textContent = "";
    delen.forEach(([k, v, naam]) => {
      const aandeel = u.bruto > 0 ? (v / u.bruto) * 100 : 0;
      const d = document.createElement("i"); d.className = "deel-" + k; d.style.width = aandeel + "%"; d.title = naam;
      balk.appendChild(d);
      const li = document.createElement("li");
      const sw = document.createElement("span"); sw.className = "sw deel-" + k;
      li.append(sw, document.createTextNode(`${naam}: ${eur(v)} (${nf1.format(aandeel)}${P_TEKEN})`));
      leg.appendChild(li);
    });

    // stappen
    const t = $("r-stappen"); t.textContent = "";
    t.append(
      rij(T("r_loon"), eur(u.loon)),
      ...(u.vakantiegeld ? [rij(T("r_vg"), eur(u.vakantiegeld))] : []),
      ...(u.eindejaarspremie ? [rij(T("r_ejp"), eur(u.eindejaarspremie))] : []),
      rij(T("r_bruto"), eur(u.bruto), "som"),
      rij(T("r_rsz_rij", { pct: nf2.format(P.rsz_werknemer.percentage) }), "− " + eur(u.rsz)),
      rij(T("r_kosten_rij", { pct: nf2.format(P.forfaitaire_beroepskosten.percentage), max: eur(P.forfaitaire_beroepskosten.maximum) }), "− " + eur(u.beroepskosten)),
      rij(T("r_belastbaar"), eur(u.belastbaar), "som"),
    );
    const s = $("r-schijven"); s.textContent = "";
    u.basisbelasting.per.forEach((x) => {
      if (x.deel <= 0) return;
      s.appendChild(rij(T("r_schijf", { van: eur(x.van), tot: x.tot === null ? T("r_meer") : eur(x.tot), tarief: nf2.format(x.tarief) }), `${eur(x.deel)} → ${eur(x.belasting)}`));
    });
    s.append(
      rij(T("r_belasting_inkomen"), eur(u.basisbelasting.totaal), "som"),
      rij(T("r_bvs", { bedrag: eur(u.belastingvrijeSom.totaal) }), "− " + eur(u.vrijstelling)),
      rij(T("r_pb_som"), eur(u.personenbelasting), "som"),
      rij(T("r_gem_rij", { pct: nf1.format(i.gemeentePct) }), eur(u.gemeentebelasting)),
      rij(T("r_totaal"), eur(u.totaal), "som totaal"),
    );

    // waar gaat het naartoe?
    const w = $("r-waarheen");
    if (w && uitgaven) {
      w.textContent = "";
      const jaar = String(uitgaven.jaar);
      const f = uitgaven.functies.map((x) => [x, (uitgaven.aandelen[x.code] && uitgaven.aandelen[x.code].BE || {})[jaar] || 0]).sort((a, b) => b[1] - a[1]);
      const max = f[0][1];
      f.forEach(([x, a]) => {
        const li = document.createElement("li");
        const naam = document.createElement("span"); naam.className = "w-naam"; naam.textContent = (UI.uitgaven && UI.uitgaven[x.code]) || x.nl;
        const balkje = document.createElement("span"); balkje.className = "w-balk"; const b = document.createElement("i"); b.style.width = (a / max) * 100 + "%"; balkje.appendChild(b);
        const bedrag = document.createElement("span"); bedrag.className = "w-bedrag"; bedrag.textContent = eur((u.totaal * a) / 100);
        li.append(naam, balkje, bedrag);
        w.appendChild(li);
      });
      $("r-waarheen-jaar").textContent = jaar;
    }
  }

  form.addEventListener("input", toon);
  form.addEventListener("submit", (e) => e.preventDefault());
  Promise.all([
    fetch(BASIS + "data/fiscaal-2026.json").then((r) => r.json()),
    fetch(BASIS + "data/dashboard.json").then((r) => r.json()).catch(() => null),
  ]).then(([p, d]) => { P = p; uitgaven = d && d.uitgaven; toon(); });
})();
