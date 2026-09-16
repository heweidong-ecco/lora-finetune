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