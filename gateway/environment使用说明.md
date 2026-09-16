# 如何使用：
从环境文件创建新环境：
```bash
cd /root/autodl-fs/llm-gateway
conda env create -f environment.yml
```
更新已有环境（以后添加了新包）：

```bash
conda env update -f environment.yml --prune
```
--prune 会移除环境中不在文件里的旧包，保持环境干净。

以后你的项目就有了自描述能力，无论在哪台机器上，只要这一个文件，就能精确复现出完全一致的运行环境。现在，你可以用这个文件替代之前手动创建的空文件夹，正式将项目环境标准化。

第一步：修复当前的 conda activate 报错

报错信息已经给出了明确的解决方案，在 AutoDL 实例终端中执行：

```bash
conda init bash
```
执行后，你需要关闭当前终端，并重新打开一个新的终端（在 JupyterLab 中点击 File -> New -> Terminal）。新终端打开后，你会看到命令提示符前面出现 (llm-env)，说明环境已自动激活。如果没有自动激活，手动执行 conda activate llm-env 即可。