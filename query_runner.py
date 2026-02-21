"""
Ejecuta queries contra Redshift y devuelve resultados como DataFrame.

Uso:
    python query_runner.py 'SELECT ...'
    python query_runner.py 'SELECT ...' --user financing
"""

import sys
import os
import argparse
import pandas as pd
import redshift_connector
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

HOST     = os.getenv("RS_HOST", "general.cptvidurgnhk.us-west-2.redshift.amazonaws.com")
DATABASE = os.getenv("RS_DATABASE", "prod")
PORT     = int(os.getenv("RS_PORT", 5439))

USERS = {
    "default":    (os.getenv("RS_USER"),                os.getenv("RS_PASSWORD")),
    "financing":  (os.getenv("RS_USER_FINANCING"),      os.getenv("RS_PASSWORD_FINANCING")),
    "serving":    (os.getenv("RS_USER_SERVING"),        os.getenv("RS_PASSWORD_SERVING")),
}


def run_query(sql: str, user_key: str = "default") -> pd.DataFrame:
    user, password = USERS.get(user_key, USERS["default"])
    if not user or not password:
        # fallback a credenciales default
        user, password = USERS["default"]

    conn = redshift_connector.connect(
        host=HOST,
        database=DATABASE,
        user=user,
        password=password,
        port=PORT,
    )
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=cols)
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="SQL query to execute")
    parser.add_argument("--user", default="default", choices=USERS.keys(),
                        help="Credential set to use")
    args = parser.parse_args()

    df = run_query(args.query, args.user)
    print(df.to_string(index=False))
