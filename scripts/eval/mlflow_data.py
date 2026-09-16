'''
bash

python3 << 'EOF'
import mlflow
mlflow.set_tracking_uri("sqlite:////root/autodl-fs/LLaMA-Factory/mlflow.db")

experiments = mlflow.search_experiments()
for exp in experiments:
    runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
    print(f"实验: {exp.name}, 总运行次数: {len(runs)}")
    if len(runs) > 0:
        # 只显示最新的3次运行
        recent = runs.sort_values("start_time", ascending=False).head(3)
        cols = [c for c in recent.columns if c in [
            'run_id',
            'metrics.train_loss', 
            'metrics.train_runtime',
            'params.lora_rank',
            'params.learning_rate',
            'params.num_train_epochs'
        ]]
        print(recent[cols].to_string())
EOF

'''