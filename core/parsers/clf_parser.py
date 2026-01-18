from core.parsers.base_parser import BaseParser
import re
from datetime import datetime


class CLFParser(BaseParser):
    """
    Class for parsing Common Log Format files, used by Apache and Nginx among others.
    Example (sourced from https://graylog.org/post/log-formats-a-complete-guide/):
    127.0.0.1 user-identifier john [20/Jan/2020:21:32:14 -0700] "GET /apache_pb.gif HTTP/1.0" 200 4782
    """

    def __init__(self, service: str = "apache"):
        self.service = service  # E.g. "apache" or "NGINX"

    def parse_line(self, line: str):
        """
        Parses line into the below schema
        {
        "timestamp": str,        # e.g. "YYYY-MM-DD HH:MM:SS"
        "service": str,
        "severity": str | None,  # e.g. "INFO", "WARN", "ERROR" (if available)
        "message": str,          # raw log text
        "user": str | None,      # user identifier if extractable
        "extra_fields": dict     # other fields / metadata
        }
        """
        regex = re.compile(
            r"(?P<ip>\S+) (?P<identifier>\S+) (?P<user>\S+) "
            r"\[(?P<datetime>[^\]]+)\] "
            r'"(?P<request>[^"]+)" (?P<status>\d{3}) (?P<bytes>\d+|-)'
        )
        regex_match = re.match(regex, line)

        if not regex_match:
            return None
        groups = regex_match.groupdict()
        timestamp = self.to_uniform_timestamp(groups["datetime"])
        return {
            "timestamp": timestamp,
            "service": self.service,
            "severity": None,
            "message": groups["request"],
            "user": groups["user"] if groups["user"] != "-" else None,
            "extra_fields": {
                "ip": groups["ip"],
                "identifier": (
                    groups["identifier"]
                    if groups["identifier"] != "-"
                    else None
                ),
                "status": int(groups["status"]),
                "bytes": (
                    int(groups["bytes"]) if groups["bytes"].isdigit() else None
                ),
            },
        }
