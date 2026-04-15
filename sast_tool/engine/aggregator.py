from typing import List, Dict, Tuple
from sast_tool.engine.models import Finding, Severity


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
                existing = unique[key]

                # 🔥 Boost confidence (multi-engine detection)
                existing.confidence = min(1.0, getattr(existing, "confidence", 0.5) + 0.2)

                # 🔥 Keep higher confidence finding
                if getattr(f, "confidence", 0.5) > getattr(existing, "confidence", 0.5):
                    unique[key] = f

                # 🔥 Optional severity boost
                if existing.severity.value == "MEDIUM":
                    existing.severity = Severity.HIGH

        return list(unique.values())

    def normalize_message(self, message: str) -> str:
        message = message.lower()

        if "eval" in message:
            return "eval_usage"

        if "exec" in message:
            return "exec_usage"

        if "sql" in message:
            return "sql_injection"

        return message.strip()

    def severity_rank(self, severity: str) -> int:
        ranking = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
        }
        return ranking.get(severity, 0)