from abc import ABC, abstractmethod
from typing import List
from tree_sitter import Node 
from sast_tool.engine.models import Finding

class Rule(ABC):
    rule_id: str
    name: str

    @abstractmethod
    def analyze(self, file_path: str, code: str) -> List[Finding]:
        pass

    def visit(self, node: Node, file_path: str, code: str) -> List[Finding]:
        """Recursive AST traversal engine"""
        findings = []
        for child in node.children:
            findings.extend(self.visit(child, file_path, code))
        return findings