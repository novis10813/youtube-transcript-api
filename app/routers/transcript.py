"""YouTube 字幕 API 路由模組"""

from fastapi import APIRouter, Depends, HTTPException, Form, status
from typing import Optional

from ..config import Settings
from ..dependencies import validate_youtube_url, get_settings
from ..schemas.transcript import (
    TranscriptRequest, 
    TranscriptResponse, 
    TranscriptTextResponse,
    AvailableLanguagesResponse,
    TranscriptItem
)
from ..services import transcript as service
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
        transcript_data, actual_language = await service.get_transcript_with_fallback(
            video_id, target_language, settings.fallback_languages
        )
        
        # 處理資料
        transcript_items, total_duration = service.process_transcript_data(transcript_data)
        
        return TranscriptResponse(
            success=True,
            video_id=video_id,
            language=actual_language,
            transcript=[TranscriptItem(**item) for item in transcript_items],
            total_items=len(transcript_items),
            duration=total_duration
        )
        
    except TranscriptDisabledError:
        raise
    except VideoNotFoundError:
        raise
    except TranscriptNotFoundError:
        raise


@router.post("/text", response_model=TranscriptTextResponse)
async def get_transcript_text(
    request: TranscriptRequest,
    settings: Settings = Depends(get_settings)
):
    """
    獲取 YouTube 影片字幕（純文字格式）
    
    - **youtube_url**: YouTube 影片網址
    - **language**: 可選的語言代碼，預設為繁體中文
    - **include_chapters**: 是否包含章節標題
    """
    # 驗證並提取影片 ID
    video_id = validate_youtube_url(request.youtube_url)
    
    # 確定要使用的語言
    target_language = request.language or settings.default_language
    
    try:
        # 獲取字幕
        transcript_data, actual_language = await service.get_transcript_with_fallback(
            video_id, target_language, settings.fallback_languages
        )
        
        # 生成輸出
        full_text, title, has_chapters = service.generate_text_output(
            transcript_data, 
            request.youtube_url, 
            request.include_chapters
        )
        
        return TranscriptTextResponse(
            success=True,
            video_id=video_id,
            language=actual_language,
            text=full_text,
            title=title,
            has_chapters=has_chapters
        )
        
    except TranscriptDisabledError:
        raise
    except VideoNotFoundError:
        raise
    except TranscriptNotFoundError:
        raise


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
        languages = service.get_available_languages(video_id)
        
        return AvailableLanguagesResponse(
            success=True,
            video_id=video_id,
            languages=languages
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取可用語言時發生錯誤: {str(e)}"
        )