# sast_tool/dashboard/app.py
import os
import aiohttp
import asyncio
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sast_tool.engine.scanner import Scanner
from sast_tool.dast.crawler import DASTCrawler
from sast_tool.dast.scanner import DASTScanner

app = FastAPI(title="Static & Dynamic Security Analyzer Dashboard")

templates = Jinja2Templates(directory="sast_tool/dashboard/templates")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Renders the main dashboard panel homepage view."""
    return templates.TemplateResponse(request, "index.html", {"active_tab": "sast"})


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
                tasks = [ai_engine.enrich_finding(f) for f in findings]
                await asyncio.gather(*tasks)
            except Exception as ai_err:
                print(f"[DASHBOARD AI WARNING] Enrichment pipeline timed out: {ai_err}")
                for f in findings:
                    # TEMP DEBUG PATCH: Let's dump the real error directly into the UI!
                    f.ai_remediation = f"API Error Detail Trace: {str(ai_err)}"
        for finding in findings:
            if isinstance(finding, dict):
                finding["location"]["file"] = file.filename
                if not finding.get("ai_remediation"):
                    finding["ai_remediation"] = "No supplementary analysis generated."
            else:
                finding.location.file = file.filename
                if not hasattr(finding, 'ai_remediation') or not finding.ai_remediation:
                    finding.ai_remediation = "No supplementary analysis generated."
            # Sort findings array inline based on physical line sequence vectors
        findings.sort(key=lambda x: int(x["location"]["line"]) if isinstance(x, dict) else int(getattr(x.location, "line", 0) or 0))
    except Exception as e:
        findings = [{
            "rule_id": "ENGINE-CRASH",
            "severity": "CRITICAL",
            "message": f"Breakdown during AST parsing sequence: {e}",
            "snippet": "Parser Pipeline Exception Context",
            "location": {"file": file.filename, "line": "N/A", "column": 0},
            "ai_remediation": "Review the terminal console trace metrics to debug local parser runtime failures."
        }]
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
    return templates.TemplateResponse(
        request,
        "index.html", 
        {"sast_findings": findings, "active_tab": "sast", "scanned_file": file.filename}
    )


@app.post("/scan/dast", response_class=HTMLResponse)
async def handle_dast_scan(request: Request, url: str = Form(...)):
    """Triggers the asynchronous web crawler and fuzzer mapping pipeline."""
    dast_findings = []
    pages_crawled = 0
    
    try:
        crawler = DASTCrawler(url, max_depth=2)
        results = await crawler.start()
        pages_crawled = len(results["visited_pages"])
        
        fuzzer = DASTScanner()
        async with aiohttp.ClientSession() as session:
            for page, forms in results["attack_surface_forms"].items():
                for form in forms:
                    findings = await fuzzer.scan_form(session, page, form)
                    if findings:
                        dast_findings.extend(findings)
    except Exception as e:
        dast_findings.append({
            "rule_id": "DAST-ERROR",
            "message": f"Web crawler network trace failed: {e}",
            "severity": "HIGH",
            "snippet": url
        })

    return templates.TemplateResponse(
        request,
        "index.html", 
        {
            "dast_findings": dast_findings, 
            "active_tab": "dast", 
            "scanned_url": url,
            "pages_crawled": pages_crawled
        }
    )