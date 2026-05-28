# Regelbestanden — single source of truth

Alle harde regeldata (blacklists, false friends, drempel-archaïsmen,
participium-triggers, fossiele genitieven, cap-stoplist, carryover-
allowlist) staat **gecentraliseerd** in `scripts/rules_data.py` en
`scripts/stoplist.txt`. De linters en de validator **importeren** die
lijsten — ze bevatten zelf geen eigen kopie meer.

> **Gevolg:** een regel wijzigen doe je op de bronlocatie hieronder.
> Het bewerken van `validate.py`, `lint_*.py` of `adversarial_scan.py`
> zelf om een woord toe te voegen is **zinloos** — die scripts lezen de
> data uit `rules_data.py` / `stoplist.txt`. Dit document is leidend; waar
> een skill of prompt nog een oude locatie noemt, geldt deze tabel.

## Waar woont welke regel

| Regelcategorie | Bronlocatie (enige plek om te wijzigen) | Geïmporteerd door |
|---|---|---|
| Archaïsme-blacklist (HARD in validator) | `ARCHAISM_BLACKLIST` in `scripts/rules_data.py` | `validate.py` |
| Carryover-allowlist (STOPLIST) | `scripts/stoplist.txt` (één woord/regex per regel) | `rules_data._load_stoplist()` → `lint_carryovers.py` |
| False friends | `FALSE_FRIENDS` in `scripts/rules_data.py` (+ mensentabel in `ARCHAISMEN.md` synchroon houden) | `lint_false_friends.py`, `meta_diff_aggregate.py` |
| Drempel-archaïsmen | `DREMPEL_ARCHAISMEN` in `scripts/rules_data.py` | `adversarial_scan.py` |
| Drempel-fossielen | `DREMPEL_FOSSIELEN` in `scripts/rules_data.py` | `adversarial_scan.py` |
| Fossiele genitief-paren | `FOSSIL_GENITIVE_PAIRS` in `scripts/rules_data.py` | `adversarial_scan.py`, `validate.py` |
| Participium adverbial-triggers (§2.3) | `ADVERBIAL_TRIGGERS_AFTER_PARTICIPLE` in `scripts/rules_data.py` | `validate.py` |
| Cap-check stoplist | `CAP_CHECK_STOPLIST` in `scripts/rules_data.py` | `validate.py` |
| Eigennamen-mapping (NBV21) | `ARCHAISMEN.md` | n.v.t. (referentie voor het model) |

## Synchronisatie-plichten

- **`FALSE_FRIENDS` ↔ `ARCHAISMEN.md` False-friends-tabel**: houd beide
  in sync. De codecommentaar bovenaan `lint_false_friends.py` zegt dit
  ook. De code-lijst is normatief voor de linter; de mensentabel voor het
  model.
- **STOPLIST**: voeg één woord per regel toe aan `scripts/stoplist.txt`.
  Geen Python bewerken.
- Na elke wijziging: draai de relevante linter/validator om te bevestigen
  dat de import klopt (geen syntaxfout in `rules_data.py`).

## Niet hier — leidende prozaregels

De *inhoudelijke* vertaalregels (wat is een drempel-archaïsme, §2.3
participium-ontvouwing, §2.7 drempeltests, hoofdletterdiscipline) staan
in `MODERNISATIE.md` en `AGENTS.md`. Dit bestand zegt alleen **waar de
machine-leesbare lijsten staan** zodat een edit ook effect heeft.
