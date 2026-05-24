---
name: model-routing
description: 模型路由预检 — 判断当前任务是否需要提醒用户切换到更强/更便宜/更合适的模型
triggers:
  - 模型路由
  - 换模型
  - 切模型
  - 复杂模型
  - 复杂任务
  - 深度推理
  - 架构设计
  - 系统设计
  - 代码审查
  - 安全审查
  - review
  - 安全问题
  - 有没有安全问题
  - 脚本安全
  - 审查脚本
  - review 脚本
  - 根因分析
  - 多轮任务
  - 工作流设计
  - provider
  - token
  - 成本
  - 选哪个模型
tools_required: []
version: 1.3.6
author: PMO天策
date: 2026-05-22
--- 
changelog:
  - "1.3.6: 反馈记录与主规则彻底分离：用户反馈只写 observations 和 promotion_candidates，不再自动写入 corrections 或直接影响后续路由；同类反馈达到阈值后提示询问用户是否升级主规则"
  - "1.3.5: 修复 L2 严重误触：Cron/系统维护消息/Skill wrapper/Kanban worker 命令直接旁路；provider/gateway/cron/MCP 不再裸词触发，必须处于分析/排查/修复/配置等机制语境才触发 L2"
  - "1.3.4: 收紧 L1/L2 边界：简单文档整理仍为 L1，拆/设计工作流、判断标准、时长分配、审核清单、复盘流程等流程设计任务归 L2；反馈校准新增 last-task 记录，支持纠正未触发路由的 false negative"
  - "1.3.3: L3 Codex 路径从 openai-codex provider 改为 Codex CLI 本地执行 — 解决超时/retry 吞额度问题；新增 codex-delegate skill + codex_delegate.sh；薄 proxy 降级为备选"
  - "1.3.2: 新增使用轨迹与用户反馈校准机制 — 用户可反馈路由偏差（如 L1→L2/L3→L2），系统自动记录并参考反馈修正后续同类任务"
  - "1.3.1: 修复 L2/L3 命中时 rec_model 未定义导致 hook 崩溃；修复 L2 regex 漏逗号；新增 ~/.hermes/logs/model-routing.jsonl 路由日志；强模型切换后优先注入续跑上下文"
  - "1.3.0: L1 成熟工作流边界收缩（按.*模板→按已有/套用）；L2 新增泛化多轮/worker/新建skill等16个pattern；L3 不可降级+gpt-5.5出口检查；delegate_only 改为session-scoped；修复 PPT任务被误归L1的bug"
  - "1.2.0: L3 Codex 派发方案升级：ACP 降级为备选，推荐 thin proxy + built-in openai-codex + provenance 签名；新增 references/codex-proxy.md；已知陷阱增加 preflight 状态残留坑位（含 TTL 修复说明）"
---

# 模型路由预检

这个 skill 只负责判断“是否应该提醒用户切换模型”，不负责工具选择。工具选择仍使用 `tool-routing`。

## 核心原则

1. 默认不自动切模型，只提醒用户并等待确认。
2. 简单任务不打扰，复杂任务才提醒。
3. 如果当前模型已经适合当前任务，不重复提醒。
4. 如果 provider 或 API key 明显异常，优先提醒修复可用性，而不是推荐同一个不可用模型。
5. 模型路由建议必须简短，不要打断用户思路。
6. 关键路由事件必须写入 `~/.hermes/logs/model-routing.jsonl`，用于后续复盘真实模型使用情况。

## 任务分级

### 特殊例外：Cron 定时任务
- Cron Job 运行时视为 **L1**，直接执行当前模型，**不进行路由预检**，不询问用户。
- 避免后台自动化任务因等待确认而阻塞。
- 只记录 `route_bypassed` 日志，不写 pending，不写 continuation。

### 特殊例外：系统维护消息

以下不是用户真实任务，不参与 L2/L3 路由：

- `[IMPORTANT: You are running as a scheduled cron job...]`
- `[IMPORTANT: The user has invoked the ... skill...]` 后面展开的 skill 全文
- `Review the conversation above and update the skill library...`
- `Review the conversation above and consider saving to memory...`
- `work kanban task ...`

这些内容可能包含 `review`、`provider`、`gateway`、`cron`、`MCP` 等词，但它们是系统包装或维护任务，不应触发模型升级。

### L1：简单任务 / 成熟流程任务，使用当前默认模型

命中以下场景时，不提醒切模型：

- 简单问答、命令解释、状态查询
- 短文本润色、标题候选、轻量总结
- 读写单个文件、查找路径、普通配置说明
- 简单搜索、单页阅读、常规信息整理
- 用户明确说“快点”“简单说”“不用复杂分析”
- 已有成熟 skill 可直接执行的标准任务
- 已有固定工作流/SOP 可直接套用，且不涉及高风险修改
- 跑已有 skill，例如 `ai-daily-news`、`lark-cli`、`project-state-manager`、`shot-generation`
- 跑已有标准工作流，例如 PRD -> code -> review，且任务边界清楚
- 按已有模板生成文档、报告、脚本、复盘
- 套用已有模板生成内容
- 按已有 SOP 做 Obsidian 写回、飞书任务同步、项目文件落位
- 写说明文档、整理文档、整理记录、轻量复盘

⚠️ L1 边界约束（2026-05-20 修复）：只有"按已有模板 / 套用模板"归 L1。"按我提供的模板做一个新的 Skill/工具"表示新建能力，应归 L2。代码级区分：`r"按已有.*模板"` + `r"套用.*模板"` ∈ MATURE_WORKFLOW；`r"按我.*模板.*[Ss]kill"` → L2。

⚠️ L1/L2 文档边界约束（2026-05-21 修复）：只有"写说明文档 / 整理文档 / 整理记录"这类低推理整理任务归 L1。凡是"拆工作流 / 设计工作流 / 步骤拆解 / 判断标准 / 时长分配 / 审核清单 / 复盘流程 / 短视频工作流"等需要设计执行方案和判断标准的任务，归 L2。

有些任务看起来步骤多，但已经有成熟 skill 或固定流程承接，不必默认升级模型。

升级条件：

- 执行中连续失败 2 次
- 发现需求不清、流程不适配、需要重新设计 SOP
- 涉及安全审查、源码修改、长期规则修改、批量迁移、外部发布
- 用户明确要求深度分析或高质量判断

### L2：复杂任务，必须先询问是否切换模型

命中以下任一场景，且当前不是强推理模型时，必须先提醒用户，并等待用户确认是切换模型、继续当前模型，还是派发给 Codex 后才能继续：

- 架构设计、系统设计、跨模块方案
- 复杂 bug 根因分析，尤其是已经失败 2 次以上
- 代码审查、安全审查、回归风险分析
- 用户说“review 这个脚本/代码有没有安全问题”
- 用户说“帮我看有没有安全问题/风险/漏洞”
- 需要重新设计或重构已有 skill / SOP / 固定工作流
- 多轮任务工作流设计、worker 拆分、Kanban 编排
- 工作流/流程拆解、流程设计、步骤拆解、判断标准、审核清单、审核要点、时长分配、分镜规划、发布流程、复盘流程
- Hermes 源码、gateway、context compression、provider、cron、MCP 等机制分析
- 多轮任务工作流设计、worker 拆分、Kanban 编排
- 用户明确提到 prd-worker / code-worker / review-worker / design-worker / ui-worker 等 worker 名称
- 新建 Skill、新建工具、设计新功能、开发新模块
- Hermes 源码、gateway、context compression、provider、cron、MCP 等机制分析

⚠️ L2 关键词边界约束（2026-05-22 修复）：`provider`、`gateway`、`cron`、`MCP` 这些词本身不再触发 L2。只有当用户意图是"分析/检查/配置/调试/修复/排查/设计/优化这些机制"时，才归 L2。例：`分析 Provider 配置和成本` → L2；cron job wrapper 里出现 `cron` → L1/旁路。

推荐命令：

```text
/model deepseek-v4-pro --provider deepseek
```

备选（DeepSeek 不可用时）：

```text
/model mimo-v2.5-pro --provider xiaomi
```

### L3：高风险/高价值任务，不可降级，必须使用 Codex

命中以下场景时，必须先提醒，并等待用户确认以下出口之一：

- 派发给 Codex CLI 执行（通过 codex_delegate.sh + Task Package）——**主路径**
- 切换 Codex 聊天模型（通过 openai-codex provider）——**备选，不推荐**
- 用户明确要求继续当前模型（不可用于 L3——L3 不可降级）

**L3 不可降级（硬规则，2026-05-20 生效，2026-05-21 更新执行路径）：** L3 任务不能用 L2 模型替代。如果 Codex CLI 不可用（npx codex 未安装/未认证），可降级使用 openai-codex provider 或告知用户"出口不可用"。不得自动降级推荐 L2 模型。

**L3 Codex 执行方案（推荐）：Codex CLI 本地执行 + Task Package**

Codex 当作本地命令行专家工具使用，不作为 Hermes 聊天模型接入。每次调用生成结构化 Task Package，通过 `codex_delegate.sh` 一次性执行。

```
主控（MiniMax/DeepSeek）
    → 用户确认 L3
    → 天策生成 Task Package（标准 Markdown 格式）
    → bash codex_delegate.sh --cd <project-dir> <task-package.md>
    → npx codex exec（sandbox=workspace-write，ephemeral）
    → stdout + /tmp/codex_output.json 回传
    → 天策 review 结果
    → 汇报用户
    → 提醒切回便宜模型
```

关键文件：
- `~/.hermes/scripts/codex_delegate.sh`：CLI 包装脚本
- `~/.hermes/skills/devops/codex-delegate/SKILL.md`：Task Package 格式 + 调用规范

详见 `skills/devops/codex-delegate/SKILL.md`。

**L3 Codex 执行方案（备选）：Built-in openai-codex + Thin Proxy**

仅在 Codex CLI 不可用时使用。Codex 作为聊天模型接入 Hermes，通过 thin proxy 转发请求。**已知问题：容易超时和重复 retry，可能导致 Codex 后台已执行但 Hermes 没拿到完整反馈，重复调用消耗额度。**

```
Hermes openai-codex ──codex_responses──▶ 127.0.0.1:8002(proxy) ──▶ Codex backend
                                          ↑ 只做转发 + provenance 签名注入
```

配置（一次性）：
```bash
echo 'HERMES_CODEX_BASE_URL=http://127.0.0.1:8002' >> ~/.hermes/.env
hermes login --provider openai-codex
```

详见 `references/codex-proxy.md`。

- 会修改 Hermes 源码、provider、gateway、context compressor
- 会影响长期规则、memory、skills、projects 结构
- 会发外部消息、创建飞书任务、生成对外交付物
- 需要产出可直接发布的视频脚本、商业方案、PR/issue 内容
- 需要同时考虑安全、成本、架构、回归风险

## 提醒格式

当需要提醒时，使用这个格式，保持简短：

```markdown
这类任务属于 L2/L3，我建议先切到更适合的模型再继续：

`/model deepseek-v4-pro --provider deepseek`

你也可以回复“继续当前模型”或“派发给 Codex”，我再继续处理。
```

如果当前模型已经适合：

```markdown
当前模型足够处理这个任务，我直接继续。
```

## 已知陷阱

详见 `references/enforcement-gaps.md`、`references/codex-proxy.md`、`references/preflight-profile-key-fix.md`、`references/handoff-live-session-transfer.md`、`references/l2-pending-tool-block-fix.md` 和 `references/pattern-test-checklist.md`。

14. **子代理 delegate_task 继承路由规则但无法与用户交互（2026-05-22 发现）**——当主 agent 通过 `delegate_task` 派发子代理时，子代理的 preflight hook 会正常检测任务复杂度并触发 L2/L3 路由。但子代理**没有 clarify 能力**，无法向用户提问等待确认。结果：子代理输出路由提醒后直接 "completed"（因为无法继续），或者长时间等待导致 timeout（600s）。**表现**：子代理 summary 仅包含路由提醒，`api_calls` 仅 1 次，`tool_trace` 为空。**解决方案**：主 agent 派发子代理时，必须在 `context` 中加入强制指令：`【强制 L1 规则】禁止请求切换模型，禁止提问，直接使用当前模型执行。` 这能覆盖 preflight 的路由检测，让子代理直接跑完。
15. **L2 路由过度触发——大量误报（2026-05-22 数据验证）**——路由日志分析显示 44 条记录中 42 条触发 L2，大部分为误触。原因：L2 pattern 中 `gateway`/`cron`/`MCP`/`worker` 等关键词过于宽泛，匹配了大量普通查询和 Cron 任务。即使 Cron 已在特殊例外中声明为 L1，但 hook 的 regex 匹配在 Cron 模式检测之前执行。**影响**：Cron 任务、日常查询频繁被打断。**临时解决**：主 agent 在 prompt 中显式声明 L1 属性。长期修复需要收紧 L2 regex 或调整 hook 中 Cron 检测的优先级。

7. **delegate_only 跨 session 锁定（2026-05-20 已修复 ✅）**——旧实现：`_session_key()` 用 profile name 作 delegate_only state key → 同 profile 下所有 session 共享 delegate_only 状态 → 新会话被锁。**修复**：delegate_only 改为 session-scoped（使用 `_pending_key`），与 pending 保持一致的隔离粒度。旧状态文件中的残留条目已清理。

8. **Codex proxy 实际不可用（2026-05-20 验证，2026-05-21 降级）**——`~/.hermes/scripts/codex_proxy.py` 已写好但 proxy 从未成功运行（OAuth 未配置）。v1.3.3 起 L3 主路径已从 Thin Proxy 切换到 Codex CLI 本地执行，不再默认推荐 `/model gpt-5.5 --provider openai-codex`。Thin Proxy 保留为备选，仅在 `npx codex` 不可用时启用。

9. **L1 成熟工作流误吞新建任务（2026-05-20 发现并修复 ✅）**——旧 pattern `r"按.*模板"` 匹配了"按我提供的模板生成新 PPT 的 Hermes Skill"（实际是新建 Skill，应归 L2）。**修复**：`r"按.*模板"` → `r"按已有.*模板"` + `r"套用.*模板"`，同时 L2 新增 `r"Hermes.*[Ss]kill"`、`r"新建.*[Ss]kill"` 等 pattern 覆盖新建场景。

10. **L2/L3 命中即崩溃（2026-05-20 已修复 ✅）**——旧实现先调用 `_write_continuation(..., rec_model, ...)`，后定义 `rec_model`，导致任何 L2/L3 命中都会触发 `UnboundLocalError`。**修复**：先计算 `rec_model`，再写 pending/continuation/log。同步修复 `r"撰写.*"` 后漏逗号导致的 regex 拼接问题。

11. **切强模型后无法续跑（2026-05-20 V1 修复）**——旧流程里，用户切模型后若回复"继续"，可能被当作"继续当前模型"并清空 continuation。**修复**：强模型续跑检查优先于普通确认清理；首次进入强模型时注入 `[模型路由续跑]` 上下文，并记录 `route_resumed_on_strong_model` 日志。

12. **"写文档"误吞流程设计（2026-05-21 已修复 ✅）**——旧 L1 pattern `r"写.*文档"` 过宽，可能把"写/拆一个工作流文档"误判成 L1。**修复**：L1 收窄为 `写.*说明文档`、`整理.*文档`；L2 新增 `拆.*工作流`、`设计.*工作流`、`判断标准`、`时长分配`、`审核清单`、`复盘流程`、`短视频.*工作流` 等流程设计 pattern。

13. **反馈校准无法纠正 false negative（2026-05-21 已修复 ✅）**——旧反馈机制只读取最近一次 `route_triggered` 日志。如果任务本来就没触发路由，用户说"这个应该是 L2"时没有原始任务可绑定。**修复**：新增 `~/.hermes/.model-route-last-task.json`，记录最近一条正常用户任务及匹配 pattern；反馈校准优先绑定 last-task，再回退到 last routing event。

快速要点：

1. **L3 禁制不是纯 prompt 约束**——`model_route_preflight.py` 注册为 pre_tool_call hook，在 delegate_only 模式下硬拦截非派发工具调用。但如果 hook 未注册或 session 隔离导致状态不共享，禁制可能失效。v1.3.3 起 L3 主路径为 Codex CLI（codex_delegate.sh），不再走 delegate_task/acp_command 派发路径；delegate_only 拦截逻辑仅对备选 openai-codex 路径生效。
2. **Codex CLI 优先于 provider**——`npx codex exec` 已安装（v0.132.0），`~/.hermes` 已 trusted。优先使用 codex_delegate.sh 一次性执行，不将 Codex 当聊天模型接入 Hermes。
3. **L3 不再默认推荐 `/model gpt-5.5 --provider openai-codex`**——改为推荐生成 Task Package + 调用 codex_delegate.sh。
4. **Preflight 状态残留**——`model_route_preflight.py` 的 pending/delegate_only 状态持久化到 `~/.hermes/.model-route-preflight-state.json`。早期版本无 TTL，状态会永久残留。2026-05-19 已修复：添加 30 分钟 TTL 自动过期 + `created_at` 时间戳。如果未来仍遇到 write_file 等普通操作被误拦，检查状态文件并清理：`echo '{}' > ~/.hermes/.model-route-preflight-state.json`。
5. **Profile-scoped key 导致跨 session 误拦（2026-05-19 修复）**——`_session_key()` 早期实现用 profile name（如 `"default"`）作为 state key。任一 session 触发 L2 检测 → 为 key `"default"` 设 `pending` → 整个 profile 下所有 session 的工具调用全被 block。修复：拆分为两个 key：`_session_key()`（profile-scoped，仅 delegate_only 用）+ `_pending_key()`（session-scoped，格式 `"profile:session_id"`）。修复后的行为：pending 只 block 当前 session，delegate_only 仍跨 session 生效。
6. **L2 pending 误拦全部工具调用（2026-05-20 修复）**——即使 pending 改为 session-scoped，`_handle_pre_tool_call` 仍对所有工具返回 `action: block`，包括 `read_file`、`web_search`、`execute_code` 等无害操作。Agent 被完全锁死，连"提醒用户"所需的信息检索都做不了。修复：pending 状态改为注入上下文提醒（`action: context`）但放行工具调用（`return 0`）。只有 `delegate_only`（L3）保持硬拦截。详见 `references/l2-pending-tool-block-fix.md`。
7. **路由日志位置**——每次触发、确认、派发、强模型续跑等事件写入 `~/.hermes/logs/model-routing.jsonl`。这是临时审计日志，用于复盘真实模型路由效果；稳定后可关闭或降级。

## Codex 调用方案

### 当前方案（v1.3.3+）：Codex CLI 本地执行（推荐）

```
主控 → Task Package → codex_delegate.sh → npx codex exec
                                              ↓
                              sandbox=workspace-write, ephemeral
                                              ↓
                              stdout + /tmp/codex_output.json 回传
```

优势：
- 一次性执行，不依赖长会话
- 无超时 retry 吞额度问题
- 输出可通过 `--json` + `-o` 精确回传
- 主控模型不变，不需要切模型再切回来

### 旧方案（v1.2.0-v1.3.2）：Thin Proxy + openai-codex provider（备选）

仅在 Codex CLI 不可用时使用。Codex 作为聊天模型接入 Hermes，通过 thin proxy 转发。

已知问题：
- 容易超时和重复 retry → 吞额度
- OAuth 配置复杂
- 执行回执不可靠

详见 `references/codex-proxy.md`。

- 不要每轮都提醒切模型。
- 不要对简单任务提醒切模型。
- 不要在 provider 明显不可用时继续推荐同一个 provider。
- 不要为了模型路由打断已经确认的执行流程，除非任务风险升高。
- 不要把工具选择问题交给本 skill，工具选择仍使用 `tool-routing`。
- L2 执行 `_set_pending` 后，Agent 上下文会注入模型切换提醒，但工具调用**不阻塞**——Agent 可以继续读文件、搜索、查询。2026-05-20 修复前 L2 pending 曾误拦全部工具（见 pitfall #6）。
- L3 在用户确认派发前不得调用工具、读取文件或开始执行任务。
- L3 用户确认"派发给 Codex"后，`delegate_only` 模式下只允许 `delegate_task`/`acp_command`，其他工具全部拦截。

## 模型切换后自动继续任务（2026-05-20 设计）

用户切换模型后不需要重新输入指令——preflight 写入 continuation 文件，agent 自动检测并继续：

```json
// ~/.hermes/.model-route-continue.json
{
  "task_summary": "分析浅色 PPT 模板，输出 schema JSON",
  "continue_command": "继续分析 PPT 模板，输出到 ~/.hermes/Temp/template-schema.json",
  "input_files": ["/path/to/source.pptx"],
  "expected_output": "/path/to/output",
  "triggered_at": "2026-05-20T16:30:00",
  "cleared": false
}
```

流程：
1. L2 触发时，preflight 写入该文件
2. 用户 `/model deepseek-v4-pro` 切换
3. 下一轮 agent 启动时检测文件存在且 `cleared=false`
4. 自动执行 `continue_command`
5. 完成后设置 `cleared=true`

用户只需做一步：`/model xxx`，不需要再输入任何指令。

详见 `references/feishu-card-callback.md`。

## 使用轨迹与用户反馈校准（v1.3.6 更新）

模型路由不是一个完美的静态规则系统。用户在使用过程中会发现自己对任务等级有不同判断，这个机制让路由引擎从"死规则"变成"可学习的系统"。

### 工作原理

```
用户执行任务（如 L1 路由）
    ↓
用户反馈："L1 不够，这个任务应该 L2"
    ↓
preflight 检测到反馈消息 → 提取校准信息 → 写入 feedback observations
    ↓
同类反馈达到阈值 → 提示询问用户是否升级主规则
    ↓
用户确认后 → 再人工修改主规则或 approved_corrections
```

### 反馈格式（自然语言）

以下任一说法都会被识别并记录：

- **"这次 L1 不够，应该是 L2"** — 上次路由 L1 → 应该 L2
- **"这个任务 L3 太高了，L2 就够了"** — 上次路由 L3 → 应该 L2
- **"以后做 PPT 这种任务走 L2"** — 匹配 PPT 模式 → 强制 L2
- **"L1 升 L2"** — 明确升一级
- **"L3 降 L2"** — 明确降一级
- **"这个应该走 L2"** — 任意 → L2
- **"做 PPT 这种 L2 就够了"** — PPT 相关 → L2

### 数据存储

- **反馈日志**：`~/.hermes/logs/model-routing-feedback.jsonl` — 每次校准事件的完整记录（含上一轮路由信息、匹配的 task pattern）
- **模式库**：`~/.hermes/.model-route-feedback-patterns.json` — 按 task pattern 聚合 observations 和 promotion_candidates
- **日志事件**：`model-routing.jsonl` 中写入 `feedback_calibrated` 事件；只有用户确认后的 approved_corrections 才会产生 `feedback_correction_applied`

### 校准生效

1. preflight 检测到路由反馈消息 → 只记录观察，不触发路由
2. 后续任务消息到达 → 不因为 observations 自动调级
3. 同一 pattern + target 的反馈次数达到阈值后，写入 `promotion_candidates`
4. Agent 必须询问用户是否把该反馈升级为主规则
5. 用户确认前，不得修改主规则，也不得让反馈自动生效

### 生效范围

- **升级**：原 L1 → 用户反馈 L2，先记录；达到阈值后询问是否升级主规则
- **降级**：原 L3 → 用户反馈 L2，先记录；达到阈值后询问是否升级主规则（但 L3 硬规则中的"改源码/删 skill"不可降）
- **不生效**：L3 硬规则中涉及系统破坏性操作的模式不参与降级

### 示例流程

```
[第1次] 用户："用联通红模板生成PPT"
         → preflight: 匹配 "做个?PPT" → L2
         → Agent 切换到 deepseek-v4-pro 执行

[第2次] 用户："用浅色模板做3页简介"
         → preflight: 匹配 "做个?PPT" → L2 ✅ 无需重复校准

[第3次] 用户："这个任务 L2 太高了，L1 就够了"
         → preflight: 检测到反馈 → 记录 observations，不自动改规则
         
[第4次] 用户："用联通红模板做封面页"
         → preflight: 仍按主规则判断

[第5次] 用户再次反馈同类误判
         → preflight: promotion_candidates 达到阈值
         → Agent 询问用户是否升级主规则
```

### 人工覆写

用户随时可以说"这次用 L2"/"切换到 deepseek-v4-pro"来临时覆盖路由规则。反馈记录是**复盘证据**，不是自动规则。只有用户明确确认升级后，才允许修改主规则或 approved_corrections。

详见 `references/feedback-calibration.md`。

## 完成后提醒切回便宜模型（硬规则）

L2/L3 任务完成（或用户确认跳过）后，**当前 agent 必须主动提醒用户切回默认便宜模型**。

触发条件：
- 用户切换到 L2/L3 强模型后，任务已完成
- 用户回复"继续当前模型"跳过了切换（不需要提醒）
- 用户切换了模型但当前对话看起来已经结束（可提醒）

提醒格式：
```
✅ 任务完成。当前模型仍为 [强模型名]，建议切回便宜模型节省 token：

/model MiniMax-M2.7 --provider minimax-cn
```

注意事项：
- 这条规则由 agent 行为驱动，不走 hook
- 只在 L2/L3 任务确实完成后提醒，不要中途打断
- 用户明确说"不用切""继续用"时不重复提醒
- 提醒是建议性的，不阻塞后续操作
