from db.init_db import get_db_connection 

def record_alert(alert: dict) -> None:
    """
    Insert an alert into the alerts table
    :param alert: dict containing relevant info including rule_id, triggered_at, message and related_log_ids
    :type alert: dict 
    """
    con = get_db_connection()
    cur = con.cursor()
    # cur.execute("INSERT INTO alerts (rule_id, triggered_at, message, related_log_ids)" \
    # "VALUES (%s, %s, %s, %s)", (alert['rule_id'], alert['triggered_at'], alert['message'], ','.join(map(str, alert['related_log_ids'])) or '{}'))
    cur.execute("""
        INSERT INTO alerts (rule_id, triggered_at, message, related_log_ids)
        VALUES (%s, %s, %s, %s)
    """, (
        alert['rule_id'],
        alert['triggered_at'],
        alert['message'],
        alert['related_log_ids'] or []
    ))
    con.commit()
    con.close()    
