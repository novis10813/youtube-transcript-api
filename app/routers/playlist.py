"""YouTube 播放清單 API 路由模組"""

from fastapi import APIRouter, HTTPException, Query, status
from ..schemas.playlist import PlaylistVideosResponse, PlaylistInfoResponse, PlaylistVideoItem
from ..services import playlist as service

router = APIRouter(
    prefix="/playlist",
    tags=["播放清單"],
    responses={404: {"description": "播放清單不存在"}}
)


@router.get("/{playlist_id}/videos", response_model=PlaylistVideosResponse)
async def get_playlist_videos(
    playlist_id: str,
    limit: int = Query(50, ge=1, le=200, description="回傳數量上限")
):
    """
    獲取播放清單影片列表
    
    - **playlist_id**: 播放清單 ID（以 PL 開頭）
    - **limit**: 回傳數量上限（預設 50，最大 200）
    """
    try:
        videos = []
        position = 1
        
        video_generator = service.get_playlist_videos_generator(playlist_id, limit=limit)
        
        for video_data in video_generator:
            if len(videos) >= limit:
                break
            
            info = service.extract_playlist_video_info(video_data, position)
            if not info:
                continue
            
            videos.append(PlaylistVideoItem(**info))
            position += 1
        
        return PlaylistVideosResponse(
            success=True,
            playlist_id=playlist_id,
            videos=videos,
            count=len(videos)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取播放清單影片時發生錯誤: {str(e)}"
        )


@router.get("/{playlist_id}/info", response_model=PlaylistInfoResponse)
async def get_playlist_info(playlist_id: str):
    """
    獲取播放清單資訊
    
    - **playlist_id**: 播放清單 ID（以 PL 開頭）
    """
    try:
        info = service.get_playlist_basic_info(playlist_id)
        
        return PlaylistInfoResponse(
            success=True,
            **info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取播放清單資訊時發生錯誤: {str(e)}"
        )
