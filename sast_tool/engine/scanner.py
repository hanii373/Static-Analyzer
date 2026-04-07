from pathlib import Path
from typing import List

from sast_tool.engine.models import Finding
from sast_tool.rules.sec_001_dangerous_calls import DangerousEvalRule


class Scanner:
    def __init__(self):
        # Register rules (for now manually)
        self.rules = [
            DangerousEvalRule(),
        ]

    def scan_file(self, file_path: Path) -> List[Finding]:
        findings: List[Finding] = []

        try:
            code = file_path.read_text(encoding="utf-8")
        except Exception:
            return findings  # skip unreadable files

        for rule in self.rules:
            rule_findings = rule.analyze(str(file_path), code)
            findings.extend(rule_findings)

        return findings

    def scan_directory(self, directory: str) -> List[Finding]:
        findings: List[Finding] = []

        path = Path(directory)

        for file_path in path.rglob("*.py"):
            file_findings = self.scan_file(file_path)
            findings.extend(file_findings)

        return findings