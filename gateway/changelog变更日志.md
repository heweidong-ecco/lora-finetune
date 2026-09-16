# CHANGELOG — LLM Gateway 开发日志
# 开发日志时间只是仅作为节点有关内容显示表示和节点戳，非正常时间戳内完成的内容详情。

本文档记录从项目启动到系统整合的完整开发历程，共40天融合版计划中的第一阶段（推理平台搭建）和第二阶段（LoRA微调与评估体系）的关键节点。

---

## 第一阶段：生产级推理平台搭建（第1-9天）

### 第1天 — AutoDL环境准备与Ollama部署

- 注册AutoDL，创建GPU实例（RTX 3090）
- 安装Ollama，下载qwen2.5:1.7b测试模型
- Python调用Ollama验证
- 产出：云端环境就绪

### 第2天 — FastAPI骨架与API认证

- 搭建FastAPI服务
- 实现API Key认证中间件
- 编写 `/v1/generate` 接口
- 定义统一响应格式 `{code, message, data, request_id}`
- 产出：带认证的API服务

### 第3天 — 限流与请求验证

- 安装Redis，实现 `@RateLimiter` 令牌桶限流
- Pydantic参数校验（`GenerateRequest`模型）
- 统一错误处理
- 产出：完整的API服务（认证+限流+验证）

### 第4天 — Modelfile定制与模型量化入门

- 学习Modelfile语法，创建自定义模型
- 下载多量化版本，量化对比测试
- 产出：自定义模型 + 量化对比数据

### 第5天 — vLLM部署与推理测试

- 安装vLLM
- 学习Continuous Batching原理
- 用vLLM加载模型，启动OpenAI兼容API
- 产出：vLLM推理服务

### 第6天 — vLLM性能基线建立

- 固定输入/输出长度（512/512），记录不同并发下的延迟和吞吐量
- 实验 `--tensor-parallel-size`、`--gpu-memory-utilization` 等参数影响
- 整理《vLLM vs Ollama性能对比报告》
- 产出：vLLM性能基线数据 + 对比报告

### 第7天 — Docker Compose编排

- 编写Dockerfile（vLLM服务容器化）
- 编写docker-compose.yml（vLLM + Redis + FastAPI网关）
- `docker compose up -d` 一键启动全家桶
- 处理服务启动顺序（`depends_on` + `healthcheck` + `wait_for_service`）
- 产出：Docker Compose编排的完整推理平台

### 第8天 — 多模型路由系统

- 用3B模型做意图分类器（chat/qa/code/summary）
- 实现 `classify_intent_with_confidence` 函数
- 多级路由表（1.5B→3B→7B）
- 极简问候检测（`is_simple_greeting`）
- 集成到FastAPI路由 `/v1/chat/smart-routed`
- 产出：多模型路由系统

### 第9天 — 第一阶段总结与压测

- 编写Locust压测脚本（模拟5/10/20并发）
- 记录QPS、P50/P95/P99延迟、错误率
- 整理《第一阶段知识地图》
- 产出：压测报告 + 第一阶段知识地图

---

## 第二阶段：LoRA微调与评估体系（第10-20天）

### 第10天 — LLaMA-Factory环境搭建与LoRA原理

- 创建微调实例（RTX 4090），挂载文件存储
- 安装LLaMA-Factory
- 学习LoRA原理（低秩分解、rank/alpha含义）
- 安装MLflow，配置实验名称
- 产出：LLaMA-Factory环境就绪 + MLflow配置完成

### 第11天 — 数据集准备与质量检查

- 从HuggingFace下载 `yahma/alpaca-cleaned` 数据集
- 构建500条纯英文指令微调数据集
- 编写 `check_data_quality.py` 质量检查脚本（空值/长度/格式/重复/乱码五重检查）
- 学习全球和中国大陆专业数据集渠道
- 产出：微调数据集 + 质量报告

### 第12天 — LoRA训练与MLflow实验管理

- 首次LoRA微调（Qwen3-8B，rank=8，500条数据）
- 配置 `report_to: mlflow` 记录超参数和loss
- 产出6个核心文件（adapter_config/model、trainer_state/log、all_results、loss图）
- 修复MLflow文件系统后端废弃问题，改用SQLite数据库
- 产出：训练日志 + LoRA适配器 + MLflow实验记录

### 第13天 — 微调模型评估与Bad Case分析

- 设计测试集（50条，未参与训练）
- 编写 `evaluate.py` 自动化评估管道（五步流水线）
- 裁判模型设计（5项原则保证客观性：角色分离/标准前置/消除偏见/结构化输出/温度归零）
- 构建数据集总结脚本
- 产出：评估管道 + 数据集总结

### 第14天 — 第二轮训练（参数调优）

- 设计三组对比实验：exp1_baseline（rank=8,lr=2e-4,epoch=3）、exp2_rank16、exp3_lr5e5_epoch5
- MLflow对比三组实验的loss曲线和超参数
- 最优参数组合：rank=8, lr=2e-4, epoch=3（loss=0.56）
- 固化最优配置 `best_lora_config.yaml`
- 关键发现：数据量决定rank上限（500条配rank=8刚好，rank=16过拟合）
- 产出：最优参数组合 + MLflow实验对比

### 第15天 — 自动化评估流水线

- 编写 `evaluate.py` 脚本（加载模型→批量推理→计算准确率→生成报告）
- 实现一键评估，自动输出评估报告
- 理解Ollama（开发测试）vs vLLM（生产部署）的策略选择
- 产出：自动化评估脚本

### 第16天 — 模型导出与GGUF转换

- 合并LoRA权重到基座模型（`llamafactory-cli export`）
- 转换为GGUF格式
- Q4_K_M量化（16GB→6GB，质量损失极小）
- 产出：GGUF模型文件

### 第17天 — Ollama部署微调模型

- 创建Modelfile（FROM、SYSTEM、PARAMETER、TEMPLATE）
- `ollama create` 导入GGUF模型
- 功能测试（3个不同问题）+ 性能测试（推理速度对比）
- 编写 `test_both_models.py` 同时调用基座和微调模型
- 产出：可运行的微调模型

### 第18天 — 查询改写数据集构建

- 手工构建50个种子问题（覆盖5种类型：指代不明/用词模糊/信息缺失/口语化/多意图）
- 用qwen3:8b为每个种子生成3个改写版本
- 产出150条查询改写微调数据集
- 质量检查（空值率<1%、重复率<3%）
- 产出：查询改写数据集

### 第19天 — 查询改写模型微调与RAG集成

- 用3B模型微调查询改写能力（150条数据）
- 3B vs 7B模型选型策略：150条数据+单一任务，3B是最优解
- 部署到Ollama（`query-rewriter`）
- 对比三种方案：无改写 vs 云端7B改写 vs 本地3B改写
- 关键发现：本地3B延迟100ms，达到7B的90%效果，比云端快80%
- 产出：查询改写模型 + 对比报告

### 第20天 — 第二阶段总结

- 完整回顾11天微调流程：数据→训练→评估→导出→GGUF→Ollama
- MLflow汇总所有实验：5次训练，最优loss=0.56，最优参数固化
- 整理第二阶段知识地图
- 核心认知：数据质量决定上限，早停保护最优检查点，小模型+专项微调是性价比最优解
- 产出：第二阶段知识地图 + 优化反思

---

## 第三阶段：专项微调与作品输出（第21-30天）

### 第21天 — 代码补全数据集构建

- 从本地Python库提取代码片段（备选方案，因The Stack需要授权）
- 集成 `ast.parse` 语法检查过滤语法错误
- 构建250条代码补全FIM数据集
- 产出：代码补全数据集

### 第22天 — 代码补全模型微调

- 用Qwen3-Coder-7B微调代码补全能力
- 部署到Ollama（`code-completer`）
- 功能测试（函数补全/类方法补全/注释转代码）
- 对比通用模型vs代码模型的补全差异
- 产出：代码补全微调模型

### 第23天 — 云端VSCode集成

- 安装code-server（云端VSCode）
- 配置Continue.dev插件连接 `code-completer`
- 在实际编码中测试Tab补全效果
- 产出：云端VSCode集成 + 补全测试

### 第24天 — 系统整合

- 将FastAPI网关 + Ollama（3个微调模型）+ vLLM + Redis编排到Docker Compose
- 新增 `/v1/rewrite` 和 `/v1/code/complete` 接口
- `docker compose up -d` 一键启动全家桶
- 端到端测试 + 绘制系统架构图
- 产出：完整的Docker Compose项目 + 系统架构图

### 第25天 — 项目文档撰写

- 编写README.md（项目介绍/架构图/快速开始/API文档入口/性能数据）
- 编写API.md（6个接口详细说明）
- 编写DEPLOY.md（环境要求/部署步骤/故障排查）
- 编写CHANGELOG.md（本文档）
- 产出：完整的项目文档套件

---

## 核心成果总结

### 模型产出

| 模型         | 参数量 | 用途        | 训练数据  | 最优loss | 部署方式          |
| ------------ | ------ | ----------- | --------- | -------- | ----------------- |
| 通用指令模型 | 8B     | 通用对话    | 500条英文 | 0.56     | Ollama            |
| 查询改写模型 | 3B     | RAG查询优化 | 150条中文 | —        | Ollama            |
| 代码补全模型 | 7B     | Tab补全     | 250条     | —        | Ollama + Continue |

### 技术栈

FastAPI + Ollama + vLLM + Redis + Docker Compose + LLaMA-Factory + LoRA + MLflow + Locust

### 工程能力

模型部署、LoRA微调、参数调优、评估管道、GGUF导出、容器化编排、API开发、项目文档撰写