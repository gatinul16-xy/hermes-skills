# Preflight Profile-Scoped Key Bug — Fix Notes

**Date**: 2026-05-19
**File patched**: `~/.hermes/scripts/model_route_preflight.py`

## Root Cause

`_session_key()` used the profile name (e.g. `"default"`) as the state key. Since Hermes state is keyed by profile:
1. Any session in `default` profile triggering L2 → sets `pending` for key `"default"`
2. ALL sessions under `"default"` profile share this key
3. Every tool call in every session gets blocked until explicitly cleared

## Fix

Split into two keys with different scopes:

```python
_session_key()  → profile name (e.g. "default") — only for delegate_only mode
_pending_key()  → "profile:session_id" (e.g. "default:abc123") — for pending mode
```

### Files changed

`~/.hermes/scripts/model_route_preflight.py`:
1. Renamed `_session_key()` → only returns profile name (for delegate_only)
2. Added `_pending_key()` → returns `"profile:session_id"` (for pending)
3. `_handle_pre_tool_call()` now checks both keys:
   - `_session_key` → delegate_only check
   - `_pending_key` → pending check
4. `_clear_pending()` accepts both keys, clears both
5. `main()` uses both keys for slash/confirm/bypass clearing
6. `_set_pending()` uses `_pending_key`

### Expected behavior after fix

- **Pending mode**: blocks only the current session, won't affect other sessions in same profile
- **Delegate_only mode**: still profile-scoped (intentional — L3 decisions span all sessions)
- **Confirmation** (继续当前模型) clears BOTH keys
- **Slash commands** (/model, etc.) clear BOTH keys

### Cleanup command (if state is stale)

```bash
echo '{}' > ~/.hermes/.model-route-preflight-state.json
```

### 遗留问题：delegate_only 跨 session 锁定

2026-05-20 验证了 delegate_only profile-scoped 的实际影响：

**场景**：Session A 中确认"派发给 Codex" → delegate_only 写入 key="default" → 30 分钟内用户开新 Session B → 所有工具被拦截（read_file、search_files、terminal），Agent 无法开始新任务。

**为什么选择保留 profile 作用域**：L3 高风险/高价值任务故意跨 session 持续——防止同一 profile 的 session 在已确认"派发"后"偷偷继续"。但实际问题是：

- 用户可能以为新对话是"干净的"
- Agent 也没有提示"当前 profile 处于 delegate_only 状态"
- 工具被静默拦截，用户和 Agent 都莫名其妙

**缓解方案**：Agent 在新对话中遇到 delegate_only 拦截时，应在回复中主动提示"当前 profile 存在上一个 session 的 L3 派发锁，是否清除？"并等待用户确认再执行 `rm -f`。清除操作本身不需要锁——因为 `terminal` 也被拦了。
