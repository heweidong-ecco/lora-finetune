第24天：系统整合——全家桶一键启动

今日目标：将FastAPI网关、Ollama推理（通用+查询改写+代码补全）、vLLM推理、Redis缓存全部编排到Docker Compose，实现 docker compose up -d 一键启动全部服务。

一、降维打击——理解系统整合

1. 大白话解释

之前：你的FastAPI网关、Redis缓存、Ollama推理服务、vLLM推理服务……它们像散落在仓库各处的零件。每次开机，你需要先启动Redis，再启动Ollama，再启动vLLM，再启动FastAPI，还得确保它们的启动顺序正确，配置不冲突。这就像每天开店前，你要挨个去开电闸、开灯、开空调、开收银机——烦琐且容易漏。

今天：你把所有服务的启动方式、配置、依赖关系写在一张“开店清单”（docker-compose.yml）里。以后每天开机，只需要对着清单喊一声“开店”（docker compose up -d）。所有服务自动按顺序启动，配置不会错，端口不会冲突，数据不会丢。从“手动管理多个服务”到“一键启动全家桶”，这是从开发者到运维者的关键一步。

2. 系统架构总览

text
用户请求
```
    ↓
```
FastAPI 网关 (8000端口)
```
    ├── API Key 认证
    ├── Redis 限流
    └── 智能路由 (/v1/chat/smart-routed)
        ├── 查询改写 (query-rewriter, 3B, 100ms)
        ├── 通用对话 (qwen3:8b)
        └── 代码补全 (code-completer, 7B)
            ↓
        Ollama (11434端口) ← 管理所有微调模型
        vLLM (8001端口) ← 高性能推理（可选）
            ↓
        Redis (6379端口) ← 限流计数 + 缓存
```

二、动手操作

第1步：确认所有服务组件就绪

```bash
#确认Ollama中有三个模型
ollama list | grep -E "qwen3:8b|query-rewriter|code-completer"

#确认Redis可用
redis-cli ping

#确认FastAPI代码完整
ls /root/autodl-fs/llm-gateway/main.py
第2步：更新FastAPI网关代码
```
在/root/autodl-fs/llm-gateway/main.py中，确保集成了所有路由：

```python
#已有的路由（确认都存在）
@app.get("/health")                    # 健康检查
@app.post("/v1/generate")             # 原始生成接口
@app.post("/v1/chat/smart-routed")    # 智能路由接口（第8天）
@app.post("/v1/compare")              # 对比测试接口（第7天）

#新增：查询改写接口
@app.post("/v1/rewrite")
async def rewrite_query(req: RewriteRequest):
    """调用query-rewriter模型改写查询"""
    response = ollama_chat(
        prompt=f"将以下用户口语查询改写为精确的检索查询：{req.query}",
        model="query-rewriter",
        temperature=0.0,
        max_tokens=100
    )
    return {"original": req.query, "rewritten": response}

#新增：代码补全接口
@app.post("/v1/code/complete")
async def complete_code(req: CodeCompleteRequest):
    """调用code-completer模型补全代码"""
    response = ollama_chat(
        prompt=req.prefix,
        model="code-completer",
        temperature=0.0,
        max_tokens=256
    )
    return {"completion": response}
```
第3步：更新docker-compose.yml

在/root/autodl-fs/llm-gateway/docker-compose.yml中，确保Ollama服务的volumes映射正确：

yaml
services:
```
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: llm-gateway
    ports:
      - "8000:8000"
    environment:
      - API_KEY=${API_KEY:?API_KEY 未设置}
      - REDIS_HOST=redis
      - OLLAMA_HOST=ollama
      - VLLM_HOST=vllm
    depends_on:
      redis:
        condition: service_healthy
      ollama:
        condition: service_started
    restart: unless-stopped
```

```
  redis:
    image: redis:7-alpine
    container_name: llm-redis
    ports:
      - "6379:6379"
    volumes:
      - /root/autodl-fs/redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3
    restart: unless-stopped
```

```
  ollama:
    image: ollama/ollama:latest
    container_name: llm-ollama
    ports:
      - "11434:11434"
    volumes:
      - /root/autodl-fs/ollama-models:/root/.ollama
    restart: unless-stopped
    command: ["serve"]
```

```
  vllm:
    image: vllm/vllm-openai:latest
    container_name: llm-vllm
    ports:
      - "8001:8001"
    volumes:
      - /root/autodl-fs/vllm-models:/models
    command: >
      --model /models/qwen2.5-7b-instruct
      --served-model-name my-local-model
      --host 0.0.0.0
      --port 8001
    restart: unless-stopped
```
第4步：构建并启动全家桶

```bash
cd /root/autodl-fs/llm-gateway
docker compose build api
docker compose up -d
```
第5步：验证所有服务

```bash
#查看服务状态
docker compose ps

#测试各接口
curl http://localhost:8000/health                          # 健康检查
curl -X POST http://localhost:8000/v1/rewrite \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"query":"那个蓝色的怎么卖？"}'                      # 查询改写
curl -X POST http://localhost:8000/v1/code/complete \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"prefix":"def quicksort(arr):\n    \"\"\"快速排序\"\"\""}'  # 代码补全
```
三、练习题

必做1：docker compose up -d一键启动全部服务成功。
必做2：docker compose ps确认四个服务（api、redis、ollama、vllm）全部UP。
必做3：测试三个接口（health、rewrite、code/complete）全部返回正常。

选做：绘制系统架构图（Markdown或Mermaid格式），纳入README。

四、今日收工标准

□ main.py已更新，包含/v1/rewrite和/v1/code/complete路由
□ docker-compose.yml已更新
□ docker compose up -d一键启动成功
□ docker compose ps所有服务状态为UP
□ 健康检查、查询改写、代码补全三个接口测试通过
□ 系统架构图已绘制

# 选做：绘制系统架构图（Markdown或Mermaid格式），纳入README。
以下是可直接纳入项目README的系统架构图，提供Markdown文本图和Mermaid代码两种格式。

系统架构图（Markdown文本版）

```text
                          ┌─────────────────────────────────────────┐
                          │              用户请求                    │
                          └────────────────────┬────────────────────┘
                                               │
                                               ▼
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FastAPI 网关 (端口 8000)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────────┐ │
│  │ API Key 认证 │  │ Redis 限流  │  │          智能路由                    │ │
│  │ (第2天)     │  │ (第3天)     │  │  ┌───────────┬──────────┬─────────┐ │ │
│  │             │  │             │  │  │ 查询改写   │ 通用对话  │ 代码补全 │ │ │
│  │             │  │             │  │  │ (第19天)  │ (第12天) │ (第22天)│ │ │
│  │             │  │             │  │  └─────┬─────┴────┬─────┴────┬────┘ │ │
│  └─────────────┘  └──────┬──────┘  └───────┼──────────┼──────────┼──────┘ │
│                          │                  │          │          │        │
└──────────────────────────┼──────────────────┼──────────┼──────────┼────────┘
```
                           │                  │          │          │
                           ▼                  └──────────┼──────────┘
              ┌─────────────────────┐                    │
              │   Redis (端口 6379)  │                    ▼
              │   限流计数 + 缓存    │     ┌─────────────────────────────┐
              │   数据卷: redis-data│     │    Ollama (端口 11434)       │
              └─────────────────────┘     │  ┌─────────────────────────┐│
                                          │  │ query-rewriter (3B)     ││
                                          │  │ 查询改写 · 100ms 延迟   ││
                                          │  ├─────────────────────────┤│
                                          │  │ qwen3:8b (8B)           ││
                                          │  │ 通用对话 · 主力模型     ││
                                          │  ├─────────────────────────┤│
                                          │  │ code-completer (7B)     ││
                                          │  │ 代码补全 · FIM微调      ││
                                          │  └─────────────────────────┘│
                                          │  数据卷: ollama-models       │
                                          └─────────────────────────────┘
```
                                          
```
              ┌─────────────────────────────┐
              │    vLLM (端口 8001)          │
              │   高性能推理 · OpenAI兼容API │
              │   数据卷: vllm-models        │
              └─────────────────────────────┘
```
系统架构图（Mermaid版 · 可直接嵌入README.md）
graph TD
```
    User[用户请求] --> Gateway[FastAPI 网关 :8000]
```
    
```
    Gateway --> Auth[API Key 认证<br/>第2天]
    Gateway --> Limiter[Redis 限流<br/>第3天]
    Gateway --> Router[智能路由<br/>第8天]
```
    
```
    Limiter --> Redis[(Redis :6379<br/>限流计数 + 缓存)]
```
    
```
    Router --> Rewriter[查询改写<br/>query-rewriter 3B<br/>第19天 · 100ms]
    Router --> General[通用对话<br/>qwen3:8b<br/>第12天]
    Router --> CodeCompleter[代码补全<br/>code-completer 7B<br/>第22天]
```
    
```
    Rewriter --> Ollama[Ollama :11434]
    General --> Ollama
    CodeCompleter --> Ollama
```
    
```
    Gateway --> VLLM[vLLM :8001<br/>高性能推理<br/>Continuous Batching]
```
    
```
    Redis -.->|数据卷| RedisVol[/root/autodl-fs/redis-data/]
    Ollama -.->|数据卷| OllamaVol[/root/autodl-fs/ollama-models/]
    VLLM -.->|数据卷| VLLMVol[/root/autodl-fs/vllm-models/]
```

核心服务说明表

服务	端口	角色	关键接口
FastAPI 网关	8000	统一入口，认证、限流、路由	/health, /v1/generate, /v1/chat/smart-routed, /v1/rewrite, /v1/code/complete, /v1/compare
Redis	6379	限流计数、缓存	—
Ollama	11434	管理所有微调模型	内部调用
vLLM	8001	高性能推理（可选）	OpenAI兼容API
复制以上Mermaid代码到README.md中即可在支持Mermaid的平台上渲染为可视化架构图。