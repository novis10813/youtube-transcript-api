from pydantic import BaseModel, Field
from typing import Optional, List
from .base import BaseResponse

class VideoItem(BaseModel):
    """影片項目"""
    video_id: str = Field(..., description="影片 ID")
    title: str = Field(..., description="影片標題")
    publish_date: Optional[str] = Field(None, description="發布日期")
    duration: Optional[int] = Field(None, description="影片長度（秒）")
    thumbnail_url: Optional[str] = Field(None, description="縮圖網址")
    view_count: Optional[int] = Field(None, description="觀看次數")

class ChannelVideosResponse(BaseResponse):
    """頻道影片列表回應"""
    channel_id: str = Field(..., description="頻道 ID")
    videos: List[VideoItem] = Field(..., description="影片列表")
    count: int = Field(..., description="回傳影片數量")

class ChannelInfoResponse(BaseResponse):
    """頻道資訊回應"""
    channel_id: str = Field(..., description="頻道 ID")
    name: Optional[str] = Field(None, description="頻道名稱")
    description: Optional[str] = Field(None, description="頻道描述")
    subscriber_count: Optional[int] = Field(None, description="訂閱數")
    video_count: Optional[int] = Field(None, description="影片數量")
    thumbnail_url: Optional[str] = Field(None, description="頻道頭像")
