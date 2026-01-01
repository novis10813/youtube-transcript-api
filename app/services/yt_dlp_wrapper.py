"""yt-dlp 封裝模組

提供 YouTube 字幕獲取功能，替代 youtube-transcript-api。
yt-dlp 內建模擬瀏覽器行為，較不易被 YouTube 封鎖。
"""

import yt_dlp
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class YtDlpWrapper:
    """yt-dlp 封裝類別"""
    
    def __init__(self, proxy: Optional[str] = None, cookies_from_browser: Optional[str] = None):
        """
        初始化 yt-dlp 封裝
        
        Args:
            proxy: 可選的代理伺服器 (e.g., "http://proxy:8080")
            cookies_from_browser: 可選的瀏覽器名稱 (e.g., "chrome", "firefox")
        """
        self.proxy = proxy
        self.cookies_from_browser = cookies_from_browser
    
    def _get_base_opts(self) -> dict:
        """獲取基礎 yt-dlp 選項"""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        if self.proxy:
            opts['proxy'] = self.proxy
            
        if self.cookies_from_browser:
            opts['cookiesfrombrowser'] = (self.cookies_from_browser,)
            
        return opts
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        獲取影片資訊（包含可用字幕列表）
        
        Args:
            video_id: YouTube 影片 ID
            
        Returns:
            yt-dlp 的 info_dict
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        opts = self._get_base_opts()
        opts.update({
            'skip_download': True,
        })
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    
    def list_available_subtitles(self, video_id: str) -> List[Dict[str, Any]]:
        """
        列出可用的字幕語言
        
        Args:
            video_id: YouTube 影片 ID
            
        Returns:
            語言列表，每個包含 code, name, is_generated, is_translatable
        """
        info = self.get_video_info(video_id)
        
        languages = []
        
        # 手動上傳的字幕
        subtitles = info.get('subtitles', {})
        for lang_code, sub_list in subtitles.items():
            languages.append({
                'code': lang_code,
                'name': lang_code,  # yt-dlp 不直接提供語言名稱
                'is_generated': False,
                'is_translatable': True
            })
        
        # 自動產生的字幕
        automatic_captions = info.get('automatic_captions', {})
        for lang_code, sub_list in automatic_captions.items():
            # 避免重複
            if not any(l['code'] == lang_code for l in languages):
                languages.append({
                    'code': lang_code,
                    'name': lang_code,
                    'is_generated': True,
                    'is_translatable': True
                })
        
        return languages
    
    def get_subtitles(
        self, 
        video_id: str, 
        preferred_language: str,
        fallback_languages: List[str]
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        獲取字幕內容
        
        Args:
            video_id: YouTube 影片 ID
            preferred_language: 偏好語言代碼
            fallback_languages: 回退語言代碼列表
            
        Returns:
            (字幕列表, 實際使用的語言代碼)
            字幕列表格式: [{"text": str, "start": float, "duration": float}, ...]
        """
        info = self.get_video_info(video_id)
        
        languages_to_try = [preferred_language] + fallback_languages
        
        # 先嘗試手動上傳的字幕
        subtitles = info.get('subtitles', {})
        automatic_captions = info.get('automatic_captions', {})
        
        # 找到匹配的字幕
        selected_sub = None
        selected_lang = None
        is_auto = False
        
        for lang in languages_to_try:
            if lang in subtitles:
                selected_sub = subtitles[lang]
                selected_lang = lang
                break
            elif lang in automatic_captions:
                selected_sub = automatic_captions[lang]
                selected_lang = lang
                is_auto = True
                break
        
        # 如果沒有匹配，使用第一個可用的
        if selected_sub is None:
            if subtitles:
                selected_lang = list(subtitles.keys())[0]
                selected_sub = subtitles[selected_lang]
            elif automatic_captions:
                selected_lang = list(automatic_captions.keys())[0]
                selected_sub = automatic_captions[selected_lang]
                is_auto = True
            else:
                raise ValueError(f"No subtitles available for video {video_id}")
        
        # 下載字幕內容
        transcript_items = self._download_subtitle(video_id, selected_lang, is_auto)
        
        return transcript_items, selected_lang
    
    def _download_subtitle(
        self, 
        video_id: str, 
        lang_code: str, 
        is_auto: bool = False
    ) -> List[Dict[str, Any]]:
        """
        下載並解析字幕
        
        Args:
            video_id: YouTube 影片 ID
            lang_code: 語言代碼
            is_auto: 是否為自動產生的字幕
            
        Returns:
            字幕列表 [{"text": str, "start": float, "duration": float}, ...]
        """
        import tempfile
        import os
        import json
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            opts = self._get_base_opts()
            opts.update({
                'skip_download': True,
                'writesubtitles': not is_auto,
                'writeautomaticsub': is_auto,
                'subtitleslangs': [lang_code],
                'subtitlesformat': 'json3',
                'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
            })
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            
            # 讀取字幕檔案
            subtitle_file = os.path.join(tmpdir, f"{video_id}.{lang_code}.json3")
            
            if not os.path.exists(subtitle_file):
                # 有時候檔名格式不同，嘗試找到任何 json3 檔案
                for f in os.listdir(tmpdir):
                    if f.endswith('.json3'):
                        subtitle_file = os.path.join(tmpdir, f)
                        break
            
            if not os.path.exists(subtitle_file):
                raise ValueError(f"Failed to download subtitle for {video_id}")
            
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                json3_data = json.load(f)
            
            return self._parse_json3(json3_data)
    
    def _parse_json3(self, json3_data: dict) -> List[Dict[str, Any]]:
        """
        解析 json3 格式字幕
        
        Args:
            json3_data: yt-dlp 下載的 json3 格式資料
            
        Returns:
            標準化的字幕列表 [{"text": str, "start": float, "duration": float}, ...]
        """
        events = json3_data.get('events', [])
        items = []
        
        for event in events:
            # 跳過沒有文字的事件（例如空格、格式標記）
            segs = event.get('segs', [])
            if not segs:
                continue
            
            # 合併所有段落的文字
            text = ''.join(seg.get('utf8', '') for seg in segs).strip()
            if not text:
                continue
            
            # 時間單位轉換 (毫秒 -> 秒)
            start_ms = event.get('tStartMs', 0)
            duration_ms = event.get('dDurationMs', 0)
            
            items.append({
                'text': text,
                'start': start_ms / 1000.0,
                'duration': duration_ms / 1000.0
            })
        
        return items


# 模組級別的預設實例
_default_wrapper: Optional[YtDlpWrapper] = None


def get_wrapper() -> YtDlpWrapper:
    """獲取預設的 YtDlpWrapper 實例"""
    global _default_wrapper
    if _default_wrapper is None:
        _default_wrapper = YtDlpWrapper()
    return _default_wrapper
