// Rekenmotor "Hoeveel belastingen betaal ik?" — werkt in de browser en in Node (voor de tests).
// Alle parameters komen uit config/fiscaal/<jaar>.yaml (met bron per waarde); hier staan geen bedragen.
(function (wortel, fabriek) {
  if (typeof module === "object" && module.exports) module.exports = fabriek();
  else wortel.Rekenmodule = fabriek();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const r2 = (x) => Math.round(x * 100) / 100;

  // Past de progressieve schijven toe op een bedrag. Geeft per schijf het belaste deel en de belasting.
  function schijfbelasting(bedrag, schijven) {
    let totaal = 0;
    const per = schijven.map(([van, tot, tarief]) => {
      const boven = tot === null ? Infinity : tot;
      const deel = Math.max(0, Math.min(bedrag, boven) - van);
      const belasting = (deel * tarief) / 100;
      totaal += belasting;
      return { van, tot, tarief, deel: r2(deel), belasting: r2(belasting) };
    });
    return { totaal: r2(totaal), per };
  }

  function belastingvrijeSom(invoer, P) {
    const b = P.belastingvrije_som;
    const k = Math.max(0, Math.floor(invoer.kinderen || 0));
    let kind = 0;
    if (k >= 1 && k <= 4) kind = b.kinderen[k] || b.kinderen[String(k)];
    else if (k > 4) kind = (b.kinderen[4] || b.kinderen["4"]) + (k - 4) * b.per_kind_vanaf_5;
    const jong = Math.min(k, Math.max(0, Math.floor(invoer.jongerDan3 || 0))) * b.per_kind_jonger_dan_3;
    const alleen = invoer.alleenstaandeOuder && k > 0 ? b.alleenstaande_met_kinderen : 0;
    return { basis: b.basis, kinderen: kind, jongerDan3: jong, alleenstaandeOuder: alleen, totaal: b.basis + kind + jong + alleen };
  }

  // invoer: { maandloon, vakantiegeld (bool), eindejaarspremie (bool), eindejaarsMaanden, kinderen, jongerDan3,
  //           alleenstaandeOuder (bool), gemeentePct }
  function bereken(invoer, P) {
    const m = Math.max(0, +invoer.maandloon || 0);
    const loon = 12 * m;
    const vakantiegeld = invoer.vakantiegeld ? (m * P.dubbel_vakantiegeld.percentage_maandloon) / 100 : 0;
    const eindejaarspremie = invoer.eindejaarspremie ? m * (invoer.eindejaarsMaanden ?? 1) : 0;
    const bruto = loon + vakantiegeld + eindejaarspremie;
    const rsz = (bruto * P.rsz_werknemer.percentage) / 100;
    const naRsz = bruto - rsz;
    const kosten = Math.min((naRsz * P.forfaitaire_beroepskosten.percentage) / 100, P.forfaitaire_beroepskosten.maximum);
    const belastbaar = Math.max(0, naRsz - kosten);
    const schijven = P.schijven.lijst;
    const basisbelasting = schijfbelasting(belastbaar, schijven);
    const bvs = belastingvrijeSom(invoer, P);
    const vrijstelling = schijfbelasting(bvs.totaal, schijven);
    const personenbelasting = Math.max(0, basisbelasting.totaal - vrijstelling.totaal);
    const gemeentebelasting = (personenbelasting * (+invoer.gemeentePct || 0)) / 100;
    const totaal = rsz + personenbelasting + gemeentebelasting;
    const netto = bruto - totaal;
    return {
      loon: r2(loon), vakantiegeld: r2(vakantiegeld), eindejaarspremie: r2(eindejaarspremie), bruto: r2(bruto),
      rsz: r2(rsz), naRsz: r2(naRsz), beroepskosten: r2(kosten), belastbaar: r2(belastbaar),
      basisbelasting, belastingvrijeSom: bvs, vrijstelling: r2(Math.min(vrijstelling.totaal, basisbelasting.totaal)),
      personenbelasting: r2(personenbelasting), gemeentebelasting: r2(gemeentebelasting),
      totaal: r2(totaal), netto: r2(netto), nettoPerMaand: r2(netto / 12),
      druk: bruto > 0 ? totaal / bruto : 0,
      drukZonderRsz: bruto > 0 ? (personenbelasting + gemeentebelasting) / bruto : 0,
    };
  }

  // Van elke 100 euro extra brutoloon per jaar: hoeveel hou je netto over?
  function marginaal(invoer, P) {
    const a = bereken(invoer, P);
    const b = bereken({ ...invoer, maandloon: (+invoer.maandloon || 0) + 100 / 12 }, P);
    const extraBruto = b.bruto - a.bruto;
    return extraBruto > 0 ? ((b.netto - a.netto) / extraBruto) * 100 : 0;
  }

  return { bereken, marginaal, schijfbelasting, belastingvrijeSom };
});
