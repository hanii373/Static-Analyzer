# Create this file: check_ai.py
import asyncio
from sast_tool.ai.client import AIClient
from sast_tool.ai.cache import AICache
from sast_tool.engine.models import Finding, Severity, Location

async def main():
    client = AIClient()
    cache = AICache()
    
    # Create a dummy finding to test
    test_finding = Finding(
        rule_id="SEC-001",
        message="Dangerous eval()",
        severity=Severity.HIGH,
        location=Location(file="test.py", line=1, column=1),
        snippet="eval(user_input)"
    )

    print("Checking AI Connection...")
    result = await client.enrich_finding(test_finding, "eval(user_input)")
    
    if result:
        print("✅ AI Success! Explanation received.")
        cache.set("SEC-001", "eval(user_input)", result)
        
        print("Checking Cache...")
        cached = cache.get("SEC-001", "eval(user_input)")
        if cached:
            print("✅ Cache Success! Data stored and retrieved.")
    else:
        print("❌ AI Failed. Check your API key and connection.")

if __name__ == "__main__":
    asyncio.run(main())