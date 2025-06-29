"""
YouTube 字幕 API 主應用程式
FastAPI 應用程式的入口點
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .config import settings
from .routers import transcript
from .exceptions import (
    YouTubeTranscriptError,
    youtube_transcript_exception_handler,
    general_exception_handler
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時執行
    print(f"🚀 {settings.app_name} v{settings.app_version} 正在啟動...")
    print(f"📝 API 文檔可在以下網址查看: http://localhost:8000/docs")
    yield
    # 關閉時執行
    print(f"👋 {settings.app_name} 正在關閉...")


# 建立 FastAPI 應用程式實例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.description,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 設定 CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# 註冊例外處理器
app.add_exception_handler(YouTubeTranscriptError, youtube_transcript_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 包含路由
app.include_router(
    transcript.router,
    prefix=settings.api_prefix,
    responses={404: {"description": "Not found"}}
)


# 根路由
@app.get("/", tags=["系統"])
async def root():
    """
    根端點 - 系統資訊
    """
    return {
        "message": f"歡迎使用 {settings.app_name}",
        "version": settings.app_version,
        "description": settings.description,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_prefix": settings.api_prefix
    }


@app.get("/health", tags=["系統"])
async def health_check():
    """
    健康檢查端點
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.get("/version", tags=["系統"])
async def get_version():
    """
    取得版本資訊
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "api_version": "v1"
    } 