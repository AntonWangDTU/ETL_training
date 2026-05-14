# Module 02 — SQL Intermediate

Same `ibis.db`. Run setup if needed:
```bash
uv run python 01_sql_basics/setup_db.py
```

---

## Assignments

### 1. CTEs — answering real research questions

- **Yield improvement**: Write a CTE that calculates the average final yield per experiment,
  then compare each inoculated experiment's yield against the control yield from the **same site and crop**.
  Show: site, crop, strain, inoculated yield, control yield, and the improvement in %.

- **Best-performing strains**: Using a CTE, rank strains by their average yield improvement
  over the control across all sites. Which strain performs best?

### 2. Window Functions

- For each country, rank experiments by final yield (highest = rank 1).
  Show: country, experiment_id, strain_code, yield, rank.

- For each experiment that has 2 measurements (mid-season + harvest), calculate the
  growth in plant height between the two measurements using `LAG`.

- Show each measurement's yield as a percentage of the maximum yield recorded
  for that same crop, using `MAX() OVER`.

### 3. Subqueries

- Find all strains that have **never** been tested in a tropical climate zone
  (use a subquery against the `sites` table).

- Find experiments where the final yield is **below** the average yield for that crop.

### 4. Data Quality Checks
These are exactly what you'd run before loading new partner data into the database.

Write queries that answer:
- Are there any experiments referencing a `site_id` or `strain_id` that doesn't exist?
- Are there any measurements with biologically impossible values?
  (e.g. `plant_height_cm > 300`, `chlorophyll_spad > 80`, `yield_kg_per_ha > 15000`)
- Which experiments have measurements recorded but no final yield (`yield_kg_per_ha IS NULL`
  for all their measurements)?
- Are there any duplicate `experiment_id` values?

---

See `solutions.sql` after attempting.
