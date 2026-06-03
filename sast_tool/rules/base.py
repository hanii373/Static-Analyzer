from abc import ABC, abstractmethod
from typing import List
from tree_sitter import Node 
from sast_tool.engine.models import Finding, Location, Severity
from sast_tool.engine.ast_analyzer import ASTAnalyzer

class Rule(ABC):
    rule_id: str
    name: str
    severity: Severity

    @abstractmethod
    def analyze(self, file_path: str, code: str) -> List[Finding]:
        pass

class ASTRule(Rule, ABC):
    def __init__(self):
        self.analyzer = ASTAnalyzer()

    @abstractmethod
    def get_target_names(self) -> List[str]:
        pass

    def analyze(self, file_path: str, code: str) -> List[Finding]:
        findings = []
        try:
            targets = self.get_target_names()
            lines = code.splitlines()
            
            captures = []
            for target in targets:
                captures.extend(self.analyzer.find_sinks(code, target))
                captures.extend(self.analyzer.find_attribute_sinks(code, target))
            
            for match in captures:
                node = match[0]
                
                # Ensure we point to the parent 'call' node block
                while node and node.type != "call" and node.parent:
                    node = node.parent

                if node and node.type == "call":
                    line_num = node.start_point[0] + 1
                    col_num = node.start_point[1]
                    snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    if not any(f.location.line == line_num for f in findings):
                        findings.append(Finding(
                            rule_id=self.rule_id,
                            message=self.name,
                            severity=self.severity,
                            location=Location(file=file_path, line=line_num, column=col_num),
                            snippet=snippet
                        ))
        except Exception:
            pass
            
        return findings
