"""YouTube 影片資訊 API 路由模組"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

from ..services.video_info import get_video_info

router = APIRouter(
    prefix="/video",
    tags=["影片"],
    responses={404: {"description": "影片不存在"}}
)


class ChapterInfo(BaseModel):
    """章節資訊"""
    title: str = Field(..., description="章節標題")
    start_seconds: float = Field(..., description="開始時間（秒）")


class VideoInfoResponse(BaseModel):
    """影片資訊回應"""
    success: bool = Field(..., description="是否成功")
    video_id: str = Field(..., description="YouTube 影片 ID")
    title: Optional[str] = Field(None, description="影片標題")
    channel_id: Optional[str] = Field(None, description="頻道 ID")
    channel_name: Optional[str] = Field(None, description="頻道名稱")
    duration: Optional[int] = Field(None, description="影片長度（秒）")
    publish_date: Optional[str] = Field(None, description="發布日期")
    chapters: List[ChapterInfo] = Field(default=[], description="章節列表")
    thumbnail_url: Optional[str] = Field(None, description="縮圖網址")


@router.get("/{video_id}/info", response_model=VideoInfoResponse)
async def get_video_metadata(video_id: str):
    """
    獲取影片 metadata
    
    - **video_id**: YouTube 影片 ID
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        info = get_video_info(url)
        
        if not info.get('title'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"無法獲取影片資訊: {video_id}"
            )
        
        # 從 pytubefix 獲取更多資訊
        from pytubefix import YouTube
        yt = YouTube(url)
        
        chapters = [
            ChapterInfo(title=ch['title'], start_seconds=ch['start_seconds'])
            for ch in info.get('chapters', [])
        ]
        
        return VideoInfoResponse(
            success=True,
            video_id=video_id,
            title=info.get('title'),
            channel_id=yt.channel_id,
            channel_name=yt.author,
            duration=yt.length,
            publish_date=yt.publish_date.isoformat() if yt.publish_date else None,
            chapters=chapters,
            thumbnail_url=yt.thumbnail_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取影片資訊時發生錯誤: {str(e)}"
        )
