FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# mirrors镜像下载，阿里云加速
RUN mkdir -p /root/.pip && echo "[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/" > /root/.pip/pip.conf
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]