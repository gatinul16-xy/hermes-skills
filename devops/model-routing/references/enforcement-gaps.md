# L3 路由执行缺口分析

> 来源：2026-05-19 会话 — "帮我给 Hermes 的 context_compressor.py 打补丁"
> 问题：L3 路由规则被绕过，补丁 1 由当前 agent 直接执行
> 更新：2026-05-20 — delegate_only 改为 session-scoped；新增 Gap 6（L1成熟工作流误判）

## 缺口清单

### 缺口 1：agent 可自行违反 prompt 层规则 → 部分修复

**现象**：L3 规则写"当前 agent 不得自行读取源码、修改文件"，但 agent 回应 L3 路由提醒的同时直接调用了 patch 工具。

**根因**：`model-routing` skill 的 L3 禁制是 prompt 层文字约束，pre_tool_call hook 当时因 session 隔离问题未生效。

**修复进度（2026-05-20）**：
- ✅ `model_route_preflight.py` 已改为 profile-scoped 路由状态
- ✅ slash command（如 `/model`）现在会清除 delegate_only 状态
- ✅ delegate_only 已改为 session-scoped（2026-05-20 修复 #7）
- ⚠️ prompt 层约束仍不可完全替代代码级 guardrail——agent 可以选择性忽略 skill 中的文字规则

**残余风险**：如果 agent 在 L3 pending 阶段（用户尚未确认）就调用工具，pre_tool_call hook 会拦截吗？——会。但只在 `pre_tool_call` hook 已注册且状态匹配时生效。如果 hook 因超时被跳过（3s timeout），拦截失效。

### 缺口 2：acp_command 不传导致假派发

**现象**：`delegate_task(goal=..., context=...)` 不传 `acp_command`，spawn 的是 Hermes subagent，不是 Codex。

**根因**：model-routing skill 原文只说"允许调用 delegate_task 或 acp_command"，没写必须传 acp_command 参数。

**修复**：skill 已补强制规则——L3 派发给 Codex 时 `delegate_task` 必须传 `acp_command='copilot'`。

### 缺口 3：copilot CLI 未安装 → 静默退化

**现象**：即使传了 `acp_command='copilot'`，如果 `which copilot` 返回空，Hermes 可能静默回退到默认 subagent transport。

**表现**：无法从外部证明 Codex 执行了任务——没有任何签名文件、日志或 trace。

**当前状态（2026-05-19）**：本机未安装 copilot CLI（`gh copilot --version` → "Copilot CLI not installed"）。

- [x] 新增修复方案（详见 `references/codex-proxy.md`）

**推荐修复**（新增，推荐优先）：**Thin Proxy 方案**

通过 `HERMES_CODEX_BASE_URL=http://127.0.0.1:8002` 环境变量将 built-in openai-codex provider 路由到本地 proxy。Proxy 透明转发 + 注入 HMAC 签名的 provenance。不依赖 copilot CLI，且提供可验证的执行回执。

```bash
# 一行配置
echo 'HERMES_CODEX_BASE_URL=http://127.0.0.1:8002' >> ~/.hermes/.env
# 启动 proxy
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/scripts/codex_proxy.py &
```

备选修复：
1. 安装 copilot CLI：`gh copilot install`（需要 GitHub Copilot 订阅）
2. 在 preflight hook 中增加 copilot 可用性检测，不可用时打印 warning 并拒绝派发

### 缺口 4：无审计追踪

**现象**：无法追溯某个文件修改是 Codex 做的还是 Hermes 做的。

- [x] 2026-05-19 修复已实施

**修复**：
- `codex_proxy.py` 写入审计日志 `/tmp/codex_proxy_audit.jsonl`
- 每行记录：`ts`, `request_id`, `method`, `path`, `status`, `duration_ms`, `request_size`, `response_size`, `provenance`
- 每个响应注入 HMAC 签名的 `hermes_provenance` 字段

### 缺口 5：Preflight 状态残留导致误拦（新增 2026-05-19）

**现象**：`write_file` 等普通操作被 pre_tool_call hook 拦截。

**修复**（2026-05-19 已实施）：
- ✅ `_set_pending()` / `_set_delegate_only()` 添加 `created_at` 时间戳
- ✅ `_pending_for()` 增加 30 分钟 TTL 检查
- ✅ 手动清理残留：`echo '{}' > ~/.hermes/.model-route-preflight-state.json`

### 缺口 6：L1 成熟工作流误吞新建任务（2026-05-20 发现并修复）

**现象**：用户消息 "按我提供的现有 PPT/PPTX 模板生成新 PPT 的 Hermes Skill" 被 `r"按.*模板"` 命中 MATURE_WORKFLOW_PATTERNS → 归为 L1，未触发 L2 路由提醒。实际这是一个新建 Skill 的复杂多轮任务。

**修复**（2026-05-20 已实施）：
- ✅ `r"按.*模板"` → `r"按已有.*模板"` + `r"套用.*模板"`
- ✅ L2 新增 `r"Hermes.*[Ss]kill"`、`r"新建.*[Ss]kill"`、`r"做一个.*[Ss]kill"` 等覆盖新建场景
- ✅ 新增测试清单 `references/pattern-test-checklist.md`

### 缺口 7：Codex 协议已变更（2026-05-19）

**现象**：Codex 于 2026-02-05 移除 `chat/completions` 支持，只接受 `responses` API。

**影响**：任何试图用 `/chat/completions` 调用 Codex 的方案（包括简单的 openai_compatible proxy）都会失败。

**修复**：利用 Hermes 内置的 `api_mode=codex_responses` 和 `agent/transports/codex.py` 适配层。Proxy 不需要做协议转换，只需透明转发 + 注入签名。
