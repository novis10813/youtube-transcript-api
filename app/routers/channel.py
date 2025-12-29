"""YouTube 頻道 API 路由模組"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from datetime import datetime
from ..schemas.channel import ChannelVideosResponse, ChannelInfoResponse, VideoItem
from ..services import channel as service

router = APIRouter(
    prefix="/channel",
    tags=["頻道"],
    responses={404: {"description": "頻道不存在"}}
)


@router.get("/{channel_id}/videos", response_model=ChannelVideosResponse)
async def get_channel_videos(
    channel_id: str,
    since: Optional[datetime] = Query(None, description="只回傳此時間之後發佈的影片 (ISO 8601)"),
    limit: int = Query(20, ge=1, le=100, description="回傳數量上限")
):
    """
    獲取頻道影片列表
    
    - **channel_id**: 頻道 ID（以 UC 開頭）
    - **since**: 只回傳此時間之後發佈的影片
    - **limit**: 回傳數量上限（預設 20，最大 100）
    """
    try:
        videos = []
        
        # 獲取生成器，多抓一些以便過濾
        video_generator = service.get_channel_videos_generator(channel_id, limit=limit * 2)
        
        for video_data in video_generator:
            if len(videos) >= limit:
                break
            
            info = service.extract_video_info(video_data)
            if not info:
                continue
            
            # TODO: 處理 since 時間篩選 (scrapetube 只回傳相對時間，需要更複雜的轉換)
            # 目前僅作範例，實際轉換需要額外邏輯
            
            videos.append(VideoItem(**info))
        
        return ChannelVideosResponse(
            success=True,
            channel_id=channel_id,
            videos=videos,
            count=len(videos)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取頻道影片時發生錯誤: {str(e)}"
        )


@router.get("/{channel_id}/info", response_model=ChannelInfoResponse)
async def get_channel_info(channel_id: str):
    """
    獲取頻道資訊
    
    - **channel_id**: 頻道 ID（以 UC 開頭）
    """
    try:
        info = service.get_channel_basic_info(channel_id)
        
        return ChannelInfoResponse(
            success=True,
            **info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取頻道資訊時發生錯誤: {str(e)}"
        )
