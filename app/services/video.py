"""YouTube 影片資訊服務

使用 pytubefix 獲取 YouTube 影片的標題和章節資訊。
"""

from pytubefix import YouTube
from typing import Optional
import re


def extract_video_id(url: str) -> str:
    """從各種 YouTube URL 格式中提取影片 ID"""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:live/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError(f"無法從 URL 中提取影片 ID: {url}")


def get_video_info(url: str) -> dict:
    """
    獲取影片標題和章節資訊
    
    Args:
        url: YouTube 影片網址
        
    Returns:
        dict: 包含 'title' 和 'chapters' 的字典
              chapters 為章節列表，每個章節包含 'title' 和 'start_seconds'
    """
    try:
        yt = YouTube(url)
        
        chapters = []
        if yt.chapters:
            for chapter in yt.chapters:
                chapters.append({
                    'title': chapter.title,
                    'start_seconds': chapter.start_seconds,
                })
        
        return {
            'title': yt.title,
            'chapters': chapters,
        }
    except Exception as e:
        # 如果無法獲取影片資訊，返回空的資訊
        return {
            'title': None,
            'chapters': [],
        }


def assign_transcript_to_chapters(
    transcript: list[dict], 
    chapters: list[dict]
) -> dict[str, list[dict]]:
    """
    將字幕分配到對應的章節
    
    Args:
        transcript: 字幕列表，每個項目包含 'text', 'start', 'duration'
        chapters: 章節列表，每個項目包含 'title' 和 'start_seconds'
        
    Returns:
        dict: 以章節標題為 key，字幕列表為 value 的字典
              如果沒有章節，返回 {'': transcript}
    """
    if not chapters:
        return {'': transcript}
    
    # 按開始時間排序章節
    sorted_chapters = sorted(chapters, key=lambda x: x['start_seconds'])
    
    result = {chapter['title']: [] for chapter in sorted_chapters}
    
    for snippet in transcript:
        snippet_start = snippet['start']
        
        # 找出這個字幕段落屬於哪個章節
        chapter_title = sorted_chapters[0]['title']
        for chapter in sorted_chapters:
            if snippet_start >= chapter['start_seconds']:
                chapter_title = chapter['title']
            else:
                break
        
        result[chapter_title].append(snippet)
    
    return result


def generate_markdown(
    title: Optional[str],
    chapters: list[dict],
    transcript: list[dict]
) -> str:
    """
    從影片資訊和字幕生成 Markdown 內容
    
    Args:
        title: 影片標題（目前未使用，標題已在 response 欄位中返回）
        chapters: 章節列表
        transcript: 字幕列表
        
    Returns:
        str: Markdown 格式的字幕內容（只包含 H2 章節標題，不含 H1 影片標題）
    """
    lines = []
    
    if chapters:
        # 依章節組織字幕
        chapter_transcripts = assign_transcript_to_chapters(transcript, chapters)
        
        # 按開始時間排序章節輸出
        sorted_chapters = sorted(chapters, key=lambda x: x['start_seconds'])
        
        for chapter in sorted_chapters:
            chapter_title = chapter['title']
            chapter_snippets = chapter_transcripts.get(chapter_title, [])
            
            if chapter_snippets:
                # H2: 章節標題
                lines.append(f"## {chapter_title}")
                lines.append("")
                
                # 合併字幕文字
                text_parts = [snippet['text'] for snippet in chapter_snippets]
                combined_text = ' '.join(text_parts)
                lines.append(combined_text)
                lines.append("")
    else:
        # 沒有章節，輸出所有字幕文字
        text_parts = [snippet['text'] for snippet in transcript]
        combined_text = ' '.join(text_parts)
        lines.append(combined_text)
        lines.append("")
    
    return '\n'.join(lines)
