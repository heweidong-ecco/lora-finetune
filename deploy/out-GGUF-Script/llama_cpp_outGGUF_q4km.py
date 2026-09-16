'''
前置条件：
cd /root/autodl-fs/LLaMA-Factory
source llama-factory-env/bin/activate

合并 LoRA 权重到基座模型
bash
llamafactory-cli export \
    --model_name_or_path /root/autodl-fs/vllm-models/Qwen3-8B/models/Qwen--Qwen3-8B \
    --adapter_name_or_path /root/autodl-fs/LLaMA-Factory/saves/exp1_baseline \
    --template qwen \
    --finetuning_type lora \
    --export_dir /root/autodl-fs/LLaMA-Factory/saves/exp1_merged \
    --export_size 2 \
    --export_device cpu \
    --export_legacy_format false
等待约 2-3 分钟，看到 Export finished 即成功
ls /root/autodl-fs/LLaMA-Factory/saves/exp1_merged/
# 应该看到 config.json, tokenizer.json, model*.safetensors 等文件
'''
# 第一步安装工具：
# pip install gguf
# pip install llama_cpp 
# 执行cli 转换GGUF 格式 
# -Python命令 python3 << 'EOF' ... EOF 包含直接（Q4_K_M 量化）
# -或者 这个脚本llama_cpp_outGGUF_q4km.py
# 等待 5-10 分钟，转换完成后验证：
# ls -lh /root/autodl-fs/LLaMA-Factory/saves/exp1_q4km.gguf
# 转换为 GGUF 格式（Q4_K_M 量化）
# 直接使用 bash终端命令使用 python3 << 'EOF' ... EOF
# python3 << 'EOF'
from llama_cpp import Llama
import os

# 路径配置
merged_path = "/root/autodl-fs/LLaMA-Factory/saves/exp1_merged"
gguf_output = "/root/autodl-fs/LLaMA-Factory/saves/exp1_q4km.gguf"

print("开始转换 GGUF 格式（Q4_K_M 量化）...")
print("这可能需要 5-10 分钟，请耐心等待...")

# 加载合并后的模型并转换为 GGUF
model = Llama.from_pretrained(
    repo_id=merged_path,
    filename="*",
    verbose=False
)

# 保存为 GGUF 格式，使用 Q4_K_M 量化
model.save_pretrained(
    gguf_output,
    quantization="Q4_K_M"
)

print(f"✅ GGUF 转换完成: {gguf_output}")

# 查看文件大小
size_mb = os.path.getsize(gguf_output) / (1024 * 1024)
print(f"文件大小: {size_mb:.1f} MB")
# EOF