from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from models.schemas import (
    UploadResponse,
    BatchUploadResponse,
    UrlUploadRequest,
    BatchUrlUploadRequest,
    FileInfo
)
from services.file_service import file_service

router = APIRouter(prefix="/api/upload", tags=["上传"])


@router.post("/file", response_model=UploadResponse, summary="单文件上传")
async def upload_file(file: UploadFile = File(..., description="要上传的文件")):
    """
    上传单个文件 (multipart/form-data)
    
    支持的图片格式: jpg, jpeg, png, gif, webp, bmp, svg, ico
    支持的视频格式: mp4, avi, mov, mkv, flv, wmv, webm, m4v, mpg, mpeg
    """
    try:
        file_info = await file_service.save_upload_file(file)
        return UploadResponse(
            success=True,
            message="文件上传成功",
            data=file_info
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/binary", response_model=UploadResponse, summary="二进制数据上传")
async def upload_binary(
    request: Request,
    content_type: Optional[str] = Header(None),
    filename: Optional[str] = Header(None, description="原始文件名")
):
    """
    上传二进制数据 (application/octet-stream)
    
    请求头:
    - Content-Type: application/octet-stream
    - filename: 原始文件名(可选,用于确定文件格式)
    
    请求体: 二进制文件内容
    """
    try:
        content = await request.body()
        
        if not content:
            raise HTTPException(status_code=400, detail="请求体为空")
        
        file_info = await file_service.save_binary_data(
            content=content,
            original_filename=filename,
            content_type=content_type
        )
        
        return UploadResponse(
            success=True,
            message="二进制数据上传成功",
            data=file_info
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/url", response_model=UploadResponse, summary="URL 直链上传")
async def upload_from_url(request: UrlUploadRequest):
    """
    从 URL 下载文件并保存
    
    请求体:
    ```json
    {
        "url": "https://example.com/image.jpg",
        "filename": "custom_name.jpg"  // 可选
    }
    ```
    """
    try:
        file_info = await file_service.save_from_url(
            url=str(request.url),
            custom_filename=request.filename
        )
        
        return UploadResponse(
            success=True,
            message="URL 文件上传成功",
            data=file_info
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/batch/files", response_model=BatchUploadResponse, summary="批量文件上传")
async def batch_upload_files(files: List[UploadFile] = File(..., description="要上传的文件列表")):
    """
    批量上传文件 (multipart/form-data)
    
    支持同时上传多个文件
    """
    if not files:
        raise HTTPException(status_code=400, detail="未提供文件")
    
    results = []
    errors = []
    
    for idx, file in enumerate(files):
        try:
            file_info = await file_service.save_upload_file(file)
            results.append(file_info)
        except Exception as e:
            errors.append({
                "index": idx,
                "filename": file.filename,
                "error": str(e)
            })
    
    total = len(files)
    successful = len(results)
    failed = len(errors)
    
    return BatchUploadResponse(
        success=failed == 0,
        message=f"批量上传完成: 成功 {successful}/{total}",
        total=total,
        successful=successful,
        failed=failed,
        data=results,
        errors=errors
    )


@router.post("/batch/urls", response_model=BatchUploadResponse, summary="批量 URL 上传")
async def batch_upload_from_urls(request: BatchUrlUploadRequest):
    """
    从多个 URL 下载文件并保存
    
    请求体:
    ```json
    {
        "urls": [
            "https://example.com/image1.jpg",
            "https://example.com/video1.mp4"
        ]
    }
    ```
    """
    if not request.urls:
        raise HTTPException(status_code=400, detail="未提供 URL")
    
    results = []
    errors = []
    
    for idx, url in enumerate(request.urls):
        try:
            file_info = await file_service.save_from_url(str(url))
            results.append(file_info)
        except Exception as e:
            errors.append({
                "index": idx,
                "url": str(url),
                "error": str(e)
            })
    
    total = len(request.urls)
    successful = len(results)
    failed = len(errors)
    
    return BatchUploadResponse(
        success=failed == 0,
        message=f"批量 URL 上传完成: 成功 {successful}/{total}",
        total=total,
        successful=successful,
        failed=failed,
        data=results,
        errors=errors
    )
