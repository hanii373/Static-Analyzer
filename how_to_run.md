# 🔍 Static Analyzer

> A hybrid static analysis tool that combines **custom rules** with **open-source security engines** to deliver fast, extensible, and developer-friendly code scanning.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)
![License](https://img.shields.io/github/license/your-org/static-analyzer?style=flat-square)
![Status](https://img.shields.io/badge/status-active%20development-yellow?style=flat-square)

---

## 📋 Overview

**Static Analyzer** is a modular security scanning tool designed to combine:

* 🧠 **Custom rule engine**
* 🔎 **Open-source SAST tools (Bandit, soon Semgrep)**
* 🧩 **Unified findings model**

Instead of reinventing every detection rule, this project **integrates proven tools** and layers custom logic on top — enabling fast results while remaining fully extensible.

---

## ⚙️ Current Capabilities

### 🔐 Static Analysis (SAST)

* ✅ Scans Python projects recursively (`*.py`)
* ✅ Detects vulnerabilities using:

  * Custom rules (e.g. `eval()` detection)
  * Integrated Bandit engine
* ✅ Outputs structured findings with:

  * File path
  * Line & column
  * Code snippet
  * Severity level

---

### 🧩 Hybrid Engine

The scanner combines multiple sources:

```text
Custom Rules + Bandit → Unified Findings
```

* All results are normalized into a single format (`Finding`)
* Designed for future integration with:

  * Semgrep (multi-language)
  * Pylint (code quality)

---

### 💻 CLI Interface

Run scans directly from terminal:

```bash
python3 -m sast_tool.cli scan <project_path>
```

Example:

```bash
python3 -m sast_tool.cli scan ./test_project
```

---

### 📍 Precise Location Tracking

Each finding includes:

* File path
* Line number
* Column number
* Code snippet

---

## 🏗️ Architecture

```text
CLI
 ↓
Scanner
 ├── Custom Rule Engine
 └── Bandit Integration
 ↓
Unified Findings Model
 ↓
Terminal Output
```

---

## 📦 Installation

```bash
git clone https://github.com/your-org/static-analyzer.git
cd static-analyzer

python3 -m venv .venv
source .venv/bin/activate
pip install bandit
```

---

## 🚀 Quick Start

Create a test project:

```python
# vuln.py
user = input()
result = eval(user)
```

Run:

```bash
python3 -m sast_tool.cli scan .
```

---

## 📊 Example Output

```text
[Severity.HIGH] Use of eval() is dangerous...
File: test_project/vuln.py
Line: 2
Snippet: result = eval(user)
```

---

## 🧠 Design Principles

* **Hybrid over reinventing** — leverage existing tools (Bandit, Semgrep)
* **Unified data model** — all findings use the same structure
* **Extensibility first** — easy to add new rules or engines
* **Fast feedback** — simple CLI-based workflow

---

## 🚧 Roadmap

### 🔜 Near Term

* [ ] Semgrep integration (multi-language support)
* [ ] Rule auto-discovery (registry system)
* [ ] Findings deduplication (aggregator)
* [ ] JSON & SARIF output

### 🔜 Mid Term

* [ ] AST-based analysis (tree-sitter)
* [ ] Taint analysis (data flow tracking)
* [ ] Code quality rules (Pylint integration)

### 🔜 Long Term

* [ ] AI-powered fix suggestions
* [ ] DAST integration (ZAP)
* [ ] CI/CD integration (GitHub Actions)
* [ ] HTML reporting dashboard

---

## 🤝 Contributing

```bash
git clone https://github.com/your-org/static-analyzer.git
cd static-analyzer
```

Set up environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## 📄 License

MIT License
