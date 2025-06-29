# YouTube 字幕 API 服務

## 專案簡介

這是一個基於 FastAPI 建立的 API 服務，用於獲取 YouTube 影片的繁體中文字幕。使用者可以透過 API endpoint 傳送 YouTube 影片網址，系統會自動提取該影片的繁體中文字幕並回傳。

## 使用套件

- **FastAPI**: 現代、快速的 Python Web 框架，用於建立 API 服務
- **youtube_transcript_api**: 用於獲取 YouTube 影片字幕的 Python 套件

## 功能說明

1. **接收 YouTube 影片網址**: 透過 FastAPI endpoint 監聽使用者傳送的 YouTube 影片網址
2. **提取繁體中文字幕**: 使用 youtube_transcript_api 自動獲取影片的繁體中文字幕
3. **回傳字幕內容**: 將提取到的字幕內容透過 API 回傳給使用者

## 安裝說明

```bash
# 使用 uv 安裝相依套件
uv sync

# 或者僅安裝生產環境依賴
uv sync --no-dev
```

## 使用方法

```bash
# 啟動 API 服務
uv run uvicorn app.main:app --reload

# 或者激活虛擬環境後執行
uv run fastapi run app/main.py --reload
```

## API 端點

- **POST /transcript**: 傳送 YouTube 影片網址，獲取繁體中文字幕

## 專案檔案結構

根據 FastAPI 最佳實務，本專案採用以下檔案結構：

```
YTtranscript/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用程式入口
│   ├── config.py            # 應用程式配置
│   ├── dependencies.py      # 共用依賴項
│   ├── exceptions.py        # 自定義例外處理
│   └── routers/
│       ├── __init__.py
│       └── transcript.py    # 字幕相關 API 路由
├── tests/
│   ├── __init__.py
│   └── test_transcript.py   # 測試檔案
├── pyproject.toml           # 專案配置和 Python 套件依賴
├── .env.example            # 環境變數範例檔
├── .gitignore              # Git 忽略檔案設定
├── Dockerfile              # Docker 容器化設定（可選）
└── README.md               # 專案說明文件
```

### 檔案結構說明

- **`app/`**: 主要應用程式包，包含所有業務邏輯
  - **`main.py`**: FastAPI 應用程式的入口點，註冊路由和中介軟體
  - **`config.py`**: 應用程式配置，包含環境變數和設定
  - **`dependencies.py`**: 可重用的依賴項注入函數
  - **`exceptions.py`**: 自定義例外類別和錯誤處理
  - **`routers/`**: API 路由子包
    - **`transcript.py`**: 處理 YouTube 字幕相關的 API 端點

- **`tests/`**: 測試檔案目錄，與 `app/` 結構對應

- **`pyproject.toml`**: 專案配置檔案，包含所有必要的 Python 套件及版本、開發工具設定

- **`.env.example`**: 環境變數範例，說明需要設定的環境變數

- **`Dockerfile`**: 用於建立 Docker 映像檔（適合部署使用）

這種結構的優點：
1. **模組化**: 清楚分離不同功能模組
2. **可擴展**: 容易新增新的路由或功能
3. **易維護**: 程式碼組織清晰，便於維護
4. **符合標準**: 遵循 FastAPI 官方建議的專案結構
5. **測試友善**: 測試檔案結構清楚，易於編寫和執行測試

## API 使用指南

### 🚀 基本端點

#### 1. 系統資訊
```bash
# 獲取 API 基本資訊
curl -X GET "http://localhost:7999/"

# 健康檢查
curl -X GET "http://localhost:7999/health"

# 版本資訊
curl -X GET "http://localhost:7999/version"
```

### 📝 字幕 API 端點

#### 1. 獲取完整字幕 (JSON 格式)
```bash
# 基本使用
curl -X POST "http://localhost:7999/api/v1/transcript/" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

# 指定語言
curl -X POST "http://localhost:7999/api/v1/transcript/" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID", "language": "zh-TW"}'
```

**回應範例：**
```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "language": "zh-TW",
  "transcript": [
    {
      "text": "投資朋友歡迎收看市場觀察",
      "start": 0.1,
      "duration": 1.6
    },
    {
      "text": "最近新台幣對美元",
      "start": 1.7,
      "duration": 1.166
    }
  ],
  "total_items": 910,
  "duration": 1649.466
}
```

#### 2. 獲取純文字字幕
```bash
curl -X POST "http://localhost:7999/api/v1/transcript/text" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID", "language": "zh-TW"}'
```

**回應範例：**
```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "language": "zh-TW",
  "text": "投資朋友歡迎收看市場觀察 最近新台幣對美元 單日升值幅度高達3% ..."
}
```

#### 3. 表單方式獲取字幕
```bash
curl -X POST "http://localhost:7999/api/v1/transcript/form" \
     -F "youtube_url=https://www.youtube.com/watch?v=VIDEO_ID" \
     -F "language=zh-TW"
```

#### 4. 查看可用字幕語言
```bash
curl -X GET "http://localhost:7999/api/v1/transcript/languages/VIDEO_ID"
```

**回應範例：**
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

### 🌐 支援的 YouTube 網址格式

API 支援以下 YouTube 網址格式：
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

### 🌍 語言代碼

常用語言代碼：
- `zh-Hant` 或 `zh-TW`：繁體中文
- `zh-Hans` 或 `zh-CN`：簡體中文
- `en`：英文
- `ja`：日文
- `ko`：韓文

### ❌ 錯誤處理

當發生錯誤時，API 會回傳以下格式：
```json
{
  "error": true,
  "message": "錯誤描述",
  "type": "錯誤類型",
  "status_code": 400
}
```

常見錯誤：
- **400 Bad Request**：無效的 YouTube 網址
- **403 Forbidden**：影片字幕功能已停用
- **404 Not Found**：找不到指定語言的字幕或影片不存在
- **500 Internal Server Error**：伺服器內部錯誤

### 📚 互動式 API 文檔

啟動服務後，您可以訪問以下網址查看完整的 API 文檔：

- **Swagger UI**：http://localhost:7999/docs
- **ReDoc**：http://localhost:7999/redoc

## 實際測試範例

以下是使用真實 YouTube 影片的測試範例：

```bash
# 測試影片：https://www.youtube.com/watch?v=kBCkijV4oKE
# 1. 查看可用語言
curl -s "http://localhost:7999/api/v1/transcript/languages/kBCkijV4oKE" | jq .

# 2. 獲取繁體中文字幕
curl -s -X POST "http://localhost:7999/api/v1/transcript/" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=kBCkijV4oKE", "language": "zh-TW"}' | jq .

# 3. 獲取純文字格式
curl -s -X POST "http://localhost:7999/api/v1/transcript/text" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=kBCkijV4oKE", "language": "zh-TW"}' | jq .
```

## 注意事項

- 僅支援有字幕的 YouTube 影片
- 優先獲取繁體中文字幕，支援語言回退機制
- 需要確保影片的字幕是公開可存取的
- API 會自動驗證 YouTube 網址格式
