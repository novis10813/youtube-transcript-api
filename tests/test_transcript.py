"""
YouTube 字幕 API 測試模組
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import validate_youtube_url, extract_video_id

# 建立測試客戶端
client = TestClient(app)


class TestBasicEndpoints:
    """基本端點測試"""
    
    def test_root_endpoint(self):
        """測試根端點"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "YouTube 字幕 API" in data["message"]
    
    def test_health_check(self):
        """測試健康檢查端點"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_version_endpoint(self):
        """測試版本端點"""
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "version" in data
        assert "api_version" in data


class TestYouTubeURLValidation:
    """YouTube 網址驗證測試"""
    
    def test_valid_youtube_urls(self):
        """測試有效的 YouTube 網址"""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            video_id = validate_youtube_url(url)
            assert video_id == "dQw4w9WgXcQ"
    
    def test_invalid_youtube_urls(self):
        """測試無效的 YouTube 網址"""
        invalid_urls = [
            "https://www.google.com",
            "not_a_url",
            "",
            "https://www.youtube.com/watch",
            "https://vimeo.com/123456789"
        ]
        
        for url in invalid_urls:
            with pytest.raises(Exception):  # 應該拋出 HTTPException
                validate_youtube_url(url)
    
    def test_extract_video_id(self):
        """測試影片 ID 提取功能"""
        test_cases = [
            ("https://www.youtube.com/watch?v=ABC123def45", "ABC123def45"),
            ("https://youtu.be/XYZ789xyz12", "XYZ789xyz12"),
            ("https://www.youtube.com/embed/test_video1", "test_video1"),
        ]
        
        for url, expected_id in test_cases:
            video_id = extract_video_id(url)
            assert video_id == expected_id


class TestTranscriptAPI:
    """字幕 API 測試"""
    
    def test_transcript_endpoint_invalid_url(self):
        """測試字幕端點 - 無效網址"""
        response = client.post(
            "/api/v1/transcript/",
            json={"youtube_url": "invalid_url"}
        )
        assert response.status_code == 400
        data = response.json()
        # Accept both custom error format and FastAPI validation error format
        assert "error" in data or "detail" in data
    
    def test_transcript_text_endpoint_invalid_url(self):
        """測試純文字字幕端點 - 無效網址"""
        response = client.post(
            "/api/v1/transcript/text",
            json={"youtube_url": "invalid_url"}
        )
        assert response.status_code == 400
        data = response.json()
        # Accept both custom error format and FastAPI validation error format
        assert "error" in data or "detail" in data
    
    def test_transcript_form_endpoint_invalid_url(self):
        """測試表單字幕端點 - 無效網址"""
        response = client.post(
            "/api/v1/transcript/form",
            data={"youtube_url": "invalid_url"}
        )
        assert response.status_code == 400
        data = response.json()
        # Accept both custom error format and FastAPI validation error format
        assert "error" in data or "detail" in data
    
    @pytest.mark.skipif(
        True,  # 設為 True 以跳過需要網路連接的測試
        reason="需要網路連接，跳過以避免測試依賴外部服務"
    )
    def test_transcript_endpoint_valid_url(self):
        """測試字幕端點 - 有效網址（需要網路連接）"""
        # 這是一個需要實際網路連接的測試
        # 在實際環境中，您可能需要使用測試專用的影片或模擬 API
        response = client.post(
            "/api/v1/transcript/",
            json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
        )
        # 注意：這個測試可能會失敗，因為該影片可能沒有中文字幕
        # 在真實環境中，您應該使用已知有字幕的測試影片
        print(f"Response: {response.status_code}, {response.json()}")


class TestAvailableLanguagesAPI:
    """可用語言 API 測試"""
    
    def test_available_languages_invalid_video_id(self):
        """測試可用語言端點 - 無效影片 ID"""
        response = client.get("/api/v1/transcript/languages/invalid_id")
        assert response.status_code in [400, 404, 403, 500]
        # 根據不同的錯誤類型，狀態碼可能不同
    
    @pytest.mark.skipif(
        True,  # 設為 True 以跳過需要網路連接的測試
        reason="需要網路連接，跳過以避免測試依賴外部服務"
    )
    def test_available_languages_valid_video_id(self):
        """測試可用語言端點 - 有效影片 ID（需要網路連接）"""
        response = client.get("/api/v1/transcript/languages/dQw4w9WgXcQ")
        # 這個測試同樣需要網路連接
        print(f"Response: {response.status_code}, {response.json()}")


# 執行測試的範例命令：
# uv run pytest tests/test_transcript.py -v
# 或者執行所有測試：
# uv run pytest tests/ -v 