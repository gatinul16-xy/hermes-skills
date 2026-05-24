# Pattern 测试清单

> 每次修改 `model_route_preflight.py` 的 pattern 后，用此清单验证。

## 测试方法

```bash
python3 -c "
import sys; sys.path.insert(0, '~/.hermes/scripts')
from model_route_preflight import (
    MATURE_WORKFLOW_PATTERNS, L1_PATTERNS, L2_PATTERNS, L3_PATTERNS, _match_any
)
msg = '你的测试消息'
print('L1:', _match_any(L1_PATTERNS, msg))
print('L2:', _match_any(L2_PATTERNS, msg))
print('L3:', _match_any(L3_PATTERNS, msg))
print('Mature:', _match_any(MATURE_WORKFLOW_PATTERNS, msg))
"
```

## 验证用例（v1.3.0）

| 消息 | 预期 L1 | 预期 L2 | 预期 L3 | 预期 Mature | 预期等级 |
|------|---------|---------|---------|-------------|----------|
| 按已有模板生成月报 | T | F | F | T | L1 |
| 套用这个模板做汇报 | T | F | F | T | L1 |
| 按我提供的现有 PPT 模板生成新 Hermes Skill | T | T | F | F | L2 |
| 请按标准多轮工作流执行 | F | T | F | F | L2 |
| 需要 prd-worker + code-worker | F | T | F | F | L2 |
| 做一个 AI 工具测评 Skill | F | T | F | F | L2 |
| 设计一个自动同步功能 | F | T | F | F | L2 |
| 新建一个文档处理 Skill | F | T | F | F | L2 |
| 改 Hermes context_compressor.py 源码 | F | F | T | F | L3 |
| 批量删除 skill | F | F | T | F | L3 |
| 改 projects 目录结构 | F | F | T | F | L3 |
| 重构 skill 目录 | F | F | T | F | L3 |
| 帮我解释一下 | T | F | F | F | —（不触发） |
| 今天天气怎么样 | F | F | F | F | —（不触发） |

## 关键判定逻辑

```python
if is_l3:
    level = 'L3'
elif is_l2:
    level = 'L2'
elif is_l1 and not (is_l2 or is_l3):
    level = 'L1 (no trigger)'  # L1 不触发路由提醒
else:
    level = '—'  # 不触发
```

**核心规则**：L1 只有在同时命中 L2 或 L3 时才升级。纯 L1 = 不触发。
