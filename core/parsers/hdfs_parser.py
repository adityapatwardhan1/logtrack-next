from core.parsers.base_parser import BaseParser
import csv
from io import StringIO
from datetime import datetime

class HDFSParser(BaseParser):
    """
    Class for parsing Hadoop Distributed File System files
    Example HDFS log line (sourced from Loglizer)
    LineId,Date,Time,Pid,Level,Component,Content,EventId,EventTemplate
    1,081109,203518,143,INFO,dfs.DataNode$DataXceiver,Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106 dest: /10.250.19.102:50010,E5,Receiving block <*> src: /<*> dest: /<*>
    2,081109,203518,35,INFO,dfs.FSNamesystem,BLOCK* NameSystem.allocateBlock: /mnt/hadoop/mapred/system/job_200811092030_0001/job.jar. blk_-1608999687919862906,E22,BLOCK* NameSystem.allocateBlock:<*>
    Source:
    Reference:
    Shilin He, Jieming Zhu, Pinjia He, and Michael R. Lyu. 
    "Experience Report: System Log Analysis for Anomaly Detection." 
    IEEE International Symposium on Software Reliability Engineering (ISSRE), 2016. 
    [Most Influential Paper Award]
    """

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
        ...
        reader = csv.reader(StringIO(line))  # Handles commas inside messages if in quotes
        fields = next(reader)
        
        try:
            timestamp = self.to_uniform_timestamp(fields[1], fields[2])
        except:
            timestamp = None
        
        return {
            "timestamp": timestamp,
            "service": "HDFS",
            "severity": fields[4],
            "message": fields[6],
            "user": None,
            "extra_fields": {
                "LineId": fields[0],
                "Pid": fields[3],
                "Component": fields[5],
                "EventId": fields[7],
                "EventTemplate": fields[8]
            }
        }
        