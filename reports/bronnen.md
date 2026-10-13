# Verkenning van bronnen (fase 0)

Laatste test: 2026-10-13T18:16:34+00:00

Automatisch gegenereerd door `pipeline/probe_sources.py`. ✅ = antwoordt met data, ⚠️ = antwoordt maar mogelijk geen bruikbare data, ❌ = niet bereikbaar.

| Instelling | Wat | Status | Type | Eerste tekens van het antwoord |
|---|---|---|---|---|
| Statbel | [Open data overzicht](https://statbel.fgov.be/nl/open-data) | ⚠️ HTTP 200 | text/html | `<!DOCTYPE html> <html lang="nl" dir="ltr" class="no-js" xml:lang="nl"> <head> <meta charset="utf-8" /> <meta name="Generator" content="Drupal 10 (https:/` |
| Statbel | [Bevolking per gemeente (open data)](https://statbel.fgov.be/nl/open-data/bevolking-naar-woonplaats-nationaliteit-burgerlijke-staat-leeftijd-en-geslacht-10) | ⚠️ HTTP 200 | text/html | `<!DOCTYPE html> <html lang="nl" dir="ltr" class="no-js" xml:lang="nl"> <head> <meta charset="utf-8" /> <meta name="description" content="Beschrijving: Be` |
| Nationale Bank | [NBB.Stat SDMX-dataflows](https://stat.nbb.be/restsdmx/sdmx.ashx/GetDataStructure/ALL) | ❌ | — | ConnectionError |
| Nationale Bank | [NBB data-API (nieuw)](https://nsidisseminate-stat.nbb.be/rest/dataflow/all/all/latest) | ✅ HTTP 200 | application/vnd.sdmx.structure+xml | `<?xml version="1.0" encoding="utf-8"?> <!--NSI Web Service v8.19.9.0--> <message:Structure xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/mess` |
| Infrabel | [Open data catalogus: stiptheid](https://opendata.infrabel.be/api/explore/v2.1/catalog/datasets?where=search(%22punctuality%22)&limit=20) | ✅ HTTP 200 | application/json | `{"total_count": 1, "results": [{"visibility": "domain", "fields": [{"name": "dat_dep", "annotations": {"facet": true, "timerangeFilter": true, "facetsort": "-al` |
| iRail | [Stations (NMBS, via iRail)](https://api.irail.be/stations/?format=json&lang=nl) | ✅ HTTP 200 | application/json | `{"version":"1.4","timestamp":"1791915404","station":[{"@id":"http://irail.be/stations/NMBS/008883006","id":"BE.NMBS.008883006","name":"'s Gravenbrakel","locatio` |
| data.gov.be | [Federale open-data catalogus](https://data.gov.be/api/3/action/package_search?q=statbel&rows=5) | ❌ HTTP 404 | text/html | `<!DOCTYPE html> <html lang="en" dir="ltr" prefix="og: https://ogp.me/ns#" class="no-sidebars not-logged-in page--api"> <head> <meta charset="utf-8" /> <no` |
| Sciensano | [Epistat open data](https://epistat.sciensano.be/) | ⚠️ HTTP 200 | text/html | `<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta http-equiv="x-ua-compatible" content="ie=edge"> <title>Epistat â Epi` |
| Federaal Planbureau | [Indicatoren duurzame ontwikkeling](https://indicators.be/nl/) | ❌ HTTP 404 | text/html | `<!DOCTYPE HTML> <html lang="en" prefix="og: http://ogp.me/ns#"> <head> <link rel="stylesheet" href="https://unpkg.com/orejime@2.2.1/dist/orejime.css" />` |
| Statistiek Vlaanderen | [Werkzaamheidsgraad](https://www.vlaanderen.be/statistiek-vlaanderen/arbeid/werkzaamheidsgraad) | ⚠️ HTTP 200 | text/html | `<!DOCTYPE html> <html lang="nl"> <head > <title>Werkzaamheidsgraad / Vlaanderen.be</title> <script type="application/ld+json" id="microdata-ldjson">{"@con` |
| IWEPS | [Indicateurs Wallonie](https://www.iweps.be/) | ⚠️ HTTP 200 | text/html | `<!doctype html> <html lang="fr-FR"> <head> <meta charset="utf-8"> <meta http-equiv="x-ua-compatible" content="ie=edge"> <meta name="viewport" conte` |
| BISA (Brussel) | [Statistieken Brussel](https://bisa.brussels/) | ⚠️ HTTP 200 | text/html | `<!DOCTYPE html><html lang="nl" dir="ltr" prefix="content: http://purl.org/rss/1.0/modules/content/ dc: http://purl.org/dc/terms/ foaf: http://xmlns.com/foaf/0.1` |
| De Kamer | [Kamerleden](https://www.dekamer.be/kvvcr/showpage.cfm?section=/depute&language=nl&cfm=/site/wwwcfm/depute/cvlist54.cfm) | ⚠️ HTTP 200 | text/html | `<!DOCTYPE html> <html> <head> <meta http-equiv="x-ua-compatible" content="IE=edge"> <link href="/kvvcr/css/LaChambre.css" rel="style` |
| Belgium.be | [Federale regering](https://www.belgium.be/nl/over_belgie/overheid/federale_overheid/federale_regering) | ⚠️ HTTP 200 | text/html | `<!DOCTYPE html> <html lang="nl" dir="ltr" prefix="og: https://ogp.me/ns#" class="script-disabled"> <head> <meta charset="utf-8" /> <meta name="description` |
