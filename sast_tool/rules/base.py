from abc import ABC, abstractmethod
from typing import List

from sast_tool.engine.models import Finding


class Rule(ABC):
    """
    Base class for all SAST rules.
    """

    rule_id: str
    name: str

    @abstractmethod
    def analyze(self, file_path: str, code: str) -> List[Finding]:
        """
        Analyze a file and return findings.
        """
        pass