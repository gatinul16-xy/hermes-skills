# 🛠️ Hermes Agent 自定义 Skills

个人的 Hermes Agent 技能集合和实用脚本。

## Skills 列表

| Skill | 分类 | 说明 | 用法 |
|-------|------|------|------|
| [requirement-analyst](productivity/requirement-analyst/) | productivity | 需求分析专家 — 输入想法，输出需求文档 + Excel | "我想做一个XXX，帮我出需求文档" |
| [model-routing](devops/model-routing/) | devops | 模型路由预检 — L1/L2/L3 分级，自动提醒切换模型 | 复杂任务自动触发 |
| [hermes-achievements-cn-proxy](scripts/hermes-achievements-cn-proxy.py) | scripts | Hermes Dashboard 成就页中文化代理 | `python3 hermes-achievements-cn-proxy.py` |

## 目录结构

```
hermes-skills/
├── devops/                        # 开发运维类 Skill
│   └── model-routing/
│       ├── SKILL.md               # 主规则文件
│       └── references/            # 技术细节与修复记录
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
# model-routing
mkdir -p ~/.hermes/profiles/alpha/skills/devops/model-routing
curl -o ~/.hermes/profiles/alpha/skills/devops/model-routing/SKILL.md \
  https://raw.githubusercontent.com/gatinul16-xy/hermes-skills/main/devops/model-routing/SKILL.md

# requirement-analyst
mkdir -p ~/.hermes/profiles/alpha/skills/productivity/requirement-analyst
curl -o ~/.hermes/profiles/alpha/skills/productivity/requirement-analyst/SKILL.md \
  https://raw.githubusercontent.com/gatinul16-xy/hermes-skills/main/productivity/requirement-analyst/SKILL.md
```