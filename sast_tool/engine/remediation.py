# sast_tool/engine/remediation.py
import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

# Force load the .env values inside the file scope explicitly
load_dotenv()

class RemediationEngine:
    def __init__(self):
        # Configure using the environment fallback securely
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Enforce a single concurrent task flight limit
        self._lock = asyncio.Semaphore(1)

    async def enrich_finding(self, finding):
        """Paces API generation queries safely to match Free Tier RPM constraints."""
        message = finding["message"] if isinstance(finding, dict) else finding.message
        snippet = finding["snippet"] if isinstance(finding, dict) else finding.snippet
        
        prompt = (
            f"Provide a brief, single secure code alternative fix example for this vulnerability:\n"
            f"Context: {message}\nCode snippet:\n{snippet}"
        )
        
        async with self._lock:
            try:
                # Add a 4-second safety cooldown buffer before firing to let the RPM slot clear out completely
                await asyncio.sleep(4)
                
                response = await self.model.generate_content_async(prompt)
                remediation_text = response.text
                
            except Exception as e:
                remediation_text = f"Analysis failed dynamically: {str(e)}"
                
        # Assign the string back to the object structure safely
        if isinstance(finding, dict):
            finding["ai_remediation"] = remediation_text
        else:
            finding.ai_remediation = remediation_text
            
        return finding