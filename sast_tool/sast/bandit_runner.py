import json
import subprocess
from typing import List

from sast_tool.engine.models import Finding, Severity, Location


class BanditRunner:
    def run(self, target_path: str) -> List[Finding]:
        findings: List[Finding] = []

        try:
            result = subprocess.run(
                ["bandit", "-r", target_path, "-f", "json"],
                capture_output=True,
                text=True,
            )

            data = json.loads(result.stdout)

        except Exception:
            return findings  # fail silently for now

        for issue in data.get("results", []):
            severity = self.map_severity(issue.get("issue_severity"))

            finding = Finding(
                rule_id=issue.get("test_id"),
                message=issue.get("issue_text"),
                severity=severity,
                location=Location(
                    file=issue.get("filename"),
                    line=issue.get("line_number"),
                    column=1,
                ),
                snippet=issue.get("code"),
            )

            findings.append(finding)

        return findings

    def map_severity(self, bandit_severity: str) -> Severity:
        mapping = {
            "LOW": Severity.LOW,
            "MEDIUM": Severity.MEDIUM,
            "HIGH": Severity.HIGH,
        }
        return mapping.get(bandit_severity, Severity.LOW)