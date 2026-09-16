# AutoDL 实例配置工作流

> AutoDL 实例的**环境选型与配置记录**：
> PyTorch / Python / CUDA 版本搭配、MLflow 与 Ollama 的路径设置。
> **保留原样**，仅补回 Markdown 代码围栏。

---

最新，最优解，使用官方的固定搭配 选择 PyTorch 2.5.1 + Python 3.12 + CUDA 12.4 是最优解
硬件： RTX 4090 显卡
GPU框架选择：
从你列出的固定搭配中，选择 PyTorch 2.5.1 + Python 3.12 + CUDA 12.4 是最优解。 虽然它不完全是我们之前讨论的 2.4.0 + 3.10 + 12.4，但这是当前可选方案里最稳定、最能完美支持 Qwen3 的组合。
CPU框架选择：
更新架构的CPU (如Xeon Gold 6430， 第四代至强)

- 不一定能直接进入 conda activate llama-factory-new 
不能进入重建就重新创建（conda create -n llama-factory-new python=3.12 -y）
- 还需要下载依赖库 ，在独立环境中安装依赖（这一步才受 Python 版本影响）
```
pip install -e ".[torch,metrics]" 
```
- 用环境变量指定 MLflow 数据库路径
```
  export MLFLOW_TRACKING_URI=sqlite:////root/autodl-fs/LLaMA-Factory/mlflow-runs/mlflow.db
```
- 验证路径生效 echo $MLFLOW_TRACKING_URI
- 永久生效（写入 .bashrc）
```
  echo 'export MLFLOW_TRACKING_URI=sqlite:////root/autodl-fs/LLaMA-Factory/mlflow-runs/mlflow.db' >> ~/.bashrc
  source ~/.bashrc
```
- Ollama models路径设置
```
  export OLLAMA_MODELS=/root/autodl-fs/ollama-models
  echo 'export OLLAMA_MODELS=/root/autodl-fs/ollama-models' >> ~/.bashrc
```