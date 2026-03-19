# 🔍 SAST-Tool

> A lightweight, fast, and extensible Static Application Security Testing tool
> built for modern engineering teams. Catch security vulnerabilities and code
> quality issues before they reach production — directly in your CI/CD pipeline.

![Build Status](https://img.shields.io/github/actions/workflow/status/your-org/sast-tool/ci.yml?branch=main&style=flat-square)
![Coverage](https://img.shields.io/codecov/c/github/your-org/sast-tool?style=flat-square)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)
![License](https://img.shields.io/github/license/your-org/sast-tool?style=flat-square)
![SARIF](https://img.shields.io/badge/output-SARIF%202.1.0-green?style=flat-square)
![Status](https://img.shields.io/badge/status-v1.0.0-informational?style=flat-square)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [User Stories](#user-stories)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**SAST-Tool** is an open-source static analysis engine designed to integrate
seamlessly into any engineering workflow. It analyses source code at the AST
(Abstract Syntax Tree) level using [tree-sitter](https://tree-sitter.github.io/)
grammars, applies a curated rule library covering the OWASP Top 10 and common
code quality anti-patterns, and produces structured reports in SARIF, JSON, and
HTML formats.

The tool operates entirely without executing your code, making it safe, fast,
and suitable for use in automated pipelines. It is designed with three
principles in mind:

- **Signal over noise** — every rule ships with tuned thresholds to minimise
  false positives and keep developer trust high.
- **Zero-friction integration** — a single container image and a one-line CI
  step is all that is required to get started.
- **Full transparency** — every finding includes the flagged code, a plain-
  English explanation, a CWE reference, and a suggested remediation.

---

## ✨ Features

### 🔐 Security Analysis
- Hardcoded secrets and API key detection (entropy analysis + pattern matching)
- SQL injection detection via string concatenation patterns (CWE-89)
- Path traversal detection on unsanitised file system calls (CWE-22)
- Dangerous function call detection — `eval()`, `exec()`, `os.system()` (CWE-78)
- Weak cryptography detection — MD5, SHA1, DES, RC4 (CWE-327)
- Missing input validation on external data entry points

### 🧹 Code Quality Analysis
- Cyclomatic and cognitive complexity thresholds per function
- Dead and unreachable code detection
- Duplicate code block identification via AST fingerprinting
- Function length and parameter count enforcement
- Global variable mutation detection
- Missing docstring enforcement on public interfaces

### 📤 Output & Reporting
- **SARIF 2.1.0** — native integration with GitHub Security tab and Azure DevOps
- **JSON** — structured, machine-readable findings for dashboards and scripts
- **HTML** — self-contained, shareable report with severity summary and code context
- Inline 3-line code snippets for every finding — no file-opening required

### ⚙️ Configuration & Suppression
- Single `.sast.yml` config file per repository
- Organisation-level default inheritance with per-repo overrides
- Glob-based path exclusions (`tests/**`, `vendor/**`, `*.generated.*`)
- Inline suppression via `# nosec` annotations with optional reason strings
- Per-rule severity overrides

### 🔗 CI/CD Integration
- GitHub Actions action with native SARIF upload and inline PR comments
- GitLab CI job template with Security MR widget support
- Jenkins declarative pipeline support
- Configurable quality gates: `fail_on_severity`, `max_new_findings`
- Exit code `0` (pass) / `1` (fail) for standard CI compatibility

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                          │
│         Git Repo  /  PR Diff  /  File Path  /  stdin        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    INGESTION ENGINE                         │
│      Language Detection → tree-sitter Parser → AST/CFG      │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
┌─────────────▼──────────┐  ┌──────────▼─────────────┐
│    ANALYSIS MODULES     │  │      RULE ENGINE        │
│                         │  │                         │
│  • Complexity checker   │  │  • Pattern matching     │
│  • Dead code detector   │  │  • Secrets detection    │
│  • Duplicate finder     │  │  • Injection rules      │
│  • Docstring linter     │  │  • Crypto weakness      │
└─────────────┬──────────┘  └──────────┬─────────────┘
              │                         │
              └────────────┬────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  FINDINGS AGGREGATOR                        │
│        Deduplication → CVSS Scoring → Suppression           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     OUTPUT LAYER                            │
│           SARIF 2.1.0  /  JSON  /  HTML Report              │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Responsibility |
|---|---|
| Ingestion Engine | Language detection, tree-sitter parsing, AST and CFG generation |
| Analysis Modules | Code quality checks operating on AST node traversal |
| Rule Engine | Security rules using pattern matching and AST queries |
| Findings Aggregator | Deduplication, CVSS v3.1 severity scoring, suppression handling |
| Output Layer | SARIF, JSON, and HTML serialisation |

---

## 📦 Installation

**Requirements:** Python 3.10+, pip
```bash
# Install from PyPI
pip install sast-tool

# Or run via Docker (recommended for CI)
docker pull ghcr.io/your-org/sast-tool:latest
```

---
<!--
## 🚀 Quick Start

**Scan a local directory:**
```bash
sast scan ./src
```

**Scan with a config file and produce an HTML report:**
```bash
sast scan ./src --config .sast.yml --output html
```

**Fail the pipeline on any HIGH or above finding:**
```bash
sast scan ./src --fail-on HIGH
```

**GitHub Actions — add to your workflow:**
```yaml
- name: Run SAST-Tool
  uses: your-org/sast-tool-action@v1
  with:
    config: .sast.yml
    fail-on: HIGH
    output: sarif

- name: Upload to GitHub Security tab
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results/report.sarif
```

**Suppress a false positive inline:**
```python
password = get_from_vault()  # nosec: retrieved from secret manager, not hardcoded
```

**Example `.sast.yml`:**
```yaml
version: 1

analyzer:
  languages: [python]
  exclude_paths:
    - "tests/**"
    - "vendor/**"

rules:
  enabled: ["SEC-*", "QUAL-001", "QUAL-002"]
  disabled: ["QUAL-099"]

thresholds:
  fail_on_severity: HIGH
  max_new_findings: 0

reporting:
  formats: [sarif, html]
  pr_annotation: true
```

---
-->
## 👤 User Stories

### 🧑‍💻 Developer

---

**When I** push code or open a pull request,
**I want** the static analyzer to automatically scan my changes,
**so I can** catch bugs and security issues before they reach code review.

**Acceptance Criteria:**
- [ ] Scanner triggers automatically on every push and PR
- [ ] Results appear as inline comments on the PR diff
- [ ] Only new findings are surfaced in PR mode, not pre-existing ones
- [ ] Scan completes in under 30 seconds for a typical PR diff

---

**When I** receive a finding from the analyzer,
**I want** to see the exact file, line number, and a short explanation,
**so I can** understand and fix the issue without digging through documentation.

**Acceptance Criteria:**
- [ ] Each finding shows file path, line number, and 3 lines of surrounding code
- [ ] A plain-English message explains what the problem is
- [ ] A suggested fix or remediation hint is included
- [ ] A link to the relevant CWE reference is provided

---

**When I** disagree with a finding or identify a false positive,
**I want** to suppress it inline with a `# nosec` comment,
**so I can** move forward without disabling the rule globally for the entire team.

**Acceptance Criteria:**
- [ ] `# nosec` suppresses the finding on that specific line only
- [ ] Suppressed findings are still recorded in the report, not silently dropped
- [ ] Suppressing a `CRITICAL` finding requires an explicit reason string

---

**When I** want to run the analyzer locally before pushing,
**I want** a simple CLI command I can run from my terminal,
**so I can** fix issues privately without waiting for CI to complete.

**Acceptance Criteria:**
- [ ] `sast scan .` works from the project root with zero configuration
- [ ] Output is readable in the terminal with colour-coded severity levels
- [ ] Exit code is `0` for clean scans and `1` when findings exceed the threshold

---

### 📊 Engineering Manager

---

**When I** want to understand the security posture of our codebase,
**I want** a summary report showing findings by severity and category,
**so I can** prioritise remediation work and report status to stakeholders.

**Acceptance Criteria:**
- [ ] HTML report includes a summary table broken down by severity
- [ ] Findings are grouped by rule category (Security, Quality, Style)
- [ ] Report is self-contained and shareable without any tool installation

---

**When I** onboard a new repository to the analyzer,
**I want** to configure rules, exclusions, and thresholds in a single config file,
**so I can** tailor the tool to that repo without changing shared organisation defaults.

**Acceptance Criteria:**
- [ ] A `.sast.yml` file at the repo root is automatically detected and applied
- [ ] Supports path exclusions, per-rule severity overrides, and quality gate thresholds
- [ ] Invalid config values produce a clear error message with the offending line

---

**When I** want to enforce a no-new-findings policy across all teams,
**I want** the CI pipeline to block merges that introduce findings above a set severity,
**so I can** prevent security regressions from accumulating over time.

**Acceptance Criteria:**
- [ ] Pipeline returns exit code `1` and blocks the merge when the threshold is breached
- [ ] The blocking finding is clearly identified in the CI log with a link to the PR comment
- [ ] A bypass mechanism exists for emergencies and leaves a full audit trail

---

## 🤝 Contributing

Contributions are welcome and greatly appreciated. Please read this section
carefully before opening a pull request.

### Getting Started
```bash
# 1. Fork and clone the repository
git clone https://github.com/your-org/sast-tool.git
cd sast-tool

# 2. Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3. Run the test suite to confirm everything works
pytest tests/ -v --cov=sast_tool
```

### How to Add a New Rule

1. Create a new file in `sast_tool/rules/` following the naming convention
   `<category>_<id>_<short_name>.py` (e.g. `sec_007_open_redirect.py`).
2. Extend the `Rule` base class and implement the `analyze(node, context)`
   method. Return a list of `Finding` objects.
3. Add your rule's metadata to `rules/registry.yml` — ID, name, severity,
   CWE mapping, and a one-line description.
4. Write unit tests in `tests/rules/` covering at least one true-positive
   fixture and one true-negative fixture.
5. Open a pull request with the title format: `feat(rules): add <rule-name> [CWE-XXX]`.

### Contribution Guidelines

- All pull requests must include tests. PRs without tests will not be reviewed.
- Rule false-positive rate must be below 15% when measured against the
  provided benchmark corpus (`tests/fixtures/benchmark/`).
- Follow the existing code style — `ruff` is used for linting and `black` for
  formatting. Both run automatically in pre-commit hooks.
- For significant changes (new modules, architecture changes, new rule
  categories), open an issue for discussion before writing code.
- All commits must follow [Conventional Commits](https://www.conventionalcommits.org/)
  format: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`.

### Reporting Issues

Please use the GitHub Issues tab. When reporting a false positive or false
negative, include the minimal code snippet that reproduces the finding and the
output of `sast scan --output json` on that snippet.

---

<p align="center">Built with care by the Platform Engineering team.</p>
