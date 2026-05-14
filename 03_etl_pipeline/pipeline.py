"""
Full pipeline — chains extract → transform → load.
Run after completing all three assignment files:

    uv run python 03_etl_pipeline/pipeline.py
"""
from extract import extract_kenya, extract_india, extract_strains
from transform import clean_kenya, clean_india, clean_strains
from load import load_measurements, load_strains

DB = "ibis.db"

print("=== EXTRACT ===")
kenya_raw  = extract_kenya("03_etl_pipeline/kenya_measurements.csv")
india_raw  = extract_india("03_etl_pipeline/india_measurements.csv")
strain_raw = extract_strains("03_etl_pipeline/new_strains.json")

print("\n=== TRANSFORM ===")
kenya_clean  = clean_kenya(kenya_raw, DB)
india_clean  = clean_india(india_raw, DB)
strain_clean = clean_strains(strain_raw, DB)

print("\n=== LOAD ===")
load_measurements(kenya_clean, DB)
load_measurements(india_clean, DB)
load_strains(strain_clean, DB)

print("\nPipeline complete.")
