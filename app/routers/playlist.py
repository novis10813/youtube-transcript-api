"""YouTube 播放清單 API 路由模組"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional
import scrapetube

router = APIRouter(
    prefix="/playlist",
    tags=["播放清單"],
    responses={404: {"description": "播放清單不存在"}}
)


class PlaylistVideoItem(BaseModel):
    """播放清單影片項目"""
    video_id: str = Field(..., description="影片 ID")
    title: str = Field(..., description="影片標題")
    position: int = Field(..., description="在播放清單中的位置")
    channel_id: Optional[str] = Field(None, description="頻道 ID")
    channel_name: Optional[str] = Field(None, description="頻道名稱")
    duration: Optional[int] = Field(None, description="影片長度（秒）")
    thumbnail_url: Optional[str] = Field(None, description="縮圖網址")


class PlaylistVideosResponse(BaseModel):
    """播放清單影片列表回應"""
    success: bool = Field(..., description="是否成功")
    playlist_id: str = Field(..., description="播放清單 ID")
    videos: List[PlaylistVideoItem] = Field(..., description="影片列表")
    count: int = Field(..., description="回傳影片數量")


class PlaylistInfoResponse(BaseModel):
    """播放清單資訊回應"""
    success: bool = Field(..., description="是否成功")
    playlist_id: str = Field(..., description="播放清單 ID")
    title: Optional[str] = Field(None, description="播放清單標題")
    description: Optional[str] = Field(None, description="播放清單描述")
    channel_id: Optional[str] = Field(None, description="建立者頻道 ID")
    channel_name: Optional[str] = Field(None, description="建立者頻道名稱")
    video_count: Optional[int] = Field(None, description="影片數量")
    thumbnail_url: Optional[str] = Field(None, description="縮圖網址")


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
        
        video_generator = scrapetube.get_playlist(playlist_id)
        
        for video in video_generator:
            if len(videos) >= limit:
                break
            
            video_id = video.get('videoId')
            if not video_id:
                continue
            
            # 取得縮圖
            thumbnails = video.get('thumbnail', {}).get('thumbnails', [])
            thumbnail_url = thumbnails[-1].get('url') if thumbnails else None
            
            # 取得標題
            title_runs = video.get('title', {}).get('runs', [])
            title = title_runs[0].get('text', '') if title_runs else ''
            
            # 取得時長
            duration_text = video.get('lengthText', {}).get('simpleText', '')
            duration = parse_duration(duration_text)
            
            # 取得頻道資訊
            channel_runs = video.get('shortBylineText', {}).get('runs', [])
            channel_name = channel_runs[0].get('text', '') if channel_runs else None
            channel_endpoint = channel_runs[0].get('navigationEndpoint', {}) if channel_runs else {}
            channel_id = channel_endpoint.get('browseEndpoint', {}).get('browseId')
            
            videos.append(PlaylistVideoItem(
                video_id=video_id,
                title=title,
                position=position,
                channel_id=channel_id,
                channel_name=channel_name,
                duration=duration,
                thumbnail_url=thumbnail_url
            ))
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
        from pytubefix import Playlist
        
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        playlist = Playlist(playlist_url)
        
        return PlaylistInfoResponse(
            success=True,
            playlist_id=playlist_id,
            title=playlist.title,
            description=playlist.description,
            channel_id=playlist.owner_id,
            channel_name=playlist.owner,
            video_count=playlist.length,
            thumbnail_url=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取播放清單資訊時發生錯誤: {str(e)}"
        )
