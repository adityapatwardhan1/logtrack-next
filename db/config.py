import os


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME", "logtrack"),
        "user": os.getenv("DB_USER", "logtrack_user"),
        "password": os.getenv("DB_PASSWORD", "secret"),
    }
