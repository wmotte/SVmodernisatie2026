# Tests

Smoke-tests voor de scaffolding. Niet-uitputtend; ze beschermen tegen
regressies in de stukken die de orchestrator-flow zou breken (validator
overrides-schema, `next_batch` exit-paden, etc.).

Draaien:

```bash
uv run --group dev pytest
```

Of een enkel bestand:

```bash
uv run --group dev pytest tests/test_validate_overrides.py -v
```

Geen tests voor de inhoudelijke modernisatie zelf — die hangt af van een
LLM-aanroep en hoort niet in een unit-suite.
