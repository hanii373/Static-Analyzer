import os
import asyncio
from google import genai
from dotenv import load_dotenv

# CRITICAL FIX: Ensure .env absolute path structure mapping to clear shell caches
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

class RemediationEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        # Initialize the modern 2026 Google GenAI Client
        self.client = genai.Client(api_key=api_key)
        print("[REMEDIATION ENGINE] Successfully configured with local API key.")

    async def enrich_finding(self, finding):
        # Prevent hidden reference unbound exceptions by pre-defining default text
        remediation_text = ""
        
        # Safe structural variable extraction
        message = finding["message"] if isinstance(finding, dict) else finding.message
        snippet = finding["snippet"] if isinstance(finding, dict) else finding.snippet
        rule_id = finding["rule_id"] if isinstance(finding, dict) else getattr(finding, "rule_id", "SAST-VULN")

        prompt = (
            f"Provide a brief, single secure code alternative fix example for this vulnerability:\n"
            f"Context: {message}\nCode snippet:\n{snippet}"
        )

        for attempt in range(1, 4):
            try:
                await asyncio.sleep(4)
                # Modern, native async content generation call via aio layer
                response = await self.client.aio.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                if response and hasattr(response, "text") and response.text:
                    remediation_text = response.text
                else:
                    remediation_text = self._local_fallback(message, "Empty response payload returned from API.")
                break
                
            except Exception as e:
                err = str(e).lower()
                is_rate_limited = "429" in err or "resource_exhausted" in err or "quota" in err

                if is_rate_limited:
                    print(f"[REMEDIATION ENGINE] 429 Quota hit on attempt {attempt}.")
                    if attempt == 3:
                        print("[REMEDIATION ENGINE] Sustained throttle. Serving local secure patch template.")
                        remediation_text = self._local_fallback(message, "Daily project API quota limit exhausted.")
                else:
                    # Capture connection or authorization context tracking values
                    reason = "API Key Invalid or Expired" if "400" in err else str(e).split('.')[0]
                    remediation_text = self._local_fallback(message, f"API Connection Interrupted ({reason})")
                    break

        # Fallback safeguard insurance assignment 
        if not remediation_text:
            remediation_text = self._local_fallback(message, "Analysis completed empty.")

        # Bind payload seamlessly onto finding dictionaries or classes
        if isinstance(finding, dict):
            finding["ai_remediation"] = remediation_text
        else:
            finding.ai_remediation = remediation_text

        return finding

    def _local_fallback(self, message, reason):
        """Generates beautifully styled fallback code views matching dashboard styles."""
        msg_lower = message.lower()
        code_style = "display: block; padding: 12px; background: #1c1c1e; border: 1px solid #2c2c2e; border-radius: 6px; font-family: monospace; font-size: 13px; color: #30d158; white-space: pre-wrap; line-height: 1.5;"
        
        header = (
            f"<div style='margin-bottom: 8px; color: #ff9500; font-weight: bold;'>🛡️ Secure Remediation Alternative</div>"
            f"<div style='font-size: 11px; color: #8e8e93; font-style: italic; margin-bottom: 12px;'>Offline fallback mode: {reason}</div>"
        )

        if "eval" in msg_lower:
            return (
                f"{header}"
                f"<pre style='{code_style}'>"
                f"<span style='color: #8e8e93;'># SECURE ALTERNATIVE: Avoid dynamic parsing execution</span>\n"
                f"<span style='color: #ff7b72;'>import</span> ast\n\n"
                f"<span style='color: #8e8e93;'># Use safe literal evaluation instead of raw eval()</span>\n"
                f"data = ast.literal_eval(user_input)"
                f"</pre>"
            )
        elif "system" in msg_lower or "subprocess" in msg_lower:
            return (
                f"{header}"
                f"<pre style='{code_style}'>"
                f"<span style='color: #8e8e93;'># SECURE ALTERNATIVE: Avoid raw shell execution loops</span>\n"
                f"<span style='color: #ff7b72;'>import</span> subprocess\n\n"
                f"<span style='color: #8e8e93;'># Pass variables as an explicit list with shell execution disabled</span>\n"
                f"subprocess.run([<span style='color: #a5d6ff;'>\"/usr/bin/id\"</span>], check=<span style='color: #ff7b72;'>True</span>, capture_output=<span style='color: #ff7b72;'>True</span>, text=<span style='color: #ff7b72;'>True</span>)"
                f"</pre>"
            )
            
        return (
            f"{header}"
            f"<pre style='{code_style}'>"
            f"<span style='color: #8e8e93;'># SECURE PATCH: Sanitize input parameters before processing string structures</span>\n"
            f"<span style='color: #8e8e93;'># Do not pass raw user variables directly to dynamic execution statements.</span>"
            f"</pre>"
        )