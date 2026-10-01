# spec-coder

`spec-coder` 是一组面向 Codex 的组合式工程技能：从需求澄清开始，经由轻量 DDD、Clean Architecture、规格和任务拆分，以 TDD 实现，并在完整审查与验证后交付。

它参考 Matt Pocock skills 的“小而可组合”结构，但不复制上游 skill 内容。仓库中的 wrapper 负责固定阶段、审批门禁、产物位置和 Git 安全策略。

## Skills

| Skill | 用途 |
| --- | --- |
| `spec-coder` | 总入口；识别新任务或恢复点，并编排完整流程 |
| `grill-coder` | 单问题需求拷问，并默认给出推荐选项 |
| `design-coder` | 比较 2–3 个方案，完成轻量 DDD 与 Clean Architecture 设计 |
| `plan-coder` | 创建隔离 worktree、建立基线、生成规格和垂直 tickets |
| `tdd-coder` | 对单个 ticket 执行 Red–Green、局部验证和原子提交 |
| `delivery-coder` | 对照规格审查、修复问题并运行完整验证 |

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

私有仓库安装依赖当前环境已有访问该仓库的 Git 凭据。安装或升级后启动新的 Codex 会话，再通过 `/skills` 检查六个 skill 是否出现。

## Dependencies

本仓库保持 wrapper 精简，因此运行时需要以下上游 skills：

- Matt Pocock：`grilling`、`domain-modeling`、`codebase-design`、`to-spec`、`to-tickets`、`tdd`、`code-review`
- Superpowers：`brainstorming`、`using-git-worktrees`、`verification-before-completion`
- Architecture：`clean-architecture`

缺少或不兼容的依赖会让工作流明确停止，不会静默降级。版本基线见 [`references/upstream-compatibility.md`](./references/upstream-compatibility.md)。

## Default routing

如果希望所有代码修改请求默认进入 `spec-coder`，将 [`assets/global-agents-snippet.md`](./assets/global-agents-snippet.md) 的受管理区块加入 `~/.codex/AGENTS.md`。只读解释、状态查询、调查和 review 不会自动进入此流程；使用 `skip spec-coder` 或 `directly modify` 可显式跳过。

## Validate

```bash
./scripts/validate.sh
```

验证包括仓库契约测试、六个 skill 的官方格式检查，以及 Git whitespace 检查。

## Workflow

DDD 与 Clean Architecture 根据实际复杂度展开：明确受影响的 Bounded Context、各自的语言和状态所有权，以及必要的 Entity、Value Object、Aggregate 和 Domain Service；区分领域规则、应用编排与 adapter 转换。涉及并发、重试或跨上下文协作时，明确原子性、冲突结果、幂等与恢复责任。模型角色不必逐一对应类，小任务使用简短描述。

`to-spec` 保存这些决策，`to-tickets` 按业务能力切出可验证增量并引用相关模型、规则、接口和测试证据。Gate 2 检查设计信息是否完整，Gate 3 检查场景覆盖与实施条件；实现和交付分别验证行为、规则归属与实际依赖。具体要求见 [Domain Design Contract](./references/domain-design-contract.md)，模型、并发与架构反例见 [Domain Design Examples](./references/domain-design-examples.md)。

```text
grill-coder
    -> design-coder        [设计审批]
    -> plan-coder          [规格审批 + tickets/实施审批]
    -> tdd-coder           [逐 ticket Red-Green + 原子提交]
    -> delivery-coder      [审查 + 完整验证]
```

工作流不会自动 push、创建 PR 或发布外部 issue。完整契约见 [`references/workflow-contract.md`](./references/workflow-contract.md)。
