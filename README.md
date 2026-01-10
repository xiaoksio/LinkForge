# LinkForge API

基于 FastAPI 框架的图片和视频直链生成服务,支持多种上传方式和批量处理。

## ✨ 功能特性

- 🖼️ **多格式支持** - 支持常见的图片和视频格式
  - 图片: jpg, jpeg, png, gif, webp, bmp, svg, ico
  - 视频: mp4, avi, mov, mkv, flv, wmv, webm, m4v, mpg, mpeg

- 📤 **多种上传方式**
  - 文件上传 (multipart/form-data)
  - 二进制数据上传 (application/octet-stream)
  - URL 直链上传 (自动下载)
  - 批量上传支持

- ⚡ **高性能**
  - 异步处理
  - 自动文件类型检测
  - 文件大小验证

## 📦 安装部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd LinkForge
```

### 2. 安装依赖

```bash
# 创建虚拟环境 (可选)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并根据需要修改配置:

```bash
cp .env.example .env
```

主要配置项:
- `BASE_URL` - 服务访问基础 URL (部署后的域名或 IP)
- `UPLOAD_DIR` - 文件上传目录
- `MAX_FILE_SIZE` - 最大文件大小限制 (字节)
- `DOWNLOAD_TIMEOUT` - URL 下载超时时间 (秒)

### 4. 启动服务

```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

服务启动后访问:
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

## 📖 API 使用示例

### 1. 文件上传 (multipart/form-data)

```bash
curl -X POST "http://localhost:8000/api/upload/file" \
  -F "file=@/path/to/image.jpg"
```

**响应示例:**
```json
{
  "success": true,
  "message": "文件上传成功",
  "data": {
    "filename": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
    "url": "http://localhost:8000/files/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
    "size": 102400,
    "format": "jpg"
  }
}
```

### 2. 二进制数据上传

```bash
curl -X POST "http://localhost:8000/api/upload/binary" \
  -H "Content-Type: application/octet-stream" \
  -H "filename: image.png" \
  --data-binary "@/path/to/image.png"
```

### 3. URL 直链上传

```bash
curl -X POST "http://localhost:8000/api/upload/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/image.jpg",
    "filename": "custom_name.jpg"
  }'
```

### 4. 批量文件上传

```bash
curl -X POST "http://localhost:8000/api/upload/batch/files" \
  -F "files=@/path/to/image1.jpg" \
  -F "files=@/path/to/image2.png" \
  -F "files=@/path/to/video.mp4"
```

**响应示例:**
```json
{
  "success": true,
  "message": "批量上传完成: 成功 3/3",
  "total": 3,
  "successful": 3,
  "failed": 0,
  "data": [
    {
      "filename": "uuid1.jpg",
      "url": "http://localhost:8000/files/uuid1.jpg",
      "size": 102400,
      "format": "jpg"
    },
    ...
  ],
  "errors": []
}
```

### 5. 批量 URL 上传

```bash
curl -X POST "http://localhost:8000/api/upload/batch/urls" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/image1.jpg",
      "https://example.com/video1.mp4"
    ]
  }'
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `BASE_URL` | 服务访问基础 URL | `http://localhost:8000` |
| `UPLOAD_DIR` | 文件上传目录 | `uploads` |
| `MAX_FILE_SIZE` | 最大文件大小 (字节) | `104857600` (100MB) |
| `DOWNLOAD_TIMEOUT` | URL 下载超时 (秒) | `30` |
| `ALLOWED_IMAGE_FORMATS` | 允许的图片格式 | `jpg,jpeg,png,gif,webp,bmp,svg,ico` |
| `ALLOWED_VIDEO_FORMATS` | 允许的视频格式 | `mp4,avi,mov,mkv,flv,wmv,webm,m4v,mpg,mpeg` |

## 📁 项目结构

```
LinkForge/
├── main.py                 # FastAPI 应用入口
├── config.py               # 配置管理
├── requirements.txt        # 依赖包
├── .env.example           # 环境变量示例
├── models/                # 数据模型
│   └── schemas.py         # Pydantic 模型
├── routers/               # API 路由
│   └── upload.py          # 上传相关路由
├── services/              # 服务层
│   ├── file_service.py    # 文件处理服务
│   ├── download_service.py # URL 下载服务
│   └── storage_service.py # 存储管理服务
├── utils/                 # 工具模块
│   └── validators.py      # 验证工具
└── uploads/               # 文件存储目录 (自动创建)
```

## 🚀 部署建议

### 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建并运行:

```bash
docker build -t linkforge .
docker run -d -p 8000:8000 -v $(pwd)/uploads:/app/uploads linkforge
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 增加上传大小限制
        client_max_body_size 100M;
    }
}
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!
