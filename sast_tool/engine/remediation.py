# sast_tool/engine/remediation.py
import os
from google import genai
from google.genai import types

class RemediationEngine:
    def __init__(self):
        # Automatically detects GEMINI_API_KEY from the shell environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY environmental variable allocation.")
        # Initialize the official modern SDK client wrapper
        self.client = genai.Client(api_key=api_key)

    async def enrich_finding(self, finding):
        """Asynchronously generates security fix remediation details for a finding."""
        prompt = f"""
        You are an expert security engineer. Analyze this vulnerability and provide a brief, 
        actionable remediation recommendation (maximum 3 sentences). Do not include markdown code blocks.
        
        Vulnerability: {finding.message}
        Code Snippet: {finding.snippet}
        """
        try:
            # Crucial: Use the .aio namespace for native asynchronous execution inside FastAPI
            response = await self.client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            # Assign the output text back to the custom object attribute
            finding.ai_remediation = response.text.strip()
        except Exception as e:
            print(f"[REMEDIATION ENGINE ERROR]: {e}")
            finding.ai_remediation = f"Analysis failed dynamically: {str(e)}"