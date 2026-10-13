# België in cijfers

Een open, onafhankelijk dashboard met de officiële kerncijfers van België: economie, overheidsfinanciën, werk, gezondheid, onderwijs, armoede, klimaat, mobiliteit en bevolking. Elk cijfer staat er met bronvermelding bij en de site werkt zichzelf dagelijks bij.

**Doel:** meer transparantie, een beter geïnformeerd politiek debat, en cijfers die voor elke burger toegankelijk zijn.

## Principes

1. **Elk getal heeft een bron.** Naast elk cijfer: instelling, dataset, referentiejaar, datum van ophalen en een link naar de exacte bevraging.
2. **Cijfers komen uit code, nooit uit een taalmodel.** Afgeleide cijfers tonen hun formule.
3. **Politiek neutraal.** Kleuren en lijnen tonen enkel officiële normen of doelen, geen oordelen.
4. **Reproduceerbaar.** Alle data en berekeningen staan in deze repository; elk cijfer is als CSV te downloaden.
5. **Eerlijk over onzekerheid.** Voorlopige cijfers en herzieningen worden gemarkeerd.

## Hoe het werkt

```
config/indicatoren.yaml   catalogus: thema's, indicatoren, uitleg, bronnen en filters
config/regeringen.yaml    federale regeringen met begin- en einddatum (bron: Koninklijke Commissie voor Geschiedenis)
pipeline/eurostat.py      ophalen en ontleden van Eurostat-data
pipeline/infrabel.py      ophalen van Infrabel-data (treinstiptheid), jaarcijfers gecontroleerd tegen de jaartotalen van de bron
pipeline/run.py           ophalen → valideren → herzieningen loggen → afgeleide cijfers → site-data
pipeline/build_site.py    bouwt de startpagina en één pagina per thema (cijfers en vergelijkingszinnen staan in de HTML, ook zonder JavaScript)
pipeline/og.py           maakt de preview-afbeeldingen voor LinkedIn en andere sociale media
pipeline/probe_sources.py test andere bronnen (Statbel, NBB, Infrabel, iRail, ...) → reports/bronnen.md
data/clean/               één CSV en metadata per indicator
data/changelog.json       herzieningen van cijfers door de bronnen
reports/status.md         status van elke bron bij de laatste run
site/                     de website (HTML, CSS, JS, data)
```

Elke dag om 05:23 UTC haalt een GitHub Action de cijfers op, test en valideert ze, en publiceert de site op GitHub Pages. Mislukt een bron, dan blijft de laatst geldige versie staan en meldt `reports/status.md` waarom.

## Zelf draaien

```bash
pip install -r requirements.txt
python -m pytest -q
python -m pipeline.run            # alles ophalen en de site opbouwen
python -m pipeline.run --offline  # site opbouwen uit bestaande data
cd site && python -m http.server  # bekijk op http://localhost:8000
```

## Een indicator toevoegen

Voeg een blok toe in `config/indicatoren.yaml` met de Eurostat-datasetcode en de filters voor elke dimensie behalve land en jaar. Ontbreekt een filter, dan stopt de pipeline met een melding die de mogelijke waarden opsomt.

## Plannen

Zie [docs/bouwprompt.md](docs/bouwprompt.md): meer bronnen (Statbel, NBB, Infrabel), cijfers per gewest, een loonsimulator, en "Wie is bevoegd?".

## Licentie

Code: MIT. Data: eigendom van de vermelde bronnen, hergebruikt volgens hun voorwaarden (Eurostat: [hergebruik toegestaan met bronvermelding](https://ec.europa.eu/eurostat/about-us/policies/copyright)).
