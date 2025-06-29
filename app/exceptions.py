"""
自定義例外處理模組
定義應用程式特定的例外類別和錯誤處理器
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any


class YouTubeTranscriptError(HTTPException):
    """YouTube 字幕相關的基礎例外類別"""
    
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        super().__init__(status_code=status_code, detail=message)


class InvalidYouTubeURLError(YouTubeTranscriptError):
    """無效的 YouTube 網址例外"""
    
    def __init__(self, url: str):
        message = f"無效的 YouTube 網址: {url}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class TranscriptNotFoundError(YouTubeTranscriptError):
    """字幕不存在例外"""
    
    def __init__(self, video_id: str, language: str):
        message = f"找不到影片 {video_id} 的 {language} 字幕"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class TranscriptDisabledError(YouTubeTranscriptError):
    """字幕已停用例外"""
    
    def __init__(self, video_id: str):
        message = f"影片 {video_id} 的字幕功能已停用"
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class VideoNotFoundError(YouTubeTranscriptError):
    """影片不存在例外"""
    
    def __init__(self, video_id: str):
        message = f"找不到影片: {video_id}"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


# 例外處理器
async def youtube_transcript_exception_handler(
    request: Request, exc: YouTubeTranscriptError
) -> JSONResponse:
    """YouTube 字幕例外處理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "type": exc.__class__.__name__,
            "status_code": exc.status_code
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用例外處理器"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "內部伺服器錯誤",
            "type": "InternalServerError",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    ) 