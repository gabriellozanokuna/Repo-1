"""
Cliente de BigQuery para conectarse al proyecto botmaker-bigdata.

Soporta dos formas de autenticación (en orden de prioridad):
1. Variables de entorno individuales (GCP_SA_*) — recomendado para producción/CI
2. Archivo JSON via GOOGLE_APPLICATION_CREDENTIALS — para desarrollo local
"""

import os
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

_SCOPES = ["https://www.googleapis.com/auth/bigquery"]


def _credentials_from_env_vars() -> service_account.Credentials | None:
    """
    Construye credenciales de Service Account desde variables de entorno individuales.
    Retorna None si no están configuradas.
    """
    private_key = os.getenv("GCP_SA_PRIVATE_KEY")
    client_email = os.getenv("GCP_SA_CLIENT_EMAIL")

    if not private_key or not client_email:
        return None

    # La private key en .env puede tener \n literales — los convertimos a saltos de línea reales
    private_key = private_key.replace("\\n", "\n")

    info = {
        "type": "service_account",
        "project_id": os.getenv("GCP_SA_PROJECT_ID", "m-infra"),
        "private_key_id": os.getenv("GCP_SA_PRIVATE_KEY_ID", ""),
        "private_key": private_key,
        "client_email": client_email,
        "client_id": os.getenv("GCP_SA_CLIENT_ID", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    return service_account.Credentials.from_service_account_info(info, scopes=_SCOPES)


def _credentials_from_file() -> service_account.Credentials | None:
    """
    Construye credenciales desde el archivo JSON indicado en GOOGLE_APPLICATION_CREDENTIALS.
    Retorna None si la variable no está configurada.
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        return None

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"Archivo de credenciales no encontrado: {credentials_path}\n"
            "Verifica que la ruta en GOOGLE_APPLICATION_CREDENTIALS sea correcta."
        )

    return service_account.Credentials.from_service_account_file(
        credentials_path, scopes=_SCOPES
    )


def get_client() -> bigquery.Client:
    """
    Crea y retorna un cliente de BigQuery autenticado.

    Prioridad de autenticación:
    1. Variables GCP_SA_* (private key + email directamente en .env)
    2. Archivo JSON en GOOGLE_APPLICATION_CREDENTIALS
    3. Application Default Credentials (gcloud auth)
    """
    project = os.getenv("BQ_PROJECT", "botmaker-bigdata")

    credentials = _credentials_from_env_vars() or _credentials_from_file()

    if credentials:
        return bigquery.Client(project=project, credentials=credentials)

    # Fallback: Application Default Credentials
    return bigquery.Client(project=project)


def test_connection() -> dict:
    """
    Verifica que la conexión a BigQuery funcione correctamente.
    Retorna un dict con el resultado del test.
    """
    using_env_vars = bool(os.getenv("GCP_SA_PRIVATE_KEY"))
    result = {
        "success": False,
        "project": os.getenv("BQ_PROJECT", "botmaker-bigdata"),
        "auth_method": "env_vars (GCP_SA_*)" if using_env_vars else "json_file / ADC",
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
