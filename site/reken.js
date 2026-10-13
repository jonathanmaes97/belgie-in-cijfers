// Pagina "Hoeveel belastingen betaal ik?": leest de invoer, rekent met rekenmodule.js en toont het resultaat.
(function () {
  "use strict";
  const form = document.getElementById("reken-form");
  if (!form || !window.Rekenmodule) return;
  const BASIS = document.currentScript.src.replace(/reken\.js.*$/, "");
  const nf0 = new Intl.NumberFormat("nl-BE", { maximumFractionDigits: 0 });
  const nf1 = new Intl.NumberFormat("nl-BE", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const eur = (x) => "€ " + nf0.format(Math.round(x));
  const pct = (x) => nf1.format(x * 100) + "%";
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

    // balk: netto | RSZ | personenbelasting | gemeentebelasting
    const delen = [
      ["netto", u.netto, "Netto voor jou"], ["rsz", u.rsz, "Sociale zekerheid (RSZ)"],
      ["pb", u.personenbelasting, "Personenbelasting"], ["gem", u.gemeentebelasting, "Gemeentebelasting"],
    ];
    const balk = $("r-balk"); balk.textContent = "";
    const leg = $("r-legende"); leg.textContent = "";
    delen.forEach(([k, v, naam]) => {
      const aandeel = u.bruto > 0 ? (v / u.bruto) * 100 : 0;
      const d = document.createElement("i"); d.className = "deel-" + k; d.style.width = aandeel + "%"; d.title = naam;
      balk.appendChild(d);
      const li = document.createElement("li");
      const sw = document.createElement("span"); sw.className = "sw deel-" + k;
      li.append(sw, document.createTextNode(`${naam}: ${eur(v)} (${nf1.format(aandeel)}%)`));
      leg.appendChild(li);
    });

    // stappen
    const t = $("r-stappen"); t.textContent = "";
    t.append(
      rij("Brutoloon (12 maanden)", eur(u.loon)),
      ...(u.vakantiegeld ? [rij("+ dubbel vakantiegeld", eur(u.vakantiegeld))] : []),
      ...(u.eindejaarspremie ? [rij("+ eindejaarspremie", eur(u.eindejaarspremie))] : []),
      rij("= Bruto per jaar", eur(u.bruto), "som"),
      rij(`− Sociale zekerheid (RSZ, ${new Intl.NumberFormat("nl-BE", { maximumFractionDigits: 2 }).format(P.rsz_werknemer.percentage)}%)`, "− " + eur(u.rsz)),
      rij(`− Forfaitaire beroepskosten (${P.forfaitaire_beroepskosten.percentage}%, max. ${eur(P.forfaitaire_beroepskosten.maximum)})`, "− " + eur(u.beroepskosten)),
      rij("= Belastbaar inkomen", eur(u.belastbaar), "som"),
    );
    const s = $("r-schijven"); s.textContent = "";
    u.basisbelasting.per.forEach((x) => {
      if (x.deel <= 0) return;
      s.appendChild(rij(`${eur(x.van)} tot ${x.tot === null ? "meer" : eur(x.tot)} aan ${x.tarief}%`, `${eur(x.deel)} → ${eur(x.belasting)}`));
    });
    s.append(
      rij("= Belasting op je inkomen", eur(u.basisbelasting.totaal), "som"),
      rij(`− Belastingvrije som (${eur(u.belastingvrijeSom.totaal)} wordt niet belast)`, "− " + eur(u.vrijstelling)),
      rij("= Personenbelasting", eur(u.personenbelasting), "som"),
      rij(`+ Gemeentebelasting (${nf1.format(i.gemeentePct)}% van de personenbelasting)`, eur(u.gemeentebelasting)),
      rij("Totaal aan sociale bijdragen en belastingen", eur(u.totaal), "som totaal"),
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
        const naam = document.createElement("span"); naam.className = "w-naam"; naam.textContent = x.nl;
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
