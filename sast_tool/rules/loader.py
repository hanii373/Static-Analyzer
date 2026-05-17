# sast_tool/rules/loader.py
from sast_tool.rules.sec_001_dangerous_calls import DangerousOsSystemRule, DangerousSubprocessRule
from sast_tool.rules.sec_002_dangerous_eval import DangerousEvalRule

class RuleLoader:
    """
    Explicit rule loader that directly instantiates AST security checks
    to ensure reliable cross-platform execution in virtual environments.
    """
    def load_rules(self):
        # Directly return instances of your brand new AST rule classes
        return [
            DangerousOsSystemRule(),
            DangerousSubprocessRule(),
            DangerousEvalRule()
        ]