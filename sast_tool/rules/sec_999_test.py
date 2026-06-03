from sast_tool.rules.sec_001_dangerous_calls import DangerousOsSystemRule, DangerousSubprocessRule
from sast_tool.rules.sec_002_dangerous_eval import DangerousEvalRule
from sast_tool.rules.sec_999_test import TestRule

class RuleLoader:
    def load_rules(self):
        return [
            DangerousOsSystemRule(),
            DangerousSubprocessRule(),
            DangerousEvalRule(),
            TestRule()
        ]
