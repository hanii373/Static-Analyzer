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
