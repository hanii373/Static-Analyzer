def parse_response(response: str) -> dict:
    parts = {
        "explanation": "",
        "fix": "",
        "code": "",
    }

    current = None

    for line in response.splitlines():
        if line.startswith("Explanation:"):
            current = "explanation"
            continue
        elif line.startswith("Fix:"):
            current = "fix"
            continue
        elif line.startswith("Code:"):
            current = "code"
            continue

        if current:
            parts[current] += line + "\n"

    return parts