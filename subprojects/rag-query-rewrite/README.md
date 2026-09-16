#
第1步：确认环境
bash
cd /root/autodl-fs/LLaMA-Factory
source llama-factory-env/bin/activate

第2步：设计数据集结构
数据格式（alpaca 格式）：
json
{
  "instruction": "将以下用户口语查询改写为精确的检索查询，解决指代不明、用词模糊、信息缺失等问题。",
  "input": "那个蓝色的怎么卖？",
  "output": "请问产品型号XJ-3000的蓝色款当前价格是多少？"
}
instruction 统一：所有样本使用相同的 instruction，input 是原始口语查询，output 是改写后的精确查询。

第3步：构建原始问题种子（50 个）
手工构建 50 个包含典型查询问题的种子。覆盖以下类型：
类型	示例	问题特征
指代不明	“那个蓝色的怎么卖？”	包含“这个”“那个”“它”等代词
用词模糊	“上次说的那个方案定了吗？”	包含“上次”“那个方案”等模糊词
信息缺失	“最新款多少钱？”	缺少产品名、品牌等关键信息
口语化严重	“有没有那种不用插电就能用的？”	口语化表达，缺乏专业术语
多意图混合	“帮我查一下订单还有那个物流”	一个句子包含多个查询意图
执行 generate_seeds.py 
得到 data/query_rewrite_seeds.json

第4步：用大模型批量生成改写版本
generate_rewrites.py