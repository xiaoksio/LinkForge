from pathlib import Path
import aiofiles
from config import UPLOAD_DIR


class StorageService:
    """存储管理服务"""
    
    def __init__(self, base_dir: Path = UPLOAD_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, content: bytes, filename: str) -> Path:
        """
        保存文件到存储
        
        Args:
            content: 文件内容
            filename: 文件名
            
        Returns:
            Path: 保存后的文件路径
        """
        file_path = self.base_dir / filename
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        
        return file_path
    
    def get_file_path(self, filename: str) -> Path:
        """
        获取文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            Path: 文件路径
        """
        return self.base_dir / filename
    
    def file_exists(self, filename: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否存在
        """
        return (self.base_dir / filename).exists()


# 创建全局实例
storage_service = StorageService()
