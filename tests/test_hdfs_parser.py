# Run from project root with: PYTHONPATH=. pytest -q
# Test generated with help from ChatGPT (OpenAI), 2025-09-08

import pytest
from core.parsers.hdfs_parser import HDFSParser


@pytest.fixture
def sample_hdfs_line():
    return "1,081109,203518,143,INFO,dfs.DataNode$DataXceiver,Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106 dest: /10.250.19.102:50010,E5,Receiving block <*> src: /<*> dest: /<*>"


def test_parse_line(sample_hdfs_line):
    parser = HDFSParser()
    result = parser.parse_line(sample_hdfs_line)

    # Basic schema checks
    assert "timestamp" in result
    assert "service" in result
    assert "severity" in result
    assert "message" in result
    assert "user" in result
    assert "extra_fields" in result

    # Check values
    assert result["service"] == "HDFS"
    assert result["severity"] == "INFO"
    assert "Receiving block" in result["message"]
    assert result["extra_fields"]["LineId"] == "1"
    assert result["extra_fields"]["Pid"] == "143"
    assert result["extra_fields"]["Component"] == "dfs.DataNode$DataXceiver"
    assert result["extra_fields"]["EventId"] == "E5"
    assert "Receiving block" in result["extra_fields"]["EventTemplate"]
