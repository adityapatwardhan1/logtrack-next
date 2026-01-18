# Run from project root with: PYTHONPATH=. pytest -q
# Test generated with help from ChatGPT (OpenAI), 2025-09-08

import pytest
import json
import tempfile
import os
from core.parsers.aws_cloudtrail_parser import CloudTrailParser

# Sample multi-record JSON
MULTI_RECORD_JSON = {
    "Records": [
        {
            "eventVersion": "1.08",
            "userIdentity": {"type": "IAMUser", "userName": "Alice"},
            "eventTime": "2025-09-07T12:00:00Z",
            "eventSource": "ec2.amazonaws.com",
            "eventName": "StartInstances",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "192.0.2.10",
            "userAgent": "aws-cli/2.0",
            "requestID": "req-123",
            "eventID": "evt-001",
            "eventType": "AwsApiCall",
        },
        {
            "eventVersion": "1.08",
            "userIdentity": {"type": "IAMUser", "userName": "Bob"},
            "eventTime": "2025-09-07T12:05:30Z",
            "eventSource": "s3.amazonaws.com",
            "eventName": "PutObject",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "198.51.100.5",
            "userAgent": "aws-sdk-java/1.11.100",
            "requestID": "req-456",
            "eventID": "evt-002",
            "eventType": "AwsApiCall",
        },
    ]
}

# Sample line-delimited JSON (each line is a separate JSON object)
LINE_DELIMITED_JSON = [
    {
        "eventVersion": "1.08",
        "userIdentity": {"type": "IAMUser", "userName": "Carol"},
        "eventTime": "2025-09-07T12:10:15Z",
        "eventSource": "iam.amazonaws.com",
        "eventName": "CreateUser",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "192.0.2.11",
        "userAgent": "aws-cli/2.0",
        "requestID": "req-789",
        "eventID": "evt-003",
        "eventType": "AwsApiCall",
    },
    {
        "eventVersion": "1.08",
        "userIdentity": {"type": "IAMUser", "userName": "Dave"},
        "eventTime": "2025-09-07T12:15:00Z",
        "eventSource": "ec2.amazonaws.com",
        "eventName": "StopInstances",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "192.0.2.12",
        "userAgent": "aws-cli/2.0",
        "requestID": "req-101112",
        "eventID": "evt-004",
        "eventType": "AwsApiCall",
    },
]


@pytest.fixture
def multi_record_file():
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
        json.dump(MULTI_RECORD_JSON, f)
        f.flush()
        yield f.name
    os.remove(f.name)


@pytest.fixture
def line_delimited_file():
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
        for record in LINE_DELIMITED_JSON:
            f.write(json.dumps(record) + "\n")
        f.flush()
        yield f.name
    os.remove(f.name)


def test_cloudtrail_parser_multi_record(multi_record_file):
    parser = CloudTrailParser()
    parsed = parser.parse_file(multi_record_file)
    assert parsed is not None
    assert len(parsed) == 2
    assert parsed[0]["user"] == "Alice"
    assert parsed[1]["user"] == "Bob"


def test_cloudtrail_parser_line_delimited(line_delimited_file):
    parser = CloudTrailParser()
    parsed_logs = []
    with open(line_delimited_file, "r") as f:
        for line in f:
            record = json.loads(line)
            parsed_logs.append(parser.parse_record(record))
    assert len(parsed_logs) == 2
    assert parsed_logs[0]["user"] == "Carol"
    assert parsed_logs[1]["user"] == "Dave"
