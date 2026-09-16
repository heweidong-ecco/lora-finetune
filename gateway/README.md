# LLM Gateway

```
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-24.0+-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-supported-brightgreen.svg)](https://ollama.ai/)
```

# LLM Gateway — 本地大模型推理平台

一个具备认证、限流、智能路由、多模型管理和容器化部署能力的**生产级大模型推理网关**。

## 目录

- [LLM Gateway](#llm-gateway)
- [LLM Gateway — 本地大模型推理平台](#llm-gateway--本地大模型推理平台)
```
  - [目录](#目录)
  - [核心特性](#核心特性)
  - [系统架构](#系统架构)
  - [技术栈](#技术栈)
  - [快速开始](#快速开始)
    - [前置要求](#前置要求)
    - [一键启动](#一键启动)
    - [验证服务](#验证服务)
```
- [健康检查](#健康检查)
- [智能路由对话](#智能路由对话)
```
  - [API文档](#api文档)
    - [接口总览](#接口总览)
    - [通用响应格式](#通用响应格式)
    - [错误码](#错误码)
  - [项目结构](#项目结构)
  - [模型列表](#模型列表)
  - [性能数据](#性能数据)
  - [性能数据](#性能数据-1)
    - [性能基线总结](#性能基线总结)
    - [优化方向](#优化方向)
    - [压测工具](#压测工具)
  - [许可证](#许可证)
  - [技术博客](#技术博客)
```


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
├── README.md            # 项目文档
├── test_main.md         # main.py 的测试命令集
└── （其余为文档与配置，见本目录文件列表）

> ⚠️ **本仓库的 `gateway/` 里【没有】`evaluate.py` 与 `evaluation_results/`** ——
> 它们未随本库整理一并收录。
> 本库的评测脚本与产物在别处：`../scripts/eval/`（含 `evaluate.py`）与 `../results/`，
> **但那一条线已查实不可用**（两边跑的是同一个模型），见 `../results/README.md`。

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

## 性能数据

使用 Locust 对系统进行三轮压力测试，测试环境为 AutoDL RTX 3090 (24GB显存)。

| 并发数 | 总请求数 | 失败数 | 错误率 | 平均QPS | 平均延迟 | P50延迟 | P95延迟 | P99延迟 |
| ------ | -------- | ------ | ------ | ------- | -------- | ------- | ------- | ------- |
| 5      | —        | 0      | 0%     | —       | —        | —       | —       | —       |
| 10     | —        | 0      | 0%     | —       | —        | —       | —       | —       |
| 20     | —        | —      | —      | —       | —        | —       | —       | —       |

### 性能基线总结

- **轻载（5并发）**：系统稳定，无错误，所有请求正常响应
- **中载（10并发）**：性能表现良好，P95延迟在可接受范围
- **高载（20并发）**：开始出现资源争抢，vLLM推理成为瓶颈

### 优化方向

1. 简单请求（闲聊、问候）走Ollama轻量模型（1.5B/3B），复杂请求走vLLM
2. 启用Redis缓存高频查询的改写结果
3. 增加早停机制保护训练最优检查点

### 压测工具

压测脚本位于 `locustfile.py`，执行命令：

```
locust -f locustfile.py --host=http://localhost:8000 --headless \
  --users 10 --spawn-rate 2 --run-time 60s --csv=results_10users
```

## 许可证

MIT

