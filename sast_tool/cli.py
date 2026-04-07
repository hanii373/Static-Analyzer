import argparse

from sast_tool.engine.scanner import Scanner


def main():
    parser = argparse.ArgumentParser(
        prog="sast",
        description="Simple Static Analyzer"
    )

    subparsers = parser.add_subparsers(dest="command")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a directory")
    scan_parser.add_argument("path", help="Path to scan")

    args = parser.parse_args()

    if args.command == "scan":
        run_scan(args.path)
    else:
        parser.print_help()


def run_scan(path: str):
    scanner = Scanner()
    findings = scanner.scan_directory(path)

    if not findings:
        print("✅ No issues found")
        return

    for f in findings:
        print(f"[{f.severity}] {f.message}")
        print(f"File: {f.location.file}")
        print(f"Line: {f.location.line}")
        print(f"Column: {f.location.column}")
        print(f"Snippet: {f.snippet}")
        print("-" * 50)


if __name__ == "__main__":
    main()