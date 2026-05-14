import os
import json
import logging
from google import genai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
            self.model_id = "models/gemini-2.5-flash"

    async def enrich_finding(self, finding: Any, code_context: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None

        prompt = f"""
        Analyze this security vulnerability:
        Rule: {finding.rule_id}
        Message: {finding.message}
        Severity: {finding.severity}
        Code: {code_context}

        Return a JSON object with keys: "explanation", "fix", and "cwe".
        """

        try:
            # Using Controlled Generation (JSON Mode)
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                }
            )
            # No need for complex cleaning, the output is now guaranteed JSON
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini API or Parsing Error: {e}")
            return None