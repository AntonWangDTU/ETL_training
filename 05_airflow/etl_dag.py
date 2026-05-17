"""
Module 05 — Airflow ETL DAG
Assignment: Convert the module 03 pipeline into a scheduled Airflow DAG.

Fill in each TODO in order. Do not change function signatures.

Test your DAG without the scheduler:
    airflow dags test etl_pipeline 2024-01-01

Test a single task:
    airflow tasks test etl_pipeline extract 2024-01-01

See TUTORIAL.md for all the concepts you need.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# TODO 1 ── imports
# Uncomment these once you're ready to define the DAG:
# from airflow import DAG
# from airflow.operators.python import PythonOperator


# ── paths ─────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
DB   = BASE.parent / "01_sql_basics" / "ibis.db"
DATA = BASE / "incoming"


# ── task functions ─────────────────────────────────────────────────────────────

def extract(**context):
    """
    TODO 2 ── Extract
    1. Make sure DATA/ exists (DATA.mkdir(exist_ok=True))
    2. Find all CSV files in DATA/ using DATA.glob("*.csv")
       Raise FileNotFoundError if there are none
    3. Pick the last file (sorted alphabetically, last = most recent by name)
    4. Load it into a DataFrame with pd.read_csv()
    5. Print: file name, shape, column names, null counts per column
    6. Push the file path string to XCom with key='raw_path'
       context['ti'].xcom_push(key='raw_path', value=str(path))
    """
    pass


def transform(**context):
    """
    TODO 3 ── Transform
    1. Pull the raw file path from XCom:
       path = context['ti'].xcom_pull(task_ids='extract', key='raw_path')
    2. Load the CSV into a DataFrame
    3. Strip whitespace from all column names
    4. Convert 'measured_at' from DD/MM/YYYY to YYYY-MM-DD
       (use pd.to_datetime with format='%d/%m/%Y', then .dt.strftime('%Y-%m-%d'))
    5. Drop rows where 'experiment_id' is missing — print how many were dropped
    6. Validate experiment_ids against ibis.db:
       - Query: SELECT experiment_id FROM experiments
       - Flag rows with unknown IDs (print a WARNING), then drop them
    7. Save the cleaned DataFrame to DATA / "cleaned.csv" (no index)
    8. Push the cleaned file path to XCom with key='cleaned_path'
    """
    pass


def load(**context):
    """
    TODO 4 ── Load
    1. Pull cleaned_path from XCom:
       path = context['ti'].xcom_pull(task_ids='transform', key='cleaned_path')
    2. Load the cleaned CSV into a DataFrame
    3. Connect to ibis.db
    4. Build a set of existing keys:
       SELECT experiment_id || '|' || measured_at FROM measurements
    5. Filter the DataFrame to only new rows (not already in the set)
    6. Insert new rows with df.to_sql('measurements', conn, if_exists='append', index=False)
    7. Commit and close the connection
    8. Print: "Inserted X rows, skipped Y duplicates"
    """
    pass


# ── DAG definition ─────────────────────────────────────────────────────────────

# TODO 5 ── default_args
# Define a dict called default_args with:
#   - 'owner': your name or 'ibis_team'
#   - 'retries': 2
#   - 'retry_delay': timedelta(minutes=5)

# default_args = {
#     ...
# }


# TODO 6 ── DAG
# Define a DAG with:
#   dag_id='etl_pipeline'
#   default_args=default_args
#   start_date=datetime(2024, 1, 1)
#   schedule_interval='0 1 * * *'   ← 01:00 every day
#   catchup=False

# with DAG(...) as dag:

#     # TODO 7 ── PythonOperator tasks
#     # Define t_extract, t_transform, t_load
#     # Each uses python_callable= pointing to the function above
#     # task_id should match the function name: 'extract', 'transform', 'load'

#     t_extract   = PythonOperator(...)
#     t_transform = PythonOperator(...)
#     t_load      = PythonOperator(...)

#     # TODO 8 ── dependencies
#     # extract must finish before transform; transform before load
#     ...
