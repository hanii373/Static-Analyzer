from typing import List, Set, Tuple

from sast_tool.engine.models import Finding


class Aggregator:
    def deduplicate(self, findings: List[Finding]) -> List[Finding]:
        unique: List[Finding] = []
        seen: Set[Tuple] = set()

        for f in findings:
            key = (
                f.rule_id,
                f.location.file,
                f.location.line,
                f.message,
            )

            if key not in seen:
                seen.add(key)
                unique.append(f)

        return unique

    def sort_by_severity(self, findings: List[Finding]) -> List[Finding]:
        severity_order = {
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }

        return sorted(
            findings,
            key=lambda f: severity_order.get(f.severity.value, 0),
            reverse=True,
        )

    def aggregate(self, findings: List[Finding]) -> List[Finding]:
        findings = self.deduplicate(findings)
        findings = self.sort_by_severity(findings)
        return findings