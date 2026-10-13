// Tests voor de rekenmotor. Draaien met: node tests/test_rekenmodule.js
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const R = require(path.join(__dirname, "..", "site", "rekenmodule.js"));

const P = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "site", "data", "fiscaal-2026.json"), "utf8"));

// 1. Officieel voorbeeld FOD Financiën (inkomstenjaar 2025): Pieter, alleenstaand, belastbaar 38.000 euro → 10.484,50 euro
const P2025 = JSON.parse(JSON.stringify(P));
P2025.schijven.lijst = [[0, 16320, 25], [16320, 28800, 40], [28800, 49840, 45], [49840, null, 50]];
P2025.belastingvrije_som.basis = 10910;
const basis = R.schijfbelasting(38000, P2025.schijven.lijst);
assert.strictEqual(basis.totaal, 13212);
const vrij = R.schijfbelasting(10910, P2025.schijven.lijst);
assert.strictEqual(vrij.totaal, 2727.5);
assert.strictEqual(basis.totaal - vrij.totaal, 10484.5);

// 2. Belastingvrije som met kinderen (inkomstenjaar 2026)
assert.strictEqual(R.belastingvrijeSom({ kinderen: 0 }, P).totaal, 11180);
assert.strictEqual(R.belastingvrijeSom({ kinderen: 2 }, P).totaal, 11180 + 5230);
assert.strictEqual(R.belastingvrijeSom({ kinderen: 5 }, P).totaal, 11180 + 18970 + 7240);
assert.strictEqual(R.belastingvrijeSom({ kinderen: 1, jongerDan3: 1, alleenstaandeOuder: true }, P).totaal, 11180 + 2030 + 760 + 2030);

// 3. Volledige berekening, nagerekend met de hand
const u = R.bereken({ maandloon: 3500, vakantiegeld: true, eindejaarspremie: true, eindejaarsMaanden: 1, kinderen: 0, gemeentePct: 7 }, P);
const bruto = 3500 * 12 + 3500 * 0.92 + 3500;           // 48.720
assert.strictEqual(u.bruto, bruto);
const rsz = bruto * 0.1307;                              // 6.367,70
assert.strictEqual(u.rsz, Math.round(rsz * 100) / 100);
const kosten = Math.min((bruto - rsz) * 0.3, 6070);      // maximum 6.070
assert.strictEqual(u.beroepskosten, 6070);
const belastbaar = bruto - rsz - kosten;
const pb = R.schijfbelasting(belastbaar, P.schijven.lijst).totaal - R.schijfbelasting(11180, P.schijven.lijst).totaal;
assert.ok(Math.abs(u.personenbelasting - pb) < 0.02);
assert.ok(Math.abs(u.gemeentebelasting - pb * 0.07) < 0.02);
assert.ok(Math.abs(u.netto - (bruto - rsz - pb * 1.07)) < 0.05);

// 4. Geen belasting onder de belastingvrije som; nooit negatief
const laag = R.bereken({ maandloon: 600, vakantiegeld: false, eindejaarspremie: false, kinderen: 3, gemeentePct: 8 }, P);
assert.strictEqual(laag.personenbelasting, 0);
assert.ok(laag.netto > 0);

// 5. Marginaal: bij een hoog loon zit je in de schijf van 50%
const m = R.marginaal({ maandloon: 8000, vakantiegeld: true, eindejaarspremie: true, kinderen: 0, gemeentePct: 7 }, P);
const verwacht = (1 - 0.1307) * (1 - 0.5 * 1.07) * 100;  // beroepskosten zitten al aan hun maximum
assert.ok(Math.abs(m - verwacht) < 0.05, `marginaal ${m} vs ${verwacht}`);

console.log("rekenmodule: alle tests geslaagd");
