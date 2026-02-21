"""
Módulo para consultar conversaciones de clientes desde BigQuery.
Tablas:
  - botmaker-bigdata.ext_metric_kavakcapital.message_metrics  (mensajes)
  - botmaker-bigdata.ext_metric_kavakcapital.session_metrics  (sesiones)
"""

import os
from typing import Optional
from google.cloud import bigquery
import pandas as pd

from .bigquery_client import get_client

DATASET = "botmaker-bigdata.ext_metric_kavakcapital"
TABLE_MESSAGES = f"{DATASET}.message_metrics"
TABLE_SESSIONS = f"{DATASET}.session_metrics"


def get_conversations_by_phone(
    phone_numbers: list[str],
    limit: int = 100,
) -> pd.DataFrame:
    """
    Obtiene las conversaciones (mensajes) de los números de teléfono indicados.

    Args:
        phone_numbers: Lista de números de teléfono de los leads.
        limit: Número máximo de registros a retornar.

    Returns:
        DataFrame con los mensajes de esas conversaciones.
    """
    client = get_client()

    query = f"""
        SELECT *
        FROM `{TABLE_MESSAGES}`
        WHERE phone IN UNNEST(@phone_numbers)
        ORDER BY timestamp DESC
        LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("phone_numbers", "STRING", phone_numbers),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    df = client.query(query, job_config=job_config).to_dataframe()
    return df


def get_sessions_by_phone(
    phone_numbers: list[str],
    limit: int = 100,
) -> pd.DataFrame:
    """
    Obtiene las sesiones de los números de teléfono indicados.

    Args:
        phone_numbers: Lista de números de teléfono de los leads.
        limit: Número máximo de registros a retornar.

    Returns:
        DataFrame con las sesiones de esas conversaciones.
    """
    client = get_client()

    query = f"""
        SELECT *
        FROM `{TABLE_SESSIONS}`
        WHERE phone IN UNNEST(@phone_numbers)
        ORDER BY start_time DESC
        LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("phone_numbers", "STRING", phone_numbers),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    df = client.query(query, job_config=job_config).to_dataframe()
    return df


def get_recent_conversations(
    days: int = 7,
    limit: int = 500,
) -> pd.DataFrame:
    """
    Obtiene las conversaciones de los últimos N días.

    Args:
        days: Número de días hacia atrás a consultar.
        limit: Número máximo de registros.

    Returns:
        DataFrame con los mensajes recientes.
    """
    client = get_client()

    query = f"""
        SELECT *
        FROM `{TABLE_MESSAGES}`
        WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
        ORDER BY timestamp DESC
        LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("days", "INT64", days),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    df = client.query(query, job_config=job_config).to_dataframe()
    return df
