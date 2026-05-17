# Tutorial — Apache Airflow

This explains the concepts you need for the assignments. Examples use a generic `orders` / `reports` scenario — not the assignment data. Read top to bottom, then open `etl_dag.py`.

---

## Why Airflow?

You can run a Python script on a cron job. That works until:

- The script fails at 3am and nobody notices until Monday
- Step 2 crashes but step 3 runs anyway, loading bad data
- You need to re-run just the failed step, not the whole pipeline
- A new team member wants to know what ran last week and why it failed

Airflow solves all of this. It gives you:

- **Scheduling** — run pipelines on a cron schedule
- **Dependencies** — tasks run in order; a task won't start if its upstream task failed
- **Retries** — failed tasks retry automatically, with configurable delays
- **Visibility** — a web UI shows every run, every task, every log line

---

## Core concepts

### DAG

A **DAG** (Directed Acyclic Graph) is the pipeline. It defines:

- Which tasks exist
- In what order they run
- When to run (the schedule)

Think of it as the wiring diagram.

```python
from airflow import DAG
from datetime import datetime

with DAG(
    dag_id='my_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False,
) as dag:
    ...  # tasks go here
```

`catchup=False` means Airflow won't try to run the pipeline for every past day since `start_date`. Almost always what you want.

### Task

A **task** is one step in the pipeline. Tasks are defined inside a DAG.

### Operator

An **operator** is the type of a task. The most common:

| Operator | Does |
|----------|------|
| `PythonOperator` | Calls a Python function |
| `BashOperator` | Runs a shell command |
| `EmailOperator` | Sends an email |

For ETL pipelines you'll use `PythonOperator` almost exclusively.

---

## PythonOperator

Wraps a Python function as a task.

```python
from airflow.operators.python import PythonOperator

def say_hello():
    print("hello from a task")

hello_task = PythonOperator(
    task_id='say_hello',
    python_callable=say_hello,
)
```

The function must be defined **before** the task that uses it.

### Passing context

Every callable receives `**context` if you ask for it. Context contains metadata about the current run:

```python
def my_task(**context):
    run_date = context['ds']           # '2024-01-15' — the logical date of this run
    ti       = context['ti']           # TaskInstance — used for XComs (see below)
    print(f"Running for date {run_date}")
```

---

## Task dependencies

Set the order tasks run with `>>`:

```python
extract_task >> transform_task >> load_task
```

This means: run `extract_task`, then `transform_task`, then `load_task`. If any task fails, the ones downstream of it are skipped.

Multiple dependencies:

```python
[extract_a, extract_b] >> transform_task >> load_task
```

Both `extract_a` and `extract_b` must succeed before `transform_task` starts.

---

## Scheduling — cron expressions

The `schedule_interval` accepts a cron expression or a preset:

| Preset | Meaning |
|--------|---------|
| `'@hourly'` | Every hour |
| `'@daily'` | Once a day at midnight |
| `'@weekly'` | Once a week on Sunday |
| `'@monthly'` | First of the month |

Cron expressions give you full control:

```
┌─── minute (0–59)
│  ┌─── hour (0–23)
│  │  ┌─── day of month (1–31)
│  │  │  ┌─── month (1–12)
│  │  │  │  ┌─── day of week (0–6, Sunday=0)
│  │  │  │  │
*  *  *  *  *
```

Examples:

```python
schedule_interval='0 1 * * *'    # 01:00 every day
schedule_interval='30 6 * * 1'   # 06:30 every Monday
schedule_interval='0 */3 * * *'  # every 3 hours
schedule_interval='0 0 1 * *'    # midnight on the 1st of each month
```

Use [crontab.guru](https://crontab.guru) to verify expressions.

---

## XComs — passing data between tasks

Tasks run in separate processes. To pass a value from one task to the next, use **XComs** (cross-communications).

### Push a value

```python
def extract(**context):
    path = '/data/incoming/file.csv'
    # ... do work ...
    context['ti'].xcom_push(key='raw_path', value=path)
```

### Pull a value

```python
def transform(**context):
    path = context['ti'].xcom_pull(task_ids='extract', key='raw_path')
    df = pd.read_csv(path)
    # ...
```

`task_ids` is the `task_id` of the task that pushed the value. `key` must match what was pushed.

XComs are stored in the Airflow metadata database and visible in the web UI under each task run.

**Important:** XComs are for small values — file paths, counts, status strings. Don't push entire DataFrames through XComs. Instead push a file path and read the file in the next task.

---

## Retries

Define retry behaviour in `default_args`:

```python
from datetime import timedelta

default_args = {
    'owner': 'data_team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='my_pipeline',
    default_args=default_args,
    ...
) as dag:
    ...
```

Every task in the DAG inherits these defaults. If a task raises an exception, Airflow waits `retry_delay` and tries again, up to `retries` times.

You can override per task:

```python
load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    retries=5,              # override for this task only
    retry_delay=timedelta(minutes=1),
)
```

---

## Testing a DAG locally

You don't need to wait for the scheduler. Run a single DAG for a specific date:

```bash
airflow dags test my_pipeline 2024-01-15
```

This runs all tasks in order, in the current terminal, printing all logs. Ideal for development.

Run a single task:

```bash
airflow tasks test my_pipeline extract 2024-01-15
```

---

## Putting it all together

Here's a complete minimal DAG:

```python
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract(**context):
    df = pd.read_csv('/data/orders.csv')
    print(f"Loaded {len(df)} rows")
    context['ti'].xcom_push(key='row_count', value=len(df))

def report(**context):
    count = context['ti'].xcom_pull(task_ids='extract', key='row_count')
    print(f"Pipeline processed {count} orders")

default_args = {
    'owner': 'data_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_orders',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 2 * * *',
    catchup=False,
) as dag:

    t_extract = PythonOperator(
        task_id='extract',
        python_callable=extract,
    )

    t_report = PythonOperator(
        task_id='report',
        python_callable=report,
    )

    t_extract >> t_report
```

Now open `etl_dag.py` and start from TODO 1.
