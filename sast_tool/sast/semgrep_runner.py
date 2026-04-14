import json
import subprocess
from typing import List

from sast_tool.engine.models import Finding, Severity, Location


class SemgrepRunner:
    def run(self, target_path: str) -> List[Finding]:
        findings: List[Finding] = []

        try:
            result = subprocess.run(
                ["semgrep", "--config=auto", "--json", "--no-git-ignore", target_path],
                capture_output=True,
                text=True,
            )

            data = json.loads(result.stdout)

        except Exception:
            return findings

        for issue in data.get("results", []):
            severity = self.map_severity(issue.get("extra", {}).get("severity"))

            finding = Finding(
                rule_id=issue.get("check_id"),
                message=issue.get("extra", {}).get("message"),
                severity=severity,
                location=Location(
                    file=issue.get("path"),
                    line=issue.get("start", {}).get("line"),
                    column=issue.get("start", {}).get("col"),
                ),
                snippet=issue.get("extra", {}).get("lines"),
            )

            findings.append(finding)

        return findings

    def map_severity(self, semgrep_severity: str) -> Severity:
        mapping = {
            "ERROR": Severity.HIGH,
            "WARNING": Severity.MEDIUM,
            "INFO": Severity.LOW,
        }
        return mapping.get(semgrep_severity, Severity.LOW)