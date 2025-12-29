"""YouTube 影片資訊 API 路由模組"""

from fastapi import APIRouter, HTTPException, status
from ..schemas.video import VideoInfoResponse, ChapterInfo
from ..services import video as service
from pytubefix import YouTube

router = APIRouter(
    prefix="/video",
    tags=["影片"],
    responses={404: {"description": "影片不存在"}}
)


@router.get("/{video_id}/info", response_model=VideoInfoResponse)
async def get_video_metadata(video_id: str):
    """
    獲取影片 metadata
    
    - **video_id**: YouTube 影片 ID
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        info = service.get_video_info(url)
        
        if not info.get('title'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"無法獲取影片資訊: {video_id}"
            )
        
        # 從 pytubefix 獲取更多資訊
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
