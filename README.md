# model-routing

Hermes Agent 模型路由预检 Skill — 判断当前任务是否需要提醒用户切换到更强/更便宜/更合适的模型。

## 核心逻辑

| 等级 | 场景 | 处理方式 |
|------|------|----------|
| **L1** | 简单问答、短文本润色、已有skill/模板直接执行 | 不提醒，直接用当前模型 |
| **L2** | 架构设计、复杂bug分析、代码审查、多轮工作流设计、新建Skill | 先提醒，询问用户确认后再执行 |
| **L3** | 改源码、删skill、对外发布、高风险操作 | 不可降级，必须派发给 Codex CLI 执行 |

## 文件结构

```
model-routing/
├── SKILL.md                              # 主 Skill 规则
└── references/                           # 技术细节与修复记录
    ├── codex-proxy.md                     # Codex Thin Proxy 架构（备选方案）
    ├── enforcement-gaps.md                # L3 路由执行缺口分析
    ├── feedback-calibration.md            # 用户反馈校准机制
    ├── feishu-card-callback.md            # 飞书卡片回调测试记录
    ├── handoff-live-session-transfer.md  # 活 session 交接机制
    ├── l2-pending-tool-block-fix.md       # L2 pending 误拦工具修复
    ├── pattern-test-checklist.md          # Pattern 测试清单
    └── preflight-profile-key-fix.md       # Profile-scoped key bug 修复
```

## L2 触发关键词

```
架构设计、系统设计、bug根因分析、代码审查、安全审查
多轮工作流设计、worker拆分、Kanban编排
新建Skill、新建工具、开发新模块
provider/gateway/cron/MCP（仅在分析/调试/配置语境下）
流程设计、步骤拆解、判断标准、审核清单、分镜规划
```

## 模型切换命令

**L2 推荐**：
```
/model deepseek-v4-pro --provider deepseek
```

**L3 执行路径（必须用 Codex CLI）**：
```bash
bash ~/.hermes/scripts/codex_delegate.sh --cd <项目目录> <task.md>
```

## 特殊例外

- **Cron 定时任务**：视为 L1，直接执行，不询问
- **系统维护消息**：不参与 L2/L3 路由

## 反馈校准

用户可反馈路由偏差，系统记录并参考反馈修正后续同类任务。详见 `references/feedback-calibration.md`。