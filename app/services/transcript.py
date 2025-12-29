"""字幕服務模組"""

from typing import List, Tuple, Any, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)
from ..exceptions import (
    TranscriptNotFoundError,
    TranscriptDisabledError,
    VideoNotFoundError
)
from .video import get_video_info, generate_markdown

# Create API instance for the new API style
_api = YouTubeTranscriptApi()

def get_transcript_with_fallback(video_id: str, preferred_language: str, fallback_languages: List[str]) -> Tuple[List[Dict[str, Any]], str]:
    """
    嘗試獲取字幕，包含語言回退機制
    """
    languages_to_try = [preferred_language] + fallback_languages
    
    try:
        transcript_list = _api.list(video_id)
        # Convert to list first to avoid iterator exhaustion
        available_transcripts = list(transcript_list)
        
        # Try preferred languages first
        for language in languages_to_try:
            for transcript in available_transcripts:
                if transcript.language_code == language:
                    return transcript.fetch(), language
        
        # If none of the preferred languages found, use the first available
        if available_transcripts:
            first_transcript = available_transcripts[0]
            return first_transcript.fetch(), first_transcript.language_code
            
    except TranscriptsDisabled:
        raise TranscriptDisabledError(video_id)
    except VideoUnavailable:
        raise VideoNotFoundError(video_id)
    except Exception:
        pass
    
    raise TranscriptNotFoundError(video_id, preferred_language)


def get_available_languages(video_id: str) -> List[Dict[str, Any]]:
    """獲取可用語言"""
    try:
        transcript_list = _api.list(video_id)
        
        languages = []
        for transcript in transcript_list:
            languages.append({
                "code": transcript.language_code,
                "name": transcript.language,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable
            })
        return languages
    except TranscriptsDisabled:
        raise TranscriptDisabledError(video_id)
    except VideoUnavailable:
        raise VideoNotFoundError(video_id)
    except Exception as e:
        raise e


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
