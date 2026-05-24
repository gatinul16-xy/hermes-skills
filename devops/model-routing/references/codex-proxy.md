# Codex Thin Proxy — 架构与运维

> 创建日期：2026-05-19
> 配套脚本：`~/.hermes/scripts/codex_proxy.py`
>
> **当前状态（2026-05-20）：⚠️ 未就绪**
> - Proxy 进程未运行（端口 8002 未监听）
> - `HERMES_CODEX_BASE_URL` 未写入 `.env`
> - `openai-codex` provider 未在 `config.yaml` 注册
> - OAuth 未执行（`hermes login --provider openai-codex` 未跑）
> - **L3 派发首选方案不可用，当前自动回退到 ACP fallback 或继续当前模型**

## 为什么需要 Proxy

| 问题 | ACP 方案 | Proxy 方案 |
|------|---------|-----------|
| 依赖 | 本地 copilot CLI 二进制 | 无外部依赖 |
| 失败行为 | 静默退化为 Hermes subagent | 返回明确 HTTP 错误 |
| 执行回执 | 无法注入 | HMAC 签名 provenance |
| 审计 | 无 | JSONL 审计日志 |
| Hermes 集成 | ACP transport 协议 | 原生 openai-codex provider + env var |

## 架构

```
┌─────────┐  codex_responses   ┌──────────────┐  codex_responses   ┌──────────────────────┐
│  Hermes │ ──────────────────▶│ codex_proxy  │ ──────────────────▶│ chatgpt.com/backend/ │
│         │◀──────────────────│ 127.0.0.1:8002│◀──────────────────│ api/codex            │
└─────────┘                    └──────────────┘                    └──────────────────────┘
                                   │
                                   ├─ HMAC-SHA256 签名注入
                                   ├─ /tmp/codex_proxy_audit.jsonl
                                   └─ 透传 OAuth Authorization header
```

## 环境变量

| 变量 | 用途 | 默认值 |
|------|------|--------|
| `HERMES_CODEX_BASE_URL` | Hermes 端，指向 proxy | `https://chatgpt.com/backend-api/codex` |
| `CODEX_BACKEND_URL` | Proxy 端，Codex 真实后端 | `https://chatgpt.com/backend-api/codex` |
| `CODEX_PROXY_PORT` | Proxy 监听端口 | `8002` |
| `CODEX_PROXY_SIGNING_KEY` | HMAC 签名密钥（base64） | 自动生成 |
| `CODEX_PROXY_AUDIT_LOG` | 审计日志路径 | `/tmp/codex_proxy_audit.jsonl` |

## 启动命令

```bash
# 首次：生成签名密钥 + 设置环境变量
echo 'HERMES_CODEX_BASE_URL=http://127.0.0.1:8002' >> ~/.hermes/.env

# 认证
hermes login --provider openai-codex

# 启动 proxy
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/scripts/codex_proxy.py &

# 验证
curl -s http://127.0.0.1:8002/ | head -1
# 预期：从 Codex 后端返回的响应（可能是 403 如果未认证）
```

## Provenance 签名格式

Proxy 在每个 JSON 响应中注入：

```json
{
  "hermes_provenance": {
    "backend": "codex",
    "model": "gpt-5-codex",
    "timestamp": "2026-05-19T08:24:30Z",
    "request_id": "cpx_1716100467000000",
    "response_digest": "sha256:a1b2c3d4e5f6a7b8",
    "signature": "AbCdEf123456..."
  }
}
```

签名算法：`HMAC-SHA256(json(provenance_fields, sort_keys), signing_key) → base64`

验证方式（待实现 CLI）：
```bash
hermes prov verify cpx_1716100467000000
```

## 审计日志

`/tmp/codex_proxy_audit.jsonl` 每行一条：

```json
{"ts":"2026-05-19T08:24:30Z","request_id":"cpx_...","method":"POST","path":"/v1/responses","status":200,"duration_ms":1234.5,"request_size":4567,"response_size":8901,"provenance":{...}}
```

## 运维

```bash
# 检查 proxy 是否在跑
lsof -i :8002

# 查看最近审计日志
tail -5 /tmp/codex_proxy_audit.jsonl | python3 -m json.tool

# 手动重启
kill $(lsof -ti :8002) 2>/dev/null
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/scripts/codex_proxy.py &

# 查看签名密钥
cat ~/.hermes/.codex_proxy_signing_key
```

## 已知限制

1. **OAuth token 刷新**：由 Hermes 管理。Token 过期后需重新 `hermes login`
2. **Proxy 非持久化**：重启 Mac 后需手动重启 proxy。可加入 gateway 自启动脚本
3. **签名仅覆盖 JSON 响应**：流式（SSE）响应当前不注入 provenance
4. **无 TLS**：localhost 通信为明文 HTTP。如需加固，可加自签证书或 Unix socket
5. **单实例**：`HTTPServer` 是单线程。生产可换 `ThreadingHTTPServer`
