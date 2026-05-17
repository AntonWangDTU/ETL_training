# Module 05 — Apache Airflow

You've written a working ETL pipeline. Now the biology team wants it to run automatically every night, retry on failure, and be visible to everyone on the team.

That's what Airflow does.

---

## Scenario

The IBIS programme receives new field measurement files daily from partners. Your job is to convert the manual pipeline from module 03 into a scheduled, monitored Airflow DAG that:

1. Extracts the latest incoming CSV file
2. Transforms and validates it (same rules as module 03)
3. Loads clean rows into `ibis.db`, skipping duplicates
4. Retries automatically if any step fails

---

## Setup

Install Airflow and pandas (if not already installed):

```bash
pip install "apache-airflow==2.9.1" pandas
# or with uv:
uv pip install "apache-airflow==2.9.1" pandas
```

Initialise the Airflow metadata database and create an admin user:

```bash
export AIRFLOW_HOME=~/airflow
airflow db migrate
airflow users create \
    --username admin --password admin \
    --firstname A --lastname B \
    --role Admin --email admin@example.com
```

Copy your DAG into Airflow's DAG folder:

```bash
cp 05_airflow/etl_dag.py ~/airflow/dags/
```

Start the scheduler and web server (two separate terminals):

```bash
airflow scheduler
airflow webserver --port 8080
```

Open `http://localhost:8080` and log in with `admin / admin`.

---

## Sample data

Run the helper script to create a sample incoming file:

```bash
uv run python 05_airflow/make_sample_data.py
```

This creates `05_airflow/incoming/measurements_YYYY_MM_DD.csv`.

---

## Assignment 1 — Your first DAG

Open `etl_dag.py`. Fill in the TODOs in order:

1. Import `DAG` and `PythonOperator`
2. Implement `extract()` — load the latest CSV from `incoming/`, print a summary, push the file path to XCom
3. Implement `transform()` — pull the path from XCom, clean the data, save `cleaned.csv`, push its path
4. Implement `load()` — pull the cleaned path, insert new rows into `ibis.db`, report inserted vs skipped
5. Define `default_args` with `retries=2` and `retry_delay=5 minutes`
6. Define the DAG with `schedule_interval='0 1 * * *'` (run at 01:00 every day)
7. Define three `PythonOperator` tasks
8. Set dependencies: `extract >> transform >> load`

---

## Assignment 2 — Test it

Test the DAG for a specific date without waiting for the scheduler:

```bash
airflow dags test etl_pipeline 2024-01-01
```

You should see each task log its output. Check the web UI — does the task graph look right?

---

## Assignment 3 — Break it on purpose

1. Delete `incoming/cleaned.csv` while the DAG is mid-run. Does it retry?
2. Put an invalid row in the incoming CSV (bad date format). What happens?
3. Set `retries=0`. Re-run. What changes in the web UI?

---

## Assignment 4 — Scheduling

Change the schedule to run every Monday at 06:00. Use a cron expression (not `@weekly`).

Then change it to run every 3 hours. Verify your cron expression at [crontab.guru](https://crontab.guru).

---

## Running the solution

```bash
cp 05_airflow/solution_dag.py ~/airflow/dags/solution_dag.py
airflow dags test solution_etl_pipeline 2024-01-01
```

---

See `solution_dag.py` once you've attempted the assignments.
