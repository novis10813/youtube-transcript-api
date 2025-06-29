"""
共用依賴項模組
定義可重用的依賴項注入函數
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import Optional
from fastapi import Depends, HTTPException, status

from .config import settings


def extract_video_id(youtube_url: str) -> str:
    """
    從 YouTube 網址中提取影片 ID
    
    支援的格式:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    # YouTube 影片 ID 的正則表達式模式
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]+)',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    # 如果正則表達式失敗，嘗試使用 URL 解析
    try:
        parsed_url = urlparse(youtube_url)
        
        # 處理 youtu.be 短網址
        if 'youtu.be' in parsed_url.netloc:
            return parsed_url.path[1:]  # 移除開頭的 '/'
        
        # 處理 youtube.com 網址
        if 'youtube.com' in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0]
            
            # 處理 embed 或 v 路徑
            path_parts = parsed_url.path.split('/')
            if len(path_parts) >= 3 and path_parts[1] in ['embed', 'v']:
                return path_parts[2]
    
    except Exception:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"無效的 YouTube 網址: {youtube_url}"
    )


def validate_youtube_url(url: str) -> str:
    """
    驗證 YouTube 網址並回傳影片 ID
    """
    if not url or not isinstance(url, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="請提供有效的 YouTube 網址"
        )
    
    # 移除前後空白
    url = url.strip()
    
    # 檢查是否為 YouTube 網址
    if not any(domain in url.lower() for domain in ['youtube.com', 'youtu.be']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="請提供 YouTube 網址"
        )
    
    # 提取並驗證影片 ID
    video_id = extract_video_id(url)
    
    # 驗證影片 ID 格式 (YouTube 影片 ID 通常是 11 個字符)
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無效的 YouTube 影片 ID: {video_id}"
        )
    
    return video_id


def get_settings():
    """取得應用程式設定"""
    return settings 