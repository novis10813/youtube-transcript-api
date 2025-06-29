# 使用官方 Python 映像檔作為基礎
FROM python:3.11-slim

# 設定標籤
LABEL maintainer="your-email@example.com"
LABEL description="YouTube 字幕 API 服務 - 使用 FastAPI 和 youtube_transcript_api"
LABEL version="1.0.0"

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HOST=0.0.0.0 \
    PORT=8000 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 安裝系統依賴項
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安裝 uv（官方推薦方式）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 複製專案配置檔案和 README（按照最佳實務分層）
COPY pyproject.toml uv.lock* README.md ./

# 安裝 Python 依賴項（使用 cache mount 優化）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 複製應用程式程式碼
COPY ./app /app/app

# 安裝專案本身
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 建立非 root 使用者（可選，用於生產環境）
# 注意：為了簡化，這裡暫時保持 root 用戶
# RUN groupadd -r appuser && useradd -r -g appuser appuser && \
#     chown -R appuser:appuser /app
# USER appuser

# 暴露端口（預設 8000，可透過環境變數覆蓋）
EXPOSE ${PORT:-8000}

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# 啟動命令（使用 uv run）
CMD ["sh", "-c", "uv run uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"]
