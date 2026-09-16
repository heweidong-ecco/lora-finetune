# 项目文档不是代码的附属品，是项目能力的翻译官。
二、动手操作

第1步：确认项目产出物

```bash
cd /root/autodl-fs/llm-gateway
ls -la
```
确认以下文件存在：

main.py — FastAPI主程序
docker-compose.yml — 服务编排配置
Dockerfile — API镜像构建文件
requirements.txt — Python依赖
第2步：编写README.md

在/root/autodl-fs/llm-gateway/下创建README.md：

markdown
# LLM Gateway — 本地大模型推理平台

一个具备认证、限流、智能路由、多模型管理和容器化部署能力的**生产级大模型推理网关**。

## 核心特性

- **多模型管理**：统一管理通用对话（8B）、查询改写（3B）、代码补全（7B）三个微调模型
- **智能路由**：自动识别用户意图，简单问候→1.5B秒回，复杂推理→7B保证质量
- **查询改写**：口语化、模糊查询自动转为精确检索查询，适配RAG场景
- **代码补全**：基于FIM微调的代码补全，Tab触发，只输出代码无冗余解释
- **安全防护**：API Key认证 + Redis令牌桶限流 + Pydantic参数校验
- **容器化部署**：Docker Compose一键启动全家桶，volumes数据持久化
- **性能基线**：vLLM + Ollama双引擎对比，Locust压测数据完整记录

## 系统架构

```
[系统架构图，Mermaid格式]
```

## 技术栈

| 层级      | 技术                    | 用途                       |
| --------- | ----------------------- | -------------------------- |
| API网关   | FastAPI + Pydantic      | 路由、认证、限流、参数校验 |
| 模型推理  | Ollama + vLLM           | 本地模型管理和高性能推理   |
| 缓存/限流 | Redis                   | 令牌桶限流计数             |
| 容器化    | Docker + Docker Compose | 一键部署、环境隔离         |
| 微调框架  | LLaMA-Factory + LoRA    | 模型微调和参数调优         |
| 实验管理  | MLflow                  | 训练实验追踪和对比         |
| 评估      | 自研评估管道            | 基座vs微调模型对比裁判     |
| 压测      | Locust                  | QPS/P95/P99延迟/错误率     |

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose v2
- 8GB+ 可用显存（推荐24GB）

### 一键启动

```
git clone https://github.com/your-username/llm-gateway.git
cd llm-gateway
docker compose up -d
```

### 验证服务

```
# 健康检查
curl http://localhost:8000/health
```

```
# 智能路由对话
curl -X POST http://localhost:8000/v1/chat/smart-routed \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"prompt":"你好"}'
```

## API文档

### 接口总览

| 方法 | 路径                    | 功能               | 认证    |
| ---- | ----------------------- | ------------------ | ------- |
| GET  | `/health`               | 健康检查           | 无      |
| POST | `/v1/generate`          | 直接调用指定模型   | API Key |
| POST | `/v1/chat/smart-routed` | 智能路由对话       | API Key |
| POST | `/v1/rewrite`           | 查询改写           | API Key |
| POST | `/v1/code/complete`     | 代码补全           | API Key |
| POST | `/v1/compare`           | vLLM vs Ollama对比 | API Key |

### 通用响应格式

```
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "request_id": "a1b2c3d4"
```
}

### 错误码

| 状态码 | 含义              |
| ------ | ----------------- |
| 200    | 成功              |
| 401    | API Key无效或缺失 |
| 422    | 参数校验失败      |
| 429    | 请求频率超限      |
| 500    | 服务内部错误      |

## 项目结构

llm-gateway/
├── main.py              # FastAPI主程序
├── Dockerfile           # API镜像构建
├── docker-compose.yml   # 全家桶编排
├── requirements.txt     # Python依赖
├── locustfile.py        # 压测脚本
├── evaluate.py          # 模型评估管道
├── README.md            # 项目文档
└── evaluation_results/  # 评估报告

## 模型列表

| 模型名         | 基座           | 参数量 | 用途     | 微调数据 | 训练loss |
| -------------- | -------------- | ------ | -------- | -------- | -------- |
| qwen3:8b       | Qwen3-8B       | 8B     | 通用对话 | 未微调   | —        |
| query-rewriter | Qwen3-3B       | 3B     | 查询改写 | 150条    | —        |
| code-completer | Qwen3-Coder-7B | 7B     | 代码补全 | 250条    | —        |

## 性能数据

| 并发数 | QPS | P95延迟 | P99延迟 | 错误率 |
| ------ | --- | ------- | ------- | ------ |
| 5      | —   | —       | —       | 0%     |
| 10     | —   | —       | —       | 0%     |
| 20     | —   | —       | —       | —      |

## 许可证

MIT
第3步：编写API文档

在/root/autodl-fs/llm-gateway/下创建API.md：

markdown
# LLM Gateway API 文档

## 认证方式

所有受保护接口需在请求头中携带API Key：

X-API-Key: your-api-key-here

## 接口详情

### 1. 健康检查

GET /health

响应示例：

```
{
  "status": "ok",
  "services": {
    "redis": "connected",
    "ollama": "connected",
    "vllm": "connected"
  }
```
}

### 2. 智能路由对话

POST /v1/chat/smart-routed

请求体：

```
{
  "prompt": "你好，今天天气真好",
  "temperature": 0.7,
  "max_tokens": 512
```
}

响应体：

```
{
  "code": 200,
  "message": "success",
  "data": {
    "response": "你好！今天确实是个好天气...",
    "model": "qwen2.5:1.5b",
    "intent": "chat",
    "confidence": 0.92,
    "routed": true
  },
  "request_id": "a1b2c3d4"
```
}

### 3. 查询改写

POST /v1/rewrite

请求体：

```
{
  "query": "那个蓝色的怎么卖？"
```
}

响应体：

```
{
  "original": "那个蓝色的怎么卖？",
  "rewritten": "请问产品型号XJ-3000的蓝色款当前价格是多少？"
```
}

### 4. 代码补全

POST /v1/code/complete

请求体：

```
{
  "prefix": "def quicksort(arr):\n    \"\"\"快速排序\"\"\""
```
}

响应体：

```
{
  "completion": "    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    ..."
```
}
第4步：编写部署指南

在/root/autodl-fs/llm-gateway/下创建DEPLOY.md：

markdown
# LLM Gateway 部署指南

## 环境要求

| 组件           | 最低版本 | 推荐配置             |
| -------------- | -------- | -------------------- |
| Docker         | 20.10+   | 24.0+                |
| Docker Compose | v2       | v2.20+               |
| GPU显存        | 8GB      | 24GB (RTX 3090/4090) |
| 磁盘           | 50GB     | 100GB+               |

## 部署步骤

### 1. 克隆仓库

```
git clone https://github.com/your-username/llm-gateway.git
cd llm-gateway
```

### 2. 配置环境变量

```
# 编辑 .env 文件
API_KEY=your-secret-key
REDIS_HOST=redis
OLLAMA_HOST=ollama
VLLM_HOST=vllm
```

### 3. 启动服务

```
docker compose up -d
```

### 4. 验证部署

```
curl http://localhost:8000/health
```

### 5. 停止服务

```
docker compose down
```

## 数据持久化

所有数据存储在宿主机目录：

| 数据       | 路径                          |
| ---------- | ----------------------------- |
| Redis数据  | /root/autodl-fs/redis-data    |
| Ollama模型 | /root/autodl-fs/ollama-models |
| vLLM模型   | /root/autodl-fs/vllm-models   |

## 故障排查

### 服务无法启动

```
# 查看日志
docker compose logs api
docker compose logs ollama
```

### 模型未加载

```
# 检查模型是否存在
ollama list
```

### 端口冲突

# 修改 docker-compose.yml 中的端口映射


