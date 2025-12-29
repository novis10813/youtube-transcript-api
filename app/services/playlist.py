"""播放清單服務模組"""

from typing import Optional, List, Dict, Any
import scrapetube
from pytubefix import Playlist
from .channel import _parse_duration  # 復用 duraion 解析邏輯

def get_playlist_videos_generator(playlist_id: str, limit: int = 50) -> Any:
    """獲取播放清單影片生成器"""
    return scrapetube.get_playlist(playlist_id, limit=limit)

def extract_playlist_video_info(video_data: dict, position: int) -> dict:
    """從 scrapetube 數據中提取播放清單影片資訊"""
    video_id = video_data.get('videoId')
    if not video_id:
        return None
    
    # 取得縮圖
    thumbnails = video_data.get('thumbnail', {}).get('thumbnails', [])
    thumbnail_url = thumbnails[-1].get('url') if thumbnails else None
    
    # 取得標題
    title_runs = video_data.get('title', {}).get('runs', [])
    title = title_runs[0].get('text', '') if title_runs else ''
    
    # 取得時長
    duration_text = video_data.get('lengthText', {}).get('simpleText', '')
    duration = _parse_duration(duration_text)
    
    # 取得頻道資訊
    channel_runs = video_data.get('shortBylineText', {}).get('runs', [])
    channel_name = channel_runs[0].get('text', '') if channel_runs else None
    channel_endpoint = channel_runs[0].get('navigationEndpoint', {}) if channel_runs else {}
    channel_id = channel_endpoint.get('browseEndpoint', {}).get('browseId')
    
    return {
        "video_id": video_id,
        "title": title,
        "position": position,
        "channel_id": channel_id,
        "channel_name": channel_name,
        "duration": duration,
        "thumbnail_url": thumbnail_url
    }

def get_playlist_basic_info(playlist_id: str) -> dict:
    """獲取播放清單基本資訊"""
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    playlist = Playlist(playlist_url)
    
    return {
        "playlist_id": playlist_id,
        "title": playlist.title,
        "description": playlist.description,
        "channel_id": playlist.owner_id,
        "channel_name": playlist.owner,
        "video_count": playlist.length,
        "thumbnail_url": None
    }
