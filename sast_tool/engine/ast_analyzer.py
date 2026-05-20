# sast_tool/engine/ast_analyzer.py
from tree_sitter import Parser, Language
import tree_sitter_python as tspython

class ASTAnalyzer:
    """Transforms the tool from grep-based to logic-aware for Tree-sitter 0.23+"""
    def __init__(self):
        # Explicitly wrap the PyCapsule inside the tree_sitter.Language instance constructor
        self.lang = Language(tspython.language())
        self.parser = Parser(self.lang)

    def get_tree(self, code: str):
        """Encodes string input into a parseable byte stream for tree-sitter."""
        return self.parser.parse(bytes(code, "utf8"))

    def _traverse_and_collect(self, node, sink_name: str, look_for_attribute: bool) -> list:
        matches = []

        if node.type == "call":
            func_node = node.child_by_field_name("function")
            if func_node:
                # Case A: Standalone execution sinks (ex. eval("user_input"))
                if not look_for_attribute and func_node.type == "identifier":
                    node_text = func_node.text.decode("utf-8") if func_node.text else ""
                    if node_text == sink_name:
                        matches.append((node, "fn"))
                
                # Case B: Multi-layer Attribute calls (ex. os.system("id"))
                elif look_for_attribute and func_node.type == "attribute":
                    obj_node = func_node.child_by_field_name("object")
                    attr_node = func_node.child_by_field_name("attribute")
                    
                    if obj_node and attr_node:
                        obj_text = obj_node.text.decode("utf-8") if obj_node.text else ""
                        attr_text = attr_node.text.decode("utf-8") if attr_node.text else ""
                        full_signature = f"{obj_text}.{attr_text}"
                        
                        # Full path validation (ex. "os.system" matches signature targets precisely)
                        if attr_text == sink_name or full_signature == sink_name:
                            matches.append((node, "attr"))
                            
        for child in node.children:
            matches.extend(self._traverse_and_collect(child, sink_name, look_for_attribute))
        return matches

    def find_sinks(self, code: str, sink_name: str):
        tree = self.get_tree(code)
        return self._traverse_and_collect(tree.root_node, sink_name, look_for_attribute=False)

    def find_attribute_sinks(self, code: str, sink_name: str):
        tree = self.get_tree(code)
        return self._traverse_and_collect(tree.root_node, sink_name, look_for_attribute=True)
