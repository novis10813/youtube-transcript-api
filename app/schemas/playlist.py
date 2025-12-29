from pydantic import BaseModel, Field
from typing import Optional, List
from .base import BaseResponse

class PlaylistVideoItem(BaseModel):
    """播放清單影片項目"""
    video_id: str = Field(..., description="影片 ID")
    title: str = Field(..., description="影片標題")
    position: int = Field(..., description="在播放清單中的位置")
    channel_id: Optional[str] = Field(None, description="頻道 ID")
    channel_name: Optional[str] = Field(None, description="頻道名稱")
    duration: Optional[int] = Field(None, description="影片長度（秒）")
    thumbnail_url: Optional[str] = Field(None, description="縮圖網址")

class PlaylistVideosResponse(BaseResponse):
    """播放清單影片列表回應"""
    playlist_id: str = Field(..., description="播放清單 ID")
    videos: List[PlaylistVideoItem] = Field(..., description="影片列表")
    count: int = Field(..., description="回傳影片數量")

class PlaylistInfoResponse(BaseResponse):
    """播放清單資訊回應"""
    playlist_id: str = Field(..., description="播放清單 ID")
    title: Optional[str] = Field(None, description="播放清單標題")
    description: Optional[str] = Field(None, description="播放清單描述")
    channel_id: Optional[str] = Field(None, description="建立者頻道 ID")
    channel_name: Optional[str] = Field(None, description="建立者頻道名稱")
    video_count: Optional[int] = Field(None, description="影片數量")
    thumbnail_url: Optional[str] = Field(None, description="縮圖網址")
