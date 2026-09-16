# 第 1 步：在本地 Mac 上，用 Python 脚本下载文件
# 有时候终端下载会受限，换成 Python 脚本可能会成功。
# 把上面的代码保存为 download_ollama.py，放在桌面运行，就可以得到一个离线的安装包。
import urllib.request

# 可以多试几个代理源，哪个能用用哪个 实测最有效快速，gh.ddlc.top
url = "https://gh.ddlc.top/https://github.com/ollama/ollama/releases/download/v0.31.1/ollama-linux-amd64.tgz"

print("开始下载...")
urllib.request.urlretrieve(url, "ollama-linux-amd64.tgz")
print("下载完成！")