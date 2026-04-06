"""
tools.py — Claude Code CLI 封装工具

通过 subprocess 调用 Claude Code CLI（claude -p），
以非交互模式执行文件操作和 Git 操作。
"""

import subprocess
import os
import platform
from typing import Optional
from crewai.tools import BaseTool
from pydantic import Field


class ClaudeCodeTool(BaseTool):
    """封装 Claude Code CLI 的 Tool，供 Manager 调用"""

    name: str = "claude_code_executor"
    description: str = (
        "通过 Claude Code CLI 执行文件操作、Git 命令和代码修改的非交互工具。"
        "调用方式：claude -p '指令' --dangerously-skip-permissions --add-dir <工作目录>。"
        "接收完整的自然语言指令字符串，返回 CLI 的标准输出。"
        "重要：claude -p 会直接执行操作，需确保指令明确指向正确路径。"
        "示例：'在 agent_system/README.md 末尾添加一行维护声明'"
    )

    working_dir: str = Field(
        default="/Users/wangjk/Documents/Codes/agent_system",
        description="Claude Code 执行时的工作目录"
    )

    def _run(self, instruction: str) -> str:
        """内部执行逻辑"""
        # 查找 claude 可执行文件路径
        claude_path = self._find_claude_path()
        if not claude_path:
            return "错误：未找到 claude 命令，请确保 Claude Code 已安装并配置到 PATH"

        # 构造完整指令：-p 非交互模式
        # --dangerously-skip-permissions 跳过权限确认提示
        # --add-dir 允许工具访问目录
        cmd = [
            claude_path,
            "-p",
            instruction,
            "--dangerously-skip-permissions",
            "--add-dir",
            self.working_dir
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300,
            )
            output = result.stdout if result.stdout else ""
            error = result.stderr if result.stderr else ""

            if result.returncode != 0:
                return f"执行失败 (exit {result.returncode}):\n{error}\n{output}"

            return output if output else "执行完成，无输出。"

        except subprocess.TimeoutExpired:
            return "执行超时（5分钟），任务可能过于复杂。"
        except Exception as e:
            return f"执行异常: {str(e)}"

    def _find_claude_path(self) -> Optional[str]:
        """查找 claude 命令路径"""
        system = platform.system()

        if system == "Windows":
            # 先尝试 where 命令
            try:
                result = subprocess.run(
                    ["where", "claude"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    paths = result.stdout.strip().split("\n")
                    if paths:
                        return paths[0].strip()
            except Exception:
                pass

            # 尝试常见安装路径
            common_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Claude\claude.exe"),
                r"C:\Program Files\Claude\claude.exe",
                r"C:\Users\KaiPc\AppData\Local\Programs\Claude\claude.exe",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path

        else:
            # macOS / Linux
            try:
                result = subprocess.run(
                    ["which", "claude"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass

        return None
