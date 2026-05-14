# IBIS Data Steward — SQL & ETL Practice

Scenario: you are the data steward for the IBIS project (microbial biofertilizer research).
Partners in Kenya, India, Denmark, and Brazil submit experimental data.
Your job is to wrangle it into a clean central database that researchers can query.

## Setup

```bash
uv sync
uv run python 01_sql_basics/setup_db.py   # creates ibis.db
```

## Learning Path

| Module | Topic | Time |
|--------|-------|------|
| [01 - SQL Basics](./01_sql_basics/) | SELECT, JOIN, GROUP BY on research data | ~1.5h |
| [02 - SQL Intermediate](./02_sql_intermediate/) | Window functions, CTEs, data quality checks | ~1.5h |
| [03 - ETL Pipeline](./03_etl_pipeline/) | Extract & clean messy partner submissions | ~2h |
| [04 - Full Pipeline](./04_full_pipeline/) | End-to-end pipeline into ibis.db | ~2h |

## The IBIS database schema

```
strains      — bacterial strains being tested as biofertilizers
sites        — field trial locations (country, soil type, climate)
researchers  — collaborators submitting data
experiments  — one experiment = one strain tested at one site
measurements — observations recorded during an experiment
               (plant height, yield, chlorophyll, root weight, etc.)
```

## What is ETL?

```
[Partner CSV/JSON]  →  Extract  →  Transform  →  Load  →  [ibis.db]
messy, inconsistent    read it     clean it       write it   ready for analysis
```

Key things that go wrong with real research data:
- Different date formats across countries (DD/MM/YYYY vs YYYY-MM-DD)
- Units not standardised (t/ha vs kg/ha, cm vs mm)
- Strain IDs named inconsistently between partners
- Missing values, duplicate rows, out-of-range measurements
