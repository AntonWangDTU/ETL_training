"""
Assignment 2 - Transform
Complete the functions below, then run:
    uv run python 03_etl_pipeline/transform.py
"""

import sqlite3
import pandas as pd
from extract import extract, extract_strains


def get_valid_experiment_ids(db_path: str) -> set[str]:
    """Helper: fetch all known experiment_id values from ibis.db."""
    conn = sqlite3.connect(db_path)
    ids = {row[0] for row in conn.execute("SELECT experiment_id FROM experiments")}
    conn.close()
    return ids


def clean_kenya(df: pd.DataFrame, db_path: str) -> pd.DataFrame:
    # TODO: strip whitespace from all column names and string columns
    # TODO: convert measured_at from DD/MM/YYYY to YYYY-MM-DD
    # TODO: convert plant_height_mm to plant_height_cm (divide by 10), rename column
    # TODO: drop duplicate rows
    # TODO: drop rows where experiment_id is null
    # TODO: check all experiment_ids exist in ibis.db — print a warning for unknowns, then drop them
    # TODO: print before/after row count
    pass


def clean_india(df: pd.DataFrame, db_path: str) -> pd.DataFrame:
    # TODO: strip whitespace from column names and string values
    # TODO: fix decimal commas in numeric columns ("42,5" -> 42.5)
    # TODO: convert yield_t_per_ha -> yield_kg_per_ha (* 1000), rename column
    # TODO: validate experiment_ids against ibis.db, warn and drop unknowns
    # TODO: print before/after row count
    pass


def clean_strains(records: list[dict], db_path: str) -> list[dict]:
    # TODO: fetch existing strain_codes from ibis.db
    # TODO: for each record, if strain_code already exists print a warning and skip it
    # TODO: return only new strains
    pass


if __name__ == "__main__":
    DB = "ibis.db"
    kenya_raw = extract("kenya_measurements.csv")
    india_raw = extract("india_measurements.csv")
    strain_raw = extract_strains("03_etl_pipeline/new_strains.json")

    kenya_clean = clean_kenya(kenya_raw, DB)
    india_clean = clean_india(india_raw, DB)
    strain_clean = clean_strains(strain_raw, DB)

    print("\nKenya clean sample:")
    print(kenya_clean.head())
    print("\nIndia clean sample:")
    print(india_clean.head())
    print("\nNew strains to insert:", strain_clean)
