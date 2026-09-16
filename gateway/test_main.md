# main.py 的测试命令集
# 启动服务 在终端中执行
'''
第2天：
```bash
cd /root/autodl-fs/llm-gateway
uvicorn main:app --host 0.0.0.0 --port 8000
```
启动成功后，终端会显示：
```text
INFO:     Uvicorn running on http://0.0.0.0:8000
```

第6步：测试API
打开一个新的终端窗口（在JupyterLab中点击 File → New → Terminal），执行以下测试：
测试1：健康检查（无需认证）
```bash
curl http://localhost:8000/health
```
预期返回：{"status":"healthy","service":"LLM Gateway"}
测试2：不带API Key调用（应该被拒绝）
```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"你好","model":"qwen2.5:1.7b"}'
```
预期返回：{"detail":"缺少 API Key，请在请求头中携带 X-API-Key"}
测试3：带正确API Key调用（应该成功）
```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"prompt":"用一句话解释什么是GPU","model":"qwen2.5:1.7b"}'
```
预期返回：包含模型回复的完整JSON。
测试4：用错误的API Key调用（应该被拒绝）
```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key" \
  -d '{"prompt":"你好"}'
```
预期返回：{"detail":"API Key 无效"}

测试新增功能
重启服务后，测试模型校验：
```bash
# 测试不允许的模型（应返回422）
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"prompt":"你好","model":"qwen3:8b"}'
```
测试 max_tokens：
```bash
# 限制最大输出为20个token
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"prompt":"请详细介绍一下Python编程语言","model":"qwen2.5:1.7b","max_tokens":20}'
```
'''
'''
第3天测试
三、测试验证

重启服务：

```bash
cd /root/autodl-fs/llm-gateway
uvicorn main:app --host 0.0.0.0 --port 8000
```
测试1：正常请求（应该成功）

```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"prompt":"你好","model":"qwen2.5:1.7b"}'
```
测试2：参数校验——传入无效的temperature（应返回422）

```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"prompt":"你好","temperature":2.0}'
```
测试3：限流测试——连续发送11次请求（第11次应返回429）

```bash
for i in {1..11}; do
  echo "请求 $i:"
  curl -s -w "\nHTTP状态码: %{http_code}\n" \
    -X POST http://localhost:8000/v1/generate \
    -H "Content-Type: application/json" \
    -H "X-API-Key: your-api-key-here" \
    -d '{"prompt":"hi","model":"qwen2.5:1.7b","max_tokens":5}'
  echo "---"
done
```
前10次应返回200，第11次应返回429（Too Many Requests）。
'''