# Just to reset it if I make a mistake, this is for a developer hack
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "logtrack")
DB_USER = os.getenv("DB_USER", "logtrack_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")

SCHEMA_FILE = "db/migrations/001_initial.sql"

def reset_db():
    con = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD
    )
    con.autocommit = True
    cur = con.cursor()

    # Drop and recreate database
    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
    cur.execute(f"CREATE DATABASE {DB_NAME};")
    cur.close()
    con.close()
    print(f"Database {DB_NAME} reset.")

    # Now run migrations
    con2 = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur2 = con2.cursor()
    with open(SCHEMA_FILE, "r") as f:
        cur2.execute(f.read())
    con2.commit()
    cur2.close()
    con2.close()
    print("Schema initialized.")

if __name__ == "__main__":
    reset_db()
