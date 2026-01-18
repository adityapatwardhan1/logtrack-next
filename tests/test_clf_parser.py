# Run from project root with: PYTHONPATH=. pytest -q
# Test generated with help from ChatGPT (OpenAI), 2025-09-08

import pytest
from core.parsers.clf_parser import CLFParser


@pytest.fixture
def parser():
    return CLFParser(service="apache")


def test_clf_parser_valid_lines(parser):
    # Sample CLF lines
    lines = [
        '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326',
        '192.168.1.1 - - [12/Dec/2021:06:25:24 +0000] "POST /login HTTP/1.1" 302 1234',
        '203.0.113.45 - john [05/Mar/2023:14:12:09 +0200] "GET /dashboard HTTP/2.0" 404 512',
        '10.0.0.5 - - [21/Jun/2022:09:45:55 -0500] "PUT /api/data HTTP/1.1" 500 -',
    ]

    for line in lines:
        result = parser.parse_line(line)
        assert result is not None, f"Parser failed on line: {line}"
        assert result["service"] == "apache"
        assert "timestamp" in result
        assert "message" in result
        assert "extra_fields" in result
        assert "status" in result["extra_fields"]


def test_clf_parser_invalid_line(parser):
    bad_line = "this is not a valid log"
    assert parser.parse_line(bad_line) is None
