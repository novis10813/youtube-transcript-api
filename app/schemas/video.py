from pydantic import BaseModel, Field
from typing import Optional, List
from .base import BaseResponse

class ChapterInfo(BaseModel):
    """章節資訊"""
    title: str = Field(..., description="章節標題")
    start_seconds: float = Field(..., description="開始時間（秒）")

class VideoInfoResponse(BaseResponse):
    """影片資訊回應"""
    video_id: str = Field(..., description="YouTube 影片 ID")
    title: Optional[str] = Field(None, description="影片標題")
    channel_id: Optional[str] = Field(None, description="頻道 ID")
    channel_name: Optional[str] = Field(None, description="頻道名稱")
    duration: Optional[int] = Field(None, description="影片長度（秒）")
    publish_date: Optional[str] = Field(None, description="發布日期")
    chapters: List[ChapterInfo] = Field(default=[], description="章節列表")
    thumbnail_url: Optional[str] = Field(None, description="縮圖網址")
