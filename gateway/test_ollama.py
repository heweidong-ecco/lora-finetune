import requests
import json

def ollama_chat(prompt, model="qwen2.5:7b", temperature=0.7):
    """调用Ollama API进行对话"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }
    response = requests.post(url, json=payload)
    return response.json()["response"]

if __name__ == "__main__":
    # 测试
    result = ollama_chat("你好，请介绍一下你自己", model="qwen2.5:7b")
    print(result)