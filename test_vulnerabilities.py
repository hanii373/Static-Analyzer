import os
import subprocess
import ast

# SECTION 1: TRUE POSITIVES (tool MUST flag these)

def true_positives_demo(user_input):
    # PY-AST-002: Direct execution of user input via eval
    eval(user_input)

    # PY-AST-001: Direct command execution with raw os.system
    os.system("ping -c 1 " + user_input)

    # PY-AST-001: Subprocess call executing in shell mode
    subprocess.Popen(f"echo {user_input}", shell=True)

    # PY-AST-001: Subprocess run with shell=True string commands
    subprocess.run("ls -la /tmp", shell=True)

# SECTION 2: FALSE POSITIVE DECOYS (Regex would fail; AST MUST pass)

class CustomLogger:
    def system(self, message):
        print(f"[LOG]: {message}")

def false_positives_test():
    # 1. Comment Decoy: Regex search for "eval" or "system" will flag this,
    # but the AST parser sees a 'comment' node and must ignore it.
    # os.system("rm -rf /")
    # eval("dangerous_code")

    # 2. String Literal Decoy: The word "eval" is inside a harmless string.
    harmless_message = "Please evaluate your model parameters carefully."
    print(harmless_message)

    # 3. Variable Decoy: Variables named 'eval' or 'system' are assignments,
    # not actual invocation 'call' nodes.
    eval = "This is a safe string variable, not the builtin function"
    system = "Safe variable holding name of operational system"
    print(eval, system)

    # 4. Custom Namespace Decoy: Call to a custom method named "system".
    # Harmless class method, shouldn't be treated as os.system.
    logger = CustomLogger()
    logger.system("Database backup completed successfully.")


# SECTION 3: COMPLEX NESTED SCENARIOS (Testing AST traversal depth)

def nested_scenarios_test(complex_input):
    # Nested call: eval() inside an eval() statement
    eval(eval("complex_input"))

    # Comprehension: Calling os.system inside a list comprehension
    commands = ["id", "whoami"]
    results = [os.system(cmd) for cmd in commands]

    # Nested Argument calls: passing os.system output inside print call
    print("Execution output is: ", os.system("ls"))


# SECTION 4: FAULT TOLERANCE & BROKEN SYNTAX (Tree-sitter Recovery)

def broken_syntax_test():
    # Tree-sitter excels at parsing code even with syntax errors!
    # Let's create a deliberate syntax error (an unclosed parenthesis)
    # to prove the engine doesn't crash and still finds subsequent sinks.
    unclosed_tuple = (1, 2, 3
    
    # Immediately following a syntax error, we have a real vulnerability:
    os.system("whoami")
