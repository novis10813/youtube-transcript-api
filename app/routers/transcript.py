"""
YouTube 字幕 API 路由模組
處理與 YouTube 字幕相關的 API 端點
"""

from fastapi import APIRouter, Depends, HTTPException, Form, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

from ..config import Settings
from ..dependencies import validate_youtube_url, get_settings
from ..exceptions import (
    TranscriptNotFoundError,
    TranscriptDisabledError,
    VideoNotFoundError
)

# 建立路由器
router = APIRouter(
    prefix="/transcript",
    tags=["字幕"],
    responses={404: {"description": "字幕不存在"}}
)


# Pydantic 模型定義
class TranscriptRequest(BaseModel):
    """字幕請求模型"""
    youtube_url: str = Field(..., description="YouTube 影片網址")
    language: Optional[str] = Field(None, description="指定語言代碼 (例如: zh-Hant, en)")


class TranscriptItem(BaseModel):
    """字幕項目模型"""
    text: str = Field(..., description="字幕文字")
    start: float = Field(..., description="開始時間（秒）")
    duration: float = Field(..., description="持續時間（秒）")


class TranscriptResponse(BaseModel):
    """字幕回應模型"""
    success: bool = Field(..., description="是否成功")
    video_id: str = Field(..., description="YouTube 影片 ID")
    language: str = Field(..., description="字幕語言")
    transcript: List[TranscriptItem] = Field(..., description="字幕內容")
    total_items: int = Field(..., description="字幕項目總數")
    duration: float = Field(..., description="影片總長度（秒）")


class TranscriptTextResponse(BaseModel):
    """純文字字幕回應模型"""
    success: bool = Field(..., description="是否成功")
    video_id: str = Field(..., description="YouTube 影片 ID")
    language: str = Field(..., description="字幕語言")
    text: str = Field(..., description="完整字幕文字")


class AvailableLanguagesResponse(BaseModel):
    """可用語言回應模型"""
    success: bool = Field(..., description="是否成功")
    video_id: str = Field(..., description="YouTube 影片 ID")
    languages: List[Dict[str, Any]] = Field(..., description="可用語言列表")


def get_transcript_with_fallback(video_id: str, preferred_language: str, fallback_languages: List[str]):
    """
    嘗試獲取字幕，包含語言回退機制
    """
    languages_to_try = [preferred_language] + fallback_languages
    
    for language in languages_to_try:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            return transcript, language
        except NoTranscriptFound:
            continue
    
    # 如果指定語言都找不到，嘗試獲取任何可用的字幕
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_transcripts = list(transcript_list)
        if available_transcripts:
            first_transcript = available_transcripts[0]
            transcript = first_transcript.fetch()
            return transcript, first_transcript.language_code
    except Exception:
        pass
    
    raise TranscriptNotFoundError(video_id, preferred_language)


@router.post("/", response_model=TranscriptResponse)
async def get_transcript(
    request: TranscriptRequest,
    settings: Settings = Depends(get_settings)
):
    """
    獲取 YouTube 影片字幕
    
    - **youtube_url**: YouTube 影片網址
    - **language**: 可選的語言代碼，預設為繁體中文
    """
    # 驗證並提取影片 ID
    video_id = validate_youtube_url(request.youtube_url)
    
    # 確定要使用的語言
    target_language = request.language or settings.default_language
    
    try:
        # 獲取字幕
        transcript_data, actual_language = get_transcript_with_fallback(
            video_id, target_language, settings.fallback_languages
        )
        
        # 轉換為回應格式
        transcript_items = [
            TranscriptItem(
                text=item['text'],
                start=item['start'],
                duration=item['duration']
            )
            for item in transcript_data
        ]
        
        # 計算總時長
        total_duration = max(
            item['start'] + item['duration'] for item in transcript_data
        ) if transcript_data else 0
        
        return TranscriptResponse(
            success=True,
            video_id=video_id,
            language=actual_language,
            transcript=transcript_items,
            total_items=len(transcript_items),
            duration=total_duration
        )
        
    except TranscriptsDisabled:
        raise TranscriptDisabledError(video_id)
    except VideoUnavailable:
        raise VideoNotFoundError(video_id)
    except NoTranscriptFound:
        raise TranscriptNotFoundError(video_id, target_language)


@router.post("/text", response_model=TranscriptTextResponse)
async def get_transcript_text(
    request: TranscriptRequest,
    settings: Settings = Depends(get_settings)
):
    """
    獲取 YouTube 影片字幕（純文字格式）
    
    - **youtube_url**: YouTube 影片網址
    - **language**: 可選的語言代碼，預設為繁體中文
    """
    # 驗證並提取影片 ID
    video_id = validate_youtube_url(request.youtube_url)
    
    # 確定要使用的語言
    target_language = request.language or settings.default_language
    
    try:
        # 獲取字幕
        transcript_data, actual_language = get_transcript_with_fallback(
            video_id, target_language, settings.fallback_languages
        )
        
        # 合併為純文字
        full_text = " ".join(item['text'] for item in transcript_data)
        
        return TranscriptTextResponse(
            success=True,
            video_id=video_id,
            language=actual_language,
            text=full_text
        )
        
    except TranscriptsDisabled:
        raise TranscriptDisabledError(video_id)
    except VideoUnavailable:
        raise VideoNotFoundError(video_id)
    except NoTranscriptFound:
        raise TranscriptNotFoundError(video_id, target_language)


@router.post("/form", response_model=TranscriptResponse)
async def get_transcript_form(
    youtube_url: str = Form(..., description="YouTube 影片網址"),
    language: Optional[str] = Form(None, description="語言代碼"),
    settings: Settings = Depends(get_settings)
):
    """
    使用表單方式獲取 YouTube 影片字幕
    
    這個端點接受 form-data 格式的請求，適合前端表單提交
    """
    request = TranscriptRequest(youtube_url=youtube_url, language=language)
    return await get_transcript(request, settings)


@router.get("/languages/{video_id}", response_model=AvailableLanguagesResponse)
async def get_available_languages(video_id: str):
    """
    獲取指定影片的可用字幕語言
    
    - **video_id**: YouTube 影片 ID
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        languages = []
        for transcript in transcript_list:
            languages.append({
                "code": transcript.language_code,
                "name": transcript.language,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable
            })
        
        return AvailableLanguagesResponse(
            success=True,
            video_id=video_id,
            languages=languages
        )
        
    except TranscriptsDisabled:
        raise TranscriptDisabledError(video_id)
    except VideoUnavailable:
        raise VideoNotFoundError(video_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取可用語言時發生錯誤: {str(e)}"
        ) 