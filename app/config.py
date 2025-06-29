"""
應用程式配置模組
管理環境變數和應用程式設定
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """應用程式設定"""
    
    # 應用程式基本設定
    app_name: str = "YouTube 字幕 API"
    app_version: str = "1.0.0"
    description: str = "使用 FastAPI 和 youtube_transcript_api 獲取 YouTube 影片的繁體中文字幕"
    
    # 伺服器設定
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API 設定
    api_prefix: str = "/api/v1"
    debug: bool = False
    
    # CORS 設定
    cors_origins: List[str] = ["http://localhost", "http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST"]
    cors_allow_headers: List[str] = ["*"]
    
    # YouTube Transcript API 設定
    default_language: str = "zh-Hant"  # 繁體中文
    fallback_languages: List[str] = ["zh-Hans", "zh", "en"]  # 備用語言：簡體中文、中文、英文
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 建立全域設定實例
settings = Settings() 