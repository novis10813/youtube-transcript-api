# 播放清單端點 (Playlist Endpoints)

> **狀態**：🔜 規劃中

播放清單相關的 API 端點，用於獲取 YouTube 播放清單資訊和影片列表。

---

## GET /api/v1/playlist/{playlist_id}/videos

獲取播放清單內的影片列表。

### 請求

```bash
# 獲取所有影片
curl "http://localhost:8000/api/v1/playlist/PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf/videos"

# 限制回傳數量
curl "http://localhost:8000/api/v1/playlist/PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf/videos?limit=10"
```

### 請求參數

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `playlist_id` | string | ✅ | - | 播放清單 ID |
| `limit` | integer | ❌ | 50 | 回傳數量上限 |

### 預計回應

```json
{
  "success": true,
  "playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
  "videos": [
    {
      "video_id": "abc123",
      "title": "影片標題",
      "position": 1,
      "channel_id": "UC...",
      "channel_name": "頻道名稱",
      "duration": 600
    }
  ],
  "count": 30
}
```

---

## GET /api/v1/playlist/{playlist_id}/info

獲取播放清單基本資訊。

### 請求

```bash
curl "http://localhost:8000/api/v1/playlist/PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf/info"
```

### 預計回應

```json
{
  "success": true,
  "playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
  "title": "播放清單標題",
  "description": "播放清單描述",
  "channel_id": "UC...",
  "channel_name": "建立者頻道",
  "video_count": 30,
  "thumbnail_url": "https://i.ytimg.com/vi/..."
}
```

---

## 播放清單 ID 格式

播放清單 ID 通常以 `PL` 開頭，例如：
- `PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf`

可從播放清單 URL 獲取：
- `https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf`
- `https://www.youtube.com/watch?v=VIDEO_ID&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf`
