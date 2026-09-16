"""
使用官方 ollama Python 库批量生成 alpaca 格式训练数据，并保存为 JSON 文件。
运行前请确保：
1. Ollama 已启动 (ollama serve)
2. 已拉取所需模型 (ollama pull qwen3:8b)
"""

import json
import re
import ollama
from typing import List, Dict, Optional

# ======================== 配置区 ========================
MODEL_NAME = "qwen3:8b"               # 使用的大模型
# qwen3:8b 上下文窗口（总长度）	32K tokens（约 32768 tokens）/ 16384（16K）/ 24576 （24K）
DEFAULT_MAX_TOKENS = 24576           # 最大生成 token 数（单次调用）
TEMPERATURE = 0.8                      # 温度，越高越多样
# =========================================================

def ollama_chat(prompt: str, model: str = MODEL_NAME, max_tokens: int = DEFAULT_MAX_TOKENS, temperature: float = TEMPERATURE) -> str:
    """
    使用官方 ollama 库调用大模型进行对话生成
    """
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "num_predict": max_tokens,
                "temperature": temperature
            }
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"❌ Ollama 请求失败：{e}")
        return ""

def generate_training_data(topic: str, num_samples: int = 50, save_path: Optional[str] = None) -> List[Dict]:
    """
    批量生成训练数据（alpaca 格式）

    参数：
        topic: 生成数据的主题，如 "Python基础语法"
        num_samples: 期望生成的问答对数
        save_path: 如果提供，则保存为 JSON 文件

    返回：
        生成的训练数据列表，每一项包含 instruction, input, output
    """
    # 构建 prompt，采用普通字符串拼接避免大括号转义混乱
    prompt = (
        f'请生成{num_samples}条关于"{topic}"的问答对，用于训练一个AI助手。\n'
        '每条数据必须包含：\n'
        '- instruction: 用户可能问的问题\n'
        '- input: 补充上下文（如果没有就留空字符串）\n'
        '- output: 准确、详细的回答\n\n'
        '请严格按照以下JSON格式返回，不要添加额外说明：\n'
        '[\n'
        '  {"instruction": "问题1", "input": "", "output": "回答1"},\n'
        '  {"instruction": "问题2", "input": "", "output": "回答2"}\n'
        ']'
    )

    print(f"🚀 开始生成 {num_samples} 条关于「{topic}」的训练数据...")
    response = ollama_chat(prompt, model=MODEL_NAME, max_tokens=DEFAULT_MAX_TOKENS, temperature=TEMPERATURE)

    # 解析模型返回的 JSON
    data = []
    try:
        # 先尝试直接解析
        data = json.loads(response)
        print(f"✅ 直接解析成功，共 {len(data)} 条")
    except json.JSONDecodeError:
        # 如果失败，尝试用正则提取 JSON 数组
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                print(f"✅ 正则提取成功，共 {len(data)} 条")
            except json.JSONDecodeError as e:
                print(f"❌ 正则提取后仍无法解析：{e}")
                print(f"原始回复前500字：\n{response[:500]}")
        else:
            print("❌ 未找到有效 JSON 数组")
            print(f"原始回复前500字：\n{response[:500]}")

    # 保存到文件
    if data and save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到 {save_path}")

    return data

# ======================== 主程序 ========================
'''if __name__ == "__main__":
    # 通用问答助手训练数据生成
    topic = "通用知识问答"  # 主题改为通用知识
    num = 100               # 一次生成 100 条
    output_file = "datasets_qa_general.json"

    result = generate_training_data(topic, num_samples=num, save_path=output_file)

    if result:
        print(f"🎉 最终生成 {len(result)} 条有效数据")
        print(f"示例数据预览：")
        for i, item in enumerate(result[:3]):  # 打印前3条看看效果
            print(f"\n--- 第{i+1}条 ---")
            print(f"instruction: {item['instruction']}")
            print(f"input: {item['input']}")
            print(f"output: {item['output'][:100]}...")  # 输出只显示前100字
    else:
        print("❌ 数据生成失败")
'''
if __name__ == "__main__":
    all_data = []

    # 按不同领域分别生成
    topics = [
        ("自然科学", 50),
        ("历史与文化", 50),
        ("地理常识", 30),
        ("生活百科", 50),
        ("计算机与互联网", 40),
    ]

    for topic, num in topics:
        print(f"\n{'='*50}")
        data = generate_training_data(topic, num_samples=num)
        all_data.extend(data)

    # 合并保存
    output_file = "datasets_qa_general_mix.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 总共生成 {len(all_data)} 条训练数据，已保存到 {output_file}")