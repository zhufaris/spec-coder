# spec-coder

`spec-coder` 是一组面向 Codex 的组合式工程技能：从需求澄清开始，经由轻量 DDD、Clean Architecture、规格和任务拆分，以 TDD 实现，并在完整审查与验证后交付。

当前版本为 `0.4.0`，插件包含九个 model-callable skills。

它参考 Matt Pocock skills 的“小而可组合”结构。插件负责阶段编排、审批门禁、产物位置和 Git 安全策略；`plan-coder` 使用本插件维护的模板完成规格合成与任务拆分，其余阶段组合允许模型调用的上游能力。

## Skills

| Skill | 用途 |
| --- | --- |
| `spec-coder` | 总入口；识别新任务或恢复点，并编排完整流程 |
| `grill-coder` | 组合 `grilling` + `domain-modeling` 逐问澄清，并惰性记录已确认的领域语言或 ADR |
| `design-coder` | 比较 2–3 个方案，完成轻量 DDD 与 Clean Architecture 设计 |
| `plan-coder` | 重新验证已准备的 workspace，再生成规格和垂直 tickets |
| `tdd-coder` | 对单个 ticket 执行 Red–Green、局部验证和原子提交 |
| `delivery-coder` | 对照规格审查、修复问题并运行完整验证 |
| `show-me` | 在每次 suite-owned 审批前生成紧凑的 inline ASCII review map |
| `using-git-worktrees` | 在选定隔离路径后复用或创建安全的可选 Git worktree |
| `setup-coder` | 手动、幂等地检查并初始化目标仓库的 spec-coder 使用方式 |

## Install

供 Agent 执行的完整安装、验证与故障排查流程见 [`INSTALL.md`](./INSTALL.md)。

从已经 clone 的仓库安装：

```bash
./scripts/install-local.sh
```

等价的显式命令是：

```bash
codex plugin marketplace add /absolute/path/to/spec-coder
codex plugin add spec-coder@spec-coder
```

也可以通过 GitHub 仓库注册 marketplace 后安装：

```bash
codex plugin marketplace add zhufaris/spec-coder
codex plugin add spec-coder@spec-coder
```

私有仓库安装依赖当前环境已有访问该仓库的 Git 凭据。安装或升级后启动 fresh Codex session，再通过 `/skills` 检查九个 skill 是否出现。

## Dependencies

本仓库保持 wrapper 精简，因此运行时需要以下上游 skills：

- Matt Pocock：`grilling`、`domain-modeling`、`codebase-design`、`tdd`、`code-review`
- Superpowers：`brainstorming`、`verification-before-completion`
- Architecture：`clean-architecture`

必需依赖须在当前 Host catalog 中可见、允许模型调用且输入输出契约兼容；仅有磁盘文件或启用配置不够。`using-git-worktrees` 已随插件本地化，只在选定隔离路径后调用；原地执行不调用它。详情见 [`references/upstream-compatibility.md`](./references/upstream-compatibility.md)。

`0.4.0` 不依赖手动专用的 `grill-with-docs`、`grill-me-with-doc`、`to-spec` 或 `to-tickets`。它们的 `disable-model-invocation: true` 不应被配置、改名包装或修改全局文件绕过；discovery 直接组合可调用的 `grilling` + `domain-modeling`，规划使用本地模板。

## Optional subagent model routing

`0.4.0` 可以只为新建 subagent 配置三挡模型：`economy`、`standard`、`strong`。它不会切换 active main model；Gate 解释、scope 变更、最终架构/安全决策、改动归属、commit、delivery 聚合和 completion claim 始终是 `main-only`。

可信的用户配置位于 `$XDG_CONFIG_HOME/spec-coder/model-routing.toml`；未设置 `XDG_CONFIG_HOME` 时使用 `~/.config/spec-coder/model-routing.toml`：

```toml
version = 1

[tiers.economy]
provider = "trae"
model = "GPT-5.6-Luna"

[tiers.standard]
provider = "trae"
model = "GPT-5.6-Sol"

[tiers.strong]
provider = "trae"
model = "GPT-5.6-Terra"
```

每一挡都可省略；出现时必须同时提供非空的 `provider` 和 `model`。这些名称只是示例，实际选择前以 live Host catalog 和 subagent tool interface 为准，不构成必需模型依赖。

目标仓库只能在 `.spec-coder/model-routing.toml` 提高安全下限，不能指定模型：

```toml
version = 1
minimum_tier = "standard"
```

有效顺序是 `economy < standard < strong < inherit-main`。缺少 mapping、模型不可用或 Host 不支持安全 override 时向上查找，最终 `inherit-main`；无效用户配置或试图注入 provider/model 的仓库策略也保守地继承 main。一次真实 delegated attempt 失败、不确定、缺少证据或越界时，保留证据并直接提升到 inherited main，不再轮询其他配置档位。required model 不可用或低于安全下限时明确报告冲突，不静默替换。

`setup-coder` 可以发现并报告仓库策略，但不会创建或修改用户/仓库 routing 配置；任何配置写入都需要单独展示 exact diff 并取得授权。

## Default routing

在目标仓库中手动调用 `setup-coder`，它会默认检查并提议维护 repository-local `AGENTS.md`。权威模板为 [`assets/agents-snippet.md`](./assets/agents-snippet.md)；写入前展示精确 diff，重复运行应为零 diff。全局 `~/.codex/AGENTS.md` 只在用户明确要求 global scope 并单独批准 diff 时修改。只读解释、状态查询、调查和 review 不会自动进入此流程；使用 `skip spec-coder` 或 `directly modify` 可显式跳过。

## Validate

```bash
./scripts/validate.sh
```

验证包括仓库契约测试、九个 skill 的官方格式检查，以及 Git whitespace 检查。

## Workflow

Discovery 开始前先完成 workspace preflight，并取得 fresh green baseline。Worktree 可选：已有安全 worktree 就复用；改动集中、文件归属清楚且不会干扰其他工作时可原地执行；并行开发或难以分离的已有改动优先隔离。Agent 根据任务与用户偏好说明选择，无需新增创建/跳过审批。两种方式都检查初始 Git 状态、保护用户改动、验证基线并保持提交范围清晰；缺少隔离工具时，仅在原地执行安全且符合用户要求的情况下继续。

`grill-coder` 在预检后逐问确认决策。只有明确确认的规范术语、上下文含义或 invariant 才会惰性创建或更新适用的 `GLOSSARY.md`；只有难以逆转、脱离上下文会令人意外且确有取舍的架构决策才写 ADR。其他决定保留在对话中，文档归属冲突则停止写入。`plan-coder` 在落盘规格前重新验证 prepared workspace。

Gate 1、Gate 2、Gate 3、重新打开的 Gate 以及 suite-owned mutation authorization 都会先调用本地 `show-me`，在对话中显示简短 ASCII review map。完整 artifact 或 diff 仍是审批依据；图不会自动授予批准，也不依赖 tmux、编辑器或浏览器。

DDD 与 Clean Architecture 根据实际复杂度展开：明确受影响的 Bounded Context、各自的语言和状态所有权，以及必要的 Entity、Value Object、Aggregate 和 Domain Service；区分领域规则、应用编排与 adapter 转换。涉及并发、重试或跨上下文协作时，明确原子性、冲突结果、幂等与恢复责任。模型角色不必逐一对应类，小任务使用简短描述。

`plan-coder` 用本地[规格模板](./references/specification-template.md)保存这些决策，再用[ticket 模板](./references/ticket-template.md)按业务能力切出可验证增量，引用相关模型、规则、接口和测试证据。Gate 2 检查设计信息是否完整，Gate 3 检查场景覆盖与实施条件；实现和交付分别验证行为、规则归属与实际依赖。具体要求见 [Domain Design Contract](./references/domain-design-contract.md)，模型、并发与架构反例见 [Domain Design Examples](./references/domain-design-examples.md)。

```text
workspace preflight + fresh green baseline
    -> grill-coder        [`grilling` + `domain-modeling`; lazy GLOSSARY.md / ADR]
    -> design-coder        [设计审批]
    -> plan-coder          [规格审批 + tickets/实施审批]
    -> tdd-coder           [逐 ticket Red-Green + 原子提交]
    -> delivery-coder      [审查 + 完整验证]
```

工作流不会自动 push、创建 PR 或发布外部 issue。完整契约见 [`references/workflow-contract.md`](./references/workflow-contract.md)。
