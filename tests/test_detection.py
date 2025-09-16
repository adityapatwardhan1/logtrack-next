# Run from project root with: PYTHONPATH=. pytest -q
# Test generated with help from ChatGPT (OpenAI), 2025-09-16

# tests/test_detection.py
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta, timezone
from core.detection import rule_detectors as rd

# Helper to create fake rows
def fake_row(id, timestamp, message="msg", username=None):
    return {"id": id, "timestamp": timestamp, "message": message, "username": username}

@pytest.fixture
def now():
    return datetime.now(timezone.utc).replace(microsecond=0)

@pytest.fixture
def mock_cursor():
    cur = MagicMock()
    cur.execute = MagicMock()
    cur.fetchall = MagicMock()
    cur.fetchone = MagicMock()
    return cur

# ------------------------
# Keyword threshold rule
# ------------------------
def test_keyword_threshold_alerts(mock_cursor, now):
    logs = [
        fake_row(1, now - timedelta(minutes=4), message="error occurred"),
        fake_row(2, now - timedelta(minutes=3), message="error occurred"),
        fake_row(3, now - timedelta(minutes=2), message="error occurred"),
    ]
    mock_cursor.fetchall.return_value = logs

    rule = {
        "id": "kword_test",
        "rule_type": "keyword_threshold",
        "service": "apache",
        "keyword": "error",
        "threshold": 3,
        "window_minutes": 5
    }

    alerts = rd._keyword_threshold_alerts(mock_cursor, rule)
    assert len(alerts) == 1
    assert "kword_test" in alerts[0]["rule_id"]
    assert len(alerts[0]["related_log_ids"]) == 3

# ------------------------
# Repeated message rule
# ------------------------
def test_repeated_message_alerts(mock_cursor, now):
    logs = [
        fake_row(1, now - timedelta(minutes=1), message="login failed"),
        fake_row(2, now - timedelta(minutes=1), message="login failed"),
        fake_row(3, now - timedelta(minutes=1), message="login failed"),
        fake_row(4, now - timedelta(minutes=0.5), message="login failed"),
        fake_row(5, now - timedelta(minutes=0.5), message="login failed"),
    ]
    mock_cursor.fetchall.return_value = logs

    rule = {
        "id": "repeated_test",
        "rule_type": "repeated_message",
        "message": "login failed",
        "threshold": 5,
        "window_minutes": 2
    }

    alerts = rd._repeated_message_alerts(mock_cursor, rule)
    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "repeated_test"
    assert len(alerts[0]["related_log_ids"]) == 5

# ------------------------
# Inactivity rule
# ------------------------
def test_inactivity_alerts(mock_cursor, now):
    last_log_time = now - timedelta(minutes=61)
    mock_cursor.fetchone.return_value = {"latest": last_log_time}

    rule = {
        "id": "inactivity_test",
        "rule_type": "inactivity",
        "service": "apache",
        "max_idle_minutes": 60
    }

    alerts = rd._inactivity_alerts(mock_cursor, rule)
    assert len(alerts) == 1
    assert "No logs from" in alerts[0]["message"]

# ------------------------
# Rate spike rule
# ------------------------
def test_rate_spike_alerts(mock_cursor, now):
    logs = [
        fake_row(i, now - timedelta(seconds=i*30)) for i in range(5)
    ]
    mock_cursor.fetchall.return_value = logs

    rule = {
        "id": "rate_spike_test",
        "rule_type": "rate_spike",
        "service": "apache",
        "threshold": 4,
        "window_seconds": 300
    }

    alerts = rd._rate_spike_alerts(mock_cursor, rule)
    assert len(alerts) == 1
    assert len(alerts[0]["related_log_ids"]) >= 4

# ------------------------
# User threshold rule
# ------------------------
def test_user_threshold_alerts(mock_cursor, now):
    logs = [
        fake_row(1, now - timedelta(minutes=1), message="login failed", username="user1"),
        fake_row(2, now - timedelta(minutes=0.9), message="login failed", username="user1"),
        fake_row(3, now - timedelta(minutes=0.8), message="login failed", username="user1"),
    ]
    mock_cursor.fetchall.return_value = logs

    rule = {
        "id": "user_test",
        "rule_type": "user_threshold",
        "message": "login failed",
        "threshold": 3,
        "window_minutes": 5
    }

    alerts = rd._user_threshold_alerts(mock_cursor, rule)
    assert len(alerts) == 1
    assert "user1" in alerts[0]["message"]

# ------------------------
# Z-score spike rule
# ------------------------
def test_zscore_alerts(mock_cursor, now):
    # 6 baseline windows, 1 current window with spike
    logs = []
    # Baseline windows: 2 logs each
    for i in range(12):
        logs.append(fake_row(i+1, now - timedelta(minutes=60 - i*5)))
    # Current window: 6 logs (spike)
    for i in range(12, 18):
        logs.append(fake_row(i+1, now - timedelta(minutes=1)))
    mock_cursor.fetchall.return_value = logs

    rule = {
        "id": "zscore_test",
        "rule_type": "zscore_anomaly",
        "service": "apache",
        "threshold": 2,
        "window_minutes": 5,
        "baseline_windows": 6
    }

    alerts = rd._zscore_alerts(mock_cursor, rule)
    assert len(alerts) == 1
    assert "log volume spike" in alerts[0]["message"]
