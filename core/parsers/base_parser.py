from abc import ABC, abstractmethod 
from datetime import datetime, timezone

class BaseParser(ABC):
    """
    Abstract base class / interface for parsers
    Each parser parse logs into this JSON format
    {
        "timestamp": str,        # e.g. "YYYY-MM-DD HH:MM:SS"
        "service": str,          
        "severity": str | None,  # e.g. "INFO", "WARN", "ERROR" (if available)
        "message": str,          # raw log text
        "user": str | None,      # user identifier if extractable
        "extra_fields": dict     # other fields / metadata
    }

    Subclasses implement logic for specific formats.
    """

    @staticmethod
    def to_uniform_timestamp(*parts):
        """Converts a datetime object to UTC and formats it uniformly"""
        timestamp_str = " ".join(parts).strip()
        default_formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",        # ISO w/ microseconds and Z
            "%Y-%m-%dT%H:%M:%SZ",           # ISO basic Zulu
            "%Y-%m-%dT%H:%M:%S%z",          # ISO with timezone
            "%d/%b/%Y:%H:%M:%S %z",         # CLF (Apache)
            "%y%m%d %H%M%S",                # HDFS style 1
            "%Y-%m-%d %H:%M:%S,%f",         # HDFS style 2
            "%Y-%m-%d %H:%M:%S",            # Plain
        ]

        # Try each format
        for format in default_formats:
            try:
                datetime_obj = datetime.strptime(timestamp_str, format)
                return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                continue

        raise ValueError(f"No format matched timestamp: {timestamp_str}")
    

    @abstractmethod
    def parse_line(self, line: str):
        """
        Parse individual line in log file
        :param line: Line in the log file
        :type line: str
        :returns: Parsed line as a JSON according to the above schema
        :rtype: dict
        """
        pass

    def parse_file(self, file_path: str):
        """
        Parse an entire log file into a list containing data for each log
        By default, parses line by line; override for formats that are not line based

        :param file_path: Path to the file
        :type file_path: str
        :returns: List containing data for each log (list of dicts)
        :rtype: list[dict] 
        """
        all_log_data = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                try:
                    all_log_data.append(self.parse_line(line))
                except Exception as e:
                    print(f"Exception when parsing log file at {file_path}: {e}")
        return all_log_data
