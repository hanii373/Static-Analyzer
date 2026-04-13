from pathlib import Path
from typing import List
from sast_tool.engine.aggregator import Aggregator
from sast_tool.sast.bandit_runner import BanditRunner
from sast_tool.sast.semgrep_runner import SemgrepRunner
from sast_tool.engine.models import Finding
from sast_tool.rules.sec_001_dangerous_calls import DangerousEvalRule


class Scanner:
    def __init__(self):
        # Register rules (for now manually)
        self.rules = [
            DangerousEvalRule(),
        ]
        self.bandit = BanditRunner()
        self.aggregator = Aggregator()
        self.semgrep = SemgrepRunner()

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

        # 1. Custom rules
        for file_path in path.rglob("*.py"):
            file_findings = self.scan_file(file_path)
            findings.extend(file_findings)

        # 2. Bandit
        bandit_findings = self.bandit.run(directory)
        findings.extend(bandit_findings)
        # 3. Semgrep
        semgrep_findings = self.semgrep.run(directory)
        findings.extend(semgrep_findings)

        # 4. Aggregate (dedup + sort)
        findings = self.aggregator.aggregate(findings)

        return findings