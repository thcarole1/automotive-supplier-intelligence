FROM apache/airflow:2.11.2-python3.12

USER root
RUN mkdir -p /opt/airflow/dbt_logs /opt/airflow/dbt_target \
    && chown -R airflow:root /opt/airflow/dbt_logs /opt/airflow/dbt_target
USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
