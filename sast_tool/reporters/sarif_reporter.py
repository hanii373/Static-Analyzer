import json
from typing import List

from sast_tool.engine.models import Finding


class SarifReporter:
    def report(self, findings: List[Finding]) -> str:
        results = []

        for f in findings:
            results.append({
                "ruleId": f.rule_id,
                "message": {
                    "text": f.message
                },
                "level": self.map_level(f.severity.value),
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": f.location.file
                            },
                            "region": {
                                "startLine": f.location.line,
                                "startColumn": f.location.column,
                            }
                        }
                    }
                ]
            })

        sarif = {
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Static Analyzer",
                            "informationUri": "https://github.com/your-org/static-analyzer",
                            "rules": []
                        }
                    },
                    "results": results
                }
            ]
        }

        return json.dumps(sarif, indent=2)

    def map_level(self, severity: str) -> str:
        mapping = {
            "HIGH": "error",
            "MEDIUM": "warning",
            "LOW": "note",
        }
        return mapping.get(severity, "note")