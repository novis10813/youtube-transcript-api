"""頻道服務模組"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import scrapetube
from pytubefix import Channel

# 輔助函數保持私有
def _parse_duration(duration_text: str) -> Optional[int]:
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

def _parse_view_count(view_text: str) -> Optional[int]:
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

def get_channel_videos_generator(channel_id: str, limit: int = 20) -> Any:
    """獲取頻道影片生成器"""
    return scrapetube.get_channel(channel_id, limit=limit)

def extract_video_info(video_data: dict) -> dict:
    """從 scrapetube 數據中提取影片資訊"""
    video_id = video_data.get('videoId')
    if not video_id:
        return None
    
    # 解析發布時間
    publish_text = video_data.get('publishedTimeText', {}).get('simpleText')
    
    # 取得縮圖
    thumbnails = video_data.get('thumbnail', {}).get('thumbnails', [])
    thumbnail_url = thumbnails[-1].get('url') if thumbnails else None
    
    # 取得標題
    title_runs = video_data.get('title', {}).get('runs', [])
    title = title_runs[0].get('text', '') if title_runs else ''
    
    # 取得時長
    duration_text = video_data.get('lengthText', {}).get('simpleText', '')
    duration = _parse_duration(duration_text)
    
    # 取得觀看次數
    view_text = video_data.get('viewCountText', {}).get('simpleText', '')
    view_count = _parse_view_count(view_text)
    
    return {
        "video_id": video_id,
        "title": title,
        "publish_date": publish_text,
        "duration": duration,
        "thumbnail_url": thumbnail_url,
        "view_count": view_count
    }

def get_channel_basic_info(channel_id: str) -> dict:
    """獲取頻道基本資訊"""
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    channel = Channel(channel_url)
    
    # 注意: video_urls 計算可能較慢，這裡改用 property 避免立即觸發
    # 但在 pytubefix 中 video_urls 是個 property，存取時會觸發請求
    # 若要優化可能需要避免存取它，或接受它的延遲
    
    video_count = None
    try:
        # 嘗試快速獲取數量，如果 pytubefix 支援
        # 這裡先保留原邏輯，因為 pytubefix 的 video_urls 是 iterator
        # 為了安全起見，這裡不獲取影片數量以避免效能問題，或者只在必要時獲取
        pass 
    except:
        pass
        
    return {
        "channel_id": channel_id,
        "name": channel.channel_name,
        "thumbnail_url": None, # pytubefix 目前不直接提供 user icon
        # video_count 在這裡獲取代價太高，暫回傳 None 或需另行處理
        "video_count": None 
    }
