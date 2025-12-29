# 影片端點 (Video Endpoints)

影片相關的 API 端點，用於獲取 YouTube 影片的字幕和資訊。

## POST /api/v1/transcript

獲取結構化字幕資料。

### 請求

```bash
curl -X POST "http://localhost:8000/api/v1/transcript" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### 請求參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `youtube_url` | string | ✅ | YouTube 影片網址 |
| `language` | string | ❌ | 語言代碼，預設 `zh-Hant` |

### 回應

```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "language": "zh-TW",
  "transcript": [
    {
      "text": "字幕文字",
      "start": 0.1,
      "duration": 1.6
    }
  ],
  "total_items": 100,
  "duration": 600.0
}
```

---

## POST /api/v1/transcript/text

獲取純文字或 Markdown 格式字幕。

### 請求

```bash
# 純文字（預設）
curl -X POST "http://localhost:8000/api/v1/transcript/text" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

# 含章節標題
curl -X POST "http://localhost:8000/api/v1/transcript/text" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID", "include_chapters": true}'
```

### 請求參數

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `youtube_url` | string | ✅ | - | YouTube 影片網址 |
| `language` | string | ❌ | `zh-Hant` | 語言代碼 |
| `include_chapters` | boolean | ❌ | `false` | 是否包含章節標題 |

### 回應

```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "language": "zh-TW",
  "text": "## 章節一\n\n字幕內容...\n\n## 章節二\n\n字幕內容...",
  "title": "影片標題",
  "has_chapters": true
}
```

### include_chapters 說明

| 值 | 輸出格式 |
|----|----------|
| `false` | 純文字字幕 |
| `true` | Markdown 格式，包含 H2 章節標題（如有） |

---

## POST /api/v1/transcript/form

表單方式獲取字幕（適合前端表單提交）。

### 請求

```bash
curl -X POST "http://localhost:8000/api/v1/transcript/form" \
     -F "youtube_url=https://www.youtube.com/watch?v=VIDEO_ID" \
     -F "language=zh-TW"
```

---

## GET /api/v1/transcript/languages/{video_id}

查詢指定影片的可用字幕語言。

### 請求

```bash
curl "http://localhost:8000/api/v1/transcript/languages/VIDEO_ID"
```

### 回應

```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "languages": [
    {
      "code": "zh-TW",
      "name": "Chinese (Taiwan)",
      "is_generated": false,
      "is_translatable": true
    },
    {
      "code": "en",
      "name": "English",
      "is_generated": true,
      "is_translatable": true
    }
  ]
}
```

---

## GET /api/v1/video/{video_id}/info 🔜

> **狀態**：規劃中

獲取影片 metadata。

### 預計回應

```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "title": "影片標題",
  "channel_id": "CHANNEL_ID",
  "channel_name": "頻道名稱",
  "publish_date": "2024-01-01",
  "duration": 600,
  "chapters": [
    {
      "title": "章節一",
      "start_seconds": 0
    }
  ]
}
```

---

## 支援的 URL 格式

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

## 語言代碼

| 代碼 | 語言 |
|------|------|
| `zh-Hant`, `zh-TW` | 繁體中文 |
| `zh-Hans`, `zh-CN` | 簡體中文 |
| `en` | 英文 |
| `ja` | 日文 |
| `ko` | 韓文 |
