# CrewAI + Claude Code 双 Agent 自动化运维系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

## 简介

这是一个基于 CrewAI 框架的**双 Agent 自动化运维系统**。通过 Manager-Executor 架构，实现自然语言指令到代码修改的自动执行。

Manager Agent 负责理解用户意图、拆解任务、制定执行计划；Executor Agent 通过 Claude Code CLI 执行具体的文件操作和 Git 提交。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Manager (LLM)                        │
│   架构师：拆解指令 → 制定计划 → 审计结果               │
└─────────────────────────┬───────────────────────────────┘
                          │ 任务指派
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Executor (Claude Code)                │
│   执行者：调用 CLI → 代码修改 → Git 提交                  │
│          (ClaudeCodeTool 封装)                           │
└─────────────────────────────────────────────────────────┘
```

## 文件结构

```
agent_system/
├── .env.example          # API 密钥配置模板
├── requirements.txt      # Python 依赖
├── tools.py              # Claude Code CLI 封装 Tool
├── main.py               # CrewAI 主程序（Manager + Executor）
└── README.md             # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
cd agent_system
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件，填入你的 LLM API 配置：

```env
# LLM API（支持 OpenAI 兼容接口）
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# 或使用 SiliconFlow、MiniMax 等兼容平台
```

### 3. 运行

```bash
# 使用默认测试任务（优化 README）
python main.py

# 传入自定义指令
python main.py "检查仓库 README，优化排版使其更符合 2026 年技术审美"
```

## 工作流程

1. **输入指令** — 用户以自然语言描述任务
2. **Manager 分析** — 拆解为最小可执行步骤，生成任务计划
3. **人工确认** — 展示计划，等待用户按 Enter 确认（非交互环境下自动继续）
4. **Executor 执行** — 调用 Claude Code CLI 完成文件操作和 Git 提交
5. **结果报告** — 展示执行结果和 commit 记录

## 安全约束

| 约束 | 说明 |
|------|------|
| 原子提交 | 每个独立模块完成后立即 git commit |
| 非交互执行 | Claude CLI 使用权限跳过模式，避免人工确认中断 |

## 自定义任务示例

```bash
# 优化 README 排版
python main.py "检查并优化 README 的排版，添加维护声明"

# 代码审查
python main.py "审查 src/ 目录下的代码质量"

# 自动更新依赖
python main.py "检查并更新 requirements.txt 中的过期依赖"
```

## 技术栈

| 组件 | 说明 |
|------|------|
| [CrewAI](https://www.crewai.com/) | 多 Agent 编排框架 |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | AI 代码生成与审查工具 |
| Python-dotenv | 环境变量管理 |
| 支持 OpenAI 兼容接口的 LLM | Manager Agent 的大脑 |

