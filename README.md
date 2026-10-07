# spec-coder

`spec-coder` 是一组面向 Codex 的组合式工程技能：从需求澄清开始，经由轻量 DDD、Clean Architecture、规格和任务拆分，以 TDD 实现，并在完整审查与验证后交付。

当前版本为 `0.5.0`，插件包含九个 model-callable skills。

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

`0.5.0` 不依赖手动专用的 `grill-with-docs`、`grill-me-with-doc`、`to-spec` 或 `to-tickets`。它们的 `disable-model-invocation: true` 不应被配置、改名包装或修改全局文件绕过；discovery 直接组合可调用的 `grilling` + `domain-modeling`，规划使用本地模板。

## Default delegation

Gate 3 之后，每个 dependency-ready 且具备完整输入、边界明确且可逆的 scope、独立验证 seam，并且不携带 main-only 权限或凭据的 eligible ticket 都会 default delegation 给一个 direct subagent；单个 eligible ticket 也同样委派。显式的 request-wide opt-out、ticket-specific opt-out 或 review-specific opt-out 只在对应范围改为 main-local 执行，并禁止该范围内直接或间接 spawn。opt-out 只在当前请求的对话中生效，不写入仓库或用户配置。

main 每次只维护一个 dependency-aware active execution wave。并行 wave 为 at most four 个互不冲突的 eligible tickets，且不得超过 live Host 的 direct-child capacity；parallel mutation 必须具备 real Host/task workspace isolation。没有真实隔离时继续 default delegation，但通过 serialized direct workers 逐个执行，不能因为共享 workspace 中的文件看似不相交就并行修改。Host 暂时没有空闲 slot 时等待并重新计算；spawn unavailable 时 main 记录原因并在本地执行，除非用户明确要求 delegated execution，此时缺失能力是 blocker。

所有 Gate 解释、scope 决策、Red 或结构证据、diff 接受、fresh integration verification、归属、stage、commit、delivery 汇总及 completion claim 都是 main-only。agent tree 固定为 at most two layers，only the active main agent 可以 spawn；每个 direct-child brief 都写明 `delegation_allowed = false`，child 不得直接、间接或借助其他 skill/workflow 再委派。

delivery 默认使用两个相互独立的 read-only direct reviewers：一个执行 Standards axis，一个执行 Spec axis。request-wide opt-out 或 review-specific opt-out 会让 main 在本地完成同样的两条 review；spawn unavailable 且 delegated review 未被明确要求时也如此。若 delegated review was explicitly required，则缺失 spawn 是 blocker。main 检查 reviewer evidence 并对最终结论负责。

### Worker Progress Heartbeat

当 Host 提供 proactive child-to-main messaging 时，每个 suite-owned direct
child（implementation worker、Standards reviewer、Spec reviewer，以及 main
创建的 promotion sibling）都要按共享 `ProgressSnapshot` 契约主动上报：开始
时、active 期间每 45-60 seconds、phase change、long command 前后，以及
blocker、failure 或 completion 时立即上报。它是 conversation 中的观测证据，
不是 Host 轮询、持久状态或授权机制；短任务只需要 starting 与 terminal
snapshot，不能伪造周期更新。

`heartbeat-capability-unavailable` 表示 Host 缺少该主动消息能力，仍保留既有
delegation 和最终返回流程，不承诺插件会实现 Host 消息功能。`heartbeat-overdue`
或 Host wait timeout 只表示该观察窗口没有 message：不表示 failure 或 blocker，
也不授予 interrupt、takeover、promotion 或 local fallback 权限。所有 snapshot
都不能越过 main-only 的 diff acceptance、fresh verification 或 completion
authority；direct-child 的 `delegation_allowed = false`、不 stage/commit，及
reviewer read-only 边界保持不变。

每次 suite-owned human approval 或 mutation review 都先由 `show-me` 展示 authoritative artifact、关键决定、风险、授权效果和下一阶段，并提供 two to four 个 grounded、实质不同且带后果说明的选项；`show-me` 只呈现，不代替用户选择或授予权限。

## Optional subagent model routing

`0.5.0` 为新建 subagent 提供三挡模型：`economy`、`standard`、`strong`。插件自带 trusted bundled defaults，因此 no initial configuration 也能使用 Luna/economy、Terra/standard、Sol/strong；实际委派仍以 live Host capability 为准。active main 始终使用 current Agent/session model，routing 不会切换它；Gate 解释、scope 变更、最终架构/安全决策、改动归属、commit、delivery 聚合和 completion claim 始终是 `main-only`。

完整 agent tree 固定为两层：第 1 层是 active main，第 2 层是它的 direct subagents；只有 active main 可以 spawn/delegate。每个 child brief 必须包含 `delegation_allowed = false`，子 agent 若需要进一步拆分或委派，必须把证据和 blocker 返回 main。main 可以创建新的第 2 层 sibling 完成一次 promotion，但 child 不能直接或间接创建替代者。Host 若支持禁用 child spawn tool，应作为 defense in depth 使用；这是契约约束，不代表 Host 层沙箱隔离，也不宣称跨 Host 的 sandbox enforcement。

以下可选 trusted user 配置位于 `$XDG_CONFIG_HOME/spec-coder/model-routing.toml`；未设置 `XDG_CONFIG_HOME` 时使用 `~/.config/spec-coder/model-routing.toml`。有效用户文件会完整替换 bundled defaults，不与其合并；无效用户文件会告警并选择 `inherit-main`，不会静默回退到 bundle：

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

每一挡都可省略；出现时必须同时提供非空的 `provider` 和 `model`。bundle 中固定使用上面的三组值；用户文件中的 provider/model 仍须在使用前对照 live Host catalog 和 subagent tool interface，并不构成必需模型依赖。

目标仓库只能在 `.spec-coder/model-routing.toml` 提高安全下限，不能指定模型：

```toml
version = 1
minimum_tier = "standard"
```

有效顺序是 `economy < standard < strong < inherit-main`。缺少 mapping、模型不可用或 Host 不支持安全 override 时向上查找，最终 `inherit-main`；无效用户配置或试图注入 provider/model 的仓库策略也保守地继承 main。一次真实 delegated attempt 失败、不确定、缺少证据或越界时，保留证据并直接提升到 inherited main，不再轮询其他配置档位。required model 不可用或低于安全下限时明确报告冲突，不静默替换。

`setup-coder` 可以发现并报告仓库策略，但不会创建或修改用户/仓库 routing 配置；任何用户拥有的配置写入都需要单独展示 exact diff 并取得明确授权。

`0.5.0` 的固定映射是 Luna/economy、Terra/standard、Sol/strong。已有配置仍由用户所有，不会被安装器或 workflow 自动重写；需要调整时由用户先审阅 exact diff 并明确授权。

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

Gate 1、Gate 2、Gate 3、重新打开的 Gate 以及 suite-owned mutation authorization 都会先调用本地 `show-me`，在对话中显示简短 ASCII review map 和 two to four 个 grounded choices。完整 artifact 或 diff 仍是审批依据；图不会自动授予批准，也不依赖 tmux、编辑器或浏览器。

DDD 与 Clean Architecture 根据实际复杂度展开：明确受影响的 Bounded Context、各自的语言和状态所有权，以及必要的 Entity、Value Object、Aggregate 和 Domain Service；区分领域规则、应用编排与 adapter 转换。涉及并发、重试或跨上下文协作时，明确原子性、冲突结果、幂等与恢复责任。模型角色不必逐一对应类，小任务使用简短描述。

`plan-coder` 用本地[规格模板](./references/specification-template.md)保存这些决策，再用[ticket 模板](./references/ticket-template.md)按业务能力切出可验证增量，引用相关模型、规则、接口和测试证据。Gate 2 检查设计信息是否完整，Gate 3 检查场景覆盖与实施条件；实现和交付分别验证行为、规则归属与实际依赖。具体要求见 [Domain Design Contract](./references/domain-design-contract.md)，模型、并发与架构反例见 [Domain Design Examples](./references/domain-design-examples.md)。

```text
workspace preflight + fresh green baseline
    -> grill-coder        [`grilling` + `domain-modeling`; lazy GLOSSARY.md / ADR]
    -> design-coder        [设计审批]
    -> plan-coder          [规格审批 + tickets/实施审批]
    -> tdd-coder           [dependency-aware waves + delegated Red-Green + main integration]
    -> delivery-coder      [two-reviewer Standards/Spec review + 完整验证]
```

工作流不会自动 push、创建 PR 或发布外部 issue。完整契约见 [`references/workflow-contract.md`](./references/workflow-contract.md)。
