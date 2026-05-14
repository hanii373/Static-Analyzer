from tree_sitter import Language, Parser
import tree_sitter_python as tspython

class ASTAnalyzer:
    def __init__(self):
        self.lang = Language(tspython.language())
        self.parser = Parser(self.lang)

    def get_tree(self, code):
        return self.parser.parse(bytes(code, "utf8"))

    def query(self, tree, query_str):
        # Using S-expression queries as suggested in your guide
        ts_query = self.lang.query(query_str)
        return ts_query.captures(tree.root_node)