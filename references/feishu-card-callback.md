# 飞书卡片回调 — 实际测试记录

## 核心结论

Gateway 的 feishu adapter **已内置** `card.action.trigger` 回调流水线：
- `_on_card_action_trigger()` → `_handle_card_action_event()` → 合成 COMMAND 事件
- `hermes_model_route` 值被映射为 `/model xxx` 或 `继续当前模型`

## 发送要求

**必须用 bot 身份**发卡片，回调才会推回 Gateway WebSocket：

```bash
lark-cli im +messages-send --as bot --chat-id "oc_xxx" \
  --msg-type interactive --content '{JSON}'
```

User 身份发的卡片不会触发回调（飞书不向 user identity 推送 card action events）。

## 卡片 JSON 模板

```json
{
  "config": {"wide_screen_mode": true},
  "header": {
    "title": {"tag": "plain_text", "content": "🔄 模型路由确认"},
    "template": "orange"
  },
  "elements": [
    {"tag": "div", "text": {"tag": "lark_md", "content": "**L2 复杂任务**\n\n建议切换更强模型。"}},
    {"tag": "hr"},
    {"tag": "action", "actions": [
      {
        "tag": "button",
        "text": {"tag": "plain_text", "content": "切换到 DeepSeek-v4-pro"},
        "type": "primary",
        "value": {"hermes_model_route": "switch", "model": "deepseek-v4-pro", "provider": "deepseek"}
      },
      {
        "tag": "button",
        "text": {"tag": "plain_text", "content": "继续当前模型"},
        "type": "default",
        "value": {"hermes_model_route": "keep"}
      }
    ]}
  ]
}
```

## 已知问题

### 1. 回调发送成功但回复失败

测试中 Gateway 收到 card action trigger 并正确路由为 synthetic command，但回复飞书时报错：

```
[99992354] The request you send is not a valid {open_message_id}
Invalid ids: [c-a5afcb3218249e722633d0204d9356db94833f95]
```

Gateway 尝试回复时使用的 message_id 格式错误（`c-xxx` 前缀不是飞书有效消息 ID）。**回调逻辑本身有效**，只是回复发送失败。

### 2. L2 卡片用 user 身份发送时回调不生效

第一次测试用 user 身份发卡片（含 `{"action": "test_confirm"}`），Gateway 日志显示：
```
Routing card action 'button' ... as synthetic command
Unrecognized slash command /card from feishu
```

走的是默认 `/card button` 路径（没有 `hermes_model_route` 字段），不是真正的模型路由回调。

## Gateway 回调映射

`_handle_card_action_event()` 中的映射逻辑：

| action_value.hermes_model_route | 合成命令 |
|---|---|
| `"switch"` + model + provider | `/model {model} --provider {provider}` |
| `"keep"` | `继续当前模型` |
| 其他（无 hermes_model_route） | `/card {tag} {value_json}` |

## 云文档身份区分

- **飞书云文档创建**：用 user 身份（lark-cli `--as user`），文档所有权直接归属用户
- **模型路由卡片**：用 bot 身份（lark-cli `--as bot`），回调才能推回 Gateway
- 两者身份不同，不可混用
