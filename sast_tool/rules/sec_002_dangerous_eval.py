from typing import List
from sast_tool.rules.base import ASTRule
from sast_tool.engine.models import Severity

class DangerousEvalRule(ASTRule):
    rule_id = "PY-AST-002"
    name = "Dangerous execution via eval()"
    severity = Severity.HIGH

    def get_target_names(self) -> List[str]:
        return ["eval"]
