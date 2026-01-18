import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import psycopg2
import psycopg2.extras

from db.init_db import get_db_connection


def _parse_timestamp(timestamp):
    """
    Converts a timestamp string or datetime object into a UTC datetime object
    :param timestamp: Timestamp (datetime object or string '%Y-%m-%d %H:%M:%S')
    :return: UTC datetime object
    """
    if isinstance(timestamp, datetime):
        # Normalize to UTC timezone
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=timezone.utc)
        else:
            # Convert to UTC
            return timestamp.astimezone(timezone.utc)
    elif isinstance(timestamp, str):
        # Parse naive datetime, set UTC timezone
        naive_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return naive_datetime.replace(tzinfo=timezone.utc)
    else:
        raise TypeError(
            f"Unsupported type for timestamp parsing: {type(timestamp)}"
        )


def find_sliding_windows(
    events: list[dict], window: timedelta, threshold: int
):
    """
    Yields windows of a certain time length which contain threshold number of events
    :param events: Sorted list of dicts with 'timestamp' key (timezone-aware datetime objects)
    :param window: Time window size as timedelta
    :param threshold: Minimum number of events in the window to yield
    :yields: tuple(start_index, end_index) indexes of events which define a valid window
    """
    left = 0
    for right in range(len(events)):
        while events[right]["timestamp"] - events[left]["timestamp"] > window:
            left += 1
        if right - left + 1 >= threshold:
            yield left, right


def _keyword_threshold_alerts(dict_cur, rule):
    """
    Detects alerts where the number of logs containing a keyword from a specific service
    exceeds a threshold within a time window.

    :param cur: Postgres database cursor (RealDictCursor)
    :param rule: Rule dictionary containing keys:
                 'service', 'keyword', 'threshold', 'window_minutes', 'id'
    :return: List of triggered alerts, with each alert corresponding to a dict/JSON
    """
    service = rule["service"]
    keyword = rule["keyword"]
    threshold = rule["threshold"]
    window = timedelta(minutes=rule["window_minutes"])

    dict_cur.execute(
        "SELECT id, timestamp, message FROM logs WHERE service = %s AND message LIKE %s",
        (service, f"%{keyword}%"),
    )
    rows = dict_cur.fetchall()

    parsed = []
    for row in rows:
        try:
            parsed.append(
                {
                    "id": row["id"],
                    "timestamp": _parse_timestamp(row["timestamp"]),
                    "message": row["message"],
                }
            )
        except Exception:
            continue

    parsed.sort(key=lambda x: x["timestamp"])
    alerts = []

    for left, right in find_sliding_windows(parsed, window, threshold):
        alert = {
            "rule_id": rule["id"],
            "triggered_at": parsed[right]["timestamp"].strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "message": f"Rule {rule['id']} triggered with {right - left + 1} matches",
            "related_log_ids": [e["id"] for e in parsed[left: right + 1]],
        }
        alerts.append(alert)
        break

    return alerts


# Note: repeated message requires EXACT MESSAGES,
# Oftentimes it's better to use keyword threshold
def _repeated_message_alerts(cur, rule):
    """
    Detects alerts where an exact log message repeats at least a threshold number
    of times within a time window.

    :param cur: Postgres database cursor (RealDictCursor)
    :param rule: Rule dictionary containing keys:
                 'message', 'threshold', 'window_minutes', 'id'
    :return: List of triggered alert dictionaries
    """
    message = rule["message"]
    threshold = rule["threshold"]
    window = timedelta(minutes=rule["window_minutes"])

    cur.execute(
        "SELECT id, timestamp FROM logs WHERE message = %s", (message,)
    )
    rows = cur.fetchall()
    parsed = []

    for row in rows:
        try:
            parsed.append(
                {
                    "id": row["id"],
                    "timestamp": _parse_timestamp(row["timestamp"]),
                }
            )
        except Exception:
            continue

    parsed.sort(key=lambda x: x["timestamp"])
    alerts = []

    for left, right in find_sliding_windows(parsed, window, threshold):
        alert = {
            "rule_id": rule["id"],
            "triggered_at": parsed[right]["timestamp"].strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "message": f"Message '{message}' repeated {right - left + 1} times in {rule['window_minutes']}m",
            "related_log_ids": [e["id"] for e in parsed[left: right + 1]],
        }
        alerts.append(alert)
        break

    return alerts


def _inactivity_alerts(cur, rule):
    """
    Detects alerts when no logs from a specific service have been recorded within
    a maximum allowed idle time window.

    :param cur: Postgres (RealDictCursor) database cursor
    :param rule: Rule dictionary containing keys:
                 'service', 'max_idle_minutes', 'id'
    :return: List of triggered alert dictionaries
    """
    service = rule["service"]
    max_idle = timedelta(minutes=rule["max_idle_minutes"])

    cur.execute(
        "SELECT MAX(timestamp) as latest FROM logs WHERE service = %s",
        (service,),
    )
    row = cur.fetchone()
    alerts = []
    if row and row["latest"]:
        last_ts = _parse_timestamp(row["latest"])
        now = datetime.now(timezone.utc)
        if now - last_ts > max_idle:
            alert = {
                "rule_id": rule["id"],
                "triggered_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "message": f"No logs from '{service}' in the past {rule['max_idle_minutes']} minutes",
                "related_log_ids": [],
            }
            alerts.append(alert)
    return alerts


def _rate_spike_alerts(cur, rule):
    """
    Detects if a service generates more than `threshold` log entries within `window_seconds`.

    :param cur: Postgres (RealDictCursor) cursor
    :param rule: Rule dictionary with 'service', 'threshold', 'window_seconds', 'id'
    :return: List of triggered alerts
    """
    service = rule["service"]
    threshold = rule["threshold"]
    window_seconds = rule.get("window_seconds")

    if window_seconds is None:
        window_minutes = rule.get("window_minutes")
        if window_minutes is None:
            raise ValueError(
                "Rate spike rule must have either 'window_seconds' or 'window_minutes'"
            )
        window_seconds = window_minutes * 60

    window = timedelta(seconds=window_seconds)

    cur.execute(
        "SELECT id, timestamp FROM logs WHERE service = %s", (service,)
    )
    rows = cur.fetchall()
    parsed = []
    for row in rows:
        print(
            f"Raw DB timestamp: {row['timestamp']} (type {type(row['timestamp'])})"
        )
        try:
            parsed.append(
                {
                    "id": row["id"],
                    "timestamp": _parse_timestamp(row["timestamp"]),
                }
            )
        except Exception:
            continue

    parsed.sort(key=lambda x: x["timestamp"])
    alerts = []

    for left, right in find_sliding_windows(parsed, window, threshold):
        alert = {
            "rule_id": rule["id"],
            "triggered_at": parsed[right]["timestamp"].strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "message": f"{service} logged {right - left + 1} entries in {rule['window_seconds']}s",
            "related_log_ids": [e["id"] for e in parsed[left: right + 1]],
        }
        alerts.append(alert)
        break

    return alerts


def _user_threshold_alerts(cur, rule):
    """
    Detects alerts where a specific user triggers a given message more than N times in a window.

    :param cur: Postgres (RealDictCursor) cursor
    :param rule: Rule dict with 'message', 'threshold', 'window_minutes', 'id'
    :return: List of alerts triggered
    """
    message = rule["message"]
    threshold = rule["threshold"]
    window = timedelta(minutes=rule["window_minutes"])

    cur.execute(
        "SELECT id, timestamp, username FROM logs WHERE message LIKE %s AND username IS NOT NULL",
        (f"%{message}%",),
    )
    rows = cur.fetchall()

    # Group by user
    events_by_user = {}
    for row in rows:
        if row["username"] not in events_by_user:
            events_by_user[row["username"]] = []
        try:
            events_by_user[row["username"]].append(
                {
                    "id": row["id"],
                    "timestamp": _parse_timestamp(row["timestamp"]),
                }
            )
        except Exception:
            continue

    alerts = []

    for user, events in events_by_user.items():
        events.sort(key=lambda e: e["timestamp"])
        for left, right in find_sliding_windows(events, window, threshold):
            alert = {
                "rule_id": rule["id"],
                "triggered_at": events[right]["timestamp"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "message": f"User '{user}' triggered '{message}' {right - left + 1} times in {rule['window_minutes']}m",
                "related_log_ids": [e["id"] for e in events[left: right + 1]],
            }
            alerts.append(alert)
            break  # One alert per user
    return alerts


def _zscore_alerts(cur, rule):
    """
    Detects log volume spikes for a service using z-score anomaly detection.

    :param cur: Postgres (RealDictCursor) cursor
    :param rule: Rule dict with 'service', 'threshold', 'window_minutes', 'baseline_windows', 'id'
    :return: List of alerts triggered
    """
    service = rule.get("service")
    threshold = (
        rule.get("zscore_threshold") or rule.get("threshold") or 3
    )  # Default threshold
    window_minutes = rule.get("window_minutes", 5)
    baseline_windows = rule.get("baseline_windows", 6)

    if not service or threshold is None:
        print("Missing service or threshold")
        return []

    cur.execute(
        """
        SELECT id, timestamp FROM logs
        WHERE service = %s
          AND timestamp IS NOT NULL
        ORDER BY timestamp ASC
    """,
        (service,),
    )
    rows = cur.fetchall()
    if not rows:
        print("No logs found")
        return []

    log_times = []
    for row in rows:
        log_id = row["id"]
        timestamp = row["timestamp"]
        try:
            datetime_obj = _parse_timestamp(timestamp)
            log_times.append((log_id, datetime_obj))
        except Exception:
            continue

    if not log_times:
        print("No valid timestamps")
        return []

    # Use latest log time as "now"
    max_time = max(datetime_obj for _, datetime_obj in log_times)
    now = max_time

    # Bin logs into windows
    buckets = defaultdict(list)
    for i in range(baseline_windows + 1):
        buckets[i] = []

    for log_id, datetime_obj in log_times:
        delta_minutes = (now - datetime_obj).total_seconds() / 60
        bucket_idx = baseline_windows - int(delta_minutes // window_minutes)
        if 0 <= bucket_idx <= baseline_windows:
            buckets[bucket_idx].append((log_id, datetime_obj))

    if len(buckets) < baseline_windows + 1:
        return []

    # Sort buckets oldest to newest
    sorted_indices = list(range(baseline_windows + 1))
    baseline_counts = [len(buckets[idx]) for idx in sorted_indices[:-1]]
    current_count = len(buckets[sorted_indices[-1]])
    current_bucket_log_ids = [
        log_id for log_id, _ in buckets[sorted_indices[-1]]
    ]

    # Compute z-score
    mean = sum(baseline_counts) / len(baseline_counts)
    std = (
        math.sqrt(
            sum((x - mean) ** 2 for x in baseline_counts)
            / len(baseline_counts)
        )
        if baseline_counts
        else 0
    )
    alerts = []
    if std > 0:
        z = (current_count - mean) / std
        if z >= threshold:
            alerts.append(
                {
                    "rule_id": rule["id"],
                    "triggered_at": now.isoformat(),
                    "message": f"{service} log volume spike detected (z={z:.2f})",
                    "related_log_ids": current_bucket_log_ids,
                }
            )

    elif std == 0 and current_count > mean * threshold:
        alerts.append(
            {
                "rule_id": rule["id"],
                "triggered_at": now.isoformat(),
                "message": f"{service} log volume spike detected (std=0, count={current_count}, mean={mean})",
                "related_log_ids": current_bucket_log_ids,
            }
        )

    return alerts


def evaluate_rules(
    zscore_enabled=False, db_path=None, ml_enabled=False
) -> list[dict]:
    """
    Applies all detection rules on the logs stored in the database and returns triggered alerts. # noqa: E501

    :param zscore_enabled: Whether to evaluate z-score rules
    :param ml_enabled: Whether to evaluate ML-based anomaly detection
    :return: List of alert dictionaries triggered by the rules
    """
    if db_path:  # testing with SQLite
        import sqlite3

        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
    else:
        con = get_db_connection()
        cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("SELECT * FROM rules")
        rules = cur.fetchall()
        triggered_alerts = []

        for rule in rules:
            rule_type = rule.get("rule_type")
            if rule_type == "keyword_threshold":
                triggered_alerts.extend(_keyword_threshold_alerts(cur, rule))
            elif rule_type == "repeated_message":
                triggered_alerts.extend(_repeated_message_alerts(cur, rule))
            elif rule_type == "inactivity":
                triggered_alerts.extend(_inactivity_alerts(cur, rule))
            elif rule_type == "rate_spike":
                triggered_alerts.extend(_rate_spike_alerts(cur, rule))
            elif rule_type == "user_threshold":
                triggered_alerts.extend(_user_threshold_alerts(cur, rule))
            elif rule_type == "zscore_anomaly" and zscore_enabled:
                triggered_alerts.extend(_zscore_alerts(cur, rule))
            else:
                if "rule_type" not in rule:
                    raise ValueError(f"Missing 'rule_type' in rule: {rule}")

        con.close()
        return triggered_alerts
