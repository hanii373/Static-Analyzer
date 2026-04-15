from typing import List, Dict, Tuple
from sast_tool.engine.models import Finding


class Aggregator:
    def aggregate(self, findings: List[Finding]) -> List[Finding]:
        unique: Dict[Tuple[str, int, str], Finding] = {}

        for f in findings:
            key = (
                f.location.file,
                f.location.line,
                self.normalize_message(f.message),
            )

            if key not in unique:
                unique[key] = f
            else:
                # Merge logic (keep highest severity)
                existing = unique[key]
                if self.severity_rank(f.severity.value) > self.severity_rank(existing.severity.value):
                    unique[key] = f

        return list(unique.values())

    def normalize_message(self, message: str) -> str:
        # very basic normalization
        return message.lower().strip()

    def severity_rank(self, severity: str) -> int:
        ranking = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
        }
        return ranking.get(severity, 0)