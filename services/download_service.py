from pathlib import Path
from typing import Optional
import httpx
from config import DOWNLOAD_TIMEOUT, MAX_FILE_SIZE
from utils.validators import get_extension_from_mime


class DownloadService:
    """URL 下载服务"""
    
    def __init__(self):
        self.timeout = DOWNLOAD_TIMEOUT
        self.max_size = MAX_FILE_SIZE
    
    async def download_from_url(self, url: str) -> tuple[bytes, Optional[str]]:
        """
        从 URL 下载文件
        
        Args:
            url: 文件 URL
            
        Returns:
            tuple[bytes, Optional[str]]: (文件内容, 文件扩展名)
            
        Raises:
            ValueError: 下载失败或文件过大
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                # 先发送 HEAD 请求检查文件大小
                head_response = await client.head(url)
                content_length = head_response.headers.get("content-length")
                
                if content_length and int(content_length) > self.max_size:
                    raise ValueError(f"文件过大: {int(content_length)} 字节 (最大: {self.max_size} 字节)")
                
                # 下载文件
                response = await client.get(url)
                response.raise_for_status()
                
                content = response.content
                
                # 检查实际下载大小
                if len(content) > self.max_size:
                    raise ValueError(f"文件过大: {len(content)} 字节 (最大: {self.max_size} 字节)")
                
                # 尝试从 Content-Type 获取文件扩展名
                content_type = response.headers.get("content-type", "").split(";")[0].strip()
                extension = get_extension_from_mime(content_type)
                
                # 如果无法从 MIME 获取,尝试从 URL 获取
                if not extension:
                    url_path = Path(url.split("?")[0])  # 移除查询参数
                    if url_path.suffix:
                        extension = url_path.suffix.lstrip(".")
                
                return content, extension
                
        except httpx.TimeoutException:
            raise ValueError(f"下载超时: {url}")
        except httpx.HTTPStatusError as e:
            raise ValueError(f"HTTP 错误 {e.response.status_code}: {url}")
        except Exception as e:
            raise ValueError(f"下载失败: {str(e)}")


# 创建全局实例
download_service = DownloadService()
