# Module 03 — ETL Pipeline

Scenario: two partners have submitted their field measurement files. Neither follows the IBIS data standard. Your job is to extract, clean, and load them into `ibis.db`.

## Files

| File | Partner | Problems |
|------|---------|---------|
| `kenya_measurements.csv` | Nairobi team | DD/MM/YYYY dates, height in mm not cm, duplicate rows, missing experiment IDs |
| `india_measurements.csv` | ICAR-IARI team | Comma as decimal separator, yield in t/ha not kg/ha, extra whitespace in headers, one unknown experiment ID |
| `new_strains.json` | DTU lab | Mostly clean, but one entry has a duplicate strain_code already in the DB |

---

## Assignment 1 — Extract (`extract.py`)

Write functions that:
1. Load each file into a DataFrame.
2. Print: shape, column names, dtypes, null counts.
3. Flag anything that looks immediately wrong (wrong types, obviously bad values).

**The goal of extraction is observation — don't fix anything yet.**

---

## Assignment 2 — Transform (`transform.py`)

Write `clean_kenya(df)` that:
1. Strips whitespace from all column names and string values.
2. Converts `measured_at` from DD/MM/YYYY to YYYY-MM-DD.
3. Converts `plant_height_mm` → `plant_height_cm` (divide by 10), rename the column.
4. Removes duplicate rows.
5. Drops rows where `experiment_id` is missing.
6. Validates that all `experiment_id` values exist in `ibis.db` — flag unknown ones, don't drop silently.

Write `clean_india(df)` that:
1. Fixes column headers (strip whitespace).
2. Converts decimal commas to dots in numeric columns (e.g. `"42,5"` → `42.5`).
3. Converts `yield_t_per_ha` → `yield_kg_per_ha` (multiply by 1000), rename the column.
4. Validates experiment IDs against `ibis.db`.

Write `clean_strains(records)` that:
1. Checks each strain_code against `ibis.db` — skip any that already exist (log a warning).
2. Returns only new strains ready to insert.

---

## Assignment 3 — Load (`load.py`)

Write `load_measurements(df, db_path)` that:
1. Inserts cleaned measurements into `ibis.db`.
2. Is idempotent: if a row with the same `experiment_id` + `measured_at` already exists, skip it (don't duplicate).
3. Reports how many rows were inserted vs skipped.

Write `load_strains(records, db_path)` that inserts new strains, skipping duplicates.

---

## Running the full pipeline

```bash
uv run python 03_etl_pipeline/pipeline.py
```
