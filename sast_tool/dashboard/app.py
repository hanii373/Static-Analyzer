import os
import aiohttp
import asyncio
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Initialize local environment parser securely before loading core tools
load_dotenv()

from sast_tool.engine.scanner import Scanner
from sast_tool.dast.crawler import DASTCrawler
from sast_tool.dast.scanner import DASTScanner

app = FastAPI(title="Astra Ferrum Security Analytics Hub")

templates = Jinja2Templates(directory="sast_tool/dashboard/templates")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Renders the main dashboard panel homepage view with empty contexts initialized."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {"active_tab": "sast", "sast_findings": [], "dast_findings": []}
    )


@app.post("/scan/sast", response_class=HTMLResponse)
async def handle_sast_scan(request: Request, file: UploadFile = File(...)):
    """Receives a file upload, executes an AST code scan, and appends parallel AI explanations."""
    temp_filename = f"temp_{file.filename}"
    findings = []

    try:
        contents = await file.read()
        with open(temp_filename, "wb") as f:
            f.write(contents)

        scanner = Scanner()
        findings = await scanner.scan_directory(temp_filename)

        if findings:
            try:
                from sast_tool.engine.remediation import RemediationEngine
                ai_engine = RemediationEngine()

                # Process each vulnerability one by one with a safe cooldown
                # between requests to respect the free-tier RPM quota
                for f in findings:
                    await ai_engine.enrich_finding(f)
                    await asyncio.sleep(15)  # Increased from 3s → 15s to avoid 429s

            except Exception as ai_err:
                print(f"[DASHBOARD AI WARNING] Enrichment pipeline exception: {ai_err}")
                for f in findings:
                    if isinstance(f, dict):
                        f["ai_remediation"] = "Remediation data temporarily unavailable due to upstream spikes."
                    else:
                        f.ai_remediation = "Remediation data temporarily unavailable due to upstream spikes."

        # Normalize paths and structural traits
        for finding in findings:
            if isinstance(finding, dict):
                finding["location"]["file"] = file.filename
                if not finding.get("ai_remediation"):
                    finding["ai_remediation"] = "No supplementary analysis generated."
            else:
                finding.location.file = file.filename
                if not hasattr(finding, "ai_remediation") or not finding.ai_remediation:
                    finding.ai_remediation = "No supplementary analysis generated."

        # Sort findings by physical line number
        findings.sort(
            key=lambda x: int(x["location"]["line"])
            if isinstance(x, dict)
            else int(getattr(x.location, "line", 0) or 0)
        )

        # Serialize Finding objects into plain dicts for template rendering
        serializable_sast = []
        for f in findings:
            if isinstance(f, dict):
                serializable_sast.append(f)
            else:
                serializable_sast.append({
                    "rule_id": getattr(f, "rule_id", "SAST-VULN"),
                    "severity": f.severity.name if hasattr(f.severity, "name") else str(f.severity),
                    "message": getattr(f, "message", ""),
                    "snippet": getattr(f, "snippet", ""),
                    "location": {
                        "file": getattr(f.location, "file", file.filename),
                        "line": getattr(f.location, "line", "N/A"),
                        "column": getattr(f.location, "column", 0),
                    },
                    "ai_remediation": getattr(f, "ai_remediation", ""),
                })
        findings = serializable_sast

    except Exception as e:
        findings = [{
            "rule_id": "ENGINE-CRASH",
            "severity": "CRITICAL",
            "message": f"Breakdown during AST parsing sequence: {e}",
            "snippet": "Parser Pipeline Exception Context",
            "location": {"file": file.filename, "line": "N/A", "column": 0},
            "ai_remediation": "Review the terminal console trace metrics to debug local parser runtime failures.",
        }]
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "sast_findings": findings,
            "dast_findings": [],
            "active_tab": "sast",
            "scanned_file": file.filename,
        },
    )


@app.post("/scan/dast", response_class=HTMLResponse)
async def handle_dast_scan(request: Request, url: str = Form(...)):
    """Triggers the asynchronous web crawler and fuzzer mapping pipeline."""
    dast_findings = []
    pages_crawled = 0

    try:
        crawler = DASTCrawler(url, max_depth=2)
        results = await crawler.start()

        visited_pages = results.get("visited_pages", [])
        attack_surface_forms = results.get("attack_surface_forms", {})
        pages_crawled = len(visited_pages)

        fuzzer = DASTScanner()
        async with aiohttp.ClientSession() as session:
            for page_url, forms in attack_surface_forms.items():
                for form in forms:
                    findings = await fuzzer.scan_form(session, page_url, form)
                    if findings:
                        dast_findings.extend(findings)

        # Normalize and serialize DAST findings
        serializable_dast = []
        for index, finding in enumerate(dast_findings):
            if isinstance(finding, dict):
                normalized = {
                    "rule_id": finding.get("rule_id") or f"DAST-VULN-{index+1:03d}",
                    "severity": finding.get("severity", "HIGH"),
                    "message": finding.get("message", ""),
                    "snippet": finding.get("snippet", ""),
                }
            else:
                severity_val = (
                    finding.severity.name
                    if hasattr(finding.severity, "name")
                    else str(finding.severity)
                )
                normalized = {
                    "rule_id": getattr(finding, "rule_id", "") or f"DAST-VULN-{index+1:03d}",
                    "severity": severity_val,
                    "message": getattr(finding, "message", ""),
                    "snippet": getattr(finding, "snippet", ""),
                }
            serializable_dast.append(normalized)

        dast_findings = serializable_dast

    except Exception as e:
        dast_findings = [{
            "rule_id": "DAST-CRASH",
            "severity": "HIGH",
            "message": f"Web crawler network trace failure: {str(e)}",
            "snippet": f"Target Endpoint Vector: {url}",
        }]

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "sast_findings": [],
            "dast_findings": dast_findings,
            "active_tab": "dast",
            "scanned_url": url,
            "pages_crawled": pages_crawled,
        },
    )
