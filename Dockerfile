FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# 可选：先升级 pip/打包工具，减少后续依赖冲突
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 安装依赖（使用清华镜像加速）
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir \
    -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
