# CrewAI + Claude Code 双 Agent 自动化运维系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

## 目录

- [系统架构](#系统架构)
- [文件结构](#文件结构)
- [快速开始](#快速开始)
- [安全约束](#安全约束)
- [自定义任务示例](#自定义任务示例)

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Manager (DeepSeek-V3.2)               │
│   架构师：拆解指令 → 制定计划 → 审计结果                 │
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

```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
```

### 3. 运行

```bash
# 使用默认测试任务
python main.py

# 传入自定义指令
python main.py "检查仓库 what-is-agent 的 README，优化排版"
```

## 安全约束

| 约束 | 说明 |
|------|------|
| 分支隔离 | 严禁在 main 分支操作，自动切换到 `agent-auto-update` |
| 人工介入 | Manager 生成计划后暂停，等待按 Enter 确认 |
| 原子提交 | 每个独立模块完成后立即 git commit |

## 自定义任务示例

```python
# main.py 中修改 run_crew_task 的 instruction 参数
instruction = "在 agent_system 中添加一个新工具：自动检查依赖更新"
```
