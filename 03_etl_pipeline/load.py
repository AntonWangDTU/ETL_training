"""
Assignment 3 - Load
Complete the functions below, then run:
    uv run python 03_etl_pipeline/load.py
"""

import sqlite3
import pandas as pd
from extract import extract_kenya, extract_india, extract_strains
from transform import clean_kenya, clean_india, clean_strains


def load_measurements(df: pd.DataFrame, db_path: str) -> None:
    """
    Insert cleaned measurement rows into ibis.db.

    Idempotency rule: skip rows where the same experiment_id + measured_at
    already exists in the measurements table.

    Steps to implement:
    1. Connect to ibis.db
    2. Fetch existing (experiment_id text, measured_at text) pairs
       — join measurements with experiments to get experiment_id string
    3. For each row in df, look up the integer experiments.id for its experiment_id
    4. Skip if (experiment id integer, measured_at) already in measurements
    5. Insert new rows
    6. Print inserted vs skipped counts
    """
    # TODO
    pass


def load_strains(records: list[dict], db_path: str) -> None:
    """
    Insert new strains into ibis.db.
    Records have already been deduplicated by clean_strains,
    but double-check with INSERT OR IGNORE for safety.
    Print how many were inserted.
    """
    # TODO
    pass


if __name__ == "__main__":
    DB = "ibis.db"
    kenya_clean = clean_kenya(
        extract_kenya("03_etl_pipeline/kenya_measurements.csv"), DB
    )
    india_clean = clean_india(
        extract_india("03_etl_pipeline/india_measurements.csv"), DB
    )
    strain_clean = clean_strains(
        extract_strains("03_etl_pipeline/new_strains.json"), DB
    )

    load_measurements(kenya_clean, DB)
    load_measurements(india_clean, DB)
    load_strains(strain_clean, DB)
