from tree_sitter import Language, Parser
import tree_sitter_python as tspython

class ASTAnalyzer:
    """Transforms the tool from grep-based to logic-aware"""
    def __init__(self):
        self.lang = Language(tspython.language())
        self.parser = Parser(self.lang)

    def find_sinks(self, code: str, sink_name: str):
        """Finds dangerous function calls like eval() or system()"""
        tree = self.parser.parse(bytes(code, "utf8"))
        # Using S-expression queries 
        query = self.lang.query(f"""
            (call_expression
                function: (identifier) @fn
                (#eq? @fn "{sink_name}"))
        """)
        return query.captures(tree.root_node)