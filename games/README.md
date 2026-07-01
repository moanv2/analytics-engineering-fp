# 🏭 Data Factory — the pipeline, as a game

`games/data_factory.html` is a single-file, dependency-free browser game built on top of
this repo. It's not a tutorial with quiz questions — it's a real-time arcade game where
you experience *why* every piece of this project's dbt layer exists, instead of reading
about it.

**[Play it](./games/data_factory.html)** — download and open in any browser, no server needed.

## The idea

You start the game as the entire data quality process. Rows of weather/AQI data ride a
conveyor belt up a tower — swamp → staging → intermediate → marts → dashboard — and dirty
rows (nulls, duplicates, dates-as-strings, negative AQI, a Sevilla reading of 999°C) have
to be **clicked by hand** to fix them before they reach the dashboard.

Clean deliveries earn credits. You spend credits in a shop to install the *actual* dbt
machinery from this repo — tests, a macro, contracts, CI — in the order the course taught
them. Each purchase automates a bug type off your plate. By the end of a run you've felt,
rather than read, the core pitch of dbt: you stop being the test because you bought the
test.

### Schema drift storms

Partway through, the sky turns purple and **schema drift storms** hit — rows where a
column's *type* has mutated upstream (`elevation → VARCHAR?!`). Clicking them does
nothing, and no test machine catches them either — the game tells you why: tests check
**values**, not **shape**. The only thing that stops a storm is buying the **Contract
Wall**, modeled on the real enforced contracts on `dim_location`,
`mart_city_season_summary`, and `mart_extreme_events` in this repo. Storms escalate for
the rest of the game, so contracts stay relevant to the very end.

## What maps to what

| In the game | In this repo |
|---|---|
| `stg_caster` machine | staging models casting raw text → real types |
| `not_null` / `unique` machines | PK tests on every surrogate key |
| `non_negative` / range machines | the custom `non_negative` generic test + `dbt_expectations` bounds |
| `season_from_date()` macro | the real Jinja macro, applied everywhere |
| Contract Wall | enforced contracts on 3 marts (Session 11) |
| CI robot | `.github/workflows/ci.yml` — lint → pytest → `dbt build` |
| 146 clean deliveries to win | the real check count across 17 models + 1 seed |

## Why it exists

Built as a fun companion piece to the final project presentation — a way to make the
value of tests, macros, and (especially) contracts land for an audience in under three
minutes of play, rather than a slide of bullet points.

No build step, no npm install — it's one HTML file with inline CSS/JS. Open it locally or
host it via GitHub Pages.
