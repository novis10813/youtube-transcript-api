from pydantic import BaseModel, Field
from typing import Optional, List
from .base import BaseResponse

class TranscriptRequest(BaseModel):
    """字幕請求模型"""
    youtube_url: str = Field(..., description="YouTube 影片網址")
    language: Optional[str] = Field(None, description="指定語言代碼 (例如: zh-Hant, en)")
    include_chapters: bool = Field(
        default=False,
        description="是否包含章節標題（如有）。啟用時回傳 Markdown 格式，包含 H1（影片標題）和 H2（章節標題）"
    )

class TranscriptItem(BaseModel):
    """單條字幕模型"""
    text: str = Field(..., description="字幕內容")
    start: float = Field(..., description="開始時間")
    duration: float = Field(..., description="持續時間")

class TranscriptResponse(BaseResponse):
    """完整字幕回應模型"""
    video_id: str = Field(..., description="YouTube 影片 ID")
    language: str = Field(..., description="字幕語言")
    transcript: List[TranscriptItem] = Field(..., description="字幕列表")
    total_items: int = Field(..., description="字幕總條數")
    duration: float = Field(..., description="影片總長度")

class TranscriptTextResponse(BaseResponse):
    """純文字字幕回應模型"""
    video_id: str = Field(..., description="YouTube 影片 ID")
    language: str = Field(..., description="字幕語言")
    text: str = Field(..., description="完整字幕文字（或包含章節的 Markdown 格式）")
    title: Optional[str] = Field(None, description="影片標題（僅當 include_chapters=True 時）")
    has_chapters: bool = Field(default=False, description="影片是否有章節")

class LanguageItem(BaseModel):
    """語言選項模型"""
    code: str = Field(..., description="語言代碼")
    name: str = Field(..., description="語言名稱")
    is_generated: bool = Field(..., description="是否為自動產生")
    is_translatable: bool = Field(..., description="是否可翻譯")

class AvailableLanguagesResponse(BaseResponse):
    """可用語言列表回應模型"""
    video_id: str = Field(..., description="YouTube 影片 ID")
    languages: List[LanguageItem] = Field(..., description="可用語言列表")
