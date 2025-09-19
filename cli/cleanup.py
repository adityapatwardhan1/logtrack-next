import sys
from db.init_db import get_db_connection, get_dict_cursor

def clear_all_alerts():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM alerts;")
    con.commit()
    cur.close()
    con.close()

def clear_logs(hours):
    con = get_db_connection()
    cur = con.cursor()
    cur.execute(
        """
        DELETE FROM logs
        WHERE timestamp < (NOW() AT TIME ZONE 'UTC') - (%s * INTERVAL '1 hour')
        """,
        (hours,)
    )
    con.commit()
    cur.close()
    con.close()
    print(f"Cleared all logs that are >= {hours} hours old")

def main():
    if len(sys.argv) < 2:
        print("Need to specify whether to clear alerts or logs. Exiting")
        exit(1)
    elif sys.argv[1] == "alerts":
        clear_all_alerts()
    elif sys.argv[1] == "logs":
        if len(sys.argv) == 2:
            print("Specify a number of hours. Exiting")
            sys.exit(1)
        else:
            clear_logs(int(sys.argv[2]))
    else:
        print("Only options allowed are alerts or logs. Exiting")

if __name__ == '__main__':
    main()
    