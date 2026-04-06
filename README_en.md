# CrewAI + Claude Code Dual-Agent Automation System

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Framework-purple.svg)](https://www.crewai.com/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Enabled-green.svg)](https://docs.anthropic.com/en/docs/claude-code)

*A dual-agent system where an LLM-powered Manager orchestrates tasks, and Claude Code executes them.*

[:arrow_right: 中文版](./README.md)

</div>

---

## Overview

A **CrewAI**-based dual-agent automation system. Simply输入自然语言指令，自然语言指令，系统即可自动完成代码修改，and Git submissions.

- 🤖 **Manager Agent** — LLM-driven, understands instructions, breaks down tasks, creates plans
- ⚡ **Executor Agent** — Executes file operations and Git commits via Claude Code CLI
- 🛡️ **Security Design** — Atomic commits, each step independently archived

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Manager (LLM)                        │
│                                                          │
│   "You are a rational, data-driven systems architect..."│
│                                                          │
│   Responsibilities: Analyze → Plan → Audit             │
└─────────────────────────┬───────────────────────────────┘
                          │ Task Assignment
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Executor (Claude Code)                  │
│                                                          │
│   "You are a reliable code executor..."                 │
│                                                          │
│   Responsibilities: CLI → Modify → Commit              │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
agent_system/
├── .env              # API key configuration (not committed)
├── .gitignore        # Git ignore rules
├── requirements.txt  # Python dependencies
├── tools.py          # Claude Code CLI wrapper
├── main.py           # CrewAI main program
├── README.md         # Chinese version
└── README_en.md     # English version
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd agent_system
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Create .env file
touch .env
```

Edit `.env` with your LLM configuration:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
REPO_ROOT=/path/to/your/repo
```

Compatible with: OpenAI, SiliconFlow, Azure, AI Proxy, and all OpenAI-compatible interfaces.

### 3. Run

```bash
# Default test task
python main.py

# Custom task
python main.py "Check README and optimize its layout"
```

---

## Workflow

```
User Input
     │
     ▼
┌─────────────┐
│   Manager   │  ← Analyze intent, break down tasks, generate plan
└──────┬──────┘
       │ Show Plan
       ▼
  [Press Enter to Confirm]     ← Skipped in non-interactive mode
       │
       ▼
┌─────────────┐
│  Executor   │  ← Invoke Claude Code CLI to execute
└──────┬──────┘
       │ git commit
       ▼
   Completion Report
```

---

## Security Constraints

| Constraint | Description |
|------------|-------------|
| ⚡ Atomic Commits | Each module is committed immediately after completion |
| 🔒 Permission Control | Claude CLI uses `--dangerously-skip-permissions` |

---

## Custom Task Examples

```bash
# Optimize README layout
python main.py "Check and optimize README layout"

# Code review
python main.py "Review code quality in src/ directory"

# Dependency update
python main.py "Check and update outdated dependencies in requirements.txt"
```

---

## Tech Stack

| Component | Purpose |
|-----------|---------|
| [CrewAI](https://www.crewai.com/) | Multi-Agent orchestration framework |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Code generation and review |
| Python-dotenv | Environment variable management |
| OpenAI-compatible LLM | Manager Agent's brain |

