
# 前置条件：
cd /root/autodl-fs/LLaMA-Factory
source llama-factory-env/bin/activate
启动训练：之前的exp1_baseline修改了配置文件，重新训练得到最优的loss适配器，
yaml文件中有早停 记得查看最后输出的loss数值，如果没有就用checkpoint- 文件
- llamafactory-cli train examples/train_lora/exp1_baseline.yaml
- llamafactory-cli train examples/train_lora/checkpoint-(某个检查点适配器)
# 合并 LoRA 权重到基座模型
- 方案一：直接导出为Ollama可读取的完整文件夹 包含Modelsfile
llamafactory-cli export \
    --model_name_or_path /root/autodl-fs/vllm-models/Qwen3-8B/models/Qwen--Qwen3-8B/snapshots/master \
    --adapter_name_or_path /root/autodl-fs/LLaMA-Factory/saves/exp1_baseline \
    --template qwen \
    --finetuning_type lora \
    --export_dir /root/autodl-fs/LLaMA-Factory/saves/exp1_ollama \
    --export_ollama true
- 方案二：合并文件为 单个 HuggingFace 格式，
- 给其他量化使用，比较繁琐需要自己写Modelsfile
bash
llamafactory-cli export \
    --model_name_or_path  /root/autodl-fs/vllm-models/Qwen3-8B/models/Qwen--Qwen3-8B/snapshots/master \
    --adapter_name_or_path /root/autodl-fs/LLaMA-Factory/saves/exp1_baseline \
    --template qwen \
    --finetuning_type lora \
    --export_dir /root/autodl-fs/LLaMA-Factory/saves/exp1_merged \
    --export_size 2 \
    --export_device cpu \
    --export_legacy_format false
等待约 2-3 分钟，看到 Export finished 即成功
ls /root/autodl-fs/LLaMA-Factory/saves/exp1_merged/
`#应该看到` config.json, tokenizer.json, model*.safetensors 等文件

# 转换为 GGUF 格式
## 使用 llama_cpp 可以直接量化（Q4_K_M 量化）
第4步：转换为 GGUF 格式（Q4_K_M 量化）

```bash
python3 << 'EOF'
from llama_cpp import Llama
import os

#路径配置
merged_path = "/root/autodl-fs/LLaMA-Factory/saves/exp1_merged"
gguf_output = "/root/autodl-fs/LLaMA-Factory/saves/exp1_q4km.gguf"

print("开始转换 GGUF 格式（Q4_K_M 量化）...")
print("这可能需要 5-10 分钟，请耐心等待...")

#加载合并后的模型并转换为 GGUF
model = Llama.from_pretrained(
    repo_id=merged_path,
    filename="*",
    verbose=False
)

#保存为 GGUF 格式，使用 Q4_K_M 量化
model.save_pretrained(
    gguf_output,
    quantization="Q4_K_M"
)

print(f"✅ GGUF 转换完成: {gguf_output}")

#查看文件大小
size_mb = os.path.getsize(gguf_output) / (1024 * 1024)
print(f"文件大小: {size_mb:.1f} MB")
EOF
等待 5-10 分钟，转换完成后验证：
```
bash
ls -lh /root/autodl-fs/LLaMA-Factory/saves/exp1_q4km.gguf
## 备选方案：
### LLaMA-Factory 自带的转换命令 ，先导出为 未量化的 GGUF，
如果 llama_cpp 的 API 有兼容性问题，使用 LLaMA-Factory 自带的转换命令：
```bash
#先用 LLaMA-Factory 导出为未量化的 Ollama GGUF
python3 -c "
from llamafactory.export.convert_gguf import convert_llama_to_gguf
convert_llama_to_gguf(
    input_dir='/root/autodl-fs/LLaMA-Factory/saves/exp1_merged',
    output_file='/root/autodl-fs/LLaMA-Factory/saves/exp1_fp16.gguf',
    quantization=None
)
"
```
### 如果LLaMA-Factory 自带的转换命令 也不行，直接用社区成熟的 convert-hf-to-gguf.py 脚本：
```bash
#下载转换脚本
wget https://raw.githubusercontent.com/ggerganov/llama.cpp/master/convert_hf_to_gguf.py

#转换（不量化，先得到 FP16 的 GGUF）
python3 convert_hf_to_gguf.py \
    /root/autodl-fs/LLaMA-Factory/saves/exp1_merged \
    --outfile /root/autodl-fs/LLaMA-Factory/saves/exp1_fp16.gguf \
    --outtype f16
### 最后量化（如果需要）对 FP16 GGUF 文件进行量化
bash
#如果上面产出了 FP16 的 GGUF，用 llama.cpp 的量化工具压缩
#下载量化工具（如果没有）
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp && make quantize && cd ..
#量化
./llama.cpp/quantize \
    /root/autodl-fs/LLaMA-Factory/saves/exp1_fp16.gguf \
    /root/autodl-fs/LLaMA-Factory/saves/exp1_q4km.gguf \
    Q4_K_M
```
# 量化类型
量化类型	质量损失	文件大小（8B模型）	推理速度	推荐场景
FP16（无量化）	无	~16GB	基准	需要最高精度
Q8_0	极小	~8GB	1.5x	高质量推理
Q4_K_M（推荐）	极小	~6GB	3x	开发测试、本地部署
Q4_0	略高于Q4_K_M	~5.5GB	3x	显存极度受限
Q2_K	较大	~4GB	4x	仅供极端情况
Q4_K_M 的含义：4-bit 量化，K-quant 方法，Medium 平衡。是目前公认的“质量-体积-速度”最佳平衡点。