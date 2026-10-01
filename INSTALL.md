# Agent 安装指南

本文供编码 Agent 使用。目标是把 `spec-coder` 安装到当前用户的 Codex 环境，并确认完整工作流可被新会话发现。

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

该命令会运行契约测试、逐个校验六个 skill，并检查 Git whitespace。只有验证成功后才继续。若验证器路径不是默认位置，可显式传入：

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

`spec-coder` 只编排上游 skills，不会复制或自动安装它们。启动一个新的 Codex 会话，通过 `/skills` 确认本插件和当前执行路径所需的上游 skills 可见：

- 本插件：`spec-coder`、`grill-coder`、`design-coder`、`plan-coder`、`tdd-coder`、`delivery-coder`
- Matt Pocock：`grilling`、`domain-modeling`、`codebase-design`、`to-spec`、`to-tickets`、`tdd`、`code-review`
- Superpowers：`brainstorming`、`verification-before-completion`；选择 worktree 隔离路径时另需 `using-git-worktrees`
- Architecture：`clean-architecture`

若六个本插件 skills 不可见，先确认插件已启用并再次启动新的 Codex 会话。若当前路径必需的上游 skill 缺失，停止并向用户报告缺失名称；不要用名称相近的 skill 替代。原地执行不要求 `using-git-worktrees`；选定隔离路径后才检查该能力，无法使用时按 workspace 规则决定是否有符合用户要求的安全替代方案。已验证的依赖版本基线见 [Upstream Compatibility](./references/upstream-compatibility.md)。

## 6. 可选：启用默认路由

只有用户明确希望代码修改请求默认进入 `spec-coder` 时，才执行本节。

打开全局 `~/.codex/AGENTS.md`，检查是否已经存在以下标记：

```text
<!-- spec-coder:start -->
<!-- spec-coder:end -->
```

- 若标记不存在，将 [`assets/global-agents-snippet.md`](./assets/global-agents-snippet.md) 的完整内容追加到文件。
- 若标记已经存在，只用模板内容更新这两个标记之间的区块。
- 保留标记之外的所有用户内容，不要覆盖整个文件。

修改后向用户展示 diff，并说明该规则只对后续会话生效。

## 7. 最终验收

在新的 Codex 会话中完成以下检查：

1. `/skills` 能看到六个 `spec-coder` skills。
2. 当前执行路径必需的上游依赖 skills 都可见；原地执行无需 `using-git-worktrees`。
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

### 上游依赖缺失

先判断依赖是否属于当前执行路径。原地执行缺少 `using-git-worktrees` 不构成阻塞；必需依赖缺失时，列出精确名称以及 [Upstream Compatibility](./references/upstream-compatibility.md) 中的验证基线，然后停止。依赖恢复后重新启动会话并再次检查 `/skills`。
