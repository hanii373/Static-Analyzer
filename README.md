# 🛰️ Astra Ferrum

> A unified, high-performance application security testing platform combining Structural Static Application Security Testing (SAST), Black-Box Dynamic Crawling & Fuzzing (DAST), and an AI-powered Remediation Engine. Every structural finding tracks precisely where the vulnerability lives and maps live code fixes straight to your dashboard or CI/CD pipelines.

![Build Status](https://img.shields.io/badge/build-passing-30d158?style=flat-square&logo=github)
![Python Version](https://img.shields.io/badge/python-3.10%2B-64d2ff?style=flat-square&logo=python)
![Parser Engine](https://img.shields.io/badge/parser-tree--sitter-ff2d55?style=flat-square)
![Core Framework](https://img.shields.io/badge/backend-FastAPI-009688?style=flat-square&logo=fastapi)
![AI Engine](https://img.shields.io/badge/AI-Gemini%20Flash-bf5af2?style=flat-square)
![Output Engine](https://img.shields.io/badge/output-JSON%20%7C%20SARIF-orange?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-gray?style=flat-square)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Core Features Deep Dive](#-core-features-deep-dive)
- [System Architecture & Data Flows](#-system-architecture--data-flows)
- [Installation & Environment Setup](#-installation--environment-setup)
- [Quick Start & Usage Modes](#-quick-start--usage-modes)
- [Configuration Schema (`.sast.yml`)](#-configuration-schema-sastyml)
- [Target User Profiles & Workflows](#-target-user-profiles--workflows)
- [Contributing & Extension Guide](#-contributing--extension-guide)
- [License](#-license)

---

## 🔍 Overview

**Astra Ferrum** is an open-source security testing engine designed to combine three automated detection layers into a unified execution workspace.

* **Structural SAST Engine:** Rather than relying on fragile, regular-expression pattern matching that causes excessive false positives, Astra Ferrum parses source file strings into concrete mathematical models using language-specific `tree-sitter` parsers. It analyzes the resulting Abstract Syntax Tree (AST) to evaluate syntax semantics and structural context down to individual statement nodes.
* **Black-Box DAST Pipeline:** Audits live application runtimes from an external perspective. It passes target URLs through a concurrent web crawler (`DASTCrawler`) to discover active forms, tracking parameters, and API routing schemas, before passing those targets to a scanning engine (`DASTScanner`) that injects active payloads to map dynamic application risks.
* **Defensive AI Fix Engine:** Interfaces natively with the **Gemini 2.5 Flash API** to enrich structural security reports. Instead of outputting generic vulnerability descriptions, it processes raw code context to generate ready-to-apply secure code alternatives, running through a custom sequential pacing queue to completely dodge free-tier API rate limitations.

---

## ⚙️ Core Features Deep Dive

### 🔐 SAST — Security Analysis
* **Credential Leak Detection:** Combines high-entropy calculation metrics with defined pattern constraints to flag hardcoded secrets, database connection passwords, private keys, and API tokens (**CWE-798**).
* **Injection Signature Validation:** Tracks vulnerable inputs passed directly to data layout functions without parameter protection layers, flagging SQL Injection vulnerabilities (**CWE-89**).
* **Runtime Execution Interception:** Monitors application entry points to prevent user-supplied commands from interacting directly with system loop loops, mitigating OS Command Injection risks (**CWE-78**).
* **Path Traversal Mapping:** Flags unvalidated structural directory strings used in native file-system input/output loops (**CWE-22**).
* **Dangerous Sink Enforcement:** intercepts legacy, insecure execution commands like `eval()`, `exec()`, or `os.system()` and flags them for code removal.
* **Weak Cryptography Discovery:** Highlights outdated, broken cryptographic algorithms such as MD5, SHA1, or DES when implemented within sensitive hashing or signing operations (**CWE-327**).

### 🌐 DAST — Dynamic Analysis
* **Asynchronous Web Crawler:** Discovers the attack surface by extracting anchor references, mapping active input controls, and identifying parameter boundaries across forms.
* **Session State Authentication Handling:** Injectable credential tracking parameters to handle session tracking cookies, custom HTTP header fields, or `Authorization: Bearer` OAuth token arrays.
* **OWASP Top 10 Core Coverage:**
    * *A01 Broken Access Control:* Fuzzes resource paths and tracking parameters to detect logical directory escapes.
    * *A03 Injection:* Evaluates parameter reflections across web inputs to discover Reflected Cross-Site Scripting (**XSS**) patterns.
    * *A05 Security Misconfiguration:* Audits web responses to identify missing HTTP protection layers (such as HSTS, X-Frame-Options, or CSP) and open diagnostic interfaces.

### 🤖 AI Fix & Rate-Limiting Architecture
* **Contextual Remediation:** Packages structural syntax node context directly into precise remediation queries for the Gemini API model.
* **Single-Flight Thread Isolation:** Implements an intentional class-level `asyncio.Semaphore(1)` mechanism with an active pacing window to reliably bypass free-tier rate limitations.
* **Sequential Pacing Queues:** Processes findings using an ordered sequential `for` loop, ensuring a predictable cooldown interval between requests. This completely eliminates concurrent request bursts that lead to `429 RESOURCE_EXHAUSTED` errors.

---

## 🏗️ System Architecture & Data Flows

Astra Ferrum structures operations into clean, separated tracking pipelines:

```text
[ SOURCE INPUT FILE ] ──► ( Tree-Sitter AST Engine ) ──► [ STRUCTURAL FINDINGS ]
                                                                   │
[ WEB APP TARGET ]    ──► ( Asynchronous Crawler   ) ──► [ ATTACK SURFACE FORMS ] ──► ( DAST Fuzzer )
                                                                                               │
                                                                                               ▼
[ EXPORT SECURITY REPORTS ] ◄── [ JSON TELEMETRY ] ◄── ( Sequential Gemini API ) ◄── [ AGGREGATED METRICS ]

## Ingestion
Source file contents are passed safely to the AST parser, while live endpoint URLs are routed to the web crawler.

## Analysis
The engines map code logic trees and attack surface fields concurrently to extract structural signatures.

## Enrichment
Detected vulnerabilities are normalized into standardized datasets and funneled sequentially through the Gemini API client interface.

## Reporting
Fully populated reports are rendered to the terminal stream or packaged into downloadable JSON formats.

---

# 📦 Installation & Environment Setup

## Local Workspace Setup

Initialize your virtual environment using your package management tools to insulate system dependencies:

```bash
# 1. Clone the core repository from GitHub
git clone https://github.com/hanii373/Static-Analyzer.git
cd Static-Analyzer

# 2. Build your isolated virtual tracking environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Download the exact operational package matrix
pip install --upgrade pip
pip install -r requirements.txt
pip install python-dotenv
```

## Docker Container Ingestion

Pull down the fully pre-compiled container package image from your target distribution network:

```bash
docker pull ghcr.io/hanii373/astra-ferrum:latest
```

---

# 🚀 Quick Start & Usage Modes

## 1. Configure the Local Secrets Boundary

Create a local `.env` configuration file directly in the root directory of your project workspace to manage tracking tokens securely:

```env
GEMINI_API_KEY="AIzaSyYourSecretAPIKeyProvisionedFromGoogleAIStudio"
```

## 2. Launch the Cyberpunk Web Dashboard

Spin up your local Uvicorn FastAPI dashboard server infrastructure:

```bash
python3 -m uvicorn sast_tool.dashboard.app:app --reload --port 8000
```

Open a browser window and navigate to:

```text
http://127.0.0.1:8000
```

to interact with the interface.

## 3. Run Scanning Pipelines via CLI

```bash
# Execute local folder syntax scanning operations
sast scan ./src

# Generate structured, self-contained JSON security telemetry reports
sast scan ./src --output json --export astra_report.json
```

---

# ⚙️ Configuration Schema (`.sast.yml`)

You can fully customize engine features, pass-fail quality thresholds, and paths to ignore by dropping a `.sast.yml` file into your project folder:

```yaml
version: 1

analyzer:
  languages: [python, javascript, c]
  exclude_paths:
    - "tests/**"
    - "vendor/**"
    - "**/__pycache__/**"
    - "*.generated.js"

rules:
  enabled:
    - "SEC-*"
    - "QUAL-*"
  disabled:
    - "QUAL-MISSING-DOCSTRING"

thresholds:
  fail_on_severity: HIGH
  max_new_findings: 0

reporting:
  formats: [json, html]
  rate_limiting_cooldown: 4
```

---

# 👤 Target User Profiles & Workflows

## 🧑‍💻 Security Engineer & Developer

### Pre-Staging Audits
Upload source code elements to the local sandbox interface to catch syntax errors and vulnerabilities before tracking modifications upstream.

### Visual Line Mapping
Trace vulnerabilities directly using left-aligned vertical line rails that point directly to the line causing the error.

### Drop-In Code Patching
Leverage instant, contextual code remediations to drop clean alternatives straight into development workflows.

---

## 📊 Engineering Lead / AppSec Manager

### Metrics Standardization
Export unified JSON compliance reports to monitor application risk metrics across development sprints.

### Quality Gates Enforcement
Define custom rule thresholds to block builds or flag critical vulnerabilities early in your CI pipelines.

### Cost & Resource Controls
Configure explicit pacing and throttling rules to extract maximum performance from free API resource quotas.

---

# 🤝 Contributing & Extension Guide

## Running Verification Tests

Ensure that any new syntax rules or structural logic additions match performance standards before submitting a pull request:

```bash
pytest tests/
```

## How to Add an Automated Security Rule

### Define Node Signatures
Locate or append target programming patterns inside:

```text
sast_tool/engine/rules/
```

### Write the Logic
Use the tree-sitter node capture tree to evaluate node properties, arguments, and assignment operators.

### Register the Metadata
Assign a unique tracking code (`SEC-PY-003`) inside the rule manifest configuration dictionary.

### Validate Changes
Append validation test cases inside your test folder to confirm that matches catch errors reliably without introducing regression loops.

