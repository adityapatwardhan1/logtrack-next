# db/reset_db.py
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
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    con.autocommit = True
    cur = con.cursor()

    # Drop only the tables, no schema ownership issues
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
    con.commit()
    cur.close()
    con.close()
    print("Schema initialized.")

if __name__ == '__main__':
    reset_db()