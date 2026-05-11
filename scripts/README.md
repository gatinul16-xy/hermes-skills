# Hermes Achievements 中文化代理

将 Hermes Dashboard 的 Achievements 插件页面翻译为中文。

## 原理

在本地启动一个 HTTP 代理服务器，拦截成就 API 响应并注入中文翻译。**不修改任何 Hermes Agent 源码。**

## 使用

```bash
# 1. 确保 Dashboard 在运行
hermes dashboard

# 2. 启动翻译代理
python3 hermes-achievements-cn-proxy.py

# 3. 浏览器访问 http://127.0.0.1:9120
```

## 选项

```
--port PORT      代理端口（默认 9120）
--target URL     目标 Dashboard 地址（默认 http://127.0.0.1:9119）
```

## 翻译内容

- ✅ 60+ 个成就名称和描述
- ✅ 8 个成就类别
- ✅ 5 个层级（青铜/白银/黄金/钻石/奥林匹亚）
- ✅ 页面 UI 标签（按钮、统计卡、筛选器等）

## 依赖

零外部依赖，仅需 Python 3 标准库。
