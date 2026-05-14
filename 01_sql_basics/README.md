# Module 01 — SQL Basics

## Setup

```bash
uv run python 01_sql_basics/setup_db.py
```

Opens with: `sqlite3 ibis.db` or query from Python.

## Schema

```
strains:      id, strain_code, species, isolation_source, origin_country, nitrogen_fixing
sites:        id, site_code, country, region, soil_type, climate_zone
researchers:  id, name, institution, country, email
experiments:  id, experiment_id, site_id, strain_id, researcher_id, crop, treatment, start_date, end_date
              (strain_id is NULL for control experiments)
measurements: id, experiment_id, measured_at, plant_height_cm, chlorophyll_spad,
              shoot_dw_g, root_dw_g, yield_kg_per_ha, notes
```

---

## Assignments

### 1. Basic SELECT
- List all bacterial strains (all columns).
- List only the `strain_code` and `species` of strains that fix nitrogen (`nitrogen_fixing = 1`).
- List all field sites in Kenya.

### 2. Filtering & Sorting
- Find all experiments where the crop is `'wheat'`.
- Find all experiments with `treatment = 'control'` — these are the baseline measurements.
- List all final harvest measurements (those where `yield_kg_per_ha` is not null), sorted by yield descending.

### 3. Aggregations
- How many experiments are there in total?
- How many experiments per treatment type (`inoculated`, `control`, `chemical_fertilizer`)?
- What is the average final yield (`yield_kg_per_ha`) across all measurements that have one?

### 4. JOINs
- List every experiment with the site's country and the strain's species.
  - Control experiments have no strain — make sure they still appear (hint: `LEFT JOIN`).
- List all final measurements with: experiment ID, crop, treatment, site country, strain code, and yield.
- For each researcher, show how many experiments they are responsible for.

### 5. GROUP BY + HAVING
- What is the average yield per crop type?
- Which countries have more than 2 experimental sites?
- Find strains that have been used in more than 1 experiment.

---

See `solutions.sql` after attempting each section.
