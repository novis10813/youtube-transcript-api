# 頻道端點 (Channel Endpoints)

> **狀態**：🔜 規劃中

頻道相關的 API 端點，用於獲取 YouTube 頻道資訊和影片列表。

---

## GET /api/v1/channel/{channel_id}/videos

獲取頻道的影片列表。使用時間篩選而非 offset 分頁，確保結果穩定。

### 請求

```bash
# 獲取最新 20 支影片
curl "http://localhost:8000/api/v1/channel/UC0lbAQVpenvfA2QqzsRtL_g/videos"

# 獲取指定時間後的影片
curl "http://localhost:8000/api/v1/channel/UC0lbAQVpenvfA2QqzsRtL_g/videos?since=2024-12-28T00:00:00Z"

# 限制回傳數量
curl "http://localhost:8000/api/v1/channel/UC0lbAQVpenvfA2QqzsRtL_g/videos?limit=10"
```

### 請求參數

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `channel_id` | string | ✅ | - | 頻道 ID |
| `since` | datetime | ❌ | - | 只回傳此時間之後發佈的影片 (ISO 8601) |
| `limit` | integer | ❌ | 20 | 回傳數量上限 |

### 預計回應

```json
{
  "success": true,
  "channel_id": "UC0lbAQVpenvfA2QqzsRtL_g",
  "videos": [
    {
      "video_id": "abc123",
      "title": "影片標題",
      "publish_date": "2024-12-29T08:00:00Z",
      "duration": 1800,
      "thumbnail_url": "https://i.ytimg.com/vi/abc123/default.jpg"
    }
  ],
  "count": 5
}
```

---

## GET /api/v1/channel/{channel_id}/info

獲取頻道基本資訊。

### 請求

```bash
curl "http://localhost:8000/api/v1/channel/UC0lbAQVpenvfA2QqzsRtL_g/info"
```

### 預計回應

```json
{
  "success": true,
  "channel_id": "UC0lbAQVpenvfA2QqzsRtL_g",
  "name": "頻道名稱",
  "description": "頻道描述",
  "subscriber_count": 100000,
  "video_count": 500,
  "thumbnail_url": "https://yt3.ggpht.com/..."
}
```

---

## 頻道 ID 格式

YouTube 頻道 ID 通常以 `UC` 開頭，例如：
- `UC0lbAQVpenvfA2QqzsRtL_g`
- `UCBcRF18a7Qf58cCRy5xuWwQ`

可從頻道頁面 URL 獲取：
- `https://www.youtube.com/channel/UC0lbAQVpenvfA2QqzsRtL_g`
