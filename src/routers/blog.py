"""
Blog API Router

블로그 관련 API 엔드포인트
"""
import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, AsyncGenerator
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles

from ..config import settings
from ..database import get_async_db
from ..models import BlogImage, BlogPost
from ..schemas.blog import (
    BlogImageCreate,
    BlogImageResponse,
    BlogPostCreate,
    BlogPostResponse,
    BlogPostListResponse,
    MarkdownFileCreate,
    MarkdownFileUpdate,
    MarkdownFileResponse,
    PostMetadata,
    MetadataUpdate,
    BlogNewPostRequest,
)

router = APIRouter()

# 블로그 포스트 경로
BLOG_POST_PATH = Path(settings.blog_post_path)
METADATA_FILE = BLOG_POST_PATH / "meta_data.json"


def user_directory_path(user_name: str, filename: str) -> str:
    """사용자별 업로드 디렉토리 경로 생성"""
    return f"user_{user_name}/{filename}"


async def get_metadata() -> dict:
    """메타데이터 파일 로드"""
    if not METADATA_FILE.exists():
        return {}

    async with aiofiles.open(METADATA_FILE, "r", encoding="utf-8") as f:
        content = await f.read()
        return json.loads(content) if content else {}


async def save_metadata(metadata: dict) -> None:
    """메타데이터 파일 저장"""
    BLOG_POST_PATH.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(METADATA_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(metadata, ensure_ascii=False, indent=2))


# ==================== Image Upload ====================

@router.post("/image/upload/", response_model=BlogImageResponse)
async def upload_image(
    name: str,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
):
    """이미지 업로드"""
    # 업로드 디렉토리 생성
    upload_dir = Path(settings.media_root) / f"user_{name}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 파일 저장
    file_path = upload_dir / image.filename
    async with aiofiles.open(file_path, "wb") as f:
        content = await image.read()
        await f.write(content)

    # DB 저장
    relative_path = user_directory_path(name, image.filename)
    blog_image = BlogImage(
        name=name,
        image=relative_path,
    )
    db.add(blog_image)
    await db.commit()
    await db.refresh(blog_image)

    return blog_image


# ==================== BlogPost CRUD (DB) ====================

@router.post("/post/", response_model=BlogPostResponse)
async def create_post(
    post: BlogPostCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """블로그 포스트 생성 (DB)"""
    blog_post = BlogPost(
        name=post.name,
        title=post.title,
        content=post.content,
        content_type=post.content_type,
    )
    db.add(blog_post)
    await db.commit()
    await db.refresh(blog_post)

    return blog_post


@router.get("/post/{pk}", response_model=BlogPostResponse)
async def get_post(
    pk: int,
    db: AsyncSession = Depends(get_async_db),
):
    """특정 블로그 포스트 조회"""
    result = await db.execute(select(BlogPost).where(BlogPost.id == pk))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.get("/post/list/", response_model=BlogPostListResponse)
async def list_posts(
    content_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    """블로그 포스트 목록 조회"""
    query = select(BlogPost)

    if content_type:
        query = query.where(BlogPost.content_type == content_type)

    result = await db.execute(query.order_by(BlogPost.created_at.desc()))
    posts = result.scalars().all()

    return BlogPostListResponse(posts=posts, total=len(posts))


# ==================== Markdown File CRUD ====================

@router.get("/contents/", response_model=MarkdownFileResponse)
async def read_markdown(file_name: str = Query(...)):
    """마크다운 파일 읽기"""
    file_path = BLOG_POST_PATH / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        content = await f.read()

    return MarkdownFileResponse(file_name=file_name, content=content)


@router.post("/contents/")
async def create_markdown(data: MarkdownFileCreate):
    """마크다운 파일 생성"""
    BLOG_POST_PATH.mkdir(parents=True, exist_ok=True)
    file_path = BLOG_POST_PATH / data.file_name

    if file_path.exists():
        raise HTTPException(status_code=400, detail="File already exists")

    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(data.content)

    return {"message": "File created successfully", "file_name": data.file_name}


@router.put("/contents/")
async def update_markdown(data: MarkdownFileUpdate):
    """마크다운 파일 수정"""
    file_path = BLOG_POST_PATH / data.file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(data.content)

    return {"message": "File updated successfully", "file_name": data.file_name}


@router.delete("/contents/")
async def delete_markdown(file_name: str = Query(...)):
    """마크다운 파일 삭제"""
    file_path = BLOG_POST_PATH / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(file_path)

    return {"message": "File deleted successfully"}


# ==================== Blog Delete (File + Metadata) ====================

@router.delete("/delete/")
async def delete_blog_post(file_name: str = Query(...)):
    """블로그 포스트 삭제 (파일 + 메타데이터)"""
    # 파일 삭제
    file_path = BLOG_POST_PATH / file_name
    if file_path.exists():
        os.remove(file_path)

    # 메타데이터에서 삭제
    metadata = await get_metadata()
    if file_name in metadata:
        del metadata[file_name]
        await save_metadata(metadata)

    return {"message": "Blog post deleted successfully"}


# ==================== Metadata Management ====================

@router.get("/metadata/")
async def get_all_metadata():
    """전체 메타데이터 조회"""
    metadata = await get_metadata()
    return {"posts": metadata}


@router.post("/metadata/")
async def overwrite_metadata(metadata: dict):
    """메타데이터 전체 덮어쓰기"""
    await save_metadata(metadata)
    return {"message": "Metadata overwritten successfully"}


@router.put("/metadata/")
async def update_post_metadata(data: MetadataUpdate):
    """특정 포스트 메타데이터 업데이트"""
    metadata = await get_metadata()
    metadata[data.file_name] = data.metadata.model_dump()
    await save_metadata(metadata)

    return {"message": "Metadata updated successfully"}


@router.delete("/metadata/")
async def delete_post_metadata(file_name: str = Query(...)):
    """특정 포스트 메타데이터 삭제"""
    metadata = await get_metadata()

    if file_name in metadata:
        del metadata[file_name]
        await save_metadata(metadata)

    return {"message": "Metadata deleted successfully"}


# ==================== Blog Posts (with Metadata) ====================

@router.get("/posts/")
async def get_blog_posts():
    """블로그 포스트 목록 (메타데이터 결합)"""
    metadata = await get_metadata()

    posts = []
    for file_name, meta in metadata.items():
        posts.append({
            "file_name": file_name,
            **meta,
        })

    # 최신순 정렬
    posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return {"posts": posts}


# ==================== New Blog Post ====================

@router.get("/new-post/")
async def get_new_post_info():
    """새 블로그 포스트 API 정보"""
    return {
        "message": "Use POST method to create a new blog post",
        "required_fields": ["title"],
        "optional_fields": ["excerpt", "category", "tags", "author", "content"],
    }


@router.post("/new-post/")
async def create_new_blog_post(data: BlogNewPostRequest):
    """새 블로그 포스트 생성 (파일 + 메타데이터)"""
    # 파일명 생성
    today = datetime.now().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex[:4]
    file_name = f"blog_{today}_{unique_id}.md"

    # 마크다운 파일 생성
    BLOG_POST_PATH.mkdir(parents=True, exist_ok=True)
    file_path = BLOG_POST_PATH / file_name

    content = data.content or f"# {data.title}\n\n내용을 입력하세요."
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(content)

    # 메타데이터 추가
    metadata = await get_metadata()
    now = datetime.now().isoformat()
    metadata[file_name] = {
        "title": data.title,
        "excerpt": data.excerpt,
        "category": data.category,
        "tags": data.tags,
        "author": data.author,
        "published": False,
        "created_at": now,
        "updated_at": now,
    }
    await save_metadata(metadata)

    return {
        "message": "Blog post created successfully",
        "file_name": file_name,
    }


# ==================== Post Detail ====================

@router.get("/post-detail/")
async def get_post_detail(file_name: str = Query(...)):
    """파일명으로 마크다운 파일 내용 조회"""
    file_path = BLOG_POST_PATH / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        content = await f.read()

    # 메타데이터도 함께 반환
    metadata = await get_metadata()
    meta = metadata.get(file_name, {})

    return {
        "file_name": file_name,
        "content": content,
        "metadata": meta,
    }


# ==================== AI Content Generation (SSE) ====================

async def ai_content_generator(
    subject: str,
    reference_urls: List[str],
    additional_prompt: str,
    model: str,
) -> AsyncGenerator[str, None]:
    """AI 콘텐츠 생성 제너레이터"""
    try:
        from ..core.nlp_model.services import generate_blog_content_stream

        async for chunk in generate_blog_content_stream(
            subject=subject,
            reference_urls=reference_urls,
            additional_prompt=additional_prompt,
            model=model,
        ):
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
    except ImportError:
        # NLP 모델이 없는 경우 기본 응답
        yield f"data: {json.dumps({'content': f'# {subject}\\n\\n콘텐츠 생성 중...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'content': '\\n\\nAI 콘텐츠 생성 모듈이 로드되지 않았습니다.'}, ensure_ascii=False)}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    yield "data: [DONE]\n\n"


@router.get("/ai-generate-stream/")
async def ai_generate_stream(
    subject: str = Query(...),
    reference_urls: str = Query("[]"),
    additional_prompt: str = Query(""),
    model: str = Query("gpt-4-1106-preview"),
):
    """AI 콘텐츠 생성 (SSE 스트리밍)"""
    try:
        urls = json.loads(reference_urls)
    except json.JSONDecodeError:
        urls = []

    return StreamingResponse(
        ai_content_generator(subject, urls, additional_prompt, model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )
