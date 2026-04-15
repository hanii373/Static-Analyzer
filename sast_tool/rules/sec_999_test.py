from typing import List
from sast_tool.rules.base import Rule
from sast_tool.engine.models import Finding, Severity, Location


class DummyRule(Rule):
    def analyze(self, file_path: str, code: str) -> List[Finding]:
        return [
            Finding(
                rule_id="TEST-999",
                message="Dummy rule triggered",
                severity=Severity.LOW,
                location=Location(
                    file=file_path,
                    line=1,
                    column=1,
                ),
                snippet="dummy",
            )
        ]