import sys
import traceback
from sqlite3 import OperationalError
from core.detection.rule_detectors import evaluate_rules
from core.detection.alert_manager import record_alert
import json
from pathlib import Path
import os

ARTIFACT_ALERTS_PATH = Path("artifacts/alerts/clf_alerts.json")

def canonicalize_alert(alert):
    """Return dict with stable key order for diffing"""
    return {
        "rule_id": alert.get("rule_id"),
        "message": alert.get("message"),
        "service": alert.get("service")
    }

def main():
    """Main script for running detection"""
    emit_artifacts = os.getenv("EMIT_ARTIFACTS") == "1"
    zscore_enabled = os.getenv("ZSCORE_ENABLED") == "1"

    # Rules based detection
    try:
        triggered_alerts = evaluate_rules(zscore_enabled=zscore_enabled)
        
    except OperationalError as e:
        print('An error occurred when connecting to the database file:')
        print(e)
        sys.exit(1)
    except Exception as e:
        print('An exception occurred while evaluating the provided rules:')
        print(e)
        traceback.print_exc()
        sys.exit(1)

    recorded_alerts = []
    for alert in triggered_alerts:
        recorded_alerts.append(alert)
        record_alert(alert)

    if emit_artifacts:
        ARTIFACT_ALERTS_PATH.parent.mkdir(parents=True, exist_ok=True)

        normalized_alerts = sorted(
            [canonicalize_alert(a) for a in recorded_alerts],
            key=lambda a: (a["rule_id"])
        )

        with open(ARTIFACT_ALERTS_PATH, "w") as f:
            json.dump(normalized_alerts, f, indent=2)

        print(f"Alert artifacts written to {ARTIFACT_ALERTS_PATH}")

    num_alerts_triggered = len(triggered_alerts)
    rules_triggered = set(alert["rule_id"] for alert in triggered_alerts)

    print('Number of alerts triggered:', num_alerts_triggered)
    print('Rules triggered:', ', '.join(sorted(rules_triggered)))
    print('Alerts written to DB:')
    for alert in recorded_alerts:
        print(f"  - [{alert['rule_id']}] {alert['triggered_at']}: {alert['message']}")

if __name__ == '__main__':
    main()
