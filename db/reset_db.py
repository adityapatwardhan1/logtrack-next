# db/reset_db.py
import psycopg2
from dotenv import load_dotenv

from db.config import get_db_config

load_dotenv()

SCHEMA_FILE = "db/migrations/001_initial.sql"


def reset_db() -> None:
    with psycopg2.connect(**get_db_config()) as con:
        con.autocommit = True
        with con.cursor() as cur:
            cur.execute("""
                DROP TABLE IF EXISTS alerts CASCADE;
                DROP TABLE IF EXISTS rules CASCADE;
                DROP TABLE IF EXISTS users CASCADE;
                DROP TABLE IF EXISTS logs CASCADE;
                """)
            print("Tables dropped.")

            # Recreate tables
            with open(SCHEMA_FILE, "r") as f:
                cur.execute(f.read())
            print("Schema initialized.")


if __name__ == "__main__":
    reset_db()
