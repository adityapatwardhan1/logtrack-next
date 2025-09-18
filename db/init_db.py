import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "logtrack")
DB_USER = os.getenv("DB_USER", "logtrack_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")

SCHEMA_FILE = "db/migrations/001_initial.sql"

def get_db_connection():
    """Returns connection to database at DB_NAME"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_dict_cursor(con):
    return con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def initialize_db():
    """Initializes database at DB_NAME with schema from SCHEMA_FILE"""
    con = get_db_connection()
    with con.cursor() as cur:
        with open(SCHEMA_FILE, "r") as f:
            cur.execute(f.read())
    con.commit()
    con.close()
    print(f"Initialized database {DB_NAME} with schema at {SCHEMA_FILE}")

if __name__ == "__main__":
    try:
        initialize_db()
    except Exception as e:
        print(f"An error occured while initializing {DB_NAME}: {e}")
