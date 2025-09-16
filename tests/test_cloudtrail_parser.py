# Run from project root with: PYTHONPATH=. pytest -q
# Test generated with help from ChatGPT (OpenAI), 2025-09-08

import pytest
from core.parsers.aws_cloudtrail_parser import CloudTrailParser

# Sample CloudTrail JSON (truncated for brevity)
SAMPLE_CLOUDTRAIL = {
    "Records": [
        {
            "eventVersion": "1.08",
            "userIdentity": {
                "type": "IAMUser",
                "userName": "Mateo"
            },
            "eventTime": "2023-07-19T21:17:28Z",
            "eventSource": "ec2.amazonaws.com",
            "eventName": "StartInstances",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "192.0.2.0",
            "userAgent": "aws-cli/2.13.5",
            "requestID": "e4336db0-149f-4a6b-844d-EXAMPLEb9d16",
            "eventID": "e755e09c-42f9-4c5c-9064-EXAMPLE228c7",
            "eventType": "AwsApiCall"
        }
    ]
}

import json
import tempfile
import os

@pytest.fixture
def temp_json_file():
    # Create a temporary JSON file with SAMPLE_CLOUDTRAIL
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
        json.dump(SAMPLE_CLOUDTRAIL, f)
        f.flush()
        yield f.name
    os.remove(f.name)

def test_cloudtrail_parser(temp_json_file):
    parser = CloudTrailParser()
    parsed_logs = parser.parse_file(temp_json_file)

    assert parsed_logs is not None
    assert len(parsed_logs) == 1

    log = parsed_logs[0]
    # Timestamp should be converted to YYYY-MM-DD HH:MM:SS
    assert log["timestamp"] == "2023-07-19 21:17:28"
    # assert log["service"] == "aws"
    assert log["user"] == "Mateo"
    assert log["message"] == "StartInstances"
    # Extra fields
    extra = log["extra_fields"]
    assert extra["eventSource"] == "ec2.amazonaws.com"
    assert extra["eventVersion"] == "1.08"
    assert extra["awsRegion"] == "us-east-1"
    assert extra["sourceIPAddress"] == "192.0.2.0"
    assert extra["userAgent"] == "aws-cli/2.13.5"
    assert extra["requestID"] == "e4336db0-149f-4a6b-844d-EXAMPLEb9d16"
    assert extra["eventID"] == "e755e09c-42f9-4c5c-9064-EXAMPLE228c7"
    assert extra["eventType"] == "AwsApiCall"
