Here is the raw markdown you can copy and paste directly into your `README.md` file:

```markdown
# 🔍 Static Analyzer

> A unified application security testing platform combining Static Application
> Security Testing (SAST), Dynamic Application Security Testing (DAST), and an
> AI-powered fix engine — built for modern engineering teams. Every finding tells
> you exactly where the problem is and how to fix it, directly inside your CI/CD pipeline.

![Build Status](https://img.shields.io/github/actions/workflow/status/your-org/static-analyzer/ci.yml?branch=main&style=flat-square)
![Coverage](https://img.shields.io/codecov/c/github/your-org/static-analyzer?style=flat-square)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)
![License](https://img.shields.io/github/license/your-org/static-analyzer?style=flat-square)
![SARIF](https://img.shields.io/badge/output-SARIF%202.1.0-green?style=flat-square)
![OWASP](https://img.shields.io/badge/coverage-OWASP%20Top%2010-orange?style=flat-square)
![AI](https://img.shields.io/badge/AI-Claude%20API-purple?style=flat-square)

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

**Static Analyzer** is an open-source security testing platform that combines
three capabilities in a single, CI/CD-native tool.

**SAST** analyses source code at the AST (Abstract Syntax Tree) level using
[tree-sitter](https://tree-sitter.github.io/) grammars, building a full
Control-Flow Graph and Data-Flow Graph to perform taint analysis, dataflow
analysis, and pattern matching across Python, JavaScript, TypeScript, Java,
Go, and C/C++.

**DAST** tests a running application by crawling its interface and firing real
attack payloads — covering all OWASP Top 10 categories — simulating an
external attacker with no knowledge of the source code.

**AI Fix Engine** sends every finding to the Anthropic Claude API, which
returns a plain-English explanation of the vulnerability and a ready-to-apply
code fix. Developers see not just what is wrong but exactly how to correct it.

Every finding — regardless of which engine produced it — includes the exact
file, line, column, and a code snippet with context so nothing is ever vague
or hard to locate.

The tool is built around three principles:

- **Signal over noise** — every rule ships with tuned thresholds to keep
  false-positive rates low and developer trust high.
- **Zero-friction integration** — a single container image and a one-line CI
  step is all that is required to get started.
- **Full transparency** — every finding includes the flagged code, a
  plain-English explanation, a CWE reference, an AI-generated fix, and the
  full taint propagation path where applicable.

---

## ✨ Features

### 🔐 SAST — Security Analysis

- Hardcoded secrets and API key detection (entropy analysis + pattern matching) — CWE-798
- SQL injection detection via taint analysis and string concatenation patterns — CWE-89
- OS command injection detection — CWE-78
- Path traversal detection on unsanitised file system calls — CWE-22
- Cross-Site Scripting detection (reflected, stored, DOM-based) — CWE-79
- Dangerous function call detection — `eval()`, `exec()`, `os.system()`
- Weak cryptography detection — MD5, SHA1, DES, RC4 — CWE-327
- Insecure deserialization detection — `pickle.loads`, `yaml.load` — CWE-502
- Missing input validation on external data entry points
- Security misconfigurations in application code — CWE-16
- Buffer overflow and memory management issues (C/C++) — CWE-120, CWE-121
- CSS and stylesheet injection — CWE-79
- Full taint propagation path included in every injection finding

### 🌐 DAST — Dynamic Analysis

- Automated crawler with URL discovery, form enumeration, and API endpoint mapping
- Supports session cookies, Bearer tokens, Basic auth, and custom headers
- Configurable domain scope whitelist — never scans out-of-scope targets
- OWASP Top 10 full coverage:
  - A01 Broken Access Control — IDOR, privilege escalation testing
  - A02 Cryptographic Failures — SSL/TLS probe, weak cipher detection
  - A03 Injection — SQL, LDAP, OS command, XPath fuzzing
  - A04 Insecure Design — business logic and workflow bypass testing
  - A05 Security Misconfiguration — header audit, open debug endpoints
  - A06 Vulnerable Components — version fingerprinting
  - A07 Authentication Failures — credential fuzzing, session fixation
  - A08 Integrity Failures — serialised object tampering, JWT confusion
  - A09 Logging Failures — log injection, CRLF testing
  - A10 SSRF — internal URL payload injection

### 🧹 Code Quality Analysis

- Cyclomatic and cognitive complexity thresholds per function
- Dead and unreachable code detection
- Function length and parameter count enforcement
- Global variable mutation detection
- Bare `except` clause detection
- Missing docstring enforcement on public interfaces

### 🤖 AI Fix Engine

- Powered by the Anthropic Claude API
- Every HIGH and MEDIUM finding receives an AI-generated explanation and code fix
- Fix is formatted as a unified diff — ready to apply immediately
- Claude also provides a one-sentence severity justification per finding
- False-positive confidence score included where applicable
- Cost controls configurable via `.sast.yml` — max findings, severity threshold, timeout

### 📍 Precise Error Location

- Every finding includes: file path, line number, column number
- 3-line code snippet with the flagged line highlighted
- Full taint propagation path for injection findings (SAST)
- Full HTTP request/response evidence for dynamic findings (DAST)
- Location surfaced in every output format — terminal, HTML, SARIF, PR comment

### 📤 Output & Reporting

- **SARIF 2.1.0** — native integration with GitHub Security tab and Azure DevOps
- **JSON** — structured findings with full location object and AI fix block
- **HTML** — self-contained, shareable report with severity summary, code snippets, and AI fixes
- **Terminal CLI** — colour-coded output with filename:line:col prefix

### ⚙️ Configuration & Suppression

- Single `.sast.yml` config file per repository
- Organisation-level default inheritance with per-repo overrides
- Glob-based path exclusions (`tests/**`, `vendor/**`, `*.generated.*`)
- Inline suppression via `# nosec` annotations with optional reason strings
- Per-rule severity overrides
- Baseline snapshot support — PR mode surfaces only new findings

### 🔗 CI/CD Integration

- GitHub Actions workflow with native SARIF upload and inline PR annotations
- GitLab CI job template with Security MR widget support
- Two scan modes: PR mode (diff only, < 60s) and full nightly scan (SAST + DAST)
- Configurable quality gates: `fail_on_severity`, `max_new_findings`
- Exit code `0` (pass) / `1` (fail) for standard CI compatibility

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          INPUT LAYER                            │
│      Git Repo  /  PR Diff  /  File Path  /  Target URL          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
┌──────────▼─────────────┐     ┌───────────▼──────────────┐
│      SAST ENGINE        │     │       DAST ENGINE         │
│                         │     │                           │
│  Ingestion              │     │  Spider / Crawler         │
│  ├─ Language detection  │     │  ├─ URL discovery         │
│  ├─ tree-sitter parser  │     │  ├─ Form enumeration      │
│  └─ AST / CFG / DFG     │     │  └─ API endpoint mapping  │
│                         │     │                           │
│  Analysis               │     │  Attack Modules           │
│  ├─ Taint analysis      │     │  ├─ Injection fuzzer      │
│  ├─ Dataflow analysis   │     │  ├─ XSS payload engine    │
│  ├─ CFG reachability    │     │  ├─ Auth bypass tester    │
│  ├─ Pattern matching    │     │  ├─ IDOR detector         │
│  └─ Secrets detection   │     │  └─ Misconfig scanner     │
└──────────┬─────────────┘     └───────────┬──────────────┘
           │                               │
           └───────────────┬───────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    FINDINGS AGGREGATOR                          │
│     Deduplication → CVSS Scoring → Location Enrichment          │
│     (file · line · column · snippet · taint path)               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  AI FIX ENGINE  (Claude API)                    │
│        Per-finding: explanation · code fix · severity note      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                       OUTPUT LAYER                              │
│          SARIF 2.1.0  /  JSON  /  HTML  /  CLI  /  PR comment   │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | Responsibility |
|---|---|
| SAST Engine | Source code ingestion, tree-sitter parsing, AST/CFG/DFG construction, taint and pattern analysis |
| DAST Engine | Live application crawling, OWASP Top 10 attack module execution |
| Findings Aggregator | Deduplication, CVSS v3.1 scoring, suppression, precise location enrichment |
| AI Fix Engine | Claude API integration — explanation, code fix, severity justification per finding |
| Output Layer | SARIF, JSON, HTML, CLI, and PR annotation serialisation |

---

## 📦 Installation

**Requirements:** Python 3.10+, pip

```bash
# Install from PyPI
pip install static-analyzer

# Or run via Docker (recommended for CI)
docker pull ghcr.io/your-org/static-analyzer:latest
```

---

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
- name: Run Static Analyzer
  uses: your-org/static-analyzer-action@v1
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
  languages: [python, javascript, java, go]
  exclude_paths:
    - "tests/**"
    - "vendor/**"
    - "**/*.generated.*"

rules:
  enabled: ["SEC-*", "QUAL-001", "QUAL-002"]
  disabled: ["QUAL-099"]

thresholds:
  fail_on_severity: HIGH
  max_new_findings: 0

ai:
  enrich_severity: HIGH
  max_findings: 50
  timeout_seconds: 15

reporting:
  formats: [sarif, html, json]
  pr_annotation: true
```

---

## 👤 User Stories

### 🧑‍💻 Developer

---

**When I** push code or open a pull request,
**I want** the analyzer to automatically scan my changes,
**so I can** catch bugs and security issues before they reach code review.

**Acceptance Criteria:**
- [ ] Scanner triggers automatically on every push and PR
- [ ] Results appear as inline comments on the PR diff with an AI-generated fix
- [ ] Only new findings are surfaced in PR mode, not pre-existing ones
- [ ] Scan completes in under 60 seconds for a typical PR diff

---

**When I** receive a finding from the analyzer,
**I want** to see the exact file, line number, column, and a code snippet,
**so I can** understand and fix the issue without opening any other tool.

**Acceptance Criteria:**
- [ ] Each finding shows file path, line number, column, and 3 lines of surrounding code
- [ ] A plain-English explanation of the vulnerability is included
- [ ] An AI-generated code fix formatted as a diff is attached to every HIGH+ finding
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
- [ ] HTML report includes a severity summary with SAST and DAST findings separated
- [ ] Findings are grouped by rule category (Security, Quality)
- [ ] Report is self-contained and shareable without any tool installation
- [ ] AI explanations are included in the report for every HIGH+ finding

---

**When I** onboard a new repository to the analyzer,
**I want** to configure rules, exclusions, and thresholds in a single config file,
**so I can** tailor the tool to that repo without changing shared organisation defaults.

**Acceptance Criteria:**
- [ ] A `.sast.yml` file at the repo root is automatically detected and applied
- [ ] Supports path exclusions, per-rule severity overrides, quality gate thresholds, and AI cost controls
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
git clone https://github.com/your-org/static-analyzer.git
cd static-analyzer

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
2. Extend the `Rule` base class and implement the `analyze(tree, source, path)`
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
- Security-critical components (taint engine, Claude API client, DAST attack
  modules) require two approving reviews, one from the Application Security team.
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

> **Note:** The Claude API key must be stored as an environment variable or
> in a secrets manager. It must never appear in source code, config files,
> or logs.

---

## 📄 License

This project is licensed under the MIT License.
See the [LICENSE](./LICENSE) file for full terms.

---

<p align="center">Built by the Platform Engineering team.</p>
```

Just replace `your-org` with your actual GitHub organisation name before publishing.