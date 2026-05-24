# 使用轨迹与用户反馈校准 — 实现细节

> 版本: v1.3.2 | 日期: 2026-05-21

## 概述

让模型路由引擎从"死规则"变成"可学习的系统"。用户每次纠正路由偏差（如"L1不够应该L2"），引擎自动记录并参考反馈修正后续同类任务的分级。

## 数据文件

- **反馈日志**: `~/.hermes/logs/model-routing-feedback.jsonl` — 每条校准事件的完整审计记录
- **模式库**: `~/.hermes/.model-route-feedback-patterns.json` — 按 task pattern 聚合的纠正映射，路由时快速读取

### 反馈日志格式 (JSONL)

```json
{"ts":"2026-05-21T08:30:00+0800","event":"user_calibration","from_level":"1","to_level":"3","feedback_message":"这次L1不够，应该是L3","last_routing":{"level":"L1","message":"用联通红模板做个PPT","is_l2":false,"is_l3":false},"matched_task_patterns":["做个?(?:个)?PPT"]}
```

### 模式库格式 (JSON)

```json
{
  "version": 1,
  "last_updated": "2026-05-21T08:30:00+0800",
  "corrections": {
    "做个?(?:个)?PPT": [{
      "corrected_to": "L3",
      "from": "L1",
      "feedback_ts": "2026-05-21T08:30:00+0800",
      "feedback_snippet": "这次L1不够应该L3"
    }]
  }
}
```

每个 pattern 最多保留 3 条校准记录（`[-3:]` 截断）。

## 检测模式（自然语言）

以下任一表达均会被识别并提取 from/to level：

- "这次L1不够，应该是L2" / "这个任务L3太高了，L2就够了"
- "L1升L2" / "L3降L2"
- "以后做PPT这种任务走L2"
- "这个应该走L2" / "做PPT这种L2就够了"
- "这次用L3做的太高了L1就行"

## 执行流程

```
main()
  ├─ 检测反馈校准消息  → 提取 from/to level
  │   ├─ 读取上轮路由日志（从 model-routing.jsonl 最后一行）
  │   ├─ 从上轮任务消息中提取 task patterns（NOT from feedback msg）
  │   ├─ 写入反馈日志 + 更新模式库
  │   └─ 注入 [模型路由反馈已记录] 上下文 → return 0
  │
  ├─ 正常路由决策（L1/L2/L3 匹配）
  │   └─ 如果命中 L2/L3:
  │       ├─ _apply_feedback_corrections()
  │       │   ├─ 读取模式库 → 匹配当前消息的 patterns
  │       │   ├─ 找到纠正 → 调整 is_l2/is_l3
  │       │   └─ 注入 [用户反馈校准] 上下文
  │       └─ 继续正常路由流程
  │
  └─ 未命中 L2/L3 → return 0
```

## 核心设计决策

1. **Pattern 从 LAST ROUTING EVENT 提取**（不是从反馈消息）。反馈消息 "L2不够应该L3" 不含任务关键词；需回溯上轮路由日志中的原始任务消息。
2. **升级/降级均生效**。L1→L2/L3 升级；L3→L2 降级。但 L3 硬规则中的系统破坏性操作（`改.*Hermes.*源码` 等）不可降。
3. **建议性，不阻止手动覆盖**。用户随时可用 `/model xxx` 或"这次用 L2" 临时覆盖。
4. **反馈消息本身不触发路由**。检测到反馈后立即 `return 0`。

## 已知限制

- 单次反馈只能关联 LAST routing event 的 patterns。跨多轮后的反馈可能关联错误的 pattern。
- 基于 regex pattern 匹配，不涉及语义理解。新任务表述不同但本质同类时可能无法关联。
- 模式库无自动过期机制。可后续补充 TTL 清理。

## 测试用例（全部通过 2026-05-21）

| 输入 | from | to |
|------|------|----|
| 这次L1不够，应该是L2 | 1 | 2 |
| 这个任务L3太高了，L2就够了 | 3 | 2 |
| 以后做PPT这种任务走L2 | None | 2 |
| L1升L2 | 1 | 2 |
| L3降L2 | 3 | 2 |
| 这个应该走L2 | None | 2 |
| 做PPT这种L2就够了 | None | 2 |
| 这次L2做的不对，应该L3 | 2 | 3 |
| 这次用L3做的太高了L1就行 | 3 | 1 |
| 帮我写个方案 | None | None (not feedback) |
