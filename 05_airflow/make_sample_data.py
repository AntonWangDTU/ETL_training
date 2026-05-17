"""
Generates a sample incoming CSV in 05_airflow/incoming/.

The file mimics what a partner would send:
  - dates in DD/MM/YYYY format (needs fixing in transform)
  - one row with a missing experiment_id (should be dropped)
  - one row with an experiment_id that doesn't exist in ibis.db (should be flagged)
  - otherwise clean data

Run from the repo root:
    uv run python 05_airflow/make_sample_data.py
"""

import sqlite3
import csv
import random
from datetime import date, timedelta
from pathlib import Path

BASE     = Path(__file__).parent
DB       = BASE.parent / "01_sql_basics" / "ibis.db"
INCOMING = BASE / "incoming"

INCOMING.mkdir(exist_ok=True)

# ── fetch real experiment_ids from ibis.db ─────────────────────────────────────
conn = sqlite3.connect(str(DB))
real_ids = [
    row[0]
    for row in conn.execute("SELECT experiment_id FROM experiments LIMIT 10").fetchall()
]
conn.close()

if not real_ids:
    print("No experiments found in ibis.db. Have you completed module 01 setup?")
    raise SystemExit(1)

# ── build rows ─────────────────────────────────────────────────────────────────
random.seed(42)

rows = []

# 8 clean rows with real experiment_ids
start = date(2024, 1, 1)
for i in range(8):
    d = start + timedelta(days=i)
    rows.append({
        "experiment_id":    random.choice(real_ids),
        "measured_at":      d.strftime("%d/%m/%Y"),       # DD/MM/YYYY intentionally
        "plant_height_cm":  round(random.uniform(30, 90), 1),
        "chlorophyll_spad": round(random.uniform(35, 65), 1),
        "yield_kg_per_ha":  round(random.uniform(1000, 4000), 0),
    })

# 1 row with missing experiment_id
rows.append({
    "experiment_id":    "",
    "measured_at":      "09/01/2024",
    "plant_height_cm":  55.0,
    "chlorophyll_spad": 48.2,
    "yield_kg_per_ha":  2100.0,
})

# 1 row with a fake experiment_id that doesn't exist
rows.append({
    "experiment_id":    "FAKE_EXP_999",
    "measured_at":      "10/01/2024",
    "plant_height_cm":  62.0,
    "chlorophyll_spad": 52.0,
    "yield_kg_per_ha":  2800.0,
})

# ── write CSV ──────────────────────────────────────────────────────────────────
filename = INCOMING / "measurements_2024_01_01.csv"
fieldnames = ["experiment_id", "measured_at", "plant_height_cm", "chlorophyll_spad", "yield_kg_per_ha"]

with open(filename, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Created {filename} ({len(rows)} rows)")
print(f"  - {len(rows) - 2} clean rows with real experiment_ids")
print(f"  - 1 row with missing experiment_id (should be dropped in transform)")
print(f"  - 1 row with FAKE_EXP_999 (should be flagged and dropped in transform)")
