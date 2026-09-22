"""
DAG unique ASIP : génération/ingestion -> dbt run -> dbt test -> publication de métriques.
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PROJECT_DIR = "/opt/airflow/project"
DBT_DIR = f"{PROJECT_DIR}/dbt"


def publish_metrics():
    """Interroge les KPI et log un résumé synthétique."""
    import logging

    from data_generation.db import get_connection

    logger = logging.getLogger("airflow.task")
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) AS total_suppliers,
                ROUND(AVG(health_score), 1) AS avg_health_score,
                COUNT(*) FILTER (WHERE health_score < 30) AS at_risk_suppliers
            FROM dbt_dev.kpi_supplier_health_score
        """)
        total, avg_score, at_risk = cur.fetchone()

    conn.close()

    logger.info("=== Résumé Supplier Health Score ===")
    logger.info("Fournisseurs évalués : %d", total)
    logger.info("Score moyen : %s / 100", avg_score)
    logger.info("Fournisseurs à risque (score < 30) : %d", at_risk)


with DAG(
    dag_id="asip_pipeline",
    description="Génération, transformation dbt et publication de métriques ASIP",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["asip"],
) as dag:

    generate_data = BashOperator(
        task_id="generate_data",
        bash_command=f"cd {PROJECT_DIR} && python -m data_generation.generate",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test",
    )

    publish = PythonOperator(
        task_id="publish_metrics",
        python_callable=publish_metrics,
    )

    generate_data >> dbt_run >> dbt_test >> publish
