# 阶段1: 构建依赖
FROM python:3.10-slim-bookworm AS builder

# 安装 PDM
RUN pip install pdm

WORKDIR /app
COPY pyproject.toml pdm.lock ./

# 导出依赖到 requirements.txt
RUN pdm export -o requirements.txt --without-hashes

# 阶段2: 运行时镜像
FROM python:3.10-slim-bookworm

# 安装运行时依赖和 Playwright 所需的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    fonts-unifont \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 仅安装 Playwright 浏览器（不使用 --with-deps，因为依赖已手动安装）
RUN playwright install chromium

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p src/config src/data src/cache

# 暴露端口
EXPOSE 2333

# 启动命令
CMD ["python", "bot.py"]
