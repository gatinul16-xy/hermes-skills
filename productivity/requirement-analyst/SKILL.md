---
name: requirement-analyst
description: "需求分析专家 — 输入产品想法，自动输出结构化需求文档 + 需求分项清单 Excel。适用于小软件、网站、工具等项目。"
version: 1.0.0
author: 小火
tags: [requirement, analysis, excel, product, prd]
---

# 需求分析师

将模糊的产品想法转化为结构化的需求文档和可执行的功能清单。

## 触发条件

用户说：
- "帮我分析一下这个需求"
- "我想做一个 XXX，帮我出需求文档"
- "需求分析"
- "出个 PRD"
- "帮我拆一下功能"

## 工作流程

### Step 1：需求收集（必须先问清楚）

如果用户只给了模糊描述（如"我想做个日记软件"），**必须先追问以下问题**：

1. **核心功能**：这个产品最核心的 1-3 个功能是什么？
2. **目标用户**：谁会用？（自己用 / 给朋友 / 商业产品）
3. **平台**：Web / 桌面端 / 移动端 / 小程序？
4. **技术偏好**：有指定技术栈吗？（没有就推荐）
5. **时间预期**：希望多久做出来？

如果用户说"你帮我决定"，则根据产品类型给出合理默认值。

### Step 2：需求分析

基于用户描述，输出完整需求文档，结构如下：

```markdown
# {产品名} 需求分析报告

**文档版本**: v1.0
**创建时间**: {日期}
**分析人**: 需求分析师

---

## 一、产品概述

### 1.1 产品定位
{一句话描述产品是什么、给谁用、解决什么问题}

### 1.2 目标用户
{用户画像}

### 1.3 核心价值
{用户为什么要用这个产品}

---

## 二、功能模块分析

按一级模块 → 二级功能 → 三级子功能拆解，每个功能包含：
- 功能描述
- 优先级（P0/P1/P2）
- 预估工作量
- 验收标准

### P0 - 核心功能（MVP 必备）
{表格：ID | 功能模块 | 功能描述 | 验收标准 | 工作量}

### P1 - 重要功能（提升体验）
{同上格式}

### P2 - 扩展功能（锦上添花）
{同上格式}

---

## 三、技术方案建议

### 3.1 技术栈推荐
| 层 | 推荐 | 理由 |
|---|------|------|
| 前端 | {推荐} | {理由} |
| 后端 | {推荐} | {理由} |
| 数据库 | {推荐} | {理由} |

### 3.2 项目结构
{建议的目录结构}

---

## 四、开发计划

| 迭代 | 功能范围 | 工作量 | 周期 |
|------|----------|--------|------|
| 迭代 1 | P0 全部 | {X}h | {Y}天 |
| 迭代 2 | P1 全部 | {X}h | {Y}天 |
| 迭代 3 | P2 全部 | {X}h | {Y}天 |

---

## 五、风险与建议

{技术风险、产品建议}
```

### Step 3：生成 Excel 需求分项清单（必须输出）

使用 `execute_code` 生成 `.xlsx` 文件，格式如下：

**Sheet 1: 需求分项清单**

| 列名 | 说明 |
|------|------|
| 一级模块 | 功能大类（如"用户管理"、"内容编辑"） |
| 二级功能 | 具体功能点 |
| 三级子功能 | 细分项（可选） |
| 功能描述 | 详细说明 |
| 优先级 | P0 / P1 / P2 |
| 预估工时(h) | 小时数 |
| 验收标准 | 怎么算做完了 |
| 状态 | 待开发 / 开发中 / 已完成 |

**Sheet 2: 工作量汇总**

| 优先级 | 功能数 | 总工时 | 建议迭代 | 建议周期 |
|--------|--------|--------|----------|----------|
| P0 | {n} | {X}h | 迭代 1 | {Y}天 |
| P1 | {n} | {X}h | 迭代 2 | {Y}天 |
| P2 | {n} | {X}h | 迭代 3 | {Y}天 |

Excel 生成代码模板：

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_requirements_excel(project_name, requirements, output_path):
    """
    requirements: list of dicts, each with keys:
      - module (一级模块)
      - function (二级功能)
      - sub_function (三级子功能)
      - description (功能描述)
      - priority (P0/P1/P2)
      - hours (预估工时)
      - acceptance (验收标准)
    """
    wb = openpyxl.Workbook()

    # Sheet 1: 需求分项清单
    ws1 = wb.active
    ws1.title = "需求分项清单"

    # 表头样式
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    p0_fill = PatternFill(start_color="FFD7D7", end_color="FFD7D7", fill_type="solid")
    p1_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    p2_fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    headers = ["一级模块", "二级功能", "三级子功能", "功能描述", "优先级", "预估工时(h)", "验收标准", "状态"]
    for col, header in enumerate(headers, 1):
        cell = ws1.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    # 写入数据
    for row, req in enumerate(requirements, 2):
        values = [
            req.get("module", ""),
            req.get("function", ""),
            req.get("sub_function", ""),
            req.get("description", ""),
            req.get("priority", "P1"),
            req.get("hours", 0),
            req.get("acceptance", ""),
            req.get("status", "待开发")
        ]
        priority = req.get("priority", "P1")
        fill = p0_fill if priority == "P0" else p1_fill if priority == "P1" else p2_fill

        for col, val in enumerate(values, 1):
            cell = ws1.cell(row=row, column=col, value=val)
            cell.border = thin_border
            cell.alignment = Alignment(vertical='center', wrap_text=True)
            if col == 5:  # 优先级列上色
                cell.fill = fill
                cell.alignment = Alignment(horizontal='center', vertical='center')

    # 设置列宽
    col_widths = [15, 20, 20, 40, 10, 14, 40, 12]
    for i, w in enumerate(col_widths, 1):
        ws1.column_dimensions[get_column_letter(i)].width = w

    # Sheet 2: 工作量汇总
    ws2 = wb.create_sheet("工作量汇总")
    summary_headers = ["优先级", "功能数", "总工时(h)", "建议迭代", "建议周期"]
    for col, header in enumerate(summary_headers, 1):
        cell = ws2.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    # 统计
    stats = {"P0": {"count": 0, "hours": 0}, "P1": {"count": 0, "hours": 0}, "P2": {"count": 0, "hours": 0}}
    for req in requirements:
        p = req.get("priority", "P1")
        stats[p]["count"] += 1
        stats[p]["hours"] += req.get("hours", 0)

    iterations = [
        ("P0", "迭代 1 (MVP)", max(stats["P0"]["hours"] // 8, 1)),
        ("P1", "迭代 2", max(stats["P1"]["hours"] // 8, 1)),
        ("P2", "迭代 3", max(stats["P2"]["hours"] // 8, 1)),
    ]
    for row, (prio, iteration, days) in enumerate(iterations, 2):
        ws2.cell(row=row, column=1, value=prio).border = thin_border
        ws2.cell(row=row, column=2, value=stats[prio]["count"]).border = thin_border
        ws2.cell(row=row, column=3, value=stats[prio]["hours"]).border = thin_border
        ws2.cell(row=row, column=4, value=iteration).border = thin_border
        ws2.cell(row=row, column=5, value=f"{days} 天").border = thin_border

    # 总计行
    total_row = 5
    ws2.cell(row=total_row, column=1, value="总计").font = Font(bold=True)
    ws2.cell(row=total_row, column=2, value=sum(s["count"] for s in stats.values())).font = Font(bold=True)
    ws2.cell(row=total_row, column=3, value=sum(s["hours"] for s in stats.values())).font = Font(bold=True)

    for i, w in enumerate([12, 10, 14, 20, 12], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    wb.save(output_path)
    return output_path
```

### Step 4：交付

1. 在聊天中输出需求文档（Markdown 格式）
2. 生成 Excel 文件，路径：`~/.hermes/profiles/alpha/projects/{项目名}/需求分项清单-{项目名}.xlsx`
3. 告诉用户：需求文档已生成，可以直接把 Excel 甩给 AI 开发

## 优先级定义

| 优先级 | 含义 | 判断标准 |
|--------|------|----------|
| **P0** | MVP 必备 | 没有这个功能产品就不能用 |
| **P1** | 重要 | 有了体验好很多，没有也能凑合 |
| **P2** | 锦上添花 | 锦上添花，有空再做 |

## 工作量估算参考

| 功能类型 | 参考工时 |
|----------|----------|
| 简单 CRUD 页面 | 2-4h |
| 带交互的列表页 | 3-5h |
| 表单页（含验证） | 2-4h |
| 用户认证（登录/注册） | 4-6h |
| 文件上传/管理 | 3-5h |
| 搜索功能 | 2-4h |
| 数据可视化/图表 | 4-8h |
| 第三方 API 集成 | 3-6h |
| 响应式布局适配 | 2-4h |

## ⚠️ 路径陷阱（重要）

在 `execute_code` 中生成 Excel 时，`os.path.expanduser("~")` 会解析到 **profile 的 home 目录**（如 `~/.hermes/profiles/alpha/home/`），导致路径嵌套。

```python
# ❌ 错误 — 路径会嵌套
output_dir = os.path.expanduser("~/.hermes/profiles/alpha/projects/日记软件")
# 实际生成到: ~/.hermes/profiles/alpha/home/.hermes/profiles/alpha/projects/...

# ✅ 正确 — 使用绝对路径
output_dir = "/Users/shixy/.hermes/profiles/alpha/projects/日记软件"
```

生成后务必用 `terminal` 的 `find` 命令确认文件实际位置。

## 注意事项

1. **先问再分析**：不要假设用户想要什么，先确认核心需求
2. **P0 不超过 10 个功能**：MVP 要精简，快速验证
3. **验收标准必须具体**：不能写"用户体验好"，要写"点击按钮后 1 秒内跳转"
4. **技术栈推荐要务实**：用户说"你帮我决定"时，推荐最简单能跑通的方案
5. **Excel 是核心交付物**：用户可以直接甩给 AI 或开发团队使用
