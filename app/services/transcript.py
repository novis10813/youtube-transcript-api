"""字幕服務模組

使用 yt-dlp 獲取 YouTube 字幕，替代原本的 youtube-transcript-api。
yt-dlp 內建模擬瀏覽器行為，較不易被 YouTube 封鎖。
"""

from typing import List, Tuple, Any, Dict
from ..exceptions import (
    TranscriptNotFoundError,
    TranscriptDisabledError,
    VideoNotFoundError
)
from .video import get_video_info, generate_markdown
from .yt_dlp_wrapper import get_wrapper, YtDlpWrapper
from .transcribe_client import transcribe_video
from ..config import settings
import logging

logger = logging.getLogger(__name__)

# 獲取 yt-dlp wrapper 實例
_wrapper: YtDlpWrapper = None


def _get_wrapper() -> YtDlpWrapper:
    """獲取 YtDlpWrapper 實例"""
    global _wrapper
    if _wrapper is None:
        _wrapper = get_wrapper()
    return _wrapper


async def get_transcript_with_fallback(
    video_id: str, 
    preferred_language: str, 
    fallback_languages: List[str]
) -> Tuple[List[Dict[str, Any]], str]:
    """
    嘗試獲取字幕，包含語言回退機制
    
    Args:
        video_id: YouTube 影片 ID
        preferred_language: 偏好語言代碼
        fallback_languages: 回退語言代碼列表
        
    Returns:
        (字幕列表, 實際使用的語言代碼)
    """
    wrapper = _get_wrapper()
    
    try:
        transcript_data, actual_language = wrapper.get_subtitles(
            video_id, preferred_language, fallback_languages
        )
        return transcript_data, actual_language
        
    except Exception as e:
        # 嘗試使用 fallback API
        if settings.transcribe_api_url:
            try:
                logger.info(f"yt-dlp failed ({e}), trying Whisper fallback for {video_id}")
                
                # 嘗試從 yt-dlp 獲取影片語言資訊
                detected_language = preferred_language  # 預設使用 preferred_language
                try:
                    video_info = wrapper.get_video_info(video_id)
                    detected_language = video_info.get('language') or preferred_language
                    logger.info(f"Detected video language: {detected_language}")
                except Exception as info_error:
                    logger.warning(f"Could not get video info for language detection: {info_error}")
                
                # 使用偵測到的語言呼叫 Whisper API
                transcript_data = await transcribe_video(video_id, detected_language)
                return transcript_data, detected_language
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                # 繼續拋出原始錯誤，讓後續邏輯處理
        
        error_msg = str(e).lower()
        
        # 根據錯誤訊息分類
        if 'private' in error_msg or 'unavailable' in error_msg:
            raise VideoNotFoundError(video_id)
        elif 'no subtitles' in error_msg or 'no subtitle' in error_msg:
            raise TranscriptNotFoundError(video_id, preferred_language)
        elif 'disabled' in error_msg:
            raise TranscriptDisabledError(video_id)
        else:
            logger.error(f"Failed to get transcript for {video_id}: {e}")
            raise TranscriptNotFoundError(video_id, preferred_language)


def get_available_languages(video_id: str) -> List[Dict[str, Any]]:
    """
    獲取可用字幕語言
    
    Args:
        video_id: YouTube 影片 ID
        
    Returns:
        語言列表，每個包含 code, name, is_generated, is_translatable
    """
    wrapper = _get_wrapper()
    
    try:
        return wrapper.list_available_subtitles(video_id)
    except Exception as e:
        error_msg = str(e).lower()
        
        if 'private' in error_msg or 'unavailable' in error_msg:
            raise VideoNotFoundError(video_id)
        elif 'disabled' in error_msg:
            raise TranscriptDisabledError(video_id)
        else:
            logger.error(f"Failed to list languages for {video_id}: {e}")
            raise


def _to_dict(item) -> Dict[str, Any]:
    """Convert transcript item to dict (handles FetchedTranscriptSnippet objects)"""
    if isinstance(item, dict):
        return item
    # FetchedTranscriptSnippet has .text, .start, .duration attributes
    return {
        "text": getattr(item, 'text', ''),
        "start": getattr(item, 'start', 0),
        "duration": getattr(item, 'duration', 0)
    }


def process_transcript_data(transcript_data: List[Any]) -> Tuple[List[Dict[str, Any]], float]:
    """處理原始字幕資料，回傳處理後的項目列表和總時長"""
    transcript_items = [_to_dict(item) for item in transcript_data]
    
    total_duration = max(
        item['start'] + item['duration'] for item in transcript_items
    ) if transcript_items else 0
    
    return transcript_items, total_duration


def generate_text_output(
    transcript_data: List[Dict[str, Any]], 
    video_url: str, 
    include_chapters: bool
) -> Tuple[str, str, bool]:
    """
    生成文字輸出（純文字或 Markdown）
    
    Returns:
        full_text: 內文
        title: 影片標題 (若 include_chapters=True)
        has_chapters: 是否有章節
    """
    title = None
    has_chapters = False
    
    if include_chapters:
        # 獲取影片資訊（標題和章節）
        video_info = get_video_info(video_url)
        title = video_info.get('title')
        chapters = video_info.get('chapters', [])
        has_chapters = len(chapters) > 0
        
        # 生成 Markdown 格式
        full_text = generate_markdown(
            title=title,
            chapters=chapters,
            transcript=transcript_data
        )
    else:
        # 合併為純文字
        full_text = " ".join(_to_dict(item)['text'] for item in transcript_data)
        
    return full_text, title, has_chapters
