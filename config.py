import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础配置
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 104857600))  # 默认 100MB
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", 30))  # 默认 30 秒

# 支持的文件格式
ALLOWED_IMAGE_FORMATS = set(
    os.getenv("ALLOWED_IMAGE_FORMATS", "jpg,jpeg,png,gif,webp,bmp,svg,ico").split(",")
)
ALLOWED_VIDEO_FORMATS = set(
    os.getenv("ALLOWED_VIDEO_FORMATS", "mp4,avi,mov,mkv,flv,wmv,webm,m4v,mpg,mpeg").split(",")
)
ALLOWED_FORMATS = ALLOWED_IMAGE_FORMATS | ALLOWED_VIDEO_FORMATS

# 确保上传目录存在
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
