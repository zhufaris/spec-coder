# Agent 安装指南

本文供编码 Agent 使用。目标是把 `spec-coder` 安装到当前用户的 Codex 环境，并确认完整工作流可被新会话发现。

本指南对应 `spec-coder 0.8.0`，安装后应发现九个本地 skills。

## 执行边界

- 默认只修改当前用户的 Codex 插件配置，不使用 `sudo`。
- 不提交、推送或改写用户仓库中的现有变更。
- 不覆盖用户的全局 `AGENTS.md`；启用默认路由前先检查并合并受管理区块。
- 遇到当前路径必需的依赖缺失、安装权限问题或无法识别的安装状态时，停止并报告实际输出，不猜测替代方案。
- 安装或升级后必须启动新的 Codex 会话验证；当前会话的 skill 列表不会自动刷新。

## 1. 前置检查

在仓库根目录执行：

```bash
command -v codex
git status --short --branch
test -f .codex-plugin/plugin.json
test -x scripts/install-local.sh
```

继续安装前应满足：

- `codex` 可在 `PATH` 中找到。
- 当前目录是 `spec-coder` 仓库根目录。
- 插件清单和本地安装脚本存在。

工作区可以有用户自己的未提交变更，但不要修改或清理它们。若 `codex` 不存在，停止并请用户先安装或配置 Codex CLI。

## 2. 校验插件源码

先运行仓库自带验证：

```bash
./scripts/validate.sh
```

该命令会运行契约测试、逐个校验九个 skill，并检查 Git whitespace。只有验证成功后才继续。若验证器路径不是默认位置，可显式传入：

```bash
SKILL_VALIDATOR=/absolute/path/to/quick_validate.py ./scripts/validate.sh
```

不要为了绕过失败而删除测试、跳过校验或修改用户环境。

## 3. 注册 marketplace 并安装

### 从当前 clone 安装

推荐执行仓库脚本：

```bash
./scripts/install-local.sh
```

它等价于：

```bash
codex plugin marketplace add "$(pwd)"
codex plugin add spec-coder@spec-coder
```

本地安装会关联当前 checkout。不要在安装后移动或删除该目录。

### 从 Git 仓库安装

仅当当前 Git 凭据可以访问私有仓库时使用：

```bash
codex plugin marketplace add zhufaris/spec-coder
codex plugin add spec-coder@spec-coder
```

若仓库认证或网络访问失败，报告错误并等待用户处理凭据或授权。

## 4. 验证注册状态

执行：

```bash
codex plugin list --json
```

输出中应能找到已安装且启用的 `spec-coder@spec-coder`。同时可以确认 marketplace 已注册：

```bash
codex plugin marketplace list --json
codex plugin list --json
```

不要仅依据安装命令的退出码宣布成功；保留并检查 `plugin list` 的实际输出。

## 5. 检查运行时依赖

`plan-coder` 的规划能力和模板包含在插件内；其他阶段所需的上游 skills 不会自动安装。启动一个新的 Codex 会话，通过 `/skills` 确认本插件和当前执行路径所需的上游 skills 可见且允许模型调用：

- 本插件：`spec-coder`、`grill-coder`、`design-coder`、`plan-coder`、`tdd-coder`、`delivery-coder`、`show-me`、`using-git-worktrees`、`setup-coder`
- Matt Pocock：`grilling`、`domain-modeling`、`codebase-design`、`tdd`、`code-review`
- Superpowers：`verification-before-completion`
- Architecture：`clean-architecture`

若九个本插件 skills 不可见，先确认插件已启用并再次启动新的 Codex 会话。若当前路径必需的上游 skill 缺失、仅限手动调用或契约不兼容，停止并报告具体证据；不要用名称相近的 skill 替代。原地执行不调用本地 `using-git-worktrees`；选定隔离路径后才使用它，无法隔离时按 workspace 规则决定是否有符合用户要求的安全替代方案。依赖与源快照见 [Upstream Compatibility](./references/upstream-compatibility.md)。

`design-coder` 在 interactive 与 autonomous 两种模式中都原生负责保守分类、方案比较与
Gate 路由，并按适用性组合 `domain-modeling`、`codebase-design` 与
`clean-architecture`。`brainstorming` 不属于必需 capability；用户仍可在本编排之外手动调用。

`grill-with-docs`、`grill-me-with-doc`、`to-spec`、`to-tickets` 和当前 Matt `implement-spec` 都不是 `0.8.0` 的依赖。当前 Matt `implement-spec` 声明 `disable-model-invocation: true`，因此仅为 provenance，不是 dependency；其他 manual-only skill 也不能由其他 skill 调用。fresh Codex session 或启用配置不会改变这个边界。不要修改 upstream 标志、包装改名或通过文件读取间接执行。`grill-coder` 直接组合可调用的 `grilling` + `domain-modeling`，原生 `plan-coder` 使用随插件安装的模板，native implement-spec executor 在 Gate 3 后执行批准的计划。

Task Playbook 是 `spec-coder` 的内部兼容性契约：每个任务仅选择 Feature、Bug Fix、
Refactor、Performance、Skill Change、Workflow Eval 或 Generic 之一，以调整 evidence
obligations，不增加 skill 或安装步骤，也不改变 Gate 1/2/3、native implement-spec executor
或两层 agent tree。Cursor `pstack` 是 MIT provenance，**not a dependency**：不需要
install、configuration 或 runtime invocation。详细的 route/proof contract 与 pstack
boundary 见 [Task Playbook contract](./references/task-playbook-contract.md) 和
[Upstream Compatibility](./references/upstream-compatibility.md)。

新任务先选择安全的 selected workspace，并记录 path、mode、base、initial changes 与
capabilities；随后才能进行 read-only discovery 和 design。selected-only 状态不得有
target-project writes。`grill-coder` 使用可调用的 `grilling` decision-tree frontier rounds：每轮最多三个 dependency-ready、相互独立的问题；scope、domain meaning/ownership、core invariant、architecture、overlapping coupling 或 unknown coupling 保持串行。每题提供稳定 `Qn`、适用选项和独立 recommendation/reason；多题轮次须以 `Qn: default` 接受单题推荐，partial answer 只确认明确 ID，ambiguous answer 先单题澄清并重算 frontier。repository facts 由 agent 检查而非询问用户。已明确确认的规范领域术语可以惰性更新适用的 `GLOSSARY.md`；只有难以逆转、脱离上下文会令人意外且基于真实取舍的架构决定才写 ADR。没有符合条件的决定就不产生文档写入，目标文档存在所有权冲突时必须停止。

workspace preparation 负责依赖准备与 fresh green baseline，必须在首次符合条件的
`GLOSSARY.md`/ADR 写入前完成；也可在 Gate 1 后、进入 `plan-coder` 前完成。进入规格
写入前，`plan-coder` 会重新验证 prepared workspace。

### 验证 bundled 工具

除九个 skills 外，安装来源必须包含 `scripts/verification-evidence.py`、
`scripts/check-artifacts.py` 和 `scripts/spec_coder_checks/`。不需要额外 Python 包，
需要 Python 3.11+ 和 Git。在已确认的 plugin root 执行以下只读检查：

```bash
python3 -c 'import sys; assert sys.version_info >= (3, 11), sys.version'
git --version
test -f scripts/spec_coder_checks/evidence.py
test -f scripts/spec_coder_checks/workspace.py
test -f scripts/spec_coder_checks/artifacts.py
test -f scripts/spec_coder_checks/waves.py
python3 -B scripts/verification-evidence.py --help
python3 -B scripts/check-artifacts.py --help
```

全部应 exit 0；路径缺失、Python/Git 不满足或 import 失败时报告具体命令/output，
不要把工具缺失当成已通过检查。在其他 target-project cwd 调用时，使用已验证的
plugin root 下脚本绝对路径；不要从 target cwd 猜测 `./scripts/`。
这些 smoke checks 不执行项目 baseline，也不安装任何东西。

实际流程参数见 [Verification contract](./references/verification-contract.md#worked-invocation)
和 [Artifact format](./references/artifact-format.md#command-interface)。首个 baseline
始终 fresh，capture 可指定未来 active artifact 路径并把 JSON 留在对话中，baseline
成功后才进行 target-project document writes。Planning reuse interface 对同一 uninterrupted request 保持紧凑：planning
才可比较每条 required baseline，main 需确认记录来源及依赖/环境，工具不能验证这些声明的
真实性；仅在 standalone、resume、malformed 或 uncertain evidence，以及 rerun fallback 时
加载完整 verification 细节。
查看 child `exit_code` 和 `reasons`，不能把 capture exit 1 一律当成 baseline 失败。
缺失/不确定证据重跑；resume、integrated checks 与 final full suite 始终 fresh。
新模板的 spec/plan 在 Gate 2/3 前检查，delivery phase 要求完成与记录字段；旧格式
明确 unsupported，走人工 review 或范围内格式规范化。工具不会执行文档命令、
批准 gate、改 checkbox 或证明记录真实。

### 运行时工作流契约

安装成功后，能力与日常 workflow map 见 [README.md](./README.md)。委派、durable
waves、并行隔离、main-only authority 和 `ProgressSnapshot` heartbeat emitter 由
[Subagent routing contract](./references/subagent-routing-contract.md) 维护；reopened
Gate 3 的 canonical barrier 由 [Workflow contract](./references/workflow-contract.md#reopened-gate-3-scheduling-barrier)
维护。安装器不实现或配置 Host 消息适配器。需要执行该路径时，按
[Explicit Parallel Requests](./references/subagent-routing-contract.md#explicit-parallel-requests)
和 [Worker Progress Heartbeat](./references/subagent-routing-contract.md#worker-progress-heartbeat)
读取当前规则。Interactive Gate 仍先用 `show-me`。Autonomous selection does not invoke `show-me`。

### 可选：覆盖 bundled model defaults

插件 bundled defaults 已固定把 `economy`、`standard`、`strong` 映射到 Luna、Terra、Sol，因此 no initial configuration 即可进行 routing。main 始终使用 current Agent/session model；routing 只影响新建 subagent，不会切换 main。若要覆盖 defaults，只在以下 trusted user 配置中映射 live Host 提供的 provider/model：

```text
$XDG_CONFIG_HOME/spec-coder/model-routing.toml
~/.config/spec-coder/model-routing.toml  # XDG_CONFIG_HOME 未设置时
```

```toml
version = 1

[tiers.economy]
provider = "trae"
model = "GPT-5.6-Luna"

[tiers.standard]
provider = "trae"
model = "GPT-5.6-Terra"

[tiers.strong]
provider = "trae"
model = "GPT-5.6-Sol"
```

每个 table 必须同时含非空 `provider` 和 `model`。有效用户文件会完整替换 bundled defaults，不进行逐档合并；无效用户文件会告警并选择 `inherit-main`，不会使用 bundle。安装过程不验证、下载或启用模型；Agent 每次委派前仍需检查 live Host catalog 与 subagent tool interface。

仓库可以用 `.spec-coder/model-routing.toml` 提高最低档位：

```toml
version = 1
minimum_tier = "standard"
```

仓库策略只允许 `version` 和 `minimum_tier`，后者可为 `economy`、`standard`、`strong` 或 `inherit-main`；不得包含 provider/model。缺失 mapping 或 Host 能力时按 `economy -> standard -> strong -> inherit-main` 向上 fallback。delegated attempt 失败或越界时直接提升到 inherited main 一次，不逐档重试。Gate、scope、最终架构/安全决策、commit 和 completion 都是 `main-only`，配置不会切换 active main model。

Agent tree 固定为两层：只有 active main 可以创建第 2 层 direct subagent。每个 child brief 必须明确写入 `delegation_allowed = false`；child 不得直接或间接再委派，需要更多 agent 时返回证据和 blocker 给 main。promotion 也由 main 创建新的第 2 层 sibling。若 Host 支持移除 child spawn tool，应启用该 defense in depth；否则仍执行同一契约，并明确这不是 Host 层沙箱隔离。

`setup-coder` 只发现和报告该仓库策略，不自动创建或修改这两个配置。若确需创建或编辑用户拥有的配置，必须作为独立 mutation 展示 exact diff 并获得明确授权。

`0.8.0` 使用 Luna/economy、Terra/standard、Sol/strong。安装器不会自动迁移已有用户配置；任何调整都需要先展示 exact diff 并由用户明确授权。

## 6. 初始化目标仓库

安装后在新的 Codex 会话中，用户可以显式要求“使用 `setup-coder` 初始化当前仓库”。它默认检查并提议维护 repository-local `AGENTS.md` 受管理区块，以及根 `.gitignore` 的精确 `/.worktrees/` 和 `/.cache/` 条目，同时报告 Host capabilities 和仓库验证命令；三项在同一次 exact-diff review 中确认。不要仅因执行 setup 创建 worktree、规格、tickets、提交或安装依赖。

## 7. 可选：启用全局默认路由

只有用户明确希望代码修改请求默认进入 `spec-coder` 时，才执行本节。

只有用户明确要求 global scope 时，才打开全局 `~/.codex/AGENTS.md` 并检查以下标记：

```text
<!-- spec-coder:start -->
<!-- spec-coder:end -->
```

- 若标记不存在，将 [`assets/agents-snippet.md`](./assets/agents-snippet.md) 的完整内容追加到文件。
- 若标记已经存在，只用模板内容更新这两个标记之间的区块。
- 保留标记之外的所有用户内容，不要覆盖整个文件。

修改后向用户展示 diff，并说明该规则只对后续会话生效。

## 8. 最终验收

运行时可由当前用户在单次请求中明确传入 `autonomous=true`。该选择是
request-scoped，default is false，不写入安装配置，也不能从 repository/global
config、`AGENTS.md`、历史或 subagent 推断。它只在存在唯一 recommended 选项时
跳过 Gate 1、Gate 2、Gate 3 的人工等待；design、spec、tickets、durable waves、
review 与 verification 仍完整执行。scope expansion、push、install、发布、配置、
凭据、破坏性操作及其他 separate authorization 不在该授权内。

interactive design 会先保守分类：只有 existing seam、one coherent outcome 以及所有
architecture/interface/cross-context 排除条件都有 repository evidence 时才属于 bounded；
unknown 属于 architectural。bounded 路径把 alternatives、recommended short design、
risks 与 testing seam 合并到 one Gate 1，非推荐选择返回 elaboration 后再次请求 Gate 1；
architectural 路径保留独立 approach selection 与 Gate 1。两条路径都保留 Gate 2、Gate 3
及后续权限边界；autonomous 路径仍要求 one grounded recommendation。

在新的 Codex 会话中完成以下检查：

1. `/skills` 能看到九个 `spec-coder` skills，包括本地 `show-me`、`using-git-worktrees` 和 `setup-coder`。
2. 当前执行路径必需的上游依赖 skills 都可见且允许模型调用；原地执行无需 `using-git-worktrees`，discovery 与规划均不依赖四个 manual-only wrappers。
3. 发起一个只读问题时，不应自动进入 `spec-coder`。
4. 发起一个代码修改请求时，应进入 `spec-coder`；如果未配置默认路由，则显式要求“使用 spec-coder”。

最终报告应包含：安装来源、本地源码校验结果、`plugin list` 状态、缺失依赖（如有）以及是否配置了默认路由。

## 故障排查

### `codex is not available on PATH`

不要继续。报告 `command -v codex` 失败，并请用户安装 Codex CLI 或修正 `PATH`。

### 找不到 skill validator

确认当前用户的系统 skill 安装位置，然后通过 `SKILL_VALIDATOR` 指向真实的 `quick_validate.py`。不要伪造或跳过源码验证。

### 插件已安装，但 `/skills` 看不到

依次确认：

1. `codex plugin list --json` 中插件存在且已启用。
2. 已完全退出并新建 Codex 会话。
3. 安装所引用的本地 checkout 仍然存在。

仍不可见时，报告上述三项的实际结果，不要重复盲目安装。

构建缓存与临时文件边界：分支 source worktree 使用 `<repo>/.worktrees/<branch>`，构建缓存使用 `<repo>/.cache/<branch>/target`。`/tmp` 仅用于 disposable small files，不得存放 source worktree、build cache、workflow artifact、verification evidence 或 recovery state。

### 上游依赖缺失

先判断依赖是否属于当前执行路径。本地 `using-git-worktrees` 只在隔离路径使用；这些 manual-only skills 均不在依赖集合中。必需外部依赖缺失或禁止模型调用时，列出精确名称、Host 可见性和调用资格证据，并按 [Upstream Compatibility](./references/upstream-compatibility.md) 停止；仅恢复实际必需且允许调用的能力。重启不会解除 `disable-model-invocation: true`。
