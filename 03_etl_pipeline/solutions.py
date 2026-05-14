"""
Module 03 — Solutions
"""

import json
import sqlite3
import pandas as pd


# ── Extract ────────────────────────────────────────────────────────────────


def extract_kenya(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"\n[Kenya] shape: {df.shape}")
    print(df.head())
    print("\ndtypes:\n", df.dtypes)
    print("\nnull counts:\n", df.isnull().sum())
    return df


def extract_india(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"\n[India] shape: {df.shape}")
    print(df.head())
    print("\ndtypes:\n", df.dtypes)
    print("\nnull counts:\n", df.isnull().sum())
    return df


def extract_strains(path: str) -> list[dict]:
    with open(path) as f:
        records = json.load(f)
    print(f"\n[Strains] {len(records)} records, keys: {list(records[0].keys())}")
    return records


# ── Helpers ────────────────────────────────────────────────────────────────


def get_valid_experiment_ids(db_path: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    ids = {row[0] for row in conn.execute("SELECT experiment_id FROM experiments")}
    conn.close()
    return ids


# ── Transform ──────────────────────────────────────────────────────────────


def clean_kenya(df: pd.DataFrame, db_path: str) -> pd.DataFrame:
    before = len(df)

    # Strip whitespace from column names and string columns
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip()

    # Convert date DD/MM/YYYY → YYYY-MM-DD
    df["measured_at"] = pd.to_datetime(
        df["measured_at"], format="%d/%m/%Y", errors="coerce"
    )
    df = df.dropna(subset=["measured_at"])
    df["measured_at"] = df["measured_at"].dt.strftime("%Y-%m-%d")

    # Height mm → cm
    df["plant_height_cm"] = df["plant_height_mm"] / 10
    df = df.drop(columns=["plant_height_mm"])

    # Remove duplicates
    df = df.drop_duplicates()

    # Drop rows with missing experiment_id
    df = df.dropna(subset=["experiment_id"])

    # Validate experiment IDs
    valid_ids = get_valid_experiment_ids(db_path)
    unknown = df[~df["experiment_id"].isin(valid_ids)]["experiment_id"].unique()
    if len(unknown):
        print(f"[Kenya] WARNING: unknown experiment IDs dropped: {list(unknown)}")
    df = df[df["experiment_id"].isin(valid_ids)]

    print(f"[Kenya] rows: {before} → {len(df)}")
    return df.reset_index(drop=True)


def clean_india(df: pd.DataFrame, db_path: str) -> pd.DataFrame:
    before = len(df)

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip()

    # Fix decimal commas in numeric-looking columns
    numeric_cols = [
        "plant_height_cm",
        "chlorophyll_spad",
        "shoot_dw_g",
        "root_dw_g",
        "yield_t_per_ha",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.replace('"', "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convert yield t/ha → kg/ha
    df["yield_kg_per_ha"] = df["yield_t_per_ha"] * 1000
    df = df.drop(columns=["yield_t_per_ha"])

    # Validate experiment IDs
    valid_ids = get_valid_experiment_ids(db_path)
    unknown = df[~df["experiment_id"].isin(valid_ids)]["experiment_id"].unique()
    if len(unknown):
        print(f"[India] WARNING: unknown experiment IDs dropped: {list(unknown)}")
    df = df[df["experiment_id"].isin(valid_ids)]

    print(f"[India] rows: {before} → {len(df)}")
    return df.reset_index(drop=True)


def clean_strains(records: list[dict], db_path: str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    existing = {row[0] for row in conn.execute("SELECT strain_code FROM strains")}
    conn.close()

    new_records = []
    for r in records:
        if r["strain_code"] in existing:
            print(f"[Strains] WARNING: {r['strain_code']} already exists — skipping")
        else:
            new_records.append(r)
    return new_records


# ── Load ───────────────────────────────────────────────────────────────────


def load_measurements(df: pd.DataFrame, db_path: str) -> None:
    conn = sqlite3.connect(db_path)

    # Build a map: experiment_id string → integer id
    exp_map = {
        row[0]: row[1]
        for row in conn.execute("SELECT experiment_id, id FROM experiments")
    }

    # Existing (exp integer id, measured_at) pairs
    existing = {
        (row[0], row[1])
        for row in conn.execute("SELECT experiment_id, measured_at FROM measurements")
    }

    inserted = skipped = 0
    for _, row in df.iterrows():
        exp_int_id = exp_map.get(row["experiment_id"])
        if exp_int_id is None:
            skipped += 1
            continue
        key = (exp_int_id, row["measured_at"])
        if key in existing:
            skipped += 1
            continue
        conn.execute(
            """
            INSERT INTO measurements
              (experiment_id, measured_at, plant_height_cm, chlorophyll_spad,
               shoot_dw_g, root_dw_g, yield_kg_per_ha, notes)
            VALUES (?,?,?,?,?,?,?,?)
        """,
            (
                exp_int_id,
                row["measured_at"],
                row.get("plant_height_cm"),
                row.get("chlorophyll_spad"),
                row.get("shoot_dw_g"),
                row.get("root_dw_g"),
                row.get("yield_kg_per_ha"),
                row.get("notes"),
            ),
        )
        inserted += 1
        existing.add(key)

    conn.commit()
    conn.close()
    print(f"[Load measurements] inserted: {inserted}, skipped: {skipped}")


def load_strains(records: list[dict], db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    inserted = 0
    for r in records:
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO strains
                  (strain_code, species, isolation_source, origin_country, nitrogen_fixing)
                VALUES (?,?,?,?,?)
            """,
                (
                    r["strain_code"],
                    r["species"],
                    r.get("isolation_source"),
                    r.get("origin_country"),
                    r.get("nitrogen_fixing", 0),
                ),
            )
            if conn.execute("SELECT changes()").fetchone()[0]:
                inserted += 1
        except Exception as e:
            print(f"[Strains] error inserting {r['strain_code']}: {e}")
    conn.commit()
    conn.close()
    print(f"[Load strains] inserted: {inserted}")


# ── Run ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    DB = "ibis.db"
    print("=== EXTRACT ===")
    kenya_raw = extract_kenya("03_etl_pipeline/kenya_measurements.csv")
    india_raw = extract_india("03_etl_pipeline/india_measurements.csv")
    strain_raw = extract_strains("03_etl_pipeline/new_strains.json")

    print("\n=== TRANSFORM ===")
    kenya_clean = clean_kenya(kenya_raw, DB)
    india_clean = clean_india(india_raw, DB)
    strain_clean = clean_strains(strain_raw, DB)

    print("\n=== LOAD ===")
    load_measurements(kenya_clean, DB)
    load_measurements(india_clean, DB)
    load_strains(strain_clean, DB)
    print("\nDone.")
