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
    Converts SAST engine finding objects into standard GitHub-readable SARIF format.
    Guarantees writing a valid skeleton log even if findings is empty or None.
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
    
    if findings:
        for f in findings:
            try:
                rule_id = getattr(f, "rule_id", "UNKNOWN-RULE")
                message_text = getattr(f, "message", "Security vulnerability flagged.")
                
                if rule_id not in seen_rules:
                    sarif_log["runs"][0]["tool"]["driver"]["rules"].append({
                        "id": rule_id,
                        "shortDescription": {"text": message_text},
                        "properties": {"precision": "high"}
                    })
                    seen_rules.add(rule_id)
                
                file_path = "unknown_file.py"
                line_num = 1
                col_num = 1
                
                if hasattr(f, "location") and f.location:
                    if hasattr(f.location, "file") and f.location.file:
                        file_path = str(f.location.file).replace("./", "", 1) if str(f.location.file).startswith("./") else str(f.location.file)
                    line_num = getattr(f.location, "line", 1) or 1
                    col_num = getattr(f.location, "column", 0) or 0

                result_node = {
                    "ruleId": rule_id,
                    "message": {"text": message_text},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": file_path},
                                "region": {
                                    "startLine": int(line_num),
                                    "startColumn": int(col_num) + 1
                                }
                            }
                        }
                    ]
                }
                sarif_log["runs"][0]["results"].append(result_node)
            except Exception as err:
                print(f"[EXPORTER WARNING] Skipping corrupted entry: {err}")

    try:
        with open(output_file, "w") as out:
            json.dump(sarif_log, out, indent=2)
        logger.info(f"💾 SARIF report successfully compiled and saved to: {output_file}")
    except Exception as e:
        print(f"❌ CRITICAL: Failed to write SARIF file: {e}")


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
    findings = []
    scan_failed = False
    
    try:
        logger.info(f"Starting scan for target: {target_path}")
        findings = asyncio.run(scanner.scan_directory(target_path))
    except Exception as e:
        logger.error(f"Execution boundary breakdown during analysis: {e}")
        scan_failed = True

    # This always executes if 'json' format is requested, even if the scan failed or threw errors
    if output_format == "json":
        export_to_sarif(findings)
        
    if scan_failed:
        sys.exit(1)
        
    if not findings:
        print("\n✅ Clean code scan! No security vulnerabilities identified.")
        return

    print(f"\n🚨 Identified {len(findings)} potential security vulnerabilities:\n")
    for finding in findings:
        print(f"[{finding.severity.name}] {finding.rule_id}: {finding.message}")
        print(f"  📍 File: {finding.location.file} (Line {finding.location.line}, Column {finding.location.column})")
        print(f"  🔍 Snippet: {finding.snippet}")
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="Application Security Testing Platform Engine")
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
        parser.print_help()

if __name__ == "__main__":
    main()
