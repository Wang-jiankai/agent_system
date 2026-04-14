"""
main.py — CrewAI 双 Agent 自动化运维系统

Agent A (Manager): LLM 驱动，负责指令拆解、任务规划、逻辑审计
Agent B (Executor): 封装 Claude Code CLI，执行实际代码操作
"""

import os
import subprocess
import uuid
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

from tools import ClaudeCodeTool


# ============ 环境配置 ============
load_dotenv()

api_key = os.getenv("LLM_API_KEY", "")
base_url = os.getenv("LLM_BASE_URL", "")
model_name = os.getenv("LLM_MODEL", "")

if not api_key:
    raise ValueError("请在 .env 中设置 LLM_API_KEY")

# ============ LLM 初始化 ============
llm = LLM(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0.3,
)


# ============ 工具初始化 ============
REPO_ROOT = os.getenv("REPO_ROOT", "")
claude_tool = ClaudeCodeTool(working_dir=REPO_ROOT)


# ============ Agent A: Manager (指挥官) ============
manager = Agent(
    role="架构师 & 指挥官",
    goal="将模糊指令拆解为精确的可执行任务序列，并审计 Executor 的执行结果",
    backstory=(
        "你是一个理性、数据驱动的系统架构师，擅长将复杂需求分解为清晰的执行步骤。"
        "你拥有 Claude Code CLI 工具（内置 WebSearch/WebFetch MCP 能力），"
        "可通过 claude -p 执行搜索调研，确保每一步决策都有充分的事实依据。"
        "你对代码质量有极高要求，在指派任务前会明确说明修改范围和预期结果。"
    ),
    verbose=True,
    allow_delegation=True,
    tools=[claude_tool],
    llm=llm,
)


# ============ Agent B: Executor (执行者) ============
executor = Agent(
    role="代码执行者",
    goal="精确执行 Manager 分配的代码修改任务，使用 Claude Code CLI 确保修改生效",
    backstory=(
        "你是一个可靠的代码执行者，直接受 Manager 指挥。"
        "你严格遵循 ReAct 循环：Thought(思考) → Action(调用工具) → Observation(观察结果)。"
        "每次收到工具执行结果后，必须再次 Thought 并决定是否继续 Action 或给出 Final Answer。"
        "你会严格按指令操作，不多改也不少改。完成每步操作后如实报告结果。"
        "你熟悉 Git 工作流，会在独立分支上提交修改。"
    ),
    verbose=True,
    tools=[claude_tool],
    llm=llm,
    max_iter=15,
    max_retry=3,
)


# ============ 安全检查函数 ============
def check_working_tree() -> tuple[str, bool]:
    """检查当前分支和是否有未提交的修改，返回 (分支名, 是否有变更)"""
    os.chdir(REPO_ROOT)

    # 当前分支
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    current_branch = result.stdout.strip()

    # 是否有未提交的变更
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    has_changes = bool(status.stdout.strip())

    print(f"\n📍 当前分支: {current_branch}")
    return current_branch, has_changes


def prompt_pre_execution() -> str:
    """执行前让用户选择如何处理已有变更"""
    print("\n" + "=" * 60)
    print("⚠️  检测到未提交的变更")
    print("=" * 60)
    print("1. stash — 暂存现有修改，agent 在干净状态工作")
    print("2. 继续 — agent 的修改会与现有变更混在一起")
    print("3. 退出 — 先手动处理现有修改")
    print("=" * 60)

    import sys
    if sys.stdin.isatty():
        choice = input("\n▶ 选择处理方式 [3]: ").strip()
    else:
        print("\n[自动模式] 非交互环境，默认选择 3")
        choice = "3"

    return choice or "3"


def prompt_branch_strategy(current_branch: str) -> tuple[str, str]:
    """完成后让用户选择分支策略，返回 (操作, 分支名)"""
    print("\n" + "=" * 60)
    print("📋 分支策略选择")
    print("=" * 60)
    print(f"1. 提交到 {current_branch}")
    print("2. 创建新分支提交")
    print("3. 不提交，保留工作进度")
    print("=" * 60)

    import sys
    if sys.stdin.isatty():
        choice = input("\n▶ 选择分支策略 [2]: ").strip()
    else:
        print("\n[自动模式] 非交互环境，默认选择 2")
        choice = "2"

    choice = choice or "2"

    if choice == "2":
        if sys.stdin.isatty():
            branch_name = input("▶ 输入分支名: ").strip()
        else:
            branch_name = f"agent-{uuid.uuid4().hex[:8]}"
        return choice, branch_name

    return choice, ""


def human_review(plan: str) -> bool:
    """人工介入点：展示任务计划，等待用户确认"""
    print("\n" + "=" * 60)
    print("📋 MANAGER 任务计划")
    print("=" * 60)
    print(plan)
    print("=" * 60)

    import sys
    if sys.stdin.isatty():
        confirm = input("\n▶ 按 Enter 确认执行，或输入 'q' 退出: ").strip()
        return confirm.lower() != "q"
    else:
        print("\n[自动模式] 非交互环境，自动确认执行")
        return True


# ============ 主流程 ============
def run_crew_task(user_instruction: str):
    """运行 CrewAI 任务"""

    # 检查当前状态
    current_branch, has_changes = check_working_tree()

    # 执行前：处理已有变更
    if has_changes:
        choice = prompt_pre_execution()
        if choice == "3":
            print("❌ 已退出，请先手动处理现有修改")
            return
        elif choice == "1":
            subprocess.run(["git", "stash"], check=True)
            print("✅ 现有修改已 stash")

    # 创建独立工作分支
    work_branch = f"agent-{uuid.uuid4().hex[:8]}"
    subprocess.run(["git", "checkout", "-b", work_branch], check=True)
    print(f"📦 已切换到工作分支: {work_branch}")

    # 任务 1：Manager 规划
    planning_task = Task(
        description=(
            f"分析以下用户指令，将其拆解为最小可执行步骤序列。"
            f"对于每一步，明确说明：\n"
            f"1. 要操作的文件/路径\n"
            f"2. 具体修改内容（用自然语言描述，不要代码）\n"
            f"3. 执行顺序和依赖关系\n\n"
            f"用户指令：{user_instruction}\n\n"
            f"输出格式：编号列表，每条包含 [文件]、[修改内容]、[理由]"
        ),
        agent=manager,
        expected_output="结构化的任务拆解列表，每步包含文件路径和修改说明",
    )

    # 先让 Manager 规划
    crew_planning = Crew(
        agents=[manager],
        tasks=[planning_task],
        verbose=True,
    )

    print("\n🤖 Manager 正在分析指令并制定计划...")
    plan_result = crew_planning.kickoff()

    # 人工介入
    if not human_review(str(plan_result)):
        print("❌ 用户取消执行")
        return

    # 任务 2：Executor 执行
    execution_task = Task(
        description=(
            f"根据以下任务计划，使用 Claude Code Tool 执行每一步修改。\n"
            f"注意：\n"
            f"- 每个独立子任务完成后立即 git commit\n"
            f"- 严格按计划执行，不多改也不少改\n"
            f"- 如遇错误，如实报告并说明原因\n\n"
            f"任务计划：\n{plan_result}"
        ),
        agent=executor,
        expected_output="所有任务执行完毕，包含 git commit 记录",
    )

    crew_execution = Crew(
        agents=[executor],
        tasks=[execution_task],
        verbose=True,
    )

    print("\n⚙️  Executor 开始执行...")
    result = crew_execution.kickoff()
    print("\n✅ 执行结果:")
    print(result)

    # 分支策略
    choice, new_branch = prompt_branch_strategy(current_branch)

    if choice == "1":
        print(f"\n📦 提交到 {current_branch}")
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", "chore: 执行任务"], check=True)
        print("✅ 已提交")
        # 切回原分支并删除工作分支
        subprocess.run(["git", "checkout", current_branch], check=True)
        subprocess.run(["git", "branch", "-d", work_branch], check=True)
    elif choice == "2":
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", "chore: 执行任务"], check=True)
        print(f"✅ 已在 {work_branch} 提交")
        print(f"📌 可通过 'git checkout {current_branch} && git merge {work_branch}' 合并")
    else:
        print(f"\n⚠️  未提交，修改保留在工作分支 {work_branch}")
        subprocess.run(["git", "checkout", current_branch], check=True)


# ============ 入口 ============
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        instruction = " ".join(sys.argv[1:])
    else:
        instruction = (
            "检查当前仓库的 README.md，优化排版使其更符合 2026 年技术审美，"
            "并增加一段关于本仓库由 CrewAI + Claude Code 协作维护的声明。"
        )

    print(f"🚀 启动 CrewAI 任务...")
    print(f"📌 指令: {instruction}")
    run_crew_task(instruction)
