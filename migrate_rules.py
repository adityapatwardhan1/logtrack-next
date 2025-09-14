import json
from db.init_db import get_db_connection

def migrate_rules(json_path="rules_config.json"):
    with open(json_path, "r") as f:
        rules = json.load(f)

    con = get_db_connection()
    cur = con.cursor()
    for rule in rules:
        cur.execute("""
            INSERT INTO rules (
                id, rule_type, service, keyword, message,
                threshold, window_minutes, window_seconds, max_idle_minutes,
                user_field, description, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                rule_type = EXCLUDED.rule_type,
                service = EXCLUDED.service,
                keyword = EXCLUDED.keyword,
                message = EXCLUDED.message,
                threshold = EXCLUDED.threshold,
                window_minutes = EXCLUDED.window_minutes,
                window_seconds = EXCLUDED.window_seconds,
                max_idle_minutes = EXCLUDED.max_idle_minutes,
                user_field = EXCLUDED.user_field,
                description = EXCLUDED.description,
                created_by = EXCLUDED.created_by
        """, (
            rule.get("id"),
            rule.get("rule_type"),
            rule.get("service"),
            rule.get("keyword"),
            rule.get("message"),
            rule.get("threshold"),
            rule.get("window_minutes"),
            rule.get("window_seconds"), 
            rule.get("max_idle_minutes"),
            rule.get("user_field"),
            rule.get("description", ""),
            None
        ))

    con.commit()
    con.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_rules()
