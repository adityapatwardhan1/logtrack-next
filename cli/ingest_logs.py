# PYTHONPATH=. python3 cli/ingest_logs.py example.clf
import json
import os
from pathlib import Path

from psycopg2.extras import Json

from core.parsers import aws_cloudtrail_parser, clf_parser, hdfs_parser
from db.init_db import get_db_connection

ARTIFACT_PARSED_PATH = Path("artifacts/parsed/clf_parsed.json")


def canonicalize_log(log):
    return {
        "timestamp": log.get("timestamp"),
        "service": log.get("service"),
        "severity": log.get("severity"),
        "message": log.get("message"),
        "user": log.get("user"),
        "extra_fields": log.get("extra_fields", {}),
    }


def main():
    # Arguments
    filename = os.getenv("FILE")
    if not filename:
        raise RuntimeError("FILE environment variable is required")
    emit_artifacts = os.getenv("EMIT_ARTIFACTS") == "1"

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

        if emit_artifacts:
            ARTIFACT_PARSED_PATH.parent.mkdir(parents=True, exist_ok=True)
            normalized_logs = [
                canonicalize_log(log)
                for log in sorted(
                    log_data,
                    key=lambda the_log: (
                        the_log.get("timestamp"),
                        the_log.get("service"),
                        the_log.get("message"),
                    ),
                )
            ]
            with open(ARTIFACT_PARSED_PATH, "w") as f:
                json.dump(normalized_logs, f, indent=2)
            print(f"Parsed artifacts written to {ARTIFACT_PARSED_PATH}")
        else:
            print("emit_artifacts is False")

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
                    Json(log_json.get("extra_fields", {})),
                )
                for log_json in log_data
            ],
        )

        con.commit()
        cur.close()
        con.close()
    except Exception as e:
        print(f"An exception occured when parsing log file {filename}: {e}")


if __name__ == "__main__":
    main()
