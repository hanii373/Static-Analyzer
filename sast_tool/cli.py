# sast_tool/cli.py
import argparse
import asyncio
import logging
import sys
import json
import aiohttp
from sast_tool.engine.scanner import Scanner
from sast_tool.dast.crawler import DASTCrawler
from sast_tool.dast.scanner import DASTScanner

# Unified logger configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def export_to_sarif(findings, output_file="results.sarif"):
    """
    Converts SAST engine finding objects into standard GitHub-readable SARIF format
    so vulnerabilities display natively under the repo's Security tab.
    """
    sarif_log = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Static-Analyzer",
                        "version": "1.0.0",
                        "rules": []
                    }
                },
                "results": []
            }
        ]
    }
    
    seen_rules = set()
    for f in findings:
        # Register rule definitions to satisfy the SARIF specification
        if f.rule_id not in seen_rules:
            sarif_log["runs"][0]["tool"]["driver"]["rules"].append({
                "id": f.rule_id,
                "shortDescription": {"text": getattr(f, "name", f.message)},
                "properties": {"precision": "high"}
            })
            seen_rules.add(f.rule_id)
            
        # Map structural findings to physical repository code locations
        result_node = {
            "ruleId": f.rule_id,
            "message": {"text": f.message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": f.location.file},
                        "region": {
                            "startLine": f.location.line,
                            "startColumn": f.location.column + 1
                        }
                    }
                }
            ]
        }
        sarif_log["runs"][0]["results"].append(result_node)
        
    with open(output_file, "w") as out:
        json.dump(sarif_log, out, indent=2)
    logger.info(f"SARIF report successfully compiled and saved to: {output_file}")


async def run_web_dast(url: str):
    """Asynchronous pipeline to execute the black-box crawling and fuzzing suite."""
    print(f"\n--- 🛰️ Commencing Dynamic App Security Test (DAST) Suite against: {url} ---")
    crawler = DASTCrawler(url, max_depth=2)
    results = await crawler.start()
    
    print(f"Mapped Attack Surfaces: Crawled {len(results['visited_pages'])} pages.")
    
    fuzzer = DASTScanner()
    async with aiohttp.ClientSession() as session:
        found_any = False
        for page, forms in results["attack_surface_forms"].items():
            for form in forms:
                print(f"Fuzzing targets against action path: {form.action}...")
                findings = await fuzzer.scan_form(session, page, form)
                if findings:
                    found_any = True
                    print(f"\n🚨 Identified {len(findings)} Dynamic Vulnerabilities at {page}:")
                    for f in findings:
                        print(f"  [{f.severity.name}] {f.rule_id}: {f.message}")
                        print(f"   🔍 Target Map: {f.snippet}\n")
        
        if not found_any:
            print("\n✅ Clean web scan! No active form fuzzing vulnerabilities identified.")


def run_scan(target_path: str, output_format: str):
    """Core code directory structural AST scanning pipeline."""
    logger.info(f"Initializing analyzer sequence against: {target_path}")
    scanner = Scanner()
    
    try:
        logger.info(f"Starting scan for target: {target_path}")
        findings = asyncio.run(scanner.scan_directory(target_path))
        
        # 1. ALWAYS write the SARIF file if requested, even if findings list is empty!
        # This keeps the GitHub Action from complaining that the file doesn't exist.
        if output_format == "json":
            export_to_sarif(findings)
        
        if not findings:
            print("\n✅ Clean code scan! No security vulnerabilities identified.")
            return

        print(f"\n🚨 Identified {len(findings)} potential security vulnerabilities:\n")
        for finding in findings:
            print(f"[{finding.severity.name}] {finding.rule_id}: {finding.message}")
            print(f"  📍 File: {finding.location.file} (Line {finding.location.line}, Column {finding.location.column})")
            print(f"  🔍 Snippet: {finding.snippet}")
            print("-" * 60)
            
    except Exception as e:
        logger.error(f"Execution boundary breakdown: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Application Security Testing Platform Engine")
    
    # Arguments supporting both path-based code scanning and url-based deployment testing
    parser.add_argument(
        "--path", type=str, help="Path to local target directory/file for structural AST analysis"
    )
    parser.add_argument(
        "--url", type=str, help="Target URL endpoint for black-box DAST crawling and fuzzing"
    )
    parser.add_argument(
        "--format", type=str, default="text", choices=["text", "json"], help="Output format specification report"
    )
    
    args = parser.parse_args()

    if args.url:
        asyncio.run(run_web_dast(args.url))
    elif args.path:
        run_scan(args.path, args.format)
    else:
        # Fallback to menu directions if flags are empty
        parser.print_help()

if __name__ == "__main__":
    main()