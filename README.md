# 🛠️ Hermes Agent 自定义 Skills

个人的 Hermes Agent 技能集合和实用脚本。

## Skills 列表

| Skill | 分类 | 说明 | 用法 |
|-------|------|------|------|
| [requirement-analyst](productivity/requirement-analyst/) | productivity | 需求分析专家 — 输入想法，输出需求文档 + Excel | "我想做一个XXX，帮我出需求文档" |
| [model-routing](devops/model-routing/) | devops | 模型路由预检 — L1/L2/L3 分级，自动提醒切换模型 | 复杂任务自动触发 |
| [ui-worker](devops/ui-worker/) | devops | 视觉/UI/UX 设计中枢 — UI 概念、布局、原型代码、设计系统、Remotion 视频视觉 | "帮我设计一个XXX界面" 或 kanban 协作模式 |
| [hermes-achievements-cn-proxy](scripts/hermes-achievements-cn-proxy.py) | scripts | Hermes Dashboard 成就页中文化代理 | `python3 hermes-achievements-cn-proxy.py` |

## 目录结构

```
hermes-skills/
├── devops/                        # 开发运维类 Skill
│   ├── model-routing/
│   │   ├── SKILL.md               # 主规则文件
│   │   └── references/            # 技术细节与修复记录
│   └── ui-worker/
│       ├── SKILL.md               # 主规则文件
│       ├── README.md
│       └── reference/             # 反套路规约、品牌记忆、灵感库、design tokens 等
├── productivity/                   # 生产力类 Skill
│   └── requirement-analyst/
│       └── SKILL.md
└── scripts/                       # 实用脚本
    ├── hermes-achievements-cn-proxy.py
    └── README.md
```

## 安装

**完整克隆：**

```bash
git clone https://github.com/gatinul16-xy/hermes-skills.git ~/.hermes/profiles/alpha/skills/custom
```

**单独安装某个 Skill：**

```bash
# ui-worker
mkdir -p ~/.hermes/profiles/alpha/skills/devops/ui-worker
curl -o ~/.hermes/profiles/alpha/skills/devops/ui-worker/SKILL.md \
  https://raw.githubusercontent.com/gatinul16-xy/hermes-skills/main/devops/ui-worker/SKILL.md

# model-routing
mkdir -p ~/.hermes/profiles/alpha/skills/devops/model-routing
curl -o ~/.hermes/profiles/alpha/skills/devops/model-routing/SKILL.md \
  https://raw.githubusercontent.com/gatinul16-xy/hermes-skills/main/devops/model-routing/SKILL.md
```
