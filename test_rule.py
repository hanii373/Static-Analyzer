from sast_tool.rules.sec_001_dangerous_calls import DangerousEvalRule

code = """
user_input = input()
result = eval(user_input)
"""

rule = DangerousEvalRule()
findings = rule.analyze("test.py", code)

for f in findings:
    print("Rule:", f.rule_id)
    print("Message:", f.message)
    print("Severity:", f.severity)
    print("File:", f.location.file)
    print("Line:", f.location.line)
    print("Column:", f.location.column)
    print("Snippet:", f.snippet)
    print("-" * 40)