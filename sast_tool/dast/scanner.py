# sast_tool/dast/scanner.py
import asyncio
import logging
import aiohttp
from sast_tool.engine.models import Finding, Location, Severity

logger = logging.getLogger(__name__)

class DASTScanner:
    """
    Fuzzing engine that sends test payloads against discovered form fields
    and monitors responses for execution vulnerabilities.
    """
    def __init__(self):
        # Sample payloads to test input parameters
        self.xss_payloads = [
            "<script>alert(1)</script>",
            "\"><script>alert(1)</script>",
            "<img src=x onerror=alert(1)>"
        ]
        self.sqli_payloads = [
            "' OR '1'='1",
            "admin' --",
            "' UNION SELECT NULL--"
        ]

    async def scan_form(self, session: aiohttp.ClientSession, url: str, form) -> list:
        """Fuzzes inputs inside an HTML form and watches for active reflections or errors."""
        findings = []
        
        # If the form has no active inputs to test, skip it
        if not form.inputs:
            return findings

        # Test both XSS and SQLi payload vectors
        all_payloads = [
            ("XSS", self.xss_payloads),
            ("SQLi", self.sqli_payloads)
        ]

        for vuln_type, payloads in all_payloads:
            for payload in payloads:
                # Prepare a test dictionary mapping inputs to our payload string
                data = {}
                for inp in form.inputs:
                    data[inp["name"]] = payload

                try:
                    # Choose the correct HTTP transmission method mapped by the crawler
                    if form.method == "POST":
                        async with session.post(form.action, data=data, timeout=5) as resp:
                            body = await resp.text()
                    else:
                        async with session.get(form.action, params=data, timeout=5) as resp:
                            body = await resp.text()

                    # 1. Check for Cross-Site Scripting vulnerability (reflection check)
                    if vuln_type == "XSS" and payload in body:
                        findings.append(Finding(
                            rule_id="DAST-XSS-001",
                            message=f"Reflected XSS vulnerability detected in form action target",
                            severity=Severity.HIGH,
                            location=Location(file=url, line=0, column=0),
                            snippet=f"Form Action: {form.action} | Input Fuzzed: {list(data.keys())}"
                        ))
                        break  # Found a vulnerability on this form, skip to next class

                    # 2. Check for SQL Injection vulnerability (database error trace check)
                    elif vuln_type == "SQLi":
                        db_errors = ["sql syntax", "mysql_fetch_array", "ora-", "postgre", "sqlite3"]
                        if any(err in body.lower() for err in db_errors):
                            findings.append(Finding(
                                rule_id="DAST-SQLI-001",
                                message=f"Potential SQL Injection entry point detected via database error disclosure",
                                severity=Severity.CRITICAL,
                                location=Location(file=url, line=0, column=0),
                                snippet=f"Form Action: {form.action} | Error Pattern Observed"
                            ))
                            break

                except Exception as e:
                    logger.debug(f"Error fuzzing form at {url}: {e}")

        return findings