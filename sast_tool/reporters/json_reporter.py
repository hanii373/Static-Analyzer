import json
from typing import List

from sast_tool.engine.models import Finding


class JSONReporter:
    def report(self, findings: List[Finding]) -> str:
        output = []

        for f in findings:
            output.append({
                "rule_id": f.rule_id,
                "message": f.message,
                "severity": f.severity.value,
                "file": f.location.file,
                "line": f.location.line,
                "column": f.location.column,
                "snippet": f.snippet,
            })

        return json.dumps(output, indent=2)