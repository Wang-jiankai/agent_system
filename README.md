# CrewAI + Claude Code 双 Agent 自动化运维系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Model](https://img.shields.io/badge/Model-MiniMax--M2.7-purple.svg)](https://www.minimaxi.com/)

## 目录

- [系统架构](#系统架构)
- [文件结构](#文件结构)
- [快速开始](#快速开始)
- [安全约束](#安全约束)
- [自定义任务示例](#自定义任务示例)

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Manager (MiniMax-M2.7)                │
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

**工作流程：**

1. 用户输入任务指令（默认测试任务或自定义指令）
2. Manager 分析指令，生成可执行的任务计划
3. Executor 通过 `claude -p` 调用 Claude Code CLI 执行文件操作
4. 每个独立模块完成后自动 git commit

## 文件结构

```
agent_system/
├── .env                  # MiniMax API 密钥配置（不提交）
├── .gitignore            # Git 忽略配置
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
# 获取 MiniMax API Key: https://platform.minimaxi.com
cp .env.example .env  # 如果有 .env.example
# 或直接创建 .env，内容如下：
```

`.env` 文件内容：

```env
MINIMAX_API_KEY=your_api_key_here
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MODEL_NAME=openai/MiniMax-M2.7
```

### 3. 运行

```bash
# 使用默认测试任务（优化 README）
python main.py

# 传入自定义指令
python main.py "检查仓库 xxx 的 README，优化排版"
```

## 安全约束

| 约束 | 说明 |
|------|------|
| 单分支模式 | 直接在 main 分支工作，无需切换 |
| 原子提交 | 每个独立模块完成后立即 git commit |
| 非交互模式 | Claude CLI 使用 `--dangerously-skip-permissions` |

## 自定义任务示例

```bash
# 检查其他仓库的 README
python main.py "检查 what-is-agent 仓库的 README，优化排版"

# 代码审查
python main.py "审查 src/ 目录下的代码质量"

# 自动更新依赖
python main.py "检查并更新 requirements.txt 中的过期依赖"
```

## 技术栈

| 组件 | 说明 |
|------|------|
| CrewAI | 多 Agent 编排框架 |
| Claude Code CLI | 代码执行工具（subprocess 封装） |
| MiniMax-M2.7 | Manager Agent 的大脑 |
| Python-dotenv | 环境变量管理 |
