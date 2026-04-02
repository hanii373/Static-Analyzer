from typing import List

from sast_tool.rules.base import Rule
from sast_tool.engine.models import Finding, Severity, Location


class DangerousEvalRule(Rule):
    rule_id = "SEC-001"
    name = "Dangerous use of eval()"

    def analyze(self, file_path: str, code: str) -> List[Finding]:
        findings: List[Finding] = []

        lines = code.split("\n")

        for line_number, line in enumerate(lines, start=1):
            if "eval(" in line:
                finding = Finding(
                    rule_id=self.rule_id,
                    message="Use of eval() is dangerous and can lead to code execution",
                    severity=Severity.HIGH,
                    location=Location(
                        file=file_path,
                        line=line_number,
                        column=line.find("eval(") + 1,
                    ),
                    snippet=line.strip(),
                )
                findings.append(finding)

        return findings