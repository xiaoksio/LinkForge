from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field


class FileInfo(BaseModel):
    """文件信息模型"""
    filename: str = Field(..., description="文件名")
    url: str = Field(..., description="直链 URL")
    size: int = Field(..., description="文件大小(字节)")
    format: str = Field(..., description="文件格式")


class UploadResponse(BaseModel):
    """单文件上传响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[FileInfo] = Field(None, description="文件信息")


class UrlUploadRequest(BaseModel):
    """URL 上传请求"""
    url: HttpUrl = Field(..., description="文件 URL")
    filename: Optional[str] = Field(None, description="自定义文件名(可选)")


class BatchUrlUploadRequest(BaseModel):
    """批量 URL 上传请求"""
    urls: List[HttpUrl] = Field(..., description="文件 URL 列表", min_length=1)


class BatchUploadResponse(BaseModel):
    """批量上传响应"""
    success: bool = Field(..., description="是否全部成功")
    message: str = Field(..., description="响应消息")
    total: int = Field(..., description="总数")
    successful: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")
    data: List[FileInfo] = Field(default_factory=list, description="成功上传的文件列表")
    errors: List[dict] = Field(default_factory=list, description="失败的文件及错误信息")
