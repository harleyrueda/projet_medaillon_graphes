from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime


# ------------------ DAG Architecture Globale (Pipeline seed, Architecture Medaillon, Neo4j import) ---

with DAG(
    dag_id="architecture_globale",
    description="Pipeline ( seed - architecture_medaillon - import_neo4j )",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["pipeline_medaillon_neo4j"],
) as dag:

    # ----------------------- 1) Génération de données synthétiques - SEED --------------------------------
    seed = BashOperator(
        task_id="seed",
        bash_command="cd /opt/airflow && make seed",
    )
    # ----------------------- Architecture Médaillon --------------------------------------------------------
    with TaskGroup("architecture_medaillon") as medaillon_group:

        # --------------------  2) BRONZE CSV -> Parquet  ------------------------------------------------------
        bronze = BashOperator(
            task_id="bronze",
            bash_command="cd /opt/airflow && make bronze",
        )
        # --------------------  3) SILVER Validation qualité + Partitionnement des edges  ------------------
        silver = BashOperator(
            task_id="silver",
            bash_command="cd /opt/airflow && make silver",
        )
        # --------------------  4) GOLD Import dans Neo4j  -------------------------------------------------
        gold = BashOperator(
            task_id="gold",
            bash_command="cd /opt/airflow && make gold",
        )

        bronze >> silver >> gold
    # ------------------------------------------------------------------------------------------------------
    seed >> medaillon_group
