# AutoDL 执行日志（2026.07）

> 2026 年 7 月在 AutoDL 上做 LoRA 微调时的**逐日执行记录**：命令、报错、排错过程。
> **内容保留原样** —— 仅做了两处加工：① 清理 1 处明文密钥 ② 补回丢失的 Markdown 代码围栏。
> 按日期分段（7.21 → 7.24），大致对应：LLaMA-Factory 环境搭建 → 数据集准备 → 训练与 MLflow。

---

```
export OLLAMA_MODELS=/root/autodl-fs/ollama-models
echo 'export OLLAMA_MODELS=/root/autodl-fs/ollama-models' >> ~/.bashrc
cp /root/autodl-fs/LLaMA-Factory/BadCase_AI_evaluation_pipeline/data/my_dataset.json /root/autodl-fs/LLaMA-Factory/data
```



# 2026.
# 7.21
## 执行内容：
```
cd /root/autodl-fs/llm-gateway
conda init bash
```
新建终端 
```
cd /root/autodl-fs/llm-gateway
conda activate llm-env
```
启动大模型：
```
ollama
export OLLAMA_MODELS=/root/autodl-fs/ollama-models
ollama --version
ollama serve
ollama run qwen2.5:7b
```
确保Ollama服务也在运行（默认端口11434）。

vLLM
启动 vLLM 时指定本地路径：
```bash
python -m vllm.entrypoints.openai.api_server \
  --model /root/autodl-fs/models/qwen2.5-7b-instruct \
  --served-model-name my-local-model \
  --host 0.0.0.0 \
  --port 8001
```
  启动成功后，你会看到 INFO: Uvicorn running on http://0.0.0.0:8001。

1.下载vllm HuggingFace 指定模型，
方法一：让 vLLM 自动从 HuggingFace 下载模型 自动下载模型到默认缓存目录
```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --served-model-name my-local-model \
  --host 0.0.0.0 \
  --port 8001
```
  启动成功后，你会看到 INFO: Uvicorn running on http://0.0.0.0:8001。
这里的 Qwen/Qwen2.5-7B-Instruct 是 HuggingFace 上的模型标识符。
vLLM 会自动下载模型到默认缓存目录（通常在 ~/.cache/huggingface/hub/）。
首次运行时会自动下载模型到 ~/.cache/huggingface/hub/ 目录，之后无需重复下载。

bash 启动加速器：
```
export HF_ENDPOINT=https://hf-mirror.com
python vllm_download_run_huggingface_llm.py
```

2.执行test_main.md内容
```
python -m uvicorn main:app --host 0.0.0.0 --post 8000
export API_KEY="your-api-key-here"
```
bash
执行test_main.md中的内容。
3.vLLM和Ollama 性能基线压测
确保vLLMvLLM和Ollama 服务都 已经启动
```bash
python test_banchmark_performance.py
```
得到产物 test_benchmark_results.json 文件和test_benchmark_chart.png，里面包含了所有测试数据
## 遇到报错，需要解决
1.vLLM无法下载模型
bash 启动加速器：
```
export HF_ENDPOINT=https://hf-mirror.com
python /root/autodl-fs/llm-gateway vllm_download_run_huggingface_llm.py
```
无法下载。
---------：使用魔塔下载
```
pip install modelscope
python -c "from modelscope import snapshot_download; snapshot_download('Qwen/Qwen2.5-7B-Instruct', cache_dir='/root/autodl-fs/models/qwen2.5-7b-instruct')"
```
-------：已经下载好了

2.ollama更新到了v0.31.4
怎么删除系统内的旧版 v0.5.4 一开机默认指向 v0.5.4 
每次需要执行重回系统默认值 PATH -- export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"
```
which ollama 查看当前ollama PATH
ollama --version
```
---------：已经解决：编辑终端的 ~/.bashrc 文件
✅ 最简单的清理方法（不用 vi，一行命令搞定）
复制下面这行命令，在终端里直接执行：
```bash
sed -i '/ollama/d' ~/.bashrc && source ~/.bashrc
```
这行命令会：
```
sed -i '/ollama/d' ~/.bashrc：删除 .bashrc 文件中所有包含 ollama 的行。
source ~/.bashrc：重新加载配置，使更改在当前终端立即生效（以后新终端也会自动生效）。
```
-------：已经处理好了，现在显示默认指向的是client version is 0.32.1  


3.我删除了/autodl-fs/ollama 文件夹，估计是模型系统文件被删除，
导致 ollama run qwen2.5:7b 1.5b 3b 要重新下载了，
要先执行完2.删除系统内容旧版v0.5.4，默认开机PATH 指向系统默认值export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"，
```
export OLLAMA_MODELS=/root/autodl-fs/ollama-models
ollama run qwen2.5:1.5b 
```
3b 7b 先看一下，run 下载的1.5b看一下文件会下载到什么位置。
清空了autodl-fs/model中的内容，重新下载不知道会不会到这个文件夹，要试一下
## 后续需要继续完成的内容：
```
cd /root/autodl-fs/llm-gateway
conda init bash
```
新建终端 
```
cd /root/autodl-fs/llm-gateway
conda activate llm-env
```
启动大模型：
```
ollama
export OLLAMA_MODELS=/root/autodl-fs/ollama-models
ollama --version
ollama serve
ollama run qwen2.5:7b
```
确保Ollama服务也在运行（默认端口11434）。

vLLM
启动 vLLM 时指定本地路径：
```bash
python -m vllm.entrypoints.openai.api_server \
  --model /root/autodl-fs/models/qwen2.5-7b-instruct \
  --served-model-name my-local-model \
  --host 0.0.0.0 \
  --port 8001
```
启动成功后，你会看到 INFO: Uvicorn running on http://0.0.0.0:8001。

3.vLLM和Ollama 性能基线压测
确保vLLMvLLM和Ollama 服务都 已经启动
```bash
python test_banchmark_performance.py
```
得到产物 test_benchmark_results.json 文件和test_benchmark_chart.png，里面包含了所有测试数据
# 7.22暂时新不做 Docker 
第1步：确认 Docker 已安装
在 AutoDL 实例终端中执行：
```bash
docker --version
docker compose version
```
如果提示 command not found，说明 Docker 未安装。在 AutoDL 实例上安装 Docker：
```bash
apt-get update && apt-get install -y docker.io docker-compose-v2
```
安装完成后，启动 Docker 服务：
```bash
service docker start
```

第2步：创建 Docker Compose 配置文件
在 /root/autodl-fs/llm-gateway/ 目录下创建 docker-compose.yml 文件

第3步：创建 Dockerfile
在同一个目录下创建 Dockerfile，用于构建 FastAPI 网关的镜像：

第4步：修改 main.py，让服务地址可配置
修改 main.py 中调用 Ollama 和 vLLM 的地址，改为从环境变量读取：

第5步：启动全家桶
```bash
cd /root/autodl-fs/llm-gateway
docker compose up -d
```
首次启动会自动构建 FastAPI 镜像并拉取 Redis、Ollama、vLLM 的镜像。等待约 3-5 分钟后，所有服务应该正常运行。

第6步：验证所有服务
```bash
#查看服务状态
docker compose ps
#测试 FastAPI 健康检查
curl http://localhost:8000/health
#测试 vLLM
curl http://localhost:8001/v1/models
#测试 Ollama
curl http://localhost:11434/api/tags
```
第7步：实现 /v1/compare 对比测试端点

三、练习题
必做：成功执行 docker compose up -d，验证所有服务正常运行。
必做：调用 /v1/compare 接口，对比 Ollama 和 vLLM 对同一个问题的回复和耗时差异。
选做：停止并重启所有服务（docker compose down && docker compose up -d），验证一键启动的便利性。
# 7.23 未做 (第10天：LLaMA-Factory 环境搭建)
LoRA 微调
创建实例
RTX 4090 24GB 
Ubuntu(PyTorch 2.0 CUDA 11.8 )+Python 3.10+
可以直接使用保存的镜像

Linux系统要先下载和安装 Miniconda 
**下载Miniconda安装脚本**：
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   ```
2. **执行安装脚本**：
```
   bash
   bash Miniconda3-latest-Linux-x86_64.sh  # 根据提示操作，确保勾选“添加到PATH”
```
####激活Miniconda环境管理器
1. **激活Conda环境管理器**：
```bash
   source ~/.bashrc  # 或者是 source ~/.zshrc，取决于你的shell配置
   conda --version  # 验证是否成功安装了conda
```


第1步：
每个新项目必做第一件事：环境隔离 venv = 工程习惯，
venv创建 独立 Python 环境和依赖文件 （生产级标准操作）
具体操作


第2步：安装 LLaMA-Factory：微调框架
```
cd /root/autodl-fs
```
下载最新稳定版 LLaMA-Factory-stable（如 v0.9.5）
```
cd /root/autodl-fs/
git clone -b v0.9.5 https://github.com/hiyouga/LLaMA-Factory.git LLaMA-Factory-stable
```
或者镜像加速
使用 gh-proxy.com 镜像
```bash
git clone https://gh-proxy.com/https://github.com/hiyouga/LLaMA-Factory.git
```
bash
#1. 进入 LLaMA-Factory-stable 目录
```
cd /root/autodl-fs/LLaMA-Factory-stable
```
#2. 创建独立虚拟环境
创建新环境，LLaMA-Factory：微调框架 指定 Python 3.11（推荐）
```bash
conda create -n llama-factory-stable-env python=3.11 -y
source ~/.bashrc
conda activate llama-factory-stable-env
```

```
pip install -e . --no-build-isolation
```
下面这个pip install -e ".[torch,metrics]"可能不需要安装
```
cd LLaMA-Factory
pip install -e ".[torch,metrics]" # llamafactory 包明确要求 Python 3.11 或更高版本
```

```
llamafactory-cli version
```

第3步：安装 MLflow（实验管理）
```
pip install mlflow
```
启动 MLflow UI（会占用一个端口）：
bash
mlflow ui --host 0.0.0.0 --port 5000 --backend-store-uri /root/autodl-fs/mlflow-runs
参数说明：
--host 0.0.0.0：允许外部访问
--port 5000：Web UI 端口
--backend-store-uri /root/autodl-fs/mlflow-runs：实验数据存储位置，放文件存储目录确保不丢失
注意：AutoDL 可能不开放 5000 端口，暂时先启动，后面可以通过 JupyterLab 的终端查看日志，或者配置端口转发。如果无法访问 Web UI，不影响使用——MLflow 会自动在指定目录记录所有实验数据。

第4步：配置 LLaMA-Factory
LLaMA-Factory 通过 YAML 配置文件或 Web UI 进行训练配置。先熟悉一下它的目录结构：
```bash
cd /root/autodl-fs/LLaMA-Factory
ls examples/           # 示例配置文件
ls data/               # 数据集存放位置
ls src/                # 源代码
```
关键的配置文件在 examples/train_lora/ 目录下。

第5步：下载基座模型，之前已经下载的是qwen2.5:7b，现在要重新下载，更改保存文件夹为/vllm-models 
删除旧的，下载新的 Qwen3-8B-Instruct 
使用魔搭 modelscope，（魔搭）终端指令
```
pip install modelscope 安装 modelscope
```
终端命令 python方式 下载，
```
python -c "from modelscope import snapshot_download
snapshot_download('Qwen/Qwen3-8B', cache_dir='/root/autodl-fs/vllm-models/Qwen3-8B')"
```

必做1：新微调实例创建完成，文件存储挂载成功，ls /root/autodl-fs/ 能看到之前的所有文件。
必做2：LLaMA-Factory 克隆安装完成，llamafactory-cli version 正常输出版本号。
必做3：MLflow 安装完成，启动 mlflow ui 后，/root/autodl-fs/mlflow-runs/ 目录下有文件生成。
选做：打开 LLaMA-Factory 的 Web UI（llamafactory-cli webui），熟悉一下界面布局，但今天不需要在 UI 上操作。
# 备份文件 /root/autodl-fs/2026.7.25LoRA/
# 7.23 （第11天：数据集准备与质量检查 ）
LoRA 数据集的内容：
新建 LLaMA-Factory
datasets_check_data_quality.py
datasets_generated_data.py
datasets_handcraft_data.py
datasets_merge_script.py
datasets_open_source_data.py
datasets_visualize_data.py
datesets_handcraft_data.json
自动生成的 environment.yml 和 requirements.txt 执行命令在下面

新建 LLaMA-Factory/data
```
"存放数据"：
```
执行datasets_merge_script.py 的产物 my_dataset.json
执行check_data_quality.py 的产物 data_quality_report.txt

升级 pip 和 生成 environment.yml（推荐）和 requirements.txt
#4. 升级 pip（重要，避免旧版 pip 安装失败）
```
pip install --upgrade pip
```
#6. 安装其他依赖
```
pip install mlflow matplotlib datasets
```
安装完成后，立即导出环境配置，作为项目的一部分保存：
```bash
#导出 conda 格式的环境文件
pip list --format=freeze > requirements.txt
#导出更完整的环境配置（如果能用 conda）
conda env export > environment.yml
```
# 7.24  （第12天：LoRA 训练与 MLflow 实验管理）
第1步：激活环境并进入目录
```
cd /root/autodl-fs/LLaMA-Factory
source llama-factort-env/bin/activate
```
确保文件存在
```
ls data/my_dataset.json
```

第3步：在 dataset_info.json 中注册你的数据集
编辑 /root/autodl-fs/LLaMA-Factory/data/dataset_info.json，在文件末尾的 } 之前添加：
```json
  "my_dataset": {
    "file_name": "my_dataset.json"
  }
```
完整文件结构参考（你的文件里已经有很多内置数据集，只需在最后加这一个）：
```json
{
  "identity": {
    "file_name": "identity.json"
  },
  "alpaca_en_demo": {
    "file_name": "alpaca_en_demo.json"
  },
  ...（已有的其他数据集）...,
  "my_dataset": {
    "file_name": "my_dataset.json"
  }
```
}

第4步：创建训练配置文件
在 /root/autodl-fs/LLaMA-Factory/examples/train_lora/ 下创建 my_first_lora.yaml

第5步：启动训练
```
llamafactory-cli train examples/train_lora/my_first_lora.yaml
```
启动后会看到：

```text
[INFO] ***** Running training *****
[INFO]   Num examples = 200
[INFO]   Num Epochs = 3
[INFO]   Instantaneous batch size per device = 2
[INFO]   Gradient Accumulation steps = 4
[INFO]   Total optimization steps = xxx
```
...
```
{'loss': 2.3456, 'learning_rate': 1.8e-4, 'epoch': 0.1}
{'loss': 2.1234, 'learning_rate': 1.9e-4, 'epoch': 0.2}
```
...

第7步：训练完成后检查产出物

```bash
ls /root/autodl-fs/LLaMA-Factory/saves/qwen3-8b-lora-my-first/
```
应该看到：

text
checkpoint-50/        ← 第50步的检查点
checkpoint-100/       ← 第100步的检查点
adapter_config.json   ← LoRA配置
adapter_model.bin     ← LoRA权重（你的便签纸）
trainer_state.json    ← 训练状态
training_args.bin     ← 训练参数记录
all_results.json      ← 训练结果摘要
第8步：MLflow 记录实验

训练过程中，LLaMA-Factory 会自动记录到 MLflow。查看记录：

```bash
#启动 MLflow UI（如果之前没启动）
mlflow ui --host 0.0.0.0 --port 5000 --backend-store-uri /root/autodl-fs/mlflow-runs &

#查看实验数据目录
ls /root/autodl-fs/mlflow-runs/
如果无法访问 Web UI，直接用 Python 查看：

python
import mlflow
mlflow.set_tracking_uri("file:///root/autodl-fs/mlflow-runs")

#列出所有实验
experiments = mlflow.search_experiments()
for exp in experiments:
    print(f"实验名称: {exp.name}, ID: {exp.experiment_id}")

#查看最近一次实验的指标
runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
print(runs[["metrics.loss", "params.lora_rank", "params.learning_rate"]].head())
```
四、练习题

必做1：成功启动训练，loss 从初始值开始下降。
必做2：训练完成后查看 saves/qwen3-8b-lora-my-first/ 目录，确认6个核心文件全部存在。
必做3：用 Python 脚本查看 MLflow 记录的超参数和 loss 曲线数据。
必做4：记录本次训练的最终 loss 值、训练时长、总步数。

选做：打开生成的 loss.png（如果 LLaMA-Factory 生成了），观察 loss 曲线的下降趋势。

# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 

