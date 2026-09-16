from locust import HttpUser, task, between
import random

# 测试用的 prompt 池——模拟真实用户的各种请求
PROMPTS = {
    "chat": [
        "你好",
        "今天天气真不错",
        "谢谢你的帮助",
        "早上好",
        "晚安",
    ],
    "qa": [
        "请解释什么是量子纠缠",
        "中国有多少个省份",
        "请介绍深度学习的三个主要框架",
        "什么是RESTful API",
    ],
    "code": [
        "用Python写一个快速排序算法",
        "请解释Docker和虚拟机的区别",
        "如何在FastAPI中实现依赖注入",
    ],
    "summary": [
        "请总结一下大模型部署的关键步骤",
        "帮我概括一下微服务架构的优缺点",
    ],
}

class LLMGatewayUser(HttpUser):
    # 每个模拟用户请求之间的等待时间（1-3秒随机）
    wait_time = between(1, 3)
    
    def on_start(self):
        """每个虚拟用户启动时执行一次"""
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": "your-api-key-here",
        }
    
    @task(3)  # 权重3——出现频率最高
    def test_smart_routed(self):
        """测试智能路由接口 /v1/chat/smart-routed"""
        # 随机选择一个类别
        category = random.choice(list(PROMPTS.keys()))
        prompt = random.choice(PROMPTS[category])
        
        payload = {
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 50,  # 压测时限制输出长度，避免单请求耗时过长
        }
        
        with self.client.post(
            "/v1/chat/smart-routed",
            json=payload,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # 检查路由信息是否存在
                if data.get("code") == 200 and "data" in data:
                    response.success()
                else:
                    response.failure(f"业务错误: {data.get('message')}")
            elif response.status_code == 429:
                # 限流是预期行为，不算失败
                response.success()
            else:
                response.failure(f"HTTP错误: {response.status_code}")
    
    @task(1)  # 权重1——偶尔测试健康检查
    def test_health(self):
        """测试健康检查接口"""
        self.client.get("/health", headers=self.headers)
    
    @task(2)  # 权重2
    def test_generate(self):
        """测试原始生成接口 /v1/generate"""
        prompt = random.choice(PROMPTS["qa"])
        
        payload = {
            "prompt": prompt,
            "model": "qwen2.5:1.7b",  # 用轻量模型，减少压测对GPU的压力
            "temperature": 0.7,
            "max_tokens": 30,
        }
        
        with self.client.post(
            "/v1/generate",
            json=payload,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"HTTP错误: {response.status_code}")