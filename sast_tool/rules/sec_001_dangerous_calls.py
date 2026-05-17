# sast_tool/rules/sec_001_dangerous_calls.py
from typing import List
from sast_tool.rules.base import ASTRule
from sast_tool.engine.models import Severity

class DangerousOsSystemRule(ASTRule):
    rule_id = "PY-AST-001"
    name = "Dangerous command execution via os.system()"
    severity = Severity.HIGH

    def get_target_names(self) -> List[str]:
        return ["system"]

class DangerousSubprocessRule(ASTRule):
    rule_id = "PY-AST-003"
    name = "Risky subprocess creation via subprocess.Popen()"
    severity = Severity.MEDIUM

    def get_target_names(self) -> List[str]:
        return ["Popen", "run", "call"]