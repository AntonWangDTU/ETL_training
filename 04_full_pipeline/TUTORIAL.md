# Tutorial — Full Pipeline

This module has no scaffolding. You design and build the whole thing. This tutorial is a reference for the patterns and decisions that come up when writing a pipeline from scratch.

---

## Before writing any code — read the data

Open both CSV files and look at them. Ask:

- What columns are present? Do they match the database schema exactly?
- Are there any immediately obvious formatting differences (date formats, units, column name mismatches)?
- Which columns in the database are mandatory? Which can be NULL?

This 2-minute read saves you from writing transforms that don't match what's actually in the file.

---

## Design before coding

For a pipeline this size, sketch the steps before writing any functions:

```
1. Load experiments file
2. Validate: do all site_codes and strain_codes exist in ibis.db?
3. Filter: skip experiments already in the DB
4. Insert new experiments
5. Load measurements file
6. Clean: fix date format, rename columns, drop out-of-range rows
7. Validate: all experiment_ids must now exist (we just inserted them)
8. Insert measurements, skip duplicates
9. Query and print summary report
```

Write this as a comment at the top of `pipeline.py` before you write a single function. Then implement each step in order.

---

## Connecting experiments to measurements

The experiments must be inserted **before** measurements, because measurements reference experiment IDs. If you try to insert measurements first, the foreign key validation will fail.

After inserting experiments, the IDs you need for measurement validation are now in the database — so the same `validate_foreign_keys` pattern from Module 03 works cleanly.

---

## Inserting experiments (a new table)

Module 03 covered inserting measurements. Experiments have a similar pattern, but the natural key is different — `experiment_id` is the unique business identifier. Use that for your duplicate check:

```python
existing = set(
    row[0] for row in conn.execute("SELECT experiment_id FROM experiments")
)
new = df[~df['experiment_id'].isin(existing)]
```

You'll also need to look up the integer `site_id` and `strain_id` from the codes in the CSV, since the database stores foreign key integers, not codes:

```python
site_map = dict(conn.execute("SELECT site_code, id FROM sites"))
df['site_id'] = df['site_code'].map(site_map)
```

If `site_code` doesn't exist in the map, `.map()` returns NaN — that's a validation failure.

---

## Flagging vs dropping bad rows

The assignment asks you to **flag and drop** out-of-range values, not silently drop them. The difference:

```python
# silent drop — don't do this
df = df[df['chlorophyll_spad'] <= 80]

# flag then drop
bad = df[df['chlorophyll_spad'] > 80]
if not bad.empty:
    print(f"WARNING: dropping {len(bad)} rows with chlorophyll_spad > 80:")
    print(bad[['experiment_id', 'measured_at', 'chlorophyll_spad']])
df = df[df['chlorophyll_spad'] <= 80]
```

Always tell the user what you discarded and why.

---

## The summary report

The final step queries the database and prints a comparison table. Think about what SQL from Module 02 is relevant here — comparing inoculated vs control yields for the same site and crop is exactly the kind of query you practised there.

You can run a query and print it directly from Python:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('ibis.db')
df = pd.read_sql_query("SELECT ...", conn)
print(df.to_string(index=False))
```

`pd.read_sql_query` is the easiest way to get query results into a DataFrame for formatting.

---

## Making the pipeline re-runnable

Test this explicitly: run `pipeline.py` twice in a row. The second run should:
- Print "0 new experiments inserted, N skipped"
- Print "0 new measurements inserted, N skipped"
- Still print the same summary report

If the second run crashes or inserts duplicates, your idempotency logic has a gap.

---

## Suggested file structure

You don't have to split into separate files like Module 03 — a single well-organised `pipeline.py` is fine for this scope. Use functions to keep things testable:

```python
def load_and_validate_experiments(path, conn): ...
def insert_experiments(df, conn): ...
def load_and_clean_measurements(path, conn): ...
def insert_measurements(df, conn): ...
def print_summary(conn): ...

if __name__ == '__main__':
    conn = sqlite3.connect('../ibis.db')
    df_exp = load_and_validate_experiments('brazil_experiments.csv', conn)
    insert_experiments(df_exp, conn)
    df_meas = load_and_clean_measurements('brazil_measurements.csv', conn)
    insert_measurements(df_meas, conn)
    print_summary(conn)
    conn.close()
```

---

Now open `brazil_experiments.csv` and `brazil_measurements.csv`, read the data, sketch your plan, and start coding.
