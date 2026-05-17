"""
Solution — Module 05 Airflow ETL DAG

Test with:
    cp 05_airflow/solution_dag.py ~/airflow/dags/
    airflow dags test solution_etl_pipeline 2024-01-01
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

BASE = Path(__file__).parent
DB   = BASE.parent / "01_sql_basics" / "ibis.db"
DATA = BASE / "incoming"


def extract(**context):
    DATA.mkdir(exist_ok=True)
    files = sorted(DATA.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {DATA}")

    path = files[-1]
    df = pd.read_csv(path)

    print(f"Loaded:   {path.name}")
    print(f"Shape:    {df.shape}")
    print(f"Columns:  {list(df.columns)}")
    print(f"Nulls:\n{df.isnull().sum()}")

    context['ti'].xcom_push(key='raw_path', value=str(path))


def transform(**context):
    raw_path = context['ti'].xcom_pull(task_ids='extract', key='raw_path')
    df = pd.read_csv(raw_path)

    # clean column names
    df.columns = df.columns.str.strip()

    # fix date format
    df['measured_at'] = (
        pd.to_datetime(df['measured_at'], format='%d/%m/%Y')
        .dt.strftime('%Y-%m-%d')
    )

    # drop missing experiment_ids
    before = len(df)
    df = df.dropna(subset=['experiment_id'])
    dropped = before - len(df)
    if dropped:
        print(f"Dropped {dropped} rows with missing experiment_id")

    # validate experiment_ids against the database
    conn = sqlite3.connect(str(DB))
    valid_ids = {
        row[0]
        for row in conn.execute("SELECT experiment_id FROM experiments").fetchall()
    }
    conn.close()

    unknown = df[~df['experiment_id'].isin(valid_ids)]
    if not unknown.empty:
        print(
            f"WARNING: {len(unknown)} rows reference unknown experiment_ids: "
            f"{sorted(unknown['experiment_id'].unique())}"
        )
    df = df[df['experiment_id'].isin(valid_ids)]

    cleaned_path = DATA / "cleaned.csv"
    df.to_csv(cleaned_path, index=False)
    print(f"Saved {len(df)} cleaned rows → {cleaned_path}")

    context['ti'].xcom_push(key='cleaned_path', value=str(cleaned_path))


def load(**context):
    cleaned_path = context['ti'].xcom_pull(task_ids='transform', key='cleaned_path')
    df = pd.read_csv(cleaned_path)

    conn = sqlite3.connect(str(DB))

    existing = {
        row[0]
        for row in conn.execute(
            "SELECT experiment_id || '|' || measured_at FROM measurements"
        ).fetchall()
    }

    key = df['experiment_id'].astype(str) + '|' + df['measured_at']
    new_rows = df[~key.isin(existing)]
    skipped = len(df) - len(new_rows)

    new_rows.to_sql('measurements', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

    print(f"Inserted {len(new_rows)} rows, skipped {skipped} duplicates")


default_args = {
    'owner': 'ibis_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='solution_etl_pipeline',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 1 * * *',
    catchup=False,
) as dag:

    t_extract = PythonOperator(
        task_id='extract',
        python_callable=extract,
    )

    t_transform = PythonOperator(
        task_id='transform',
        python_callable=transform,
    )

    t_load = PythonOperator(
        task_id='load',
        python_callable=load,
    )

    t_extract >> t_transform >> t_load
