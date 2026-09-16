"""
Connexion PostgreSQL et fonctions d'insertion pour le générateur ASIP.
Les identifiants de connexion viennent exclusivement de variables d'environnement.
"""

import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "asip")
DB_USER = os.environ.get("POSTGRES_USER", "asip_user")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

if not DB_PASSWORD:
    raise RuntimeError(
        "POSTGRES_PASSWORD n'est pas défini. "
        "Copiez .env.example vers .env et renseignez un mot de passe."
    )


def get_connection() -> psycopg.Connection:
    """Ouvre une connexion à la base PostgreSQL."""
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def insert_and_get_ids(
    conn: psycopg.Connection,
    table: str,
    records: list[dict],
    id_column: str,
) -> list[int]:
    """
    Insère une liste d'enregistrements (dictionnaires) dans une table
    et retourne les identifiants générés par PostgreSQL, dans l'ordre d'insertion.
    """
    if not records:
        return []

    columns = list(records[0].keys())
    columns_sql = ", ".join(columns)
    placeholders_sql = ", ".join(f"%({col})s" for col in columns)
    query = (
        f"INSERT INTO {table} ({columns_sql}) "
        f"VALUES ({placeholders_sql}) "
        f"RETURNING {id_column}"
    )

    ids = []
    with conn.cursor() as cur:
        for record in records:
            cur.execute(query, record)
            ids.append(cur.fetchone()[0])
    conn.commit()
    return ids
