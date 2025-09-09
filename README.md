## Setting up the Postgresql + Docker
```
docker compose up -d db

pip install psycopg2-binary python-dotenv

python db/init_db.py
```