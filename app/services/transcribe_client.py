"""Whisper Transcribe API 客戶端模組"""

import httpx
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

async def transcribe_video(video_id: str, language: str) -> List[Dict[str, Any]]:
    """
    呼叫 Whisper transcribe API 取得字幕
    
    Args:
        video_id: YouTube 影片 ID
        language: 影片語言 (e.g. "zh-Hant")
        
    Returns:
        字幕列表 [{"text": str, "start": float, "duration": float}, ...]
        
    Raises:
        Exception: 當 API 呼叫失敗或設定無效時
    """
    if not settings.transcribe_api_url:
        raise ValueError("Transcribe API URL not configured")
        
    url = f"{settings.transcribe_api_url}/api/v1/transcribe-youtube"
    
    payload = {
        "video_id": video_id,
        "language": language
    }
    
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Calling Transcribe API for video {video_id} with language {language}")
            response = await client.post(url, json=payload, timeout=300.0) # 轉錄可能需要較長時間，設定較長 timeout
            response.raise_for_status()
            
            return response.json()
            
    except httpx.HTTPError as e:
        logger.error(f"Transcribe API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling Transcribe API: {e}")
        raise
