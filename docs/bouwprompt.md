# Bouwprompt: "België in cijfers" — open dashboard voor burger en beleid

> Gebruik deze prompt in Claude Code (of een andere coding agent) in een lege GitHub-repository. Werk fase per fase en vraag bevestiging na elke fase.

## 1. Rol en doel

Je bent lead developer van **België in cijfers**: een publieke, gratis website die de toestand van België in één oogopslag toont, zoals een Power BI-dashboard voor de premier en de minister-presidenten, maar open voor iedereen.

Doelen:
1. **Transparantie:** elke burger ziet dezelfde officiële cijfers als de beleidsmaker.
2. **Beter politiek debat:** discussies starten van gedeelde, controleerbare feiten.
3. **Toegankelijkheid:** burgers vertalen cijfers en maatregelen naar hun eigen situatie (bv. "hoeveel belasting betaal ik op mijn loon?").
4. **Automatisch:** de data houdt zichzelf actueel, zonder handwerk.

## 2. Niet-onderhandelbare principes

1. **Elk getal heeft een bron.** Naast elk cijfer staan de bron (instelling + dataset-code), de referentieperiode, de datum van ophalen en een directe link. Een cijfer zonder bron wordt niet getoond.
2. **Cijfers komen uit code, nooit uit een taalmodel.** Een AI-agent mag de pipeline bewaken, fouten melden en teksten voorstellen, maar elk getal op de site komt rechtstreeks uit een officiële bron via deterministische code. Afgeleide cijfers (bv. schuld per inwoner) tonen hun formule.
3. **Politiek neutraal.** Geen woorden als "goed" of "slecht" zonder objectieve norm. Kleuren tonen alleen de afstand tot een officieel doel (bv. EU-norm van −3% tekort, doel 80% werkzaamheid in 2030), nooit een oordeel. Geen partijkleuren.
4. **Reproduceerbaar.** Alle ruwe data en berekeningen staan in de repository en zijn als CSV te downloaden. Iedereen kan een getal narekenen.
5. **Eerlijk over onzekerheid.** Voorlopige cijfers, breuken in reeksen en definitieverschillen tussen bronnen worden zichtbaar gemarkeerd.
6. **Meertalig en toegankelijk.** Nederlands, Frans en Duits (Engels optioneel). WCAG 2.2 AA, werkt goed op een smartphone, laadt snel.
7. **Eigen, sobere vormgeving.** Neutrale, professionele huisstijl die doet denken aan een overheidsstatistiekdienst: rustig, veel wit, één accentkleur, duidelijke typografie. Geen sjabloonlook van een AI-tool of een generieke SaaS-stijl.
8. **Privacy.** Geen tracking-cookies. De loonsimulator rekent in de browser; ingevoerde gegevens verlaten het toestel niet.

## 3. Architectuur

```
bronnen (API's, open data)
   │  fetchers per bron (Python), dagelijks/wekelijks via GitHub Actions
   ▼
data/raw/        ruwe antwoorden, met tijdstempel en checksum
   ▼  normalisatie + validatie (schema, bereik, sprong-detectie)
data/clean/      één tabel per indicator (Parquet + CSV) + metadata (YAML)
   ▼
site (statische build)   →   hosting (GitHub Pages of Cloudflare Pages)
   ▲
agent-taken: bewaken, melden, voorstellen (zie §7)
```

- **Data-laag:** Python 3.12, `requests`, `pandas`, `pandera` voor validatie, DuckDB voor queries. Elke indicator heeft een metadatabestand: `id, titel (nl/fr/de), definitie, eenheid, bron, dataset_code, url, frequentie, laatste_update, regio_niveau, norm/doel (optioneel)`.
- **Frontend:** statische site (Astro of SvelteKit in static mode) met Observable Plot of ECharts voor grafieken. Geen backend nodig voor versie 1.
- **Automatisering:** GitHub Actions met schema per bron. Bij elke run: ophalen → valideren → bij succes commit + nieuwe build; bij afwijking een issue openen in plaats van publiceren.
- **Changelog:** elke datawijziging komt in een publieke changelog ("Op 14/10 werd de schuld 2025 bijgesteld van 107,9% naar 108,1% door Eurostat").

## 4. Modules

### 4.1 Dashboard per thema
Startpagina met ±12 kerncijfers, daarna een pagina per thema. Elk thema toont België, de drie gewesten (waar beschikbaar), de buurlanden en het EU-gemiddelde, met een tijdreeks.

Thema's en voorbeeldindicatoren:
- **Economie:** reële bbp-groei, bbp per inwoner, inflatie, productiviteit, faillissementen, export.
- **Overheidsfinanciën:** schuld (% bbp en per inwoner), begrotingssaldo, rentelasten, belastingdruk, uitgaven per functie.
- **Werk:** werkzaamheidsgraad, werkloosheid, vacatures, langdurig zieken, loonkost.
- **Gezondheid:** levensverwachting, wachttijden waar beschikbaar, zorguitgaven, vaccinatiegraad, arbeidsongeschiktheid.
- **Mobiliteit:** stiptheid van de treinen, files, verkeersdoden, gebruik van openbaar vervoer.
- **Onderwijs:** vroegtijdige schoolverlaters, diploma's hoger onderwijs, PISA-scores.
- **Wonen en armoede:** woningprijzen, armoederisico, energiearmoede.
- **Klimaat en energie:** uitstoot, aandeel hernieuwbare energie, energieprijzen.
- **Veiligheid en justitie:** geregistreerde criminaliteit, doorlooptijden, gevangenisbevolking.
- **Demografie:** bevolking, vergrijzing, migratie.

### 4.2 Loonsimulator ("wat houd ik over?")
- Invoer: brutomaandloon, gezinssituatie, kinderen ten laste, gemeente.
- Uitvoer: RSZ-bijdrage, bedrijfsvoorheffing, gemeentebelasting, nettoloon, en het totaal aan belastingen en bijdragen als percentage, inclusief de werkgeversbijdragen (totale loonkost).
- Alle parameters (percentages, schalen, werkbonus, belastingvrije som) staan per inkomstenjaar in een apart bestand, met bron per parameter (FOD Financiën, RSZ).
- Duidelijke vermelding: "benadering; je echte loonbrief kan afwijken". Test de berekening tegen minstens 20 voorbeelden uit officiële simulatoren.

### 4.3 "Wie is bevoegd?" en politici-overzicht
- Zoekveld "Ik heb een vraag over …". De zoekfunctie toont het bevoegde niveau (federaal, gemeenschap, gewest, provincie, gemeente) en de bevoegde minister of schepen, met uitleg waarom.
- Basis is een **handmatig gecontroleerde bevoegdhedenkaart** (thema → bevoegdheidsniveau → bevoegdheden per minister), gebaseerd op de officiële bevoegdheidsverdelingen van de regeringen. Een taalmodel mag de vraag van de burger enkel naar een bestaand thema uit die kaart vertalen; het antwoord zelf komt altijd uit de kaart.
- Overzicht van alle regeringen en ministers met bevoegdheden, partij, start van het mandaat en link naar de officiële pagina. Dit wordt dagelijks gecontroleerd tegen de officiële regeringssites; wijzigingen worden eerst als voorstel gemeld.
- Neutraal: dezelfde informatie voor elke persoon, zonder beoordelingen.

### 4.4 Maatregelen-simulator (latere fase)
- "Wat betekent maatregel X voor mij?" Alleen voor maatregelen met officiële parameters (bv. een aangekondigde wijziging van de belastingvrije som), hergebruikt de rekenmotor van 4.2.
- Elke simulatie vermeldt de bron van de maatregel en of ze beslist, aangekondigd of nog een voorstel is. Macro-effecten alleen met verwijzing naar officiële ramingen (Planbureau, Rekenhof, NBB), nooit zelf geraamd.

## 5. Bronnencatalogus

Verifieer eerst voor **elke** bron of de API of de open data echt werkt, welke licentie geldt en hoe vaak hij bijwerkt. Leg dat vast in `sources.yaml`. Kies per indicator één primaire bron; vermeld afwijkende cijfers van andere bronnen op de pagina zelf.

Te onderzoeken bronnen (niet volledig):
- **Eurostat** dissemination API (JSON-stat en SDMX): Europese vergelijking. Let op rate limits; cache agressief.
- **Statbel** open data: bevolking, arbeidsmarkt (EAK), prijzen, armoede, bedrijven.
- **Nationale Bank (NBB.Stat)**: nationale rekeningen, overheidsfinanciën, conjunctuur.
- **Federaal Planbureau**: vooruitzichten, indicatoren voor duurzame ontwikkeling.
- **FOD Economie**: Belgian competitiveness dashboard als inspiratie en mogelijke bron.
- **FOD Financiën en RSZ**: fiscale en sociale parameters voor de loonsimulator.
- **Sciensano, RIZIV, Statbel**: gezondheid.
- **Infrabel / NMBS open data en iRail**: stiptheid van de treinen.
- **Statistiek Vlaanderen, IWEPS, BISA**: gewestelijke cijfers.
- **De Kamer, Senaat, regeringssites, belgium.be**: politici, regeringen, bevoegdheden.
- **data.gov.be**: overzicht van federale open data.

## 6. Werkwijze in fasen

1. **Fase 0, verkenning:** bouw de bronnencatalogus, test elke API en lever een rapport: wat werkt, wat niet, welke indicatoren haalbaar zijn. Nog geen site.
2. **Fase 1, fundament:** datapipeline met 3 bronnen (Eurostat, Statbel, NBB) en 12 kernindicatoren; validatie; GitHub Actions; eenvoudige statische site met bronvermelding bij elk getal.
3. **Fase 2, thema's:** alle thema's uit 4.1, gewestelijke uitsplitsing, CSV-download, changelog, meertaligheid.
4. **Fase 3, burgermodules:** loonsimulator (4.2) en "Wie is bevoegd?" (4.3).
5. **Fase 4, maatregelen-simulator** (4.4) en agent-taken uit §7.

Na elke fase: werkende demo, test-rapport, en een lijst van open vragen.

## 7. Agent-taken (automatisering)

Een geplande agent (bv. dagelijks) mag:
- controleren of elke bron nog antwoordt en of de structuur gewijzigd is;
- nieuwe cijfers vergelijken met de vorige versie en grote sprongen of herzieningen melden;
- een issue openen bij een probleem, met diagnose en voorgestelde fix;
- wijzigingen in regeringssamenstelling of bevoegdheden detecteren en als pull request voorstellen;
- conceptteksten voor de changelog schrijven.

De agent mag **niet**: zelf cijfers invullen of schatten, publiceren zonder dat de validatie slaagt, of politieke duiding toevoegen. Wijzigingen aan de bevoegdhedenkaart en de loonparameters vereisen altijd menselijke goedkeuring.

## 8. Kwaliteitseisen (acceptatiecriteria)

- Een steekproef van 20 willekeurige getallen op de site moet exact overeenkomen met de bron op de vermelde datum.
- Elk getal heeft een werkende bronlink.
- Lighthouse-scores van minstens 90 op prestaties en toegankelijkheid.
- De site werkt zonder JavaScript voor de kerncijfers (enkel grafieken en simulatoren vereisen het).
- Unit tests voor elke berekening (afgeleide indicatoren, loonsimulator).
- Bij een mislukte bron blijft de site de laatste geldige cijfers tonen, met de datum erbij.

## 9. Eerst doen

Begin met fase 0. Stel me vooraf maximaal vijf vragen over keuzes die je niet zelf kunt maken (domeinnaam, hosting, licentie, talen, prioriteit van thema's). Neem voor de rest redelijke standaardkeuzes en vermeld ze.
