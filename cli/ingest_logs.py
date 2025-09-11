# PYTHONPATH=. python3 cli/ingest_logs.py example.clf
import sys 
from core.parsers import clf_parser, hdfs_parser, aws_cloudtrail_parser
from db.init_db import *
from psycopg2.extras import Json

def main():
    filename = sys.argv[1]   
    parser = None 
    if filename.endswith(".clf"):
        parser = clf_parser.CLFParser()
    elif filename.endswith(".hdfs"):
        parser = hdfs_parser.HDFSParser()
    elif filename.endswith(".aws"):
        parser = aws_cloudtrail_parser.CloudTrailParser()
    else:
        print("No parser for the type of file provider, exiting")
        exit(1)

    try:
        log_data = parser.parse_file(filename)

        con = get_db_connection()
        cur = con.cursor()
        cur.executemany(
            """
            INSERT INTO logs (timestamp, service, severity, message, username, extra_fields)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    log_json.get("timestamp"),
                    log_json.get("service"),
                    log_json.get("severity"),
                    log_json.get("message"),
                    log_json.get("user"),
                    Json(log_json.get("extra_fields", {}))
                )
                for log_json in log_data
            ]
        )

        con.commit()
        cur.close()
        con.close()
    except Exception as e:
        print(f"An exception occured when parsing log file {filename}: {e}")

if __name__ == '__main__':
    main()
    