# Module 04 — Full Pipeline (Mini Project)

This is the capstone. No scaffolding — you build it from scratch.

## Scenario

A new partner (Brazil, EMBRAPA) has sent two files:

- `brazil_experiments.csv` — new experiments not yet in `ibis.db`
- `brazil_measurements.csv` — measurements for those experiments

Your job is to write a complete pipeline (`pipeline.py`) that:

1. **Validates** the incoming experiments against what's already in the DB
   - Check that all referenced `site_code` and `strain_code` values exist
   - Skip experiments whose `experiment_id` already exists (idempotent)

2. **Inserts** new experiments into `ibis.db`

3. **Cleans** the measurements file
   - Dates are in DD/MM/YYYY format
   - One column is named `plant_ht_cm` instead of `plant_height_cm`
   - There are a few out-of-range values (`chlorophyll_spad > 80`) — flag and drop them

4. **Loads** cleaned measurements, skipping any that already exist

5. **Queries and reports**: after loading, print a summary table showing
   for each new experiment: strain code, site, crop, treatment, and final yield.
   Compare inoculated vs control yield for the same site/crop if both are present.

## Files provided

- `brazil_experiments.csv`
- `brazil_measurements.csv`

## Deliverable

A single `pipeline.py` that runs end-to-end:

```bash
uv run python 04_full_pipeline/pipeline.py
```

And prints a clean summary at the end. No crashes on re-run (idempotent).

---

See `solution.py` once you've attempted it.
