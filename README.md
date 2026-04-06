# CrewAI + Claude Code 双 Agent 自动化运维系统

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Framework-purple.svg)](https://www.crewai.com/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Enabled-green.svg)](https://docs.anthropic.com/en/docs/claude-code)

*A dual-agent system where an LLM-powered Manager orchestrates tasks, and Claude Code executes them.*

[:arrow_right: English Version](./README_en.md)

</div>

---

## 简介

这是一个基于 **CrewAI** 框架的双 Agent 自动化运维系统。只需输入自然语言指令，系统即可自动完成代码修改、文件操作和 Git 提交。

- 🤖 **Manager Agent** — LLM 驱动，理解指令、拆解任务、制定计划
- ⚡ **Executor Agent** — 通过 Claude Code CLI 执行文件操作和 Git 提交
- 🛡️ **安全设计** — 原子化提交，每步操作独立存档

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Manager (LLM)                        │
│                                                         │
│   "你是一个理性、数据驱动的系统架构师..."                     │
│                                                         │
│   职责：拆解指令 → 制定计划 → 审计结果                       │
└─────────────────────────┬───────────────────────────────┘
                          │ 任务指派
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Executor (Claude Code)                  │
│                                                         │
│   "你是一个可靠的代码执行者..."                             │
│                                                         │
│   职责：调用 CLI → 代码修改 → Git 提交                      │
└─────────────────────────────────────────────────────────┘
```

---

## 文件结构

```
agent_system/
├── .env              # API 密钥配置（不提交 Git）
├── .gitignore        # Git 忽略配置
├── requirements.txt  # Python 依赖
├── tools.py          # Claude Code CLI 封装
├── main.py           # CrewAI 主程序
├── README.md         # 中文版
└── README_en.md      # English version
```

---

[:arrow_left: 返回英文版](./README_en.md)

---

## 快速开始

### 1. 安装依赖

```bash
cd agent_system
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 创建 .env 文件
touch .env
```

编辑 `.env`，填入你的 LLM 配置：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.minimaxi.com/v1
LLM_MODEL=openai/MiniMax-M2.7
REPO_ROOT=/path/to/your/repo
```

支持的模型平台：OpenAI、SiliconFlow、Azure、AI Proxy 等所有 OpenAI 兼容接口。

### 3. 运行

```bash
# 默认测试任务
python main.py

# 自定义任务
python main.py "检查 README，优化排版并添加维护声明"
```

---

## 工作流程

```
用户输入指令
     │
     ▼
┌─────────────┐
│   Manager   │  ← 分析意图，拆解任务，生成执行计划
└──────┬──────┘
       │ 展示计划
       ▼
  [按 Enter 确认]     ← 非交互环境自动跳过
       │
       ▼
┌─────────────┐
│  Executor   │  ← 调用 Claude Code CLI 执行
└──────┬──────┘
       │ git commit
       ▼
   完成报告
```

---

## 安全约束

| 约束 | 说明 |
|------|------|
| ⚡ 原子提交 | 每个独立模块完成后立即 `git commit` |
| 🔒 权限控制 | Claude CLI 使用 `--dangerously-skip-permissions` |

---

## 自定义任务示例

```bash
# 优化 README 排版
python main.py "检查并优化 README 排版"

# 代码审查
python main.py "审查 src/ 目录下的代码质量"

# 依赖更新
python main.py "检查并更新 requirements.txt 中的过期依赖"
```

---

## 技术栈

| 组件 | 用途 |
|------|------|
| [CrewAI](https://www.crewai.com/) | 多 Agent 编排框架 |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | 代码生成与审查 |
| Python-dotenv | 环境变量管理 |
| OpenAI 兼容 LLM | Manager Agent 的大脑 |
