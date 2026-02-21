"""
Script para verificar que la conexión a BigQuery funciona correctamente.

Uso:
    python test_connection.py

Asegúrate de tener configurado el .env con:
    GOOGLE_APPLICATION_CREDENTIALS=/ruta/al/service-account.json
    BQ_PROJECT=botmaker-bigdata
"""

import sys
import os
from pathlib import Path

# Asegurar que el src esté en el path
sys.path.insert(0, str(Path(__file__).parent))

from src.bigquery_client import test_connection


def main():
    print("=" * 60)
    print("  Test de conexión a BigQuery")
    print("=" * 60)

    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project = os.getenv("BQ_PROJECT", "botmaker-bigdata")

    print(f"\nConfiguración detectada:")
    print(f"  Proyecto      : {project}")
    print(f"  Credenciales  : {credentials_path or '(no configurada)'}")

    if credentials_path:
        exists = Path(credentials_path).exists()
        print(f"  Archivo existe: {'SI' if exists else 'NO - VERIFICA LA RUTA'}")

    print("\nEjecutando test...")
    result = test_connection()

    if result["success"]:
        print("\n[OK] Conexión exitosa a BigQuery")

        if result["tables_accessible"]:
            print("\nTablas accesibles:")
            for t in result["tables_accessible"]:
                print(f"  - {t['table']}")
                print(f"    Filas: {t['num_rows']:,}  |  Columnas: {t['schema_fields']}")

        if result["tables_inaccessible"]:
            print("\n[ADVERTENCIA] Tablas sin acceso:")
            for t in result["tables_inaccessible"]:
                print(f"  - {t['table']}")
                print(f"    Error: {t['error']}")
    else:
        print(f"\n[ERROR] No se pudo conectar a BigQuery")
        print(f"  Detalle: {result['error']}")
        sys.exit(1)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
