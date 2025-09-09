from db.init_db import get_db_connection

con = get_db_connection()
cur = con.cursor()
cur.execute("SELECT id, timestamp, service, severity, message, user FROM logs LIMIT 10;")
rows = cur.fetchall()
for row in rows:
    print(row)
cur.close()
con.close()
