# Richtlijnen voor AI-agents in deze repository

Dit project toont officiële cijfers over België. Geloofwaardigheid is alles.

- Vul **nooit** zelf een getal in, schat er geen en neem er geen over uit een webpagina of je geheugen. Elk getal komt uit een bron via `pipeline/`.
- Een nieuwe indicator = een blok in `config/indicatoren.yaml`, met bron en filters. Afgeleide cijfers krijgen een `afgeleid.formule`.
- Wijzig bestaande data in `data/clean/` niet met de hand; draai de pipeline.
- Geen politieke duiding of waardeoordelen in teksten. Kleuren alleen voor officiële normen of doelen.
- Teksten in eenvoudig Nederlands; structuur voorzien voor Frans en Duits.
- Draai `python -m pytest -q` en `python -m pipeline.run --offline` voor je commit.
- Zie `docs/bouwprompt.md` voor het volledige plan en de fasen.
