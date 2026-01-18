import json

from core.parsers.base_parser import BaseParser


class CloudTrailParser(BaseParser):
    """Parser for AWS CloudTrail-type logs"""

    def __init__(self):
        self.service = "aws"

    def parse_file(self, file_path):
        try:
            with open(file_path, "r") as f:
                logs_json = json.load(f)
        except Exception as e:
            print(f"Error reading file at {file_path}: {e}")
            return None

        records = None
        if isinstance(logs_json, dict):
            records = logs_json.get("Records")
            if not records:
                return None
        else:
            records = logs_json

        all_parsed_logs = []
        for record in records:
            all_parsed_logs.append(self.parse_record(record))

        return all_parsed_logs

    def parse_line(self, line):
        # Not actually used - necessary to inherit from BaseParser ABC
        return None

    def parse_record(self, record):
        """
        Parses record into the below schema
        {
        "timestamp": str,        # e.g. "YYYY-MM-DD HH:MM:SS"
        "service": str,
        "severity": str | None,  # e.g. "INFO", "WARN", "ERROR" (if available)
        "message": str,          # raw log text
        "user": str | None,      # user identifier if extractable
        "extra_fields": dict     # other fields / metadata
        }
        """

        userIdentity = record.get("userIdentity")
        user = userIdentity.get("userName") if userIdentity else None

        timestamp_raw = record.get("eventTime")
        timestamp = None
        if timestamp_raw:
            try:
                timestamp = self.to_uniform_timestamp(timestamp_raw)
            except ValueError:
                timestamp = timestamp_raw

        return {
            "timestamp": timestamp,
            "service": record.get("eventSource", ""),
            "severity": None,
            "message": record.get("eventName", ""),
            "user": user,
            "extra_fields": {
                "eventSource": record.get("eventSource"),
                "eventVersion": record.get("eventVersion"),
                "awsRegion": record.get("awsRegion"),
                "sourceIPAddress": record.get("sourceIPAddress"),
                "userAgent": record.get("userAgent"),
                "requestID": record.get("requestID"),
                "eventID": record.get("eventID"),
                "eventType": record.get("eventType"),
            },
        }
