#!/usr/bin/env python3
"""
Hermes Achievements Chinese Proxy
===================================
A local proxy that translates the Hermes Achievements dashboard to Chinese
without modifying any hermes source files.

Usage:
    python3 hermes-achievements-cn-proxy.py [--port PORT] [--target URL]

Default: port=9120, target=http://127.0.0.1:9119
"""

import argparse
import json
import re
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# ─── Translation Data ───────────────────────────────────────────────────────

ACHIEVEMENTS = {
    "let_him_cook": {"name": "让他做", "description": "让 Hermes 在单次会话中运行一段认真的自主工具链。"},
    "autonomous_avalanche": {"name": "自主雪崩", "description": "跨会话累积一生的 Hermes 工具调用量。"},
    "toolchain_maxxer": {"name": "工具链极客", "description": "在单次会话中使用广泛多样的 Hermes 工具。"},
    "full_send": {"name": "全力出击", "description": "终端、文件和网页/浏览器在一次实战中全部参与。"},
    "subagent_commander": {"name": "子代理指挥官", "description": "协调委派的代理工作。"},
    "background_process_enjoyer": {"name": "后台进程爱好者", "description": "启动或控制足够多的长时间运行进程，配得上这个称号。"},
    "cron_necromancer": {"name": "定时亡灵法师", "description": "从死亡中唤醒定期自主任务。"},
    "red_text_connoisseur": {"name": "红字品鉴师", "description": "遭遇足够多的错误，培养出对红色文本的鉴赏力。"},
    "stack_trace_sommelier": {"name": "堆栈品酒师", "description": "以品鉴的方式品味回溯，而不是小口啜饮。"},
    "actually_read_the_logs": {"name": "真的看了日志", "description": "反复检查日志，而不是瞎猜。"},
    "port_3000_taken": {"name": "3000 端口被占", "description": "发现开发服务器端口冲突模式次数足够多，已经麻木。"},
    "permission_denied_any_percent": {"name": "权限拒绝速通", "description": "速通进入权限墙。"},
    "dependency_hell_tourist": {"name": "依赖地狱游客", "description": "包安装失败，但生活奇迹般地继续。"},
    "the_fix_was_restarting": {"name": "修好了是因为重启了", "description": "在足够多的错误集群后重启，可以称之为技巧了。"},
    "forgot_the_env_var": {"name": "忘了环境变量", "description": "因为缺少环境变量导致认证或配置失败。"},
    "yaml_colon_incident": {"name": "YAML 冒号事件", "description": "配置语法反咬一口。"},
    "docker_name_collision": {"name": "Docker 命名冲突", "description": "容器名称已存在。当然会这样。"},
    "supposed_to_be_quick": {"name": "本来应该很快的", "description": "一个小请求变成了一场远征。"},
    "one_more_small_change": {"name": "再来一个小改动", "description": "在单次会话中做了足够多的文件编辑，让'小改动'这个词失去意义。"},
    "vibe_architect": {"name": "氛围架构师", "description": "在一个项目会话中触及广泛的表面积。"},
    "pixel_goblin": {"name": "像素哥布林", "description": "进行持续的前端、CSS、SVG 或视觉调优。"},
    "ship_first_ask_later": {"name": "先发再问", "description": "在严肃的工具链之后有 Git 活动。"},
    "css_exorcist": {"name": "CSS 驱魔师", "description": "反复从界面中驱除样式恶魔。"},
    "one_character_fix": {"name": "一个字符修好", "description": "在一堆错误之后做了个微小的编辑。痛苦。美妙。"},
    "skillsmith": {"name": "技能铁匠", "description": "足够多地使用 Hermes 技能，留下指纹。"},
    "skill_issue_skill_created": {"name": "技能问题？技能已创建", "description": "创建或修补持久化流程，而不是重复自己。"},
    "memory_keeper": {"name": "记忆守护者", "description": "用 memory 工具持久化知识。"},
    "memory_palace": {"name": "记忆宫殿", "description": "建立一条严肃的持久记忆轨迹。"},
    "context_dragon": {"name": "上下文巨龙", "description": "反复触及压缩、巨大上下文或 token 压力。"},
    "gateway_dweller": {"name": "网关居民", "description": "经历网关连接的 Hermes 工作流。"},
    "plugin_goblin": {"name": "插件哥布林", "description": "使用或开发插件，足以让仪表盘注意到。"},
    "rollback_wizard": {"name": "回滚巫师", "description": "施展回滚/检查点恢复魔法。"},
    "rabbit_hole_certified": {"name": "兔子洞认证", "description": "搜索或提取足够多的网页内容，够资格算作研究漩涡。"},
    "citation_goblin": {"name": "引用哥布林", "description": "提取足够多的网页，成为小小的图书管理员。"},
    "docs_archaeologist": {"name": "文档考古学家", "description": "反复挖掘文档来源。"},
    "browser_possession": {"name": "浏览器附身", "description": "通过自动化反复附身浏览器。"},
    "terminal_goblin": {"name": "终端哥布林", "description": "在 Shell 领域度过认真时间。"},
    "patch_wizard": {"name": "补丁巫师", "description": "用精确补丁随心所欲地弯曲文件。"},
    "file_archaeologist": {"name": "文件考古学家", "description": "通过读取和搜索挖掘文件系统。"},
    "image_whisperer": {"name": "图像低语者", "description": "足够多地使用图像生成或视觉工具进行视觉工作。"},
    "voice_of_the_machine": {"name": "机器之声", "description": "反复使用文字转语音或语音工具。"},
    "model_hopper": {"name": "模型跳蚤", "description": "切换或检查提供商/模型足够频繁，算作习惯。"},
    "openrouter_enjoyer": {"name": "OpenRouter 爱好者", "description": "反复通过 OpenRouter 路由模型工作。"},
    "codex_conjurer": {"name": "Codex 召唤师", "description": "足够频繁地召唤 Codex 风格的辅助，形成一个仪式。"},
    "multi_model_mage": {"name": "多模型法师", "description": "在 Hermes 历史中使用真正多样化的模型名称。"},
    "five_model_flight": {"name": "五模型飞行", "description": "尝试至少五个不同的 LLM，而不是和第一个回答的模型结婚。"},
    "provider_polyglot": {"name": "提供商多语者", "description": "在 Hermes 历史中跨多个提供商使用模型。"},
    "model_sommelier": {"name": "模型品酒师", "description": "品味足够多的模型/提供商对话，培养出偏好。"},
    "claude_confidant": {"name": "Claude 密友", "description": "反复将 Claude 风格的推理引入工作流。"},
    "gemini_cartographer": {"name": "Gemini 制图师", "description": "绘制足够多的 Gemini 相关工作流，了解地形。"},
    "open_weights_pilgrim": {"name": "开放权重朝圣者", "description": "通过 Hermes 会话元数据真正与本地/开放权重模型对话。"},
    "toolset_cartographer": {"name": "工具集制图师", "description": "刻意导航 Hermes 工具集，而不是把工具当作模糊的背景。"},
    "config_surgeon": {"name": "配置外科医生", "description": "毫不畏惧地操作真实的配置文件、清单、env 文件和仪表盘设置。"},
    "rebase_acrobat": {"name": "Rebase 杂技演员", "description": "处理真实的 Git 历史手术：rebase、冲突、合并、fetch、push。"},
    "test_suite_tamer": {"name": "测试套驯兽师", "description": "运行足够多的验证命令，让绿色文本成为仪式的一部分。"},
    "screenshot_hunter": {"name": "截图猎人", "description": "捕获、检查和打磨视觉证据，而不是只声称它有效。"},
    "marathon_operator": {"name": "马拉松操作员", "description": "积累大量的 Hermes 会话。"},
    "weekend_warrior": {"name": "周末战士", "description": "足够多次在周末运行 Hermes，使之成为生活方式。"},
    "night_shift_operator": {"name": "夜班操作员", "description": "在精灵时间反复运行会话。"},
    "cache_hit_appreciator": {"name": "缓存命中鉴赏家", "description": "注意到或受益于提示/缓存行为。"},
}

CATEGORIES = {
    "Agent Autonomy": "代理自主性",
    "Debugging Chaos": "调试混沌",
    "Vibe Coding": "氛围编码",
    "Hermes Native": "Hermes 原生",
    "Research/Web": "研究/网络",
    "Tool Mastery": "工具精通",
    "Model Lore": "模型传说",
    "Lifestyle": "生活方式",
}

TIERS = {
    "Copper": "青铜",
    "Silver": "白银",
    "Gold": "黄金",
    "Diamond": "钻石",
    "Olympian": "奥林匹亚",
}

# Full name patterns for tiers (e.g. "Copper Tier" or tier names used in badge objects)
TIER_NAME_MAP = {
    "Copper": "青铜",
    "Silver": "白银",
    "Gold": "黄金",
    "Diamond": "钻石",
    "Olympian": "奥林匹亚",
}

# UI strings for DOM injection
UI_STRINGS = {
    "Agent game score": "智能体游戏分数",
    "Hermes Achievements": "Hermes 成就",
    "Collectible Hermes badges": "可收集的 Hermes 徽章",
    "earned from real session history": "从真实会话历史中赢得的",
    "Known incomplete achievements": "已知未完成的成就",
    "show as": "显示为",
    "Discovered": "已发现",
    "Secret achievements stay hidden": "秘密成就保持隐藏",
    "until the first matching behavior": "直到首次出现匹配行为",
    "Unlocked": "已解锁",
    "Secrets": "秘密",
    "Secret": "秘密",
    "Highest Tier": "最高层级",
    "Latest": "最近",
    "Earned Badges": "已获得徽章",
    "Known, not earned": "已知，尚未获得",
    "Hidden until first signal": "隐藏直到首次信号",
    "None yet": "还没有",
    "Run more Hermes": "多运行 Hermes",
    "All": "全部",
    "Rescan": "重新扫描",
    "Share": "分享",
    "Share on X": "分享到 X",
    "Copy Image": "复制图片",
    "Download PNG": "下载 PNG",
    "Copied": "已复制",
    "Hidden": "隐藏",
    "Complete": "完成",
    "Objective": "目标",
    "Target": "目标",
    "Evidence": "证据",
    "No evidence yet": "暂无证据",
    "What counts": "统计范围",
    "How to reveal": "如何揭示",
    "No hidden secrets left in this scan.": "本次扫描中没有隐藏的秘密。",
    "Recent Unlocks": "最近解锁",
    "Scanning...": "扫描中…",
    "Scanning Hermes session history": "正在扫描 Hermes 会话历史",
    "Building achievement profile...": "构建成就档案…",
    "Scan Status": "扫描状态",
    "What's scanned": "扫描内容",
    "Sessions, tool calls, model metadata": "会话、工具调用、模型元数据",
    "Starting achievement scan...": "开始成就扫描…",
    "Tier": "层级",
    "Secret Achievements": "秘密成就",
    "Achievement": "成就",
    "Share:": "分享:",
    "Rendering...": "渲染中…",
    "Progress": "进度",
}

# ─── JSON Translation Logic ─────────────────────────────────────────────────

def translate_achievement_json(data):
    """Translate achievement API responses (list of achievements or single)."""
    if isinstance(data, list):
        return [translate_achievement_json(item) for item in data]
    if isinstance(data, dict):
        ach_id = data.get("id")
        if ach_id and ach_id in ACHIEVEMENTS:
            data["name"] = ACHIEVEMENTS[ach_id]["name"]
            data["description"] = ACHIEVEMENTS[ach_id]["description"]
        # Translate category
        cat = data.get("category")
        if cat and cat in CATEGORIES:
            data["category"] = CATEGORIES[cat]
        # Translate tier
        tier = data.get("tier")
        if tier and tier in TIERS:
            data["tier"] = TIERS[tier]
        tier_name = data.get("tierName")
        if tier_name and tier_name in TIER_NAME_MAP:
            data["tierName"] = TIER_NAME_MAP[tier_name]
        # Translate nested objects recursively
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                data[key] = translate_achievement_json(value)
    return data


def translate_sessions_badges(data):
    """Translate session badge data."""
    if isinstance(data, list):
        return [translate_sessions_badges(item) for item in data]
    if isinstance(data, dict):
        ach_id = data.get("id") or data.get("achievementId")
        if ach_id and ach_id in ACHIEVEMENTS:
            if "name" in data:
                data["name"] = ACHIEVEMENTS[ach_id]["name"]
            if "description" in data:
                data["description"] = ACHIEVEMENTS[ach_id]["description"]
        tier = data.get("tier")
        if tier and tier in TIERS:
            data["tier"] = TIERS[tier]
        tier_name = data.get("tierName")
        if tier_name and tier_name in TIER_NAME_MAP:
            data["tierName"] = TIER_NAME_MAP[tier_name]
        cat = data.get("category")
        if cat and cat in CATEGORIES:
            data["category"] = CATEGORIES[cat]
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                data[key] = translate_sessions_badges(value)
    return data


def is_achievements_api(path):
    """Check if the request path is an achievements API endpoint."""
    if path == "/api/plugins/hermes-achievements/achievements":
        return True
    if path == "/api/plugins/hermes-achievements/recent-unlocks":
        return True
    if re.match(r"^/api/plugins/hermes-achievements/sessions/[^/]+/badges$", path):
        return True
    return False


# ─── DOM Injection Script ───────────────────────────────────────────────────

DOM_INJECT_SCRIPT = r"""
<script>
(function() {
  'use strict';

  // Translation maps embedded from zh.json
  const ACHIEVEMENTS = ACHIEVEMENTS_PLACEHOLDER;
  const CATEGORIES = CATEGORIES_PLACEHOLDER;
  const TIERS = TIERS_PLACEHOLDER;
  const UI = UI_PLACEHOLDER;

  // Build reverse map: English name -> Chinese name for achievements
  const achNameMap = {};
  const achDescMap = {};
  for (const [id, t] of Object.entries(ACHIEVEMENTS)) {
    achNameMap[id] = t.name;
    achDescMap[id] = t.description;
  }

  // English UI string replacements (exact text -> zh)
  const textReplacements = {
    "Agent game score": "智能体游戏分数",
    "Hermes Achievements": "Hermes 成就",
    "Unlocked": "已解锁",
    "Discovered": "已发现",
    "Secrets": "秘密",
    "Secret": "秘密",
    "Highest Tier": "最高层级",
    "Latest": "最近",
    "Earned Badges": "已获得徽章",
    "Known, not earned": "已知，尚未获得",
    "Hidden until first signal": "隐藏直到首次信号",
    "None yet": "还没有",
    "Run more Hermes": "多运行 Hermes",
    "All": "全部",
    "Rescan": "重新扫描",
    "Share": "分享",
    "Share on X": "分享到 X",
    "Copy Image": "复制图片",
    "Download PNG": "下载 PNG",
    "Copied ✓": "已复制 ✓",
    "Hidden": "隐藏",
    "Complete": "完成",
    "Objective": "目标",
    "Target": "目标",
    "Evidence": "证据",
    "No evidence yet": "暂无证据",
    "What counts": "统计范围",
    "How to reveal": "如何揭示",
    "No hidden secrets left in this scan.": "本次扫描中没有隐藏的秘密。",
    "Recent Unlocks": "最近解锁",
    "Tier": "层级",
    "Achievement": "成就",
    "Share:": "分享:",
    "Rendering…": "渲染中…",
    "Scanning…": "扫描中…",
    "Starting achievement scan…": "开始成就扫描…",
    "Building achievement profile…": "构建成就档案…",
    "Scan Status": "扫描状态",
    "What's scanned": "扫描内容",
    "Sessions, tool calls, model metadata, errors, achievements, and local unlock status.":
      "会话、工具调用、模型元数据、错误、成就和本地解锁状态。",
    "Hermes is scanning local history once; cards appear automatically after.":
      "Hermes 正在扫描一次本地历史，之后卡片会自动出现。",
    "If it takes a few seconds, it's not stuck.":
      "如果这需要几秒钟，没有卡住。",
    "Secret achievements hide their exact triggers.":
      "秘密成就隐藏其精确触发条件。",
    "Once Hermes sees the relevant signal, the card flips to Discovered and shows its requirements.":
      "一旦 Hermes 看到相关信号，卡片会变成【已发现】并显示其要求。",
    "Collectible Hermes badges earned from real session history. Known incomplete achievements show as Discovered; secret achievements stay hidden until the first matching behavior.":
      "从真实会话历史中赢得的可收集的 Hermes 徽章。已知未完成的成就显示为【已发现】；秘密成就保持隐藏，直到首次出现匹配行为。",
    "Reading sessions, tool calls, model metadata and unlock status.":
      "读取会话、工具调用、模型元数据和解锁状态。",
  };

  // Tier name replacements
  const tierMap = {
    "Copper": "青铜",
    "Silver": "白银",
    "Gold": "黄金",
    "Diamond": "钻石",
    "Olympian": "奥林匹亚"
  };

  // Category replacements
  const categoryMap = {
    "Agent Autonomy": "代理自主性",
    "Debugging Chaos": "调试混沌",
    "Vibe Coding": "氛围编码",
    "Hermes Native": "Hermes 原生",
    "Research/Web": "研究/网络",
    "Tool Mastery": "工具精通",
    "Model Lore": "模型传说",
    "Lifestyle": "生活方式"
  };

  // Also build a map from English achievement names/descriptions to Chinese
  // We need the original English names which we won't have statically,
  // so we rely on the achievement id being present in the DOM somehow.
  // The DOM injection will primarily work by text replacement for UI strings
  // and by matching known English achievement content.

  // English achievement names and descriptions (reverse lookup)
  const EN_ACH_NAMES = {
    "Let Him Cook": "让他做",
    "Autonomous Avalanche": "自主雪崩",
    "Toolchain Maxxer": "工具链极客",
    "Full Send": "全力出击",
    "Subagent Commander": "子代理指挥官",
    "Background Process Enjoyer": "后台进程爱好者",
    "Cron Necromancer": "定时亡灵法师",
    "Red Text Connoisseur": "红字品鉴师",
    "Stack Trace Sommelier": "堆栈品酒师",
    "Actually Read the Logs": "真的看了日志",
    "Port 3000 Taken": "3000 端口被占",
    "Permission Denied Any%": "权限拒绝速通",
    "Dependency Hell Tourist": "依赖地狱游客",
    "The Fix Was Restarting": "修好了是因为重启了",
    "Forgot the Env Var": "忘了环境变量",
    "YAML Colon Incident": "YAML 冒号事件",
    "Docker Name Collision": "Docker 命名冲突",
    "Supposed to Be Quick": "本来应该很快的",
    "One More Small Change": "再来一个小改动",
    "Vibe Architect": "氛围架构师",
    "Pixel Goblin": "像素哥布林",
    "Ship First, Ask Later": "先发再问",
    "CSS Exorcist": "CSS 驱魔师",
    "One-Character Fix": "一个字符修好",
    "Skillsmith": "技能铁匠",
    "Skill Issue → Skill Created": "技能问题？技能已创建",
    "Memory Keeper": "记忆守护者",
    "Memory Palace": "记忆宫殿",
    "Context Dragon": "上下文巨龙",
    "Gateway Dweller": "网关居民",
    "Plugin Goblin": "插件哥布林",
    "Rollback Wizard": "回滚巫师",
    "Rabbit Hole Certified": "兔子洞认证",
    "Citation Goblin": "引用哥布林",
    "Docs Archaeologist": "文档考古学家",
    "Browser Possession": "浏览器附身",
    "Terminal Goblin": "终端哥布林",
    "Patch Wizard": "补丁巫师",
    "File Archaeologist": "文件考古学家",
    "Image Whisperer": "图像低语者",
    "Voice of the Machine": "机器之声",
    "Model Hopper": "模型跳蚤",
    "OpenRouter Enjoyer": "OpenRouter 爱好者",
    "Codex Conjurer": "Codex 召唤师",
    "Multi-Model Mage": "多模型法师",
    "Five-Model Flight": "五模型飞行",
    "Provider Polyglot": "提供商多语者",
    "Model Sommelier": "模型品酒师",
    "Claude Confidant": "Claude 密友",
    "Gemini Cartographer": "Gemini 制图师",
    "Open-Weights Pilgrim": "开放权重朝圣者",
    "Toolset Cartographer": "工具集制图师",
    "Config Surgeon": "配置外科医生",
    "Rebase Acrobat": "Rebase 杂技演员",
    "Test Suite Tamer": "测试套驯兽师",
    "Screenshot Hunter": "截图猎人",
    "Marathon Operator": "马拉松操作员",
    "Weekend Warrior": "周末战士",
    "Night Shift Operator": "夜班操作员",
    "Cache Hit Appreciator": "缓存命中鉴赏家"
  };

  const EN_ACH_DESCS = {
    "Run Hermes in a single session through a serious autonomous tool chain.":
      "让 Hermes 在单次会话中运行一段认真的自主工具链。",
    "Accumulate a lifetime of Hermes tool calls across sessions.":
      "跨会话累积一生的 Hermes 工具调用量。",
    "Use a wide variety of Hermes tools in a single session.":
      "在单次会话中使用广泛多样的 Hermes 工具。",
    "Terminal, files, and web/browser all participate in a single engagement.":
      "终端、文件和网页/浏览器在一次实战中全部参与。",
    "Coordinate delegated agent work.":
      "协调委派的代理工作。",
    "Start or control enough long-running processes to deserve the title.":
      "启动或控制足够多的长时间运行进程，配得上这个称号。",
    "Raise periodic autonomous tasks from the dead.":
      "从死亡中唤醒定期自主任务。",
    "Encounter enough errors to cultivate a taste for red text.":
      "遭遇足够多的错误，培养出对红色文本的鉴赏力。",
    "Savour backtraces with appreciation, not just sipping.":
      "以品鉴的方式品味回溯，而不是小口啜饮。",
    "Check the logs repeatedly instead of guessing.":
      "反复检查日志，而不是瞎猜。",
    "Discover dev-server port-conflict patterns enough times to go numb.":
      "发现开发服务器端口冲突模式次数足够多，已经麻木。",
    "Speedrun into a permissions wall.":
      "速通进入权限墙。",
    "Package install fails, but life miraculously continues.":
      "包安装失败，但生活奇迹般地继续。",
    "Restart after enough error clusters and you can call it a technique.":
      "在足够多的错误集群后重启，可以称之为技巧了。",
    "Auth or config failure due to missing environment variable.":
      "因为缺少环境变量导致认证或配置失败。",
    "Config syntax bites back.":
      "配置语法反咬一口。",
    "Container name already exists. Of course it does.":
      "容器名称已存在。当然会这样。",
    "A small request becomes an expedition.":
      "一个小请求变成了一场远征。",
    "Edit enough files in a single session to make 'small change' meaningless.":
      "在单次会话中做了足够多的文件编辑，让'小改动'这个词失去意义。",
    "Touch a broad surface area in a single project session.":
      "在一个项目会话中触及广泛的表面积。",
    "Do sustained frontend, CSS, SVG, or visual tuning.":
      "进行持续的前端、CSS、SVG 或视觉调优。",
    "Have git activity after a serious tool chain.":
      "在严肃的工具链之后有 Git 活动。",
    "Repeatedly exorcise styling demons from the UI.":
      "反复从界面中驱除样式恶魔。",
    "Make a tiny edit after a stack of errors. Painful. Beautiful.":
      "在一堆错误之后做了个微小的编辑。痛苦。美妙。",
    "Use Hermes skills enough to leave fingerprints.":
      "足够多地使用 Hermes 技能，留下指纹。",
    "Create or patch persistent workflows instead of repeating yourself.":
      "创建或修补持久化流程，而不是重复自己。",
    "Persist knowledge with the memory tool.":
      "用 memory 工具持久化知识。",
    "Build a serious persistent memory trail.":
      "建立一条严肃的持久记忆轨迹。",
    "Repeatedly hit compression, huge context, or token pressure.":
      "反复触及触及压缩、巨大上下文或 token 压力。",
    "Experience gateway-connected Hermes workflows.":
      "经历网关连接的 Hermes 工作流。",
    "Use or develop plugins enough for the dashboard to notice.":
      "使用或开发插件，足以让仪表盘注意到。",
    "Cast rollback/checkpoint-resume magic.":
      "施展回滚/检查点恢复魔法。",
    "Search or scrape enough web content to qualify as a research vortex.":
      "搜索或提取足够多的网页内容，够资格算作研究漩涡。",
    "Scrape enough web pages to become a tiny librarian.":
      "提取足够多的网页，成为小小的图书管理员。",
    "Repeatedly dig into documentation sources.":
      "反复挖掘文档来源。",
    "Repeatedly possess the browser via automation.":
      "通过自动化反复附身浏览器。",
    "Spend serious time in the shell domain.":
      "在 Shell 领域度过认真时间。",
    "Bend files to your will with precise patches.":
      "用精确补丁随心所欲地弯曲文件。",
    "Dig through the filesystem via reads and searches.":
      "通过读取和搜索挖掘文件系统。",
    "Use image generation or vision tools enough for visual work.":
      "足够多地使用图像生成或视觉工具进行视觉工作。",
    "Repeatedly use text-to-speech or voice tools.":
      "反复使用文字转语音或语音工具。",
    "Switch or check providers/models often enough to count as a habit.":
      "切换或检查提供商/模型足够频繁，算作习惯。",
    "Route model work through OpenRouter repeatedly.":
      "反复通过 OpenRouter 路由模型工作。",
    "Summon Codex-style assistance often enough to form a ritual.":
      "足够频繁地召唤 Codex 风格的辅助，形成一个仪式。",
    "Use genuinely diverse model names across Hermes history.":
      "在 Hermes 历史中使用真正多样化的模型名称。",
    "Try at least five different LLMs instead of marrying the first one that replies.":
      "尝试至少五个不同的 LLM，而不是和第一个回答的模型结婚。",
    "Use models across multiple providers in Hermes history.":
      "在 Hermes 历史中跨多个提供商使用模型。",
    "Taste enough model/provider conversations to develop a preference.":
      "品味足够多的模型/提供商对话，培养出偏好。",
    "Bring Claude-style reasoning into workflows repeatedly.":
      "反复将 Claude 风格的推理引入工作流。",
    "Map enough Gemini-related workflows to know the terrain.":
      "绘制足够多的 Gemini 相关工作流，了解地形。",
    "Talk to local/open-weight models via Hermes session metadata for real.":
      "通过 Hermes 会话元数据真正与本地/开放权重模型对话。",
    "Deliberately navigate the Hermes toolset instead of treating tools as a vague backdrop.":
      "刻意导航 Hermes 工具集，而不是把工具当作模糊的背景。",
    "Manipulate real config files, manifests, env files, and dashboard settings without fear.":
      "毫不畏惧地操作真实的配置文件、清单、env 文件和仪表盘设置。",
    "Handle real git history surgery: rebase, conflicts, merges, fetch, push.":
      "处理真实的 Git 历史手术：rebase、冲突、合并、fetch、push。",
    "Run enough validation commands for green text to become part of the ritual.":
      "运行足够多的验证命令，让绿色文本成为仪式的一部分。",
    "Capture, inspect, and polish visual evidence instead of just claiming it works.":
      "捕获、检查和打磨视觉证据，而不是只声称它有效。",
    "Accumulate a large number of Hermes sessions.":
      "积累大量的 Hermes 会话。",
    "Run Hermes on weekends often enough for it to become a lifestyle.":
      "足够多次在周末运行 Hermes，使之成为生活方式。",
    "Run sessions during the witching hours repeatedly.":
      "在精灵时间反复运行会话。",
    "Notice or benefit from prompt/cache behaviour.":
      "注意到或受益于提示/缓存行为。"
  };

  function isZh() {
    try { return localStorage.getItem('hermes-locale') === 'zh'; } catch(e) { return false; }
  }

  function translateTextNode(node) {
    const text = node.textContent.trim();
    if (!text) return;
    // Exact match replacements
    for (const [en, zh] of Object.entries(textReplacements)) {
      if (text === en) {
        node.textContent = node.textContent.replace(en, zh);
        return;
      }
    }
    // Achievement names
    for (const [en, zh] of Object.entries(EN_ACH_NAMES)) {
      if (text === en) {
        node.textContent = node.textContent.replace(en, zh);
        return;
      }
    }
    // Achievement descriptions
    for (const [en, zh] of Object.entries(EN_ACH_DESCS)) {
      if (text === en) {
        node.textContent = node.textContent.replace(en, zh);
        return;
      }
    }
    // Tier names
    for (const [en, zh] of Object.entries(tierMap)) {
      if (text === en) {
        node.textContent = node.textContent.replace(en, zh);
        return;
      }
    }
    // Category names
    for (const [en, zh] of Object.entries(categoryMap)) {
      if (text === en) {
        node.textContent = node.textContent.replace(en, zh);
        return;
      }
    }
  }

  function translateElement(el) {
    if (!isZh()) return;
    // Translate direct text nodes
    for (const child of el.childNodes) {
      if (child.nodeType === 3) {
        translateTextNode(child);
      }
    }
    // Translate child elements
    for (const child of el.querySelectorAll('*')) {
      for (const tn of child.childNodes) {
        if (tn.nodeType === 3) {
          translateTextNode(tn);
        }
      }
    }
    // Also handle placeholder, title, aria-label attributes
    if (el.placeholder) {
      for (const [en, zh] of Object.entries(textReplacements)) {
        if (el.placeholder === en) el.placeholder = zh;
      }
    }
    if (el.title) {
      for (const [en, zh] of Object.entries(textReplacements)) {
        if (el.title === en) el.title = zh;
      }
    }
  }

  function fullTranslate() {
    if (!isZh()) return;
    translateElement(document.body);
  }

  // Wait for .ha-page then apply translations
  function waitForPage() {
    const observer = new MutationObserver((mutations) => {
      if (!isZh()) return;
      for (const m of mutations) {
        for (const node of m.addedNodes) {
          if (node.nodeType === 1) {
            translateElement(node);
          }
        }
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Initial pass with retries
    let attempts = 0;
    function tryTranslate() {
      attempts++;
      fullTranslate();
      if (attempts < 60) setTimeout(tryTranslate, 500);
    }
    tryTranslate();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitForPage);
  } else {
    waitForPage();
  }
})();
</script>
"""

def build_dom_inject_script():
    """Build the DOM injection script with actual translation data."""
    ach_json = json.dumps(ACHIEVEMENTS, ensure_ascii=False)
    cat_json = json.dumps(CATEGORIES, ensure_ascii=False)
    tier_json = json.dumps(TIERS, ensure_ascii=False)
    ui_json = json.dumps(UI_STRINGS, ensure_ascii=False)

    script = DOM_INJECT_SCRIPT
    script = script.replace("ACHIEVEMENTS_PLACEHOLDER", ach_json)
    script = script.replace("CATEGORIES_PLACEHOLDER", cat_json)
    script = script.replace("TIERS_PLACEHOLDER", tier_json)
    script = script.replace("UI_PLACEHOLDER", ui_json)
    return script

# Pre-build the injection script once
INJECT_SCRIPT = build_dom_inject_script()

# ─── Proxy Handler ───────────────────────────────────────────────────────────

BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    '.js', '.mjs', '.css',
    '.mp3', '.mp4', '.webm', '.ogg',
    '.zip', '.gz', '.tar',
    '.pdf',
}

def is_binary_content(content_type, path):
    """Determine if response should be treated as binary."""
    if content_type:
        ct = content_type.lower()
        if any(t in ct for t in ['image/', 'font/', 'audio/', 'video/',
                                   'application/octet-stream', 'application/wasm',
                                   'application/javascript', 'text/css',
                                   'application/font']):
            return True
    # Check file extension
    path_lower = path.lower().split('?')[0]
    for ext in BINARY_EXTENSIONS:
        if path_lower.endswith(ext):
            return True
    return False


class ProxyHandler(BaseHTTPRequestHandler):
    """HTTP proxy handler that intercepts achievements API and HTML responses."""

    target = "http://127.0.0.1:9119"

    def log_message(self, format, *args):
        """Override to use our logging format."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = format % args if args else format
        line = f"[{timestamp}] {msg}\n"
        sys.stdout.write(line)
        sys.stdout.flush()
        sys.stderr.write(line)
        sys.stderr.flush()

    def do_request(self):
        """Proxy the request to the target, intercepting certain responses."""
        method = self.command
        path = self.path

        # Build target URL
        target_url = self.target + path

        # Read request body if present
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # Forward headers (exclude host and hop-by-hop headers)
        forward_headers = {}
        for key, value in self.headers.items():
            if key.lower() not in ('host', 'connection', 'transfer-encoding'):
                forward_headers[key] = value

        try:
            # Build the request
            req = urllib.request.Request(target_url, data=body, headers=forward_headers, method=method)

            # Send request to target
            with urllib.request.urlopen(req, timeout=30) as resp:
                status_code = resp.status
                response_headers = dict(resp.getheaders())
                content_type = resp.getheader('Content-Type', '')
                raw_data = resp.read()

        except urllib.error.HTTPError as e:
            status_code = e.code
            response_headers = dict(e.headers)
            content_type = e.headers.get('Content-Type', '')
            raw_data = e.read()
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            error_html = f"""<!DOCTYPE html>
<html><head><title>Proxy Error</title></head>
<body style="font-family:sans-serif;padding:40px;background:#1a1a2e;color:#e0e0e0">
<h1 style="color:#ff6b6b">⚠ 无法连接到目标仪表盘</h1>
<p>目标: <code>{self.target}</code></p>
<p>错误: <code>{e.reason}</code></p>
<p>请确保 Hermes 仪表盘正在运行。</p>
<pre style="background:#16213e;padding:12px;border-radius:6px">hermes dashboard</pre>
</body></html>"""
            self.wfile.write(error_html.encode('utf-8'))
            self.log_message(f"→ 502 {method} {path} (target unreachable)")
            return
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            error_html = f"""<!DOCTYPE html>
<html><head><title>Proxy Error</title></head>
<body style="font-family:sans-serif;padding:40px;background:#1a1a2e;color:#e0e0e0">
<h1 style="color:#ff6b6b">⚠ 代理错误</h1>
<p>错误: <code>{str(e)}</code></p>
</body></html>"""
            self.wfile.write(error_html.encode('utf-8'))
            self.log_message(f"→ 502 {method} {path} (error: {e})")
            return

        # Determine if we need to intercept
        is_ach_api = is_achievements_api(path)
        is_html = content_type and 'text/html' in content_type.lower()

        # Process response
        if is_ach_api and raw_data:
            # Translate achievements JSON
            try:
                data = json.loads(raw_data.decode('utf-8'))
                if path == "/api/plugins/hermes-achievements/recent-unlocks":
                    data = translate_sessions_badges(data)
                elif "/badges" in path:
                    data = translate_sessions_badges(data)
                else:
                    data = translate_achievement_json(data)
                modified_data = json.dumps(data, ensure_ascii=False).encode('utf-8')

                self.send_response(status_code)
                for key, value in response_headers.items():
                    if key.lower() not in ('content-length', 'transfer-encoding', 'content-encoding'):
                        self.send_header(key, value)
                self.send_header('Content-Length', str(len(modified_data)))
                self.end_headers()
                self.wfile.write(modified_data)
                self.log_message(f"→ {status_code} {method} {path} [TRANSLATED]")
                return
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fall through to raw proxy
                pass

        if is_html and raw_data:
            # Inject DOM translation script before </body>
            try:
                html = raw_data.decode('utf-8')
                if '</body>' in html:
                    html = html.replace('</body>', INJECT_SCRIPT + '\n</body>')
                    modified_data = html.encode('utf-8')

                    self.send_response(status_code)
                    for key, value in response_headers.items():
                        if key.lower() not in ('content-length', 'transfer-encoding', 'content-encoding'):
                            self.send_header(key, value)
                    self.send_header('Content-Length', str(len(modified_data)))
                    self.end_headers()
                    self.wfile.write(modified_data)
                    self.log_message(f"→ {status_code} {method} {path} [SCRIPT INJECTED]")
                    return
            except UnicodeDecodeError:
                pass

        # Default: pass through raw
        self.send_response(status_code)
        for key, value in response_headers.items():
            if key.lower() not in ('transfer-encoding', 'content-encoding'):
                self.send_header(key, value)
        if 'content-length' not in {k.lower() for k in response_headers}:
            self.send_header('Content-Length', str(len(raw_data)))
        self.end_headers()
        self.wfile.write(raw_data)
        self.log_message(f"→ {status_code} {method} {path}")

    # Handle all HTTP methods
    do_GET = do_request
    do_POST = do_request
    do_PUT = do_request
    do_DELETE = do_request
    do_PATCH = do_request
    do_HEAD = do_request
    do_OPTIONS = do_request


# ─── CLI & Server ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hermes Achievements Chinese Proxy - 中文化代理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 hermes-achievements-cn-proxy.py
  python3 hermes-achievements-cn-proxy.py --port 9120 --target http://127.0.0.1:9119

然后在浏览器中访问: http://localhost:9120
        """
    )
    parser.add_argument('--port', type=int, default=9120,
                        help='代理服务器端口 (默认: 9120)')
    parser.add_argument('--target', type=str, default='http://127.0.0.1:9119',
                        help='目标仪表盘 URL (默认: http://127.0.0.1:9119)')

    args = parser.parse_args()

    # Normalize target URL (remove trailing slash)
    target = args.target.rstrip('/')

    # Set target on handler class
    ProxyHandler.target = target

    # Allow quick restart without waiting for port release
    HTTPServer.allow_reuse_address = True
    server = HTTPServer(('0.0.0.0', args.port), ProxyHandler)

    print(f"""
╔══════════════════════════════════════════════════════╗
║   Hermes 成就中文化代理服务器                       ║
║   Hermes Achievements Chinese Proxy                  ║
╠══════════════════════════════════════════════════════╣
║   代理地址 (Proxy):    http://localhost:{args.port:<5}        ║
║   目标地址 (Target):   {target:<28} ║
╠══════════════════════════════════════════════════════╣
║   ✓ 60 个成就翻译数据已加载                          ║
║   ✓ 8 个类别翻译已加载                               ║
║   ✓ 5 个层级翻译已加载                               ║
║   ✓ DOM 注入脚本已准备                               ║
╠══════════════════════════════════════════════════════╣
║   浏览器打开: http://localhost:{args.port:<5}              ║
║   按 Ctrl+C 停止                                     ║
╚══════════════════════════════════════════════════════╝
""")

    def shutdown_handler(signum, frame):
        print("\n⏹ 正在关闭代理服务器...")
        server.shutdown()
        sys.exit(0)

    import signal
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹ 正在关闭代理服务器...")
        server.shutdown()
        sys.exit(0)


if __name__ == '__main__':
    main()
