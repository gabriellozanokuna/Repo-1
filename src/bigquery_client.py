"""
Cliente de BigQuery para conectarse al proyecto botmaker-bigdata.
Lee las credenciales desde GOOGLE_APPLICATION_CREDENTIALS y el proyecto desde BQ_PROJECT.
"""

import os
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()


def get_client() -> bigquery.Client:
    """
    Crea y retorna un cliente de BigQuery autenticado.
    Usa GOOGLE_APPLICATION_CREDENTIALS si está definida, de lo contrario
    usa Application Default Credentials.
    """
    project = os.getenv("BQ_PROJECT", "botmaker-bigdata")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if credentials_path:
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Archivo de credenciales no encontrado: {credentials_path}\n"
                "Verifica que la ruta en GOOGLE_APPLICATION_CREDENTIALS sea correcta."
            )
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/bigquery"],
        )
        client = bigquery.Client(project=project, credentials=credentials)
    else:
        # Usa Application Default Credentials (gcloud auth application-default login)
        client = bigquery.Client(project=project)

    return client


def test_connection() -> dict:
    """
    Verifica que la conexión a BigQuery funcione correctamente.
    Retorna un dict con el resultado del test.
    """
    result = {
        "success": False,
        "project": os.getenv("BQ_PROJECT", "botmaker-bigdata"),
        "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "error": None,
        "tables_accessible": [],
        "tables_inaccessible": [],
    }

    tables_to_check = [
        "botmaker-bigdata.ext_metric_kavakcapital.message_metrics",
        "botmaker-bigdata.ext_metric_kavakcapital.session_metrics",
    ]

    try:
        client = get_client()
        result["success"] = True

        # Verificar acceso a cada tabla
        for table_id in tables_to_check:
            try:
                table = client.get_table(table_id)
                result["tables_accessible"].append({
                    "table": table_id,
                    "num_rows": table.num_rows,
                    "schema_fields": len(table.schema),
                })
            except Exception as e:
                result["tables_inaccessible"].append({
                    "table": table_id,
                    "error": str(e),
                })

    except FileNotFoundError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Error de conexión: {str(e)}"

    return result
