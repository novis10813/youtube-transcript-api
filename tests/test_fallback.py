"""
Fallback 機制單元測試
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.transcript import get_transcript_with_fallback
from app.exceptions import TranscriptNotFoundError

@pytest.mark.asyncio
async def test_fallback_success():
    """測試 yt-dlp 失敗但 fallback 成功的情況"""
    
    # 模擬資料
    video_id = "test_video"
    preferred_lang = "zh-Hant"
    fallback_langs = ["en"]
    
    expected_transcript = [
        {"text": "測試字幕", "start": 0.0, "duration": 1.0}
    ]
    
    # Mock 所有依賴
    with patch('app.services.transcript._get_wrapper') as mock_get_wrapper, \
         patch('app.services.transcript.transcribe_video', new_callable=AsyncMock) as mock_transcribe, \
         patch('app.services.transcript.settings') as mock_settings:
        
        # 1. 設定 yt-dlp 失敗
        mock_wrapper = MagicMock()
        mock_wrapper.get_subtitles.side_effect = Exception("Sign in to confirm your age")
        mock_get_wrapper.return_value = mock_wrapper
        
        # 2. 設定 fallback 啟用
        mock_settings.transcribe_api_url = "http://fake-url"
        
        # 3. 設定 fallback 成功回傳
        mock_transcribe.return_value = expected_transcript
        
        # 執行
        result, lang = await get_transcript_with_fallback(video_id, preferred_lang, fallback_langs)
        
        # 驗證
        assert result == expected_transcript
        assert lang == preferred_lang
        
        # 確認有呼叫 fallback
        mock_transcribe.assert_awaited_once_with(video_id, preferred_lang)

@pytest.mark.asyncio
async def test_fallback_disabled():
    """測試 fallback 未啟用時應直接拋出錯誤"""
    
    # Mock 所有依賴
    with patch('app.services.transcript._get_wrapper') as mock_get_wrapper, \
         patch('app.services.transcript.transcribe_video', new_callable=AsyncMock) as mock_transcribe, \
         patch('app.services.transcript.settings') as mock_settings:
        
        # 1. 設定 yt-dlp 失敗
        mock_wrapper = MagicMock()
        mock_wrapper.get_subtitles.side_effect = Exception("Sign in to confirm your age")
        mock_get_wrapper.return_value = mock_wrapper
        
        # 2. 設定 fallback 停用
        mock_settings.transcribe_api_url = None
        
        # 執行 & 驗證
        with pytest.raises(TranscriptNotFoundError):
            await get_transcript_with_fallback("test", "zh-Hant", [])
        
        # 確認沒有呼叫 fallback
        mock_transcribe.assert_not_awaited()

@pytest.mark.asyncio
async def test_fallback_failure():
    """測試 fallback 也失敗時的情形"""
    
    with patch('app.services.transcript._get_wrapper') as mock_get_wrapper, \
         patch('app.services.transcript.transcribe_video', new_callable=AsyncMock) as mock_transcribe, \
         patch('app.services.transcript.settings') as mock_settings:
        
        # 1. yt-dlp 失敗
        mock_wrapper = MagicMock()
        mock_wrapper.get_subtitles.side_effect = Exception("Sign in to confirm your age")
        mock_get_wrapper.return_value = mock_wrapper
        
        # 2. fallback 啟用
        mock_settings.transcribe_api_url = "http://fake-url"
        
        # 3. fallback 也失敗
        mock_transcribe.side_effect = Exception("Whisper failed")
        
        # 執行 & 驗證 (應該拋出含有 yt-dlp 錯誤資訊的異常，或被轉為標準異常)
        # 目前邏輯是 log fallback 錯誤後拋出原始錯誤，所以會變成 TranscriptNotFoundError
        with pytest.raises(TranscriptNotFoundError):
            await get_transcript_with_fallback("test", "zh-Hant", [])
        
        mock_transcribe.assert_awaited_once()
