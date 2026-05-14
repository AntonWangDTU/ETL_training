# Tutorial — ETL Pipeline

This explains the Extract → Transform → Load pattern and the Python/pandas tools you'll use. Examples are generic — not the assignment data. Read this, then open `extract.py`, `transform.py`, and `load.py`.

---

## What is ETL?

ETL stands for **Extract, Transform, Load**. It's the standard pattern for moving data from external sources into a database:

```
Raw files (CSV, JSON, API)
        │
    EXTRACT          ← read and observe; don't fix yet
        │
    TRANSFORM        ← clean, standardise, validate
        │
      LOAD           ← insert into the database
        │
    Database
```

**Why keep these steps separate?** Each step has a different failure mode. Extraction errors are about reading the file. Transform errors are about data quality. Load errors are about database constraints. Keeping them separate makes debugging much easier.

---

## Extract — reading and observing

The goal of extraction is **observation, not fixing**. You want to understand the shape of the data before touching it.

### Reading a CSV with pandas

```python
import pandas as pd

df = pd.read_csv('data.csv')
```

Useful things to check immediately after loading:

```python
df.shape          # (rows, columns)
df.columns        # column names
df.dtypes         # data types — is a date column read as str? a number as object?
df.isnull().sum() # null count per column
df.head()         # first few rows
```

### Reading a JSON file

```python
import json

with open('data.json') as f:
    records = json.load(f)   # returns a list of dicts (usually)
```

### Flags to raise during extraction

- Columns with unexpected dtypes (e.g. a numeric column has dtype `object` — likely has non-numeric values in it)
- High null counts in columns that should be mandatory
- Unexpected column names (extra spaces, wrong case)
- Suspicious value ranges visible in `.describe()`

---

## Transform — cleaning and standardising

Once you know what's wrong, fix it systematically. Write one function per source file — they'll have different problems.

### Stripping whitespace from column names

```python
df.columns = df.columns.str.strip()
```

### Stripping whitespace from string values

```python
df = df.apply(lambda col: col.str.strip() if col.dtype == 'object' else col)
```

### Converting date formats

Partner data often uses local date formats (`DD/MM/YYYY`). Databases expect `YYYY-MM-DD`.

```python
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
```

`pd.to_datetime` is strict about the format. If one row doesn't match, it raises an error — which is what you want during development so bad data doesn't slip through silently.

### Fixing decimal separators

Some locales use `,` as the decimal separator (`42,5` instead of `42.5`):

```python
df['value'] = df['value'].str.replace(',', '.').astype(float)
```

### Unit conversion and renaming

```python
df['height_cm'] = df['height_mm'] / 10
df = df.drop(columns=['height_mm'])
# or in one step:
df = df.rename(columns={'height_mm': 'height_cm'})
df['height_cm'] = df['height_cm'] / 10
```

### Removing duplicates

```python
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicate rows")
```

### Dropping rows with missing mandatory values

```python
before = len(df)
df = df.dropna(subset=['experiment_id'])
print(f"Dropped {before - len(df)} rows with missing experiment_id")
```

### Validating foreign keys against the database

Before loading, check that every ID in the file actually exists in the database:

```python
import sqlite3

conn = sqlite3.connect('ibis.db')
valid_ids = set(
    row[0] for row in conn.execute("SELECT id FROM experiments").fetchall()
)

unknown = df[~df['experiment_id'].isin(valid_ids)]
if not unknown.empty:
    print(f"WARNING: {len(unknown)} rows reference unknown experiment IDs:")
    print(unknown['experiment_id'].unique())

df = df[df['experiment_id'].isin(valid_ids)]
```

The `~` operator inverts a boolean Series — `~df['col'].isin(s)` means "not in s".

---

## Load — inserting into the database

### Basic insert with pandas

```python
df.to_sql('measurements', conn, if_exists='append', index=False)
```

`if_exists='append'` adds rows to an existing table. Never use `'replace'` on a production table — it drops and recreates the whole table.

### Idempotency — safe to run twice

A pipeline is **idempotent** if running it a second time produces the same result as running it once. This matters because pipelines fail and get re-run.

The standard pattern: check what already exists before inserting.

```python
existing = set(
    conn.execute(
        "SELECT experiment_id || '|' || measured_at FROM measurements"
    ).fetchall()
)

new_rows = df[
    ~(df['experiment_id'].astype(str) + '|' + df['measured_at']).isin(existing)
]

new_rows.to_sql('measurements', conn, if_exists='append', index=False)
print(f"Inserted {len(new_rows)}, skipped {len(df) - len(new_rows)}")
```

Or use `INSERT OR IGNORE` in SQLite directly:

```python
for _, row in df.iterrows():
    conn.execute("""
        INSERT OR IGNORE INTO measurements (experiment_id, measured_at, ...)
        VALUES (?, ?, ...)
    """, (row['experiment_id'], row['measured_at'], ...))
conn.commit()
```

`INSERT OR IGNORE` requires a `UNIQUE` constraint on the columns you're using as the natural key.

### Logging what happened

Good pipelines report what they did:

```python
print(f"Kenya file:  {len(kenya_clean)} rows inserted, {kenya_skipped} skipped")
print(f"India file:  {len(india_clean)} rows inserted, {india_skipped} skipped")
print(f"New strains: {len(new_strains)} inserted")
```

---

## Error handling philosophy

During development: **let it crash**. A visible error with a traceback is easier to fix than silently swallowed bad data.

In production: catch specific errors, log them, and decide whether to skip the row or abort the pipeline.

---

## Running the pipeline

Each step (extract, transform, load) can be run and tested independently. `pipeline.py` ties them together in order:

```python
# pipeline.py
from extract   import load_kenya, load_india, load_strains
from transform import clean_kenya, clean_india, clean_strains
from load      import load_measurements, load_new_strains

kenya_raw  = load_kenya('kenya_measurements.csv')
kenya_clean = clean_kenya(kenya_raw)
load_measurements(kenya_clean, 'ibis.db')
```

Now open `extract.py` and start there.
