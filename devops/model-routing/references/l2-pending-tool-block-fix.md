# L2 Pending 工具拦截 Bug 修复记录

> 日期：2026-05-20
> 文件：`~/.hermes/scripts/model_route_preflight.py`

## 现象

`model_route_preflight.py` 的 pre_tool_call hook 设置 `pending` 状态后，**所有工具调用**均被拦截，报：

```
模型路由预检正在等待用户确认：L2 复杂任务 必须先询问用户是否切换模型...
在用户回复「继续当前模型/不用切/已切模型/继续/派发给 Codex」前，不允许调用工具。
```

受影响工具包括无害操作：`read_file`、`web_search`、`execute_code`、`browser_navigate` 等。

即使后续对话已进入 L1 简单任务，工具调用仍无法通过。

## 根因

`_handle_pre_tool_call` 中第 294-303 行（修复前）：

```python
pending = _pending_for(pending_key)
if not pending:
    return 0

# 对所有工具返回 block
reason = "模型路由预检正在等待用户确认..."
print(json.dumps({"action": "block", "message": reason}, ensure_ascii=False))
return 0
```

无工具白名单、无安全操作豁免。L2 的设计意图是"提醒用户切模型再干活"，但锁死全部工具阻止了 Agent 进行任何信息检索，形成死锁。

## 修复

```python
# 修复后：pending 状态只注入提醒，不拦截工具
pending = _pending_for(pending_key)
if pending:
    level = str(pending.get("level") or "L2/L3")
    reminder = (
        f"[模型路由提醒] 当前处于 {level} 待确认状态。"
        "如需切换模型，请先回复「继续当前模型/切模型/派发给 Codex」。"
    )
    print(json.dumps({"context": reminder}, ensure_ascii=False))
return 0  # 放行工具
```

核心变化：
- `action: block` → 移除
- 改为 `context` 注入提醒
- `return 0` 放行所有工具

## 不变部分

`delegate_only`（L3）模式保持不变，仍然硬拦截非派发工具：

```python
if delegate_state and delegate_state.get("mode") == "delegate_only":
    if _is_delegate_tool(tool_name):
        _clear_pending(session_key)
        return 0  # 只放行 delegate_task/acp_command
    # 其他工具全部 block
    print(json.dumps({"action": "block", "message": "用户已选择将 L3 任务派发给 Codex..."}))
    return 0
```

## 后续待办

- [ ] 确认 pending 状态 TTL（`STATE_TTL_SECONDS=1800`）是否合理，是否需要缩短
- [ ] 考虑 pending 状态在下一轮用户消息时自动清除（而非只依赖 TTL）
