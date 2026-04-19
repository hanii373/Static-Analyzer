from typing import List
from sast_tool.engine.models import Finding


class HTMLReporter:
    def report(self, findings: List[Finding]) -> str:
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
                html += f"""
                <div class="card {f.severity}">
                    <h3>[{f.severity}] {f.message}</h3>
                    <p class="file">{f.location.file}:{f.location.line}:{f.location.column}</p>

                    <div class="snippet">{f.snippet}</div>

                    {"<div class='ai'><strong>Explanation:</strong><p>" + f.explanation + "</p></div>" if f.explanation else ""}

                    {"<div class='ai'><strong>Recommendation:</strong><p>" + f.recommendation + "</p></div>" if hasattr(f, "recommendation") and f.recommendation else ""}
                </div>
                """

        html += """
        </body>
        </html>
        """

        return html