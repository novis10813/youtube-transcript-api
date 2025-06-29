# 使用官方 Python 映像檔作為基礎
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴項
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝 uv
RUN pip install uv

# 複製專案配置檔案
COPY pyproject.toml uv.lock* ./

# 安裝 Python 依賴項
RUN uv sync --frozen --no-dev

# 複製應用程式程式碼
COPY ./app /app/app

# 建立非 root 使用者
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000

# 設定環境變數
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 啟動命令
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 