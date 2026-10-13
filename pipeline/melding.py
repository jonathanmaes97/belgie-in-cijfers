"""Meldt mislukte bronnen via een GitHub-issue. GitHub mailt de eigenaar van de repository
bij elk nieuw issue en elke reactie, dus zo krijg je een mail als er iets misloopt.

- Zijn er bronnen met ❌ in reports/status.md, dan wordt een issue met het label "bronfout"
  geopend (of krijgt het bestaande issue een reactie als de lijst veranderd is).
- Werkt alles weer, dan wordt het issue automatisch gesloten.

Draait in GitHub Actions met de ingebouwde token (GH_TOKEN). Lokaal doet het niets.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

WORTEL = Path(__file__).resolve().parent.parent
LABEL = "bronfout"
EIGENAAR = "jonathanmaes97"


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def mislukte_bronnen() -> list[str]:
    status = (WORTEL / "reports" / "status.md").read_text(encoding="utf-8")
    return [r for r in status.splitlines() if r.startswith("|") and "❌" in r]


def main() -> None:
    if not os.environ.get("GH_TOKEN"):
        print("Geen GH_TOKEN: melding overgeslagen.")
        return
    fouten = mislukte_bronnen()
    gh("label", "create", LABEL, "--color", "D93F0B", "--description", "Een databron kon niet worden opgehaald", "--force")
    open_issues = json.loads(gh("issue", "list", "--label", LABEL, "--state", "open", "--json", "number,body"))
    run_url = f'{os.environ.get("GITHUB_SERVER_URL", "https://github.com")}/{os.environ.get("GITHUB_REPOSITORY", "")}/actions/runs/{os.environ.get("GITHUB_RUN_ID", "")}'
    lijst = "\n".join(fouten)
    tekst = (f"@{EIGENAAR} Bij de dagelijkse update konden deze bronnen niet worden opgehaald. "
             f"De site toont voor deze cijfers de laatste geldige versie.\n\n"
             f"| Indicator | Status | Opgehaald | Melding |\n|---|---|---|---|\n{lijst}\n\nRun: {run_url}")
    if fouten and not open_issues:
        gh("issue", "create", "--title", f"Bronfout: {len(fouten)} bron(nen) niet bijgewerkt", "--label", LABEL, "--body", tekst)
        print("Issue geopend.")
    elif fouten:
        nr = open_issues[0]["number"]
        if lijst not in open_issues[0]["body"]:
            gh("issue", "comment", str(nr), "--body", tekst)
            gh("issue", "edit", str(nr), "--body", tekst)
            print(f"Issue #{nr} bijgewerkt.")
    elif open_issues:
        for i in open_issues:
            gh("issue", "close", str(i["number"]), "--comment", "Alle bronnen werken weer. Automatisch gesloten.")
        print("Issue gesloten.")
    else:
        print("Alle bronnen in orde.")


if __name__ == "__main__":
    main()
