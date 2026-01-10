from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from routers import upload
from config import UPLOAD_DIR

# 创建 FastAPI 应用
app = FastAPI(
    title="LinkForge API",
    description="图片和视频直链生成 API - 支持文件上传、二进制上传、URL 上传和批量处理",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router)

# 挂载静态文件服务 (用于直链访问)
app.mount("/files", StaticFiles(directory=str(UPLOAD_DIR)), name="files")


@app.get("/", tags=["根路径"])
async def root():
    """API 根路径"""
    return {
        "name": "LinkForge API",
        "version": "1.0.0",
        "description": "图片和视频直链生成服务",
        "docs": "/docs",
        "features": [
            "文件上传 (multipart/form-data)",
            "二进制数据上传 (application/octet-stream)",
            "URL 直链上传",
            "批量上传支持"
        ]
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
