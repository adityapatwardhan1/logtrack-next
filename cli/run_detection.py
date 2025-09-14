import sys
import traceback
import argparse
import os
from sqlite3 import OperationalError
from core.detection.rule_detectors import evaluate_rules
from core.detection.alert_manager import record_alert

def main():
    """Main script for running detection"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', default='logtrack.db',
                        help='Path to SQLite database file (default: logtrack.db)')
    parser.add_argument("--zscore", action="store_true", help="Enable z-score based anomaly detection")
    args = parser.parse_args()

    # Rules based detection
    try:
        triggered_alerts = evaluate_rules(zscore_enabled=args.zscore)
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

    num_alerts_triggered = len(triggered_alerts)
    rules_triggered = set(alert["rule_id"] for alert in triggered_alerts)

    print('Number of alerts triggered:', num_alerts_triggered)
    print('Rules triggered:', ', '.join(sorted(rules_triggered)))
    print('Alerts written to DB:')
    for alert in recorded_alerts:
        print(f"  - [{alert['rule_id']}] {alert['triggered_at']}: {alert['message']}")

if __name__ == '__main__':
    main()
