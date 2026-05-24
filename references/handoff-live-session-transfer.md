# /handoff — CLI 到消息平台会话移交（v0.14，实测纠正）

## 官方 Release Notes 说法（2026.5.16）

> Switches models or personalities mid-conversation without losing context — every message, tool call, and context moves live.

**⚠️ 此描述严重过度简化，实测与源码不符。**

## 源码真相（`hermes_cli/commands.py` L82）

```python
CommandDef("handoff", 
    "Hand off this session to a messaging platform (Telegram, Discord, etc.)",
    "Session",
    args_hint="<platform>", 
    cli_only=True)  # ← 关键
```

## 实际功能

| 属性 | 值 |
|------|----|
| **真正作用** | CLI 会话移交给消息平台，CLI 退出 |
| **参数** | `<platform>`（telegram/discord/feishu 等） |
| **作用域** | `cli_only=True`——只限 CLI，gateway 内不可用 |
| **切模型？** | ❌ 不涉及模型切换 |
| **切 persona？** | ❌ 不涉及 persona |
| **跨平台双向？** | ❌ 仅 CLI → 平台单向 |

## 实际流程（cli.py `_handle_handoff_command`）

1. 用户在 CLI 输入 `/handoff telegram`
2. Hermes 验证平台配置 + home channel
3. 标记当前 session 为 `handoff_state='pending'`
4. Gateway watcher 轮询检测到 pending → 切换到目标平台 home channel
5. CLI 端自动退出（等同 `/quit`）
6. 用户可在目标平台 `/resume` 继续

## 真正的「跨平台双向接续」需求

GitHub issue #8366 "Feature: Cross-Platform Session Handoff (CLI ↔ Telegram ↔ iMessage)" ——这是一个 **feature request**，尚未实现。

提案内容：
- CLI 封存状态 → Telegram 继续 → 回到 CLI 继续
- 状态快照包含最后对话、上下文、文件变更
- 目前仅靠 CLI → 平台单向的 `/handoff` 无法满足

## 为什么 release notes 描述不准确

推测：v0.14 的 `/handoff` 功能在代码层面是 "session transfer to platform"，但 release notes 将其包装成更通用的 "switches models or personalities" 表述以强调上下文不丢失的特性。源码中 handlers 只在 CLI 端处理 `request_handoff()`，不涉及 `switch_model()` 或 `switch_persona()` 调用。

## 用户侧影响

- 从 Feishu gateway 使用 Hermes 时，`/handoff` **完全不可用**（`cli_only=True`）
- 即使从 CLI 使用，也只解决「桌面→手机」单向问题，不解决「模型切换」
- L2/L3 模型切换继续用 `/model` + 卡片路由方案
