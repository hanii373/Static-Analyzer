from typing import List
from sast_tool.rules.base import Rule
from sast_tool.engine.models import Finding


class DummyRule(Rule):
    def analyze(self, file_path: str, code: str) -> List[Finding]:
        return []