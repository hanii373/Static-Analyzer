# sast_tool/cli.py
import argparse
import logging
import asyncio
from sast_tool.engine.scanner import Scanner
from sast_tool.reporters.json_reporter import JSONReporter
from sast_tool.reporters.html_reporter import HTMLReporter
from sast_tool.reporters.sarif_reporter import SarifReporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_scan(path: str, format_choice: str):
    """Orchestrates scanning execution mapping async coroutines securely."""
    scanner = Scanner()
    
    logger.info(f"Initializing analyzer sequence against: {path}")
    
    findings = asyncio.run(scanner.scan_directory(path))

    if format_choice == "json":
        reporter = JSONReporter()
        print(reporter.generate(findings))
    elif format_choice == "sarif":
        reporter = SarifReporter()
        print(reporter.generate(findings))
    elif format_choice == "html":
        reporter = HTMLReporter()
        reporter.generate(findings, "report.html")
        logger.info("HTML Report generation completed successfully. Saved to report.html")
    else:
        # Standard fallback console logging output text view
        if not findings:
            print("\n✅ Clean scan! No security vulnerabilities identified.")
        else:
            print(f"\n🚨 Identified {len(findings)} potential security vulnerabilities:\n")
            for f in findings:
                print(f"[{f.severity.name}] {f.rule_id}: {f.message}")
                print(f"  📍 File: {f.location.file} (Line {f.location.line}, Column {f.location.column})")
                print(f"  🔍 Snippet: {f.snippet}")
                
                # Fix: Check for 'explanation' and 'recommendation' based on your Finding model attributes
                if getattr(f, 'explanation', None):
                    print(f"  💡 AI Explanation: {f.explanation}")
                if getattr(f, 'recommendation', None):
                    print(f"  🛠️ AI Recommended Fix:\n{f.recommendation}")
                print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description="Static-Analyzer Engine CLI Harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan target file or path directory")
    scan_parser.add_argument("path", help="Path string directory target location")
    scan_parser.add_argument(
        "--format", 
        choices=["text", "json", "sarif", "html"], 
        default="text", 
        help="Target reporter generation layout view format choice"
    )

    args = parser.parse_args()

    if args.command == "scan":
        run_scan(args.path, args.format)

if __name__ == "__main__":
    main()