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