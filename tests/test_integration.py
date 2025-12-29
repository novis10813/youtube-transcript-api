"""
整合測試 - 使用真實 YouTube 資料
這些測試會實際呼叫 YouTube，不使用 mock data
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 測試用的穩定 YouTube 資源 (知名頻道/影片較不會被刪除)
TEST_VIDEO_ID = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
TEST_VIDEO_WITH_CHAPTERS = "aircAruvnKk"  # 3Blue1Brown - Neural Network
TEST_CHANNEL_ID = "UCYO_jab_esuFRV4b17AJtAw"  # 3Blue1Brown
TEST_PLAYLIST_ID = "PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi"  # 3Blue1Brown Essence of Linear Algebra


class TestVideoEndpoints:
    """影片端點整合測試"""
    
    def test_get_video_info(self):
        """測試獲取影片資訊"""
        response = client.get(f"/api/v1/video/{TEST_VIDEO_WITH_CHAPTERS}/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["video_id"] == TEST_VIDEO_WITH_CHAPTERS
        assert "title" in data
        assert data["title"] is not None
        assert "channel_id" in data
        assert "channel_name" in data
        assert "duration" in data
        assert isinstance(data["duration"], int)
        assert data["duration"] > 0
        
    def test_get_video_info_with_chapters(self):
        """測試獲取有章節的影片資訊"""
        response = client.get(f"/api/v1/video/{TEST_VIDEO_WITH_CHAPTERS}/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "chapters" in data
        assert isinstance(data["chapters"], list)
        # 3Blue1Brown 的影片通常有章節
        if len(data["chapters"]) > 0:
            chapter = data["chapters"][0]
            assert "title" in chapter
            assert "start_seconds" in chapter
            
    def test_get_video_info_invalid_id(self):
        """測試無效的影片 ID"""
        response = client.get("/api/v1/video/invalid_video_id_123/info")
        assert response.status_code in [404, 500]  # 可能回傳 404 或 500


class TestChannelEndpoints:
    """頻道端點整合測試"""
    
    def test_get_channel_videos(self):
        """測試獲取頻道影片列表"""
        response = client.get(f"/api/v1/channel/{TEST_CHANNEL_ID}/videos?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["channel_id"] == TEST_CHANNEL_ID
        assert "videos" in data
        assert isinstance(data["videos"], list)
        assert len(data["videos"]) <= 5
        assert data["count"] == len(data["videos"])
        
        if len(data["videos"]) > 0:
            video = data["videos"][0]
            assert "video_id" in video
            assert "title" in video
            assert "publish_date" in video
            assert "duration" in video
            assert "thumbnail_url" in video
            
    def test_get_channel_videos_with_limit(self):
        """測試限制回傳數量"""
        response = client.get(f"/api/v1/channel/{TEST_CHANNEL_ID}/videos?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["videos"]) <= 3
        
    def test_get_channel_info(self):
        """測試獲取頻道資訊"""
        response = client.get(f"/api/v1/channel/{TEST_CHANNEL_ID}/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["channel_id"] == TEST_CHANNEL_ID
        assert "name" in data
        assert data["name"] is not None


class TestPlaylistEndpoints:
    """播放清單端點整合測試"""
    
    def test_get_playlist_videos(self):
        """測試獲取播放清單影片"""
        response = client.get(f"/api/v1/playlist/{TEST_PLAYLIST_ID}/videos?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["playlist_id"] == TEST_PLAYLIST_ID
        assert "videos" in data
        assert isinstance(data["videos"], list)
        assert len(data["videos"]) <= 5
        
        if len(data["videos"]) > 0:
            video = data["videos"][0]
            assert "video_id" in video
            assert "title" in video
            assert "position" in video
            assert video["position"] >= 1
            
    def test_get_playlist_info(self):
        """測試獲取播放清單資訊"""
        response = client.get(f"/api/v1/playlist/{TEST_PLAYLIST_ID}/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["playlist_id"] == TEST_PLAYLIST_ID
        assert "title" in data
        assert data["title"] is not None
        assert "video_count" in data


class TestTranscriptEndpointsIntegration:
    """字幕端點整合測試"""
    
    def test_get_transcript_text(self):
        """測試獲取純文字字幕"""
        response = client.post(
            "/api/v1/transcript/text",
            json={"youtube_url": f"https://www.youtube.com/watch?v={TEST_VIDEO_WITH_CHAPTERS}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["video_id"] == TEST_VIDEO_WITH_CHAPTERS
        assert "text" in data
        assert len(data["text"]) > 0
        assert "language" in data
        
    def test_get_transcript_with_chapters(self):
        """測試獲取含章節的 Markdown 字幕"""
        response = client.post(
            "/api/v1/transcript/text",
            json={
                "youtube_url": f"https://www.youtube.com/watch?v={TEST_VIDEO_WITH_CHAPTERS}",
                "include_chapters": True
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "title" in data
        assert "has_chapters" in data
        # 3Blue1Brown 影片有章節，應該回傳 Markdown
        if data["has_chapters"]:
            assert "##" in data["text"]  # Markdown H2 標題
            
    def test_get_available_languages(self):
        """測試獲取可用語言"""
        response = client.get(f"/api/v1/transcript/languages/{TEST_VIDEO_WITH_CHAPTERS}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "languages" in data
        assert isinstance(data["languages"], list)
        assert len(data["languages"]) > 0
        
        lang = data["languages"][0]
        assert "code" in lang
        assert "name" in lang
        assert "is_generated" in lang


# 執行測試：
# uv run pytest tests/test_integration.py -v
# 
# 注意：這些測試需要網路連接，會實際呼叫 YouTube
# 建議在 CI/CD 中設置為 optional 或 nightly 測試
