import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

from db.config import get_db_config

load_dotenv()

SCHEMA_FILE = "db/migrations/001_initial.sql"


def get_db_connection():
    """Return a new psycopg2 connection using environment-based config."""
    return psycopg2.connect(**get_db_config())


def get_dict_cursor(con):
    return con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def initialize_db():
    """Initializes database with schema from SCHEMA_FILE"""
    with psycopg2.connect(**get_db_config()) as con:
        con.autocommit = True
        with con.cursor() as cur:
            with open(SCHEMA_FILE, "r") as f:
                cur.execute(f.read())
    print(f"Initialized database with schema at {SCHEMA_FILE}")


if __name__ == "__main__":
    try:
        initialize_db()
    except Exception as e:
        raise RuntimeError("Failed to initialize database") from e
