
import os
import uuid
import time
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from loguru import logger
import requests

from pydantic import BaseModel, Field
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from contextlib import asynccontextmanager

# ==================== 路由配置 ====================
'''
多模型路由系统:
设计路由策略
用户输入
    ↓
意图分类器（qwen2.5:3b）← 用轻量模型快速判断意图
    ↓
    ├── chat（闲聊）      → qwen2.5:3b（小模型够用）
    |      └──-------   →"chat_simple": "qwen2.5:1.5b",   # 新增：极简闲聊，chat的多级路由
    ├── qa（问答）        → qwen2.5:7b（需要更多知识）
    ├── code（代码）      → qwen2.5:7b（需要推理能力）
    └── summary（总结）   → qwen2.5:7b（需要理解长文本）

路由路径：/v1/chat/smart-routed
完整的函数依赖关系:
smart_routed_chat()                    ← 路由接口入口
    ├── classify_intent_with_confidence()  ← 意图分类
    │       ├── extract_intent()           ← 解析意图标签
    │       └── extract_confidence()       ← 解析置信度
    ├── is_simple_greeting()               ← 极简问候判断
    └── ollama_chat()                      ← 调用最终模型
'''

INTENT_LABELS = {
    "chat": "闲聊/日常对话",
    "qa": "知识问答/事实查询",
    "code": "代码相关/编程问题",
    "summary": "总结/摘要/长文本处理"
}

# 意图 → 模型 映射表
ROUTING_TABLE = {
    "chat_simple": "qwen2.5:1.5b",   # 新增：极简闲聊，chat的多级路由
    "chat": "qwen2.5:3b",    # 简单对话用小模型
    "qa": "qwen2.5:7b",      # 知识问答用大模型
    "code": "qwen2.5:7b",    # 代码问题用大模型
    "summary": "qwen2.5:7b", # 总结任务用大模型
}

# 用于意图分类的轻量模型
INTENT_CLASSIFIER_MODEL = "qwen2.5:3b"

# ==================== Docker 映射端口 ====================
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
VLLM_HOST = os.getenv("VLLM_HOST", "localhost")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# ==================== 新增：模型白名单 ====================
# 新增 允许的模型白名单（后续更新Ollama后可在此添加新模型）
ALLOWED_MODELS = [
    "qwen2.5:1.5b",
    "qwen2.5:3b"
    "qwen2.5:7b",
    # 后续可添加：
    # "qwen3:1.7b",
    # "qwen3:8b",
]

# ==================== 请求模型 ====================
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="用户输入的提示词", min_length=1, max_length=2000)
    model: str = Field("qwen2.5:7b", description="使用的模型名称")
    temperature: float = Field(0.7, description="生成温度，范围0-1", ge=0.0, le=1.0)
    max_tokens: int = Field(None, description="最大输出token数，可选", ge=1, le=4096)
    top_p: float = Field(None, description="核采样参数，范围0-1，可选", ge=0.0, le=1.0)

# ==================== 应用初始化 ====================
# ==================== 应用生命周期 ====================
# 新增：应用启动时等待 vLLM 就绪，vLLm就绪探针
VLLM_HEALTH_URL = f"http://{VLLM_HOST}:8001/health"

def wait_for_vllm(max_retries: int = 12, delay: int = 10):
    """等待 vLLM 服务就绪"""
    for i in range(max_retries):
        try:
            response = requests.get(VLLM_HEALTH_URL)
            if response.status_code == 200:
                logger.info(f"vLLM 服务已就绪（尝试 {i+1}/{max_retries}）")
                return True
        except requests.ConnectionError:
            pass
        logger.info(f"等待 vLLM 就绪... ({i+1}/{max_retries})")
        time.sleep(delay)
    logger.error(f"vLLM 服务在 {max_retries * delay} 秒内未能就绪，继续启动")
    return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时连接Redis，关闭时断开"""
    # 启动时：连接Redis并初始化限流器
    redis_client = redis.from_url(f"redis://{REDIS_HOST}:6379", encoding="utf-8")
    await FastAPILimiter.init(redis_client)
    logger.info("Redis已连接，限流器已初始化")
    yield
    # 关闭时：断开Redis连接
    await redis_client.close()

app = FastAPI(title="LLM Gateway API", version="1.0.0", lifespan=lifespan)

# ==================== 日志配置 ====================
logger.add("/root/autodl-fs/llm-gateway/api.log", rotation="1 day", level="INFO")

# ==================== API Key 认证依赖 ====================
async def verify_api_key(x_api_key: str = Header(None)):
    """
    从请求头 X-API-Key 中提取并验证 API Key。
    如果无效，直接返回 401 错误。
    """
    valid_key = os.getenv("API_KEY", "")
    if not x_api_key:
        raise HTTPException(status_code=401, detail="缺少 API Key，请在请求头中携带 X-API-Key")
    if x_api_key != valid_key:
        raise HTTPException(status_code=403, detail="API Key 无效")
    return x_api_key
# ====================   函数   ====================
# ==================== Ollama 调用函数 ====================
def ollama_chat(prompt: str, model: str = "qwen2.5:7b", temperature: float = 0.7,max_tokens: int = None,top_p: float = None) -> str:
    """调用本地 Ollama API 进行对话"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }
    # 如果指定了 max_tokens，则添加到请求中
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if top_p is not None:
        payload["top_p"] = top_p

    response = requests.post(url, json=payload)
    return response.json()["response"]

# ==================== vllm 调用函数 ====================
# 调用 vLLM 的 OpenAI 兼容 API
def vllm_chat(prompt: str, temperature: float = 0.7, max_tokens: int = None) -> str:
    """调用 vLLM 的 OpenAI 兼容 API"""
    url = f"http://{VLLM_HOST}:8001/v1/chat/completions"
    payload = {
        "model": "my-local-model",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    
    response = requests.post(url, json=payload)
    data = response.json()
    return data["choices"][0]["message"]["content"]

# ==================== 意图分类函数 ===================
# === classify_intent 原始意图分类函数 ===
def classify_intent(prompt: str) -> tuple[str, float]:
    """
    使用轻量模型对用户输入进行意图分类
    返回: chat, qa, code, summary 中的一个
    """
    classification_prompt = f"""你是一个意图分类器。请分析以下用户输入，判断它属于哪个类别。
类别选项（只能选一个）：
- chat: 日常闲聊、问候、无明确信息需求的对话
- qa: 知识问答、事实查询、需要准确信息的问题
- code: 编程相关、代码编写或调试、技术问题
- summary: 要求总结、摘要、概括长文本

用户输入："{prompt[:500]}"  # 只取前500字符，避免过长

请直接回复类别名称（chat/qa/code/summary），不要解释，不要加任何其他内容。
"""
    
    try:
        # 用轻量模型快速分类
        response = ollama_chat(
            prompt=classification_prompt,
            model=INTENT_CLASSIFIER_MODEL,
            temperature=0.0,  # 温度设为0，确保结果稳定
            max_tokens=10     # 只需要返回一个词
        )
        
        # 清理响应，提取意图
        intent = response.strip().lower()
        # 如果返回的内容包含多个词，只取第一个匹配的标签
        for label in INTENT_LABELS:
            if label in intent:
                logger.info(f"意图分类结果: {label}")
                return label
        
        # 默认回退到 qa
        logger.warning(f"无法识别的意图: {intent}, 默认使用 qa")
        return "qa"
        
    except Exception as e:
        logger.error(f"意图分类失败: {e}, 默认使用 qa")
        return "qa"

# ====== 意图分类函数 新增 置信度过滤confidence :这是安全兜底机制 ======
import re
# 功能函数 extract_intent 和 功能函数 extract_confidence
# 从分类器的响应中提取置信度。 和 从分类器的响应中提取置信度。
def extract_intent(response: str) -> str:
    """
    从分类器的响应中提取意图标签。
    支持的格式：
      - "意图: chat"
      - "chat"
      - "意图：chat"（中文冒号）
      - "类别: chat"
    如果无法解析，返回 "qa" 作为安全默认值。
    """
    # 去除首尾空白和换行
    text = response.strip().lower()
    
    # 尝试匹配 "意图: xxx" 或 "意图：xxx" 格式
    match = re.search(r'(?:意图|类别|intent)[:\：]\s*(\w+)', text)
    if match:
        label = match.group(1)
        if label in INTENT_LABELS:
            return label
    
    # 尝试直接匹配已知的意图标签
    for label in INTENT_LABELS:
        if label in text:
            return label
    
    # 无法识别，回退到 qa
    logger.warning(f"无法从响应中提取意图: {response[:100]}")
    return "qa"


def extract_confidence(response: str) -> float:
    """
    从分类器的响应中提取置信度。
    支持的格式：
      - "置信度: 0.85"
      - "confidence: 0.9"
      - "0.85"
    如果无法解析，返回 0.5（中性值，会触发低置信度回退）。
    """
    text = response.strip().lower()
    
    # 尝试匹配 "置信度: 0.xx" 或 "confidence: 0.xx" 格式
    match = re.search(r'(?:置信度|confidence)[:\：]\s*([0-9]*\.?[0-9]+)', text)
    if match:
        value = float(match.group(1))
        return min(max(value, 0.0), 1.0)  # 限制在 0-1 范围内
    
    # 尝试匹配独立的浮点数（比如纯数字 "0.85"）
    match = re.search(r'([0-9]\.[0-9]+)', text)
    if match:
        value = float(match.group(1))
        return min(max(value, 0.0), 1.0)
    
    # 无法识别，返回 0.5（中性值）
    logger.warning(f"无法从响应中提取置信度: {response[:100]}")
    return 0.5

# === 主体函数：意图分类函数 新增 置信度过滤confidence ===
def classify_intent_with_confidence(prompt: str) -> tuple[str, float]:
    """
    使用轻量模型对用户输入进行意图分类，并返回置信度。
    返回: (意图 intent, 置信度 confidence)
      - intent: chat, qa, code, summary 中的一个
      - confidence: 0.0 ~ 1.0 之间的置信度
    """
    classification_prompt = f"""你是一个意图分类器。请分析以下用户输入，判断它属于哪个类别。

类别选项（只能选一个）：
- chat: 日常闲聊、问候、无明确信息需求的对话
- qa: 知识问答、事实查询、需要准确信息的问题
- code: 编程相关、代码编写或调试、技术问题
- summary: 要求总结、摘要、概括长文本

用户输入："{prompt[:500]}"

请严格按以下格式回复（不要加任何其他内容）：
意图: <chat/qa/code/summary>
置信度: <0.0到1.0之间的数字，表示你对该分类的确定程度>"""
    
    try:
        response = ollama_chat(
            prompt=classification_prompt,
            model=INTENT_CLASSIFIER_MODEL,
            temperature=0.0,
            max_tokens=30
        )
        
        intent = extract_intent(response)
        confidence = extract_confidence(response)
        
        logger.info(f"意图分类结果: intent={intent}, confidence={confidence:.2f}")
        return intent, confidence
        
    except Exception as e:
        logger.error(f"意图分类失败: {e}, 默认使用 qa")
        return "qa", 0.0

# ==================== chat的多级路由：极简闲聊 ====================
# ==================== 极简问候判断 ====================
def is_simple_greeting(prompt: str) -> bool:
    """
    判断用户输入是否为极简问候。
    极简问候的特征：
      - 长度短（<= 10个字符）
      - 不包含问号（不是提问）
      - 不包含复杂关键词
    满足所有条件才判定为极简问候。
    """
    prompt_stripped = prompt.strip()
    
    # 条件1：长度 <= 10 个字符
    if len(prompt_stripped) > 10:
        return False
    
    # 条件2：不包含问号（中文/英文）
    if "?" in prompt_stripped or "？" in prompt_stripped:
        return False
    
    # 条件3：不包含复杂意图的暗示词
    complex_hints = ["代码", "写", "解释", "总结", "分析", "code", "explain", "summarize"]
    for hint in complex_hints:
        if hint in prompt_stripped.lower():
            return False
    
    return True

# ==================== 路由定义 ====================
@app.get("/health")
async def health_check():
    """健康检查接口（无需认证）"""
    return {"status": "healthy", "service": "LLM Gateway"}

# ===== 原始 调用 ollama_chat 路由接口 ========
@app.post("/v1/generate")
# 按按IP限流
@RateLimiter(times=10, seconds=60, key_func=lambda request: request.client.host)
async def generate(
    req: GenerateRequest,  # 使用Pydantic模型自动校验
    x_api_key: str = Header(None),
):
    """
    文本生成接口（需要认证）。
    接收 req: GenerateRequest,
    prompt、model、temperature 参数，返回模型生成的文本。
    """
    
    # 1. 验证 API Key
    await verify_api_key(x_api_key)

    # 2. 生成请求ID
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] 收到请求 | model={req.model} | prompt={req.prompt[:50]}...")
    
    # 3. 校验 model 参数
    if req.model not in ALLOWED_MODELS:
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": f"模型 '{req.model}' 不在允许列表中。当前支持: {', '.join(ALLOWED_MODELS)}",
                "data": None,
                "request_id": request_id
            }
        )

    # 4. 调用 Ollama
    start_time = time.time()
    try:
        response = ollama_chat(req.prompt, req.model, req.temperature, req.max_tokens,req.top_p)
        duration = time.time() - start_time
        logger.info(f"[{request_id}] 请求完成 | duration={duration:.3f}s")
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "response": response,
                "model": req.model
            },
            "request_id": request_id
        }
    except Exception as e:
        logger.error(f"[{request_id}] 请求失败 | error={str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"模型调用失败: {str(e)}",
                "data": None,
                "request_id": request_id
            }
        )

# ===== 对比测试端点：让用户能同时调用 vLLM 和 Ollama，对比两者的回复 ========
@app.post("/v1/compare")
async def compare_engines(
    req: GenerateRequest,
    x_api_key: str = Header(None),
):
    """同时调用 vLLM 和 Ollama，返回对比结果"""
    await verify_api_key(x_api_key)
    
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] 对比测试 | prompt={req.prompt[:50]}...")
    
    # 调用 Ollama
    ollama_start = time.time()
    try:
        ollama_response = ollama_chat(req.prompt, req.model, req.temperature, req.max_tokens)
        ollama_duration = time.time() - ollama_start
    except Exception as e:
        ollama_response = f"错误: {str(e)}"
        ollama_duration = 0
    
    # 调用 vLLM
    vllm_start = time.time()
    try:
        vllm_response = vllm_chat(req.prompt, req.temperature, req.max_tokens)
        vllm_duration = time.time() - vllm_start
    except Exception as e:
        vllm_response = f"错误: {str(e)}"
        vllm_duration = 0
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "ollama": {
                "response": ollama_response,
                "duration": round(ollama_duration, 3)
            },
            "vllm": {
                "response": vllm_response,
                "duration": round(vllm_duration, 3)
            }
        },
        "request_id": request_id
    }

# ======= 多模型路由系统 路由接口 ========
@app.post("/v1/chat/smart-routed")
@RateLimiter(times=10, seconds=60)
async def smart_routed_chat(
    req: GenerateRequest,
    x_api_key: str = Header(None),
):
    # 1. 验证 API Key
    await verify_api_key(x_api_key)
    
    # 2. 生成请求ID
    request_id = str(uuid.uuid4())[:8]
    
    # 3. 意图分类（带置信度）
    intent, confidence = classify_intent_with_confidence(req.prompt)
    
    # 4. 低置信度兜底
    if confidence < 0.7:
        logger.warning(f"[{request_id}] 低置信度({confidence:.2f})，回退到7B")
        intent = "qa"
    
    # 5. 极简问候二次判断
    if intent == "chat" and is_simple_greeting(req.prompt):
        intent = "chat_simple"
        logger.info(f"[{request_id}] 检测到极简问候，使用1.5B模型")
    
    # 6. 选择模型（用户手动指定优先）
    selected_model = ROUTING_TABLE.get(intent, "qwen2.5:7b")
    final_model = req.model if req.model != selected_model else selected_model
    
    logger.info(
        f"[{request_id}] 路由决策 | intent={intent} | "
        f"confidence={confidence:.2f} | "
        f"selected={selected_model} | final={final_model}"
    )
    
    # 7. 调用模型
    start_time = time.time()
    try:
        response = ollama_chat(req.prompt, final_model, req.temperature, req.max_tokens)
        duration = time.time() - start_time
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "response": response,
                "model": final_model,
                "intent": intent,
                "confidence": round(confidence, 3),
                "routed": intent != "qa"
            },
            "request_id": request_id
        }
    except Exception as e:
        logger.error(f"[{request_id}] 请求失败 | error={str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"模型调用失败: {str(e)}",
                "data": None,
                "request_id": request_id
            }
        )

# ==================== 全局异常处理 ====================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未捕获异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None}
    )

'''
现在已更新至：docker compose up -d 启动，
映射端口已经变更为docker-compose.yml中的环境变量 端口地址。

以下是原终端映射端口未定义启动方式，现在不能用，之后如果要快速验证和测试main.py原功能可以使用。
cd /root/autodl-fs/llm-gateway
conda activate llm-env
python -m uvicorn main:app --host 0.0.0.0 --port 8000
export API_KEY="your-api-key-here"
echo 'export API_KEY="your-api-key-here"' >> ~/.bashrc
'''
