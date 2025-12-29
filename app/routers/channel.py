"""YouTube 頻道 API 路由模組"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import scrapetube

router = APIRouter(
    prefix="/channel",
    tags=["頻道"],
    responses={404: {"description": "頻道不存在"}}
)


class VideoItem(BaseModel):
    """影片項目"""
    video_id: str = Field(..., description="影片 ID")
    title: str = Field(..., description="影片標題")
    publish_date: Optional[str] = Field(None, description="發布日期")
    duration: Optional[int] = Field(None, description="影片長度（秒）")
    thumbnail_url: Optional[str] = Field(None, description="縮圖網址")
    view_count: Optional[int] = Field(None, description="觀看次數")


class ChannelVideosResponse(BaseModel):
    """頻道影片列表回應"""
    success: bool = Field(..., description="是否成功")
    channel_id: str = Field(..., description="頻道 ID")
    videos: List[VideoItem] = Field(..., description="影片列表")
    count: int = Field(..., description="回傳影片數量")


class ChannelInfoResponse(BaseModel):
    """頻道資訊回應"""
    success: bool = Field(..., description="是否成功")
    channel_id: str = Field(..., description="頻道 ID")
    name: Optional[str] = Field(None, description="頻道名稱")
    description: Optional[str] = Field(None, description="頻道描述")
    subscriber_count: Optional[int] = Field(None, description="訂閱數")
    video_count: Optional[int] = Field(None, description="影片數量")
    thumbnail_url: Optional[str] = Field(None, description="頻道頭像")


def parse_duration(duration_text: str) -> Optional[int]:
    """解析時長文字為秒數"""
    if not duration_text:
        return None
    try:
        parts = duration_text.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return None


def parse_view_count(view_text: str) -> Optional[int]:
    """解析觀看次數文字"""
    if not view_text:
        return None
    try:
        # 移除 "次觀看", "views" 等文字
        text = view_text.lower().replace('次觀看', '').replace('views', '').replace('view', '').strip()
        text = text.replace(',', '').replace(' ', '')
        
        # 處理 K, M 等縮寫
        multiplier = 1
        if text.endswith('k'):
            multiplier = 1000
            text = text[:-1]
        elif text.endswith('m'):
            multiplier = 1000000
            text = text[:-1]
        elif text.endswith('萬'):
            multiplier = 10000
            text = text[:-1]
        
        return int(float(text) * multiplier)
    except:
        pass
    return None


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
        
        # scrapetube 回傳 generator，需要限制數量
        video_generator = scrapetube.get_channel(channel_id, limit=limit * 2)  # 多抓一些以便過濾
        
        for video in video_generator:
            if len(videos) >= limit:
                break
            
            video_id = video.get('videoId')
            if not video_id:
                continue
            
            # 解析發布時間（如果有 since 篩選）
            publish_text = video.get('publishedTimeText', {}).get('simpleText', '')
            
            # 取得縮圖
            thumbnails = video.get('thumbnail', {}).get('thumbnails', [])
            thumbnail_url = thumbnails[-1].get('url') if thumbnails else None
            
            # 取得標題
            title_runs = video.get('title', {}).get('runs', [])
            title = title_runs[0].get('text', '') if title_runs else ''
            
            # 取得時長
            duration_text = video.get('lengthText', {}).get('simpleText', '')
            duration = parse_duration(duration_text)
            
            # 取得觀看次數
            view_text = video.get('viewCountText', {}).get('simpleText', '')
            view_count = parse_view_count(view_text)
            
            videos.append(VideoItem(
                video_id=video_id,
                title=title,
                publish_date=publish_text,  # scrapetube 回傳相對時間如 "1天前"
                duration=duration,
                thumbnail_url=thumbnail_url,
                view_count=view_count
            ))
        
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
        from pytubefix import Channel
        
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        channel = Channel(channel_url)
        
        return ChannelInfoResponse(
            success=True,
            channel_id=channel_id,
            name=channel.channel_name,
            description=None,  # pytubefix 不提供描述
            subscriber_count=None,  # 需要額外 API
            video_count=len(list(channel.video_urls)) if hasattr(channel, 'video_urls') else None,
            thumbnail_url=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取頻道資訊時發生錯誤: {str(e)}"
        )
