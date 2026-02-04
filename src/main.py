"""
FastAPI Application Entry Point

메인 애플리케이션 및 라우터 등록
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from .config import settings
from .routers import blog, hrjang, hskmap, lawchaser, rara


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 수명주기 관리"""
    # Startup
    print(f"🚀 Starting {settings.app_name}...")

    # 미디어/정적 파일 디렉토리 생성
    os.makedirs(settings.media_root, exist_ok=True)
    os.makedirs(settings.static_root, exist_ok=True)
    os.makedirs(settings.blog_post_path, exist_ok=True)

    yield

    # Shutdown
    print(f"👋 Shutting down {settings.app_name}...")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    description="Django REST Framework에서 마이그레이션된 FastAPI 백엔드",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "cache-control",
        "connection",
    ],
)


# 전역 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred",
        },
    )


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "app_name": settings.app_name}


# API 라우터 등록
app.include_router(blog.router, prefix=f"{settings.api_v1_prefix}/blog", tags=["Blog"])
app.include_router(hrjang.router, prefix=f"{settings.api_v1_prefix}/hrjang", tags=["HRJang"])
app.include_router(hskmap.router, prefix=f"{settings.api_v1_prefix}/hskmap", tags=["HSKMap"])
app.include_router(lawchaser.router, prefix=f"{settings.api_v1_prefix}/lawchaser", tags=["LawChaser"])
app.include_router(rara.router, prefix=f"{settings.api_v1_prefix}/rara", tags=["Rara"])


# 정적 파일 마운트 (미디어)
if os.path.exists(settings.media_root):
    app.mount("/media", StaticFiles(directory=settings.media_root), name="media")

if os.path.exists(settings.static_root):
    app.mount("/static", StaticFiles(directory=settings.static_root), name="static")


# 루트 엔드포인트
@app.get("/", tags=["Root"])
async def root():
    """API 루트"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
