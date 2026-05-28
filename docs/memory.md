# `memory/` — lokale databases

> Geplaatst in `docs/` omdat de `memory/`-map zelf gitignored is (en in
> worktrees een symlink). Deze pagina documenteert wat er fysiek in die
> map staat.

Twee SQLite-bestanden, beide **gitignored** en per-machine lokaal. Geen
artefacten in deze map worden naar GitHub gepusht; ze worden opgebouwd
door de scripts hieronder.

| Bestand | Beheerd door | Inhoud | Aanmaak |
|---|---|---|---|
| `verses.db` | `scripts/memory.py` | Vector-embeddings (Gemini, 768 dim) van SV1657-origineel + modernisatie per vers. Voedt voorbeeld-selectie in `sv-modernize` Stap 2a en concordantie-context in `sv-semantic-review` Stap 2. | `memory.py add --from-output …` (per vers) of `memory.py sync --root output/` (bulk). |
| `process.db` | `scripts/index_process_memory.py` | FTS5-index over `output/<BOEK>/review.<H>.json` issues, rebuttals, en `notes`-velden uit de output-JSON. Wordt door `scripts/query_decisions.py` en `scripts/extract_decisions.py` bevraagd. | `index_process_memory.py --root output --rebuild`. |

## Verwijderde / verouderde bestanden

- `embeddings.db` — leeg artefact uit een vroege experimenteervorm.
  Niet meer gerefereerd in code of skills. Veilig om te verwijderen als
  hij nog rondzwerft (gebeurt automatisch in een verse clone — `.gitignore`
  vangt de map).

## Operationele regels

- **Niet committen.** `memory/*.db` staat in `.gitignore`. Deze README
  is het enige getrackte bestand in deze map.
- **Worktrees delen het pad.** `scripts/wt.sh` zet `memory/` als symlink
  naar de hoofdrepository, zodat parallelle worktree-sessies dezelfde DB
  gebruiken. Zie `WORKTREE_WORKFLOW.md`.
- **Sync vóór elke batch.** De orchestrator draait
  `memory.py sync --root output/ --terse` als Stap 0.5. Verschil tussen
  output-JSON en DB wordt automatisch ge-her-embed (2 API-aanroepen
  per vers). Exitcode ≠ 0 = blokker — niet doorgaan op stdout.
- **Aanbiedersonafhankelijk.** Het huidige embeddings-model is
  Gemini-`text-embedding-004`; vervangen kan via `scripts/memory.py`
  zonder skill-aanpassingen.
