import uuid
from pathlib import Path
from typing import Union, Optional
from fastapi import UploadFile
import aiofiles
from config import BASE_URL
from models.schemas import FileInfo
from services.storage_service import storage_service
from services.download_service import download_service
from utils.validators import (
    validate_file_extension,
    validate_file_size,
    get_file_extension,
    detect_mime_type,
    get_extension_from_mime
)


class FileService:
    """文件处理服务"""
    
    @staticmethod
    def generate_filename(extension: str) -> str:
        """
        生成唯一文件名
        
        Args:
            extension: 文件扩展名
            
        Returns:
            str: 唯一文件名
        """
        return f"{uuid.uuid4()}.{extension}"
    
    @staticmethod
    def generate_direct_link(filename: str) -> str:
        """
        生成直链 URL
        
        Args:
            filename: 文件名
            
        Returns:
            str: 直链 URL
        """
        return f"{BASE_URL}/files/{filename}"
    
    async def save_upload_file(self, file: UploadFile) -> FileInfo:
        """
        保存上传的文件
        
        Args:
            file: 上传的文件对象
            
        Returns:
            FileInfo: 文件信息
            
        Raises:
            ValueError: 文件验证失败
        """
        # 验证文件扩展名
        if not validate_file_extension(file.filename):
            raise ValueError(f"不支持的文件格式: {file.filename}")
        
        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        
        # 验证文件大小
        if not validate_file_size(file_size):
            raise ValueError(f"文件过大: {file_size} 字节")
        
        # 生成文件名并保存
        extension = get_file_extension(file.filename)
        filename = self.generate_filename(extension)
        
        await storage_service.save_file(content, filename)
        
        return FileInfo(
            filename=filename,
            url=self.generate_direct_link(filename),
            size=file_size,
            format=extension
        )
    
    async def save_binary_data(
        self,
        content: bytes,
        original_filename: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> FileInfo:
        """
        保存二进制数据
        
        Args:
            content: 二进制内容
            original_filename: 原始文件名(可选)
            content_type: 内容类型(可选)
            
        Returns:
            FileInfo: 文件信息
            
        Raises:
            ValueError: 文件验证失败
        """
        file_size = len(content)
        
        # 验证文件大小
        if not validate_file_size(file_size):
            raise ValueError(f"文件过大: {file_size} 字节")
        
        # 确定文件扩展名
        extension = None
        
        # 1. 尝试从原始文件名获取
        if original_filename:
            ext = get_file_extension(original_filename)
            if validate_file_extension(original_filename):
                extension = ext
        
        # 2. 尝试从 Content-Type 获取
        if not extension and content_type:
            extension = get_extension_from_mime(content_type)
        
        # 3. 保存临时文件并检测 MIME 类型
        if not extension:
            temp_filename = f"temp_{uuid.uuid4()}"
            temp_path = await storage_service.save_file(content, temp_filename)
            mime_type = detect_mime_type(temp_path)
            
            if mime_type:
                extension = get_extension_from_mime(mime_type)
            
            # 删除临时文件
            temp_path.unlink(missing_ok=True)
        
        if not extension:
            raise ValueError("无法确定文件格式")
        
        if extension not in validate_file_extension(f"dummy.{extension}"):
            raise ValueError(f"不支持的文件格式: {extension}")
        
        # 生成文件名并保存
        filename = self.generate_filename(extension)
        await storage_service.save_file(content, filename)
        
        return FileInfo(
            filename=filename,
            url=self.generate_direct_link(filename),
            size=file_size,
            format=extension
        )
    
    async def save_from_url(self, url: str, custom_filename: Optional[str] = None) -> FileInfo:
        """
        从 URL 下载并保存文件
        
        Args:
            url: 文件 URL
            custom_filename: 自定义文件名(可选)
            
        Returns:
            FileInfo: 文件信息
            
        Raises:
            ValueError: 下载或验证失败
        """
        # 下载文件
        content, extension = await download_service.download_from_url(url)
        
        # 如果提供了自定义文件名,使用其扩展名
        if custom_filename:
            custom_ext = get_file_extension(custom_filename)
            if validate_file_extension(custom_filename):
                extension = custom_ext
        
        # 如果仍然没有扩展名,尝试检测
        if not extension:
            temp_filename = f"temp_{uuid.uuid4()}"
            temp_path = await storage_service.save_file(content, temp_filename)
            mime_type = detect_mime_type(temp_path)
            
            if mime_type:
                extension = get_extension_from_mime(mime_type)
            
            temp_path.unlink(missing_ok=True)
        
        if not extension:
            raise ValueError(f"无法确定文件格式: {url}")
        
        if not validate_file_extension(f"dummy.{extension}"):
            raise ValueError(f"不支持的文件格式: {extension}")
        
        # 生成文件名并保存
        filename = self.generate_filename(extension)
        file_size = len(content)
        
        await storage_service.save_file(content, filename)
        
        return FileInfo(
            filename=filename,
            url=self.generate_direct_link(filename),
            size=file_size,
            format=extension
        )


# 创建全局实例
file_service = FileService()
