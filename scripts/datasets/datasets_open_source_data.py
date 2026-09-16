# 来源一：开源数据集（基础数据，100-150条）

#从 HuggingFace 下载已有数据集：
# 设置 HF_ENDPOINT 镜像环境变量
# 在运行脚本之前，告诉 HuggingFace 的库“去国内镜像站找数据”，而不是去官方。在你的终端里执行：
# export HF_ENDPOINT=https://hf-mirror.com
# 如果HuggingFace 国内镜像站没有可以去 魔搭看下有没有数据集
#  ModelScope 的数据集接口 也有大量开源数据集
'''
from modelscope import MsDataset
dataset = MsDataset.load('shibing624/medical', split='train')
'''

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from datasets import load_dataset

# 下载中文通用问答数据集
# dataset = load_dataset("shibing624/medical", split="train")
# 或者用 alpaca 格式的数据
dataset = load_dataset("yahma/alpaca-cleaned", split="train")

# 导出为 JSON 文件（这行是关键，你之前的代码没有）
output_path = "datasets_open_source_data.json"
dataset.to_json(output_path, force_ascii=False, indent=2)

print(f"✅ 已生成 {output_path}，共 {len(dataset)} 条数据")