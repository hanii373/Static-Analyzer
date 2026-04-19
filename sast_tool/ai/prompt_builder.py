def build_prompt(f: Finding) -> str:
    return f"""
You are a security expert.

Explain the vulnerability and suggest how to fix it.

Vulnerability:
{f.message}

Code:
{f.snippet}

Return:

Explanation:
- What is the problem?
- Why is it dangerous?

Recommendation:
- How should developer fix it?
"""