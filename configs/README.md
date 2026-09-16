
# LoRA 训练流程 命令
进入环境 
cd /root/autodl-fs/LLaMA-Factory
conda activate llama-factory-env
确认文件
- LLaMA-Factory/data/my_dataset.json # 确认是最新训练数据集
- LLaMA-Factory/examples/train_lora/.ymal # 确认训练配置文件
- .ymal 文件中的 输入和输出路径，各项参数校验
启动训练
llamafactory-cli train examples/train_lora/(...).yaml
# YAML_LoRA通用优化策略
## 早停与评估（新增）
load_best_model_at_end: true      # 训练结束加载最优检查点
metric_for_best_model: loss        # 以 loss 为评判标准
greater_is_better: false           # loss 越低越好
eval_strategy: steps               # 按步数评估
eval_steps: 25                     # 每25步评估一次

##  检查点保存（优化）
save_steps: 50                     # 每50步保存一次
save_total_limit: 5                # 保留最近5个检查点
logging_steps: 10                  # 每10步记录一次日志
plot_loss: true                    # 生成 loss 曲线图