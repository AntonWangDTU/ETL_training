"""
Assignment 1 - Extract
Complete the functions below, then run:
    uv run python 03_etl_pipeline/extract.py
"""

import json
import pandas as pd


def extract(path: str) -> pd.DataFrame:
    # TODO: read the CSV into a DataFrame
    df = pd.read_csv(path)
    # TODO: print shape and first 5 rows
    print(df.shape)
    # TODO: print column dtypes and null counts per column
    print(df.dtypes)
    print(df.isnull().count())
    # TODO: note anything that looks immediately wrong
    print(df)
    return df


def extract_strains(path: str) -> list[dict]:
    # TODO: read the JSON file and return as a list of dicts
    with open(path) as f:
        records = json.load(f)
    # TODO: print how many records, and the keys in the first record
    print(f"Amount of records: {len(records)}")
    print(records[0].keys())

    return records


if __name__ == "__main__":
    kenya = extract("kenya_measurements.csv")
    india = extract("india_measurements.csv")
    strains = extract_strains("new_strains.json")
