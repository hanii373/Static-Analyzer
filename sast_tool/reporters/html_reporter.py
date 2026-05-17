from typing import List
from sast_tool.engine.models import Finding


class HTMLReporter:
    def report(self, findings: List[Finding]) -> str:
        """Generates the raw HTML string for the security dashboard."""
        html = """
        <html>
        <head>
            <title>Static Analyzer Report</title>
            <style>
                body { font-family: Arial; background: #0f172a; color: #e2e8f0; }
                h1 { color: #38bdf8; }
                .card {
                    background: #1e293b;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                }
                .HIGH { border-left: 5px solid red; }
                .MEDIUM { border-left: 5px solid orange; }
                .LOW { border-left: 5px solid green; }
                .file { color: #94a3b8; }
                .snippet {
                    background: #020617;
                    padding: 10px;
                    margin-top: 5px;
                    font-family: monospace;
                }
                .ai {
                    background: #020617;
                    padding: 10px;
                    margin-top: 10px;
                    border-left: 4px solid #38bdf8;
                }
            </style>
        </head>
        <body>
            <h1>🔍 Static Analyzer Report</h1>
        """

        if not findings:
            html += "<p>✅ No issues found</p>"
        else:
            for f in findings:
                # Use getattr fallback in case attributes differ across platforms
                explanation = getattr(f, "explanation", "")
                recommendation = getattr(f, "recommendation", "")

                html += f"""
                <div class="card {f.severity.name if hasattr(f.severity, 'name') else f.severity}">
                    <h3>[{f.severity.name if hasattr(f.severity, 'name') else f.severity}] {f.message}</h3>
                    <p class="file">{f.location.file}:{f.location.line}:{f.location.column}</p>

                    <div class="snippet">{f.snippet}</div>

                    {"<div class='ai'><strong>Explanation:</strong><p>" + explanation + "</p></div>" if explanation else ""}

                    {"<div class='ai'><strong>Recommendation:</strong><p>" + recommendation + "</p></div>" if recommendation else ""}
                </div>
                """

        html += """
        </body>
        </html>
        """

        return html

    def generate(self, findings: List[Finding], output_path: str = "report.html") -> None:
        """
        Fix: Added the missing generate method expected by cli.py.
        Compiles the HTML report and writes it directly to disk.
        """
        html_content = self.report(findings)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)