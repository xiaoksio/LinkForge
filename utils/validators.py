from pathlib import Path
from typing import Optional
from config import ALLOWED_FORMATS, MAX_FILE_SIZE

# 尝试导入 magic 库,如果失败则使用降级方案
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False


def validate_file_extension(filename: str) -> bool:
    """
    验证文件扩展名是否支持
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否支持该格式
    """
    ext = Path(filename).suffix.lower().lstrip(".")
    return ext in ALLOWED_FORMATS


def validate_file_size(size: int) -> bool:
    """
    验证文件大小是否在限制范围内
    
    Args:
        size: 文件大小(字节)
        
    Returns:
        bool: 是否在限制范围内
    """
    return 0 < size <= MAX_FILE_SIZE


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件扩展名(不含点)
    """
    return Path(filename).suffix.lower().lstrip(".")


def detect_mime_type(file_path: Path) -> Optional[str]:
    """
    检测文件的 MIME 类型
    
    Args:
        file_path: 文件路径
        
    Returns:
        Optional[str]: MIME 类型
    """
    if not MAGIC_AVAILABLE:
        return None
    
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(str(file_path))
    except Exception:
        return None


def get_extension_from_mime(mime_type: str) -> Optional[str]:
    """
    从 MIME 类型获取文件扩展名
    
    Args:
        mime_type: MIME 类型
        
    Returns:
        Optional[str]: 文件扩展名
    """
    mime_to_ext = {
        # 图片
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/bmp": "bmp",
        "image/svg+xml": "svg",
        "image/x-icon": "ico",
        # 视频
        "video/mp4": "mp4",
        "video/x-msvideo": "avi",
        "video/quicktime": "mov",
        "video/x-matroska": "mkv",
        "video/x-flv": "flv",
        "video/x-ms-wmv": "wmv",
        "video/webm": "webm",
        "video/mpeg": "mpg",
    }
    return mime_to_ext.get(mime_type)
