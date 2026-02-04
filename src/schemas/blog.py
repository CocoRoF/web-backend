"""
Blog Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# ==================== BlogImage Schemas ====================

class BlogImageCreate(BaseModel):
    """블로그 이미지 생성 스키마"""
    name: str = Field(..., max_length=100)


class BlogImageResponse(BaseModel):
    """블로그 이미지 응답 스키마"""
    id: int
    name: str
    image: str
    uploaded_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== BlogPost Schemas ====================

class BlogPostCreate(BaseModel):
    """블로그 포스트 생성 스키마"""
    name: str = Field(..., max_length=100)
    title: str = Field(..., max_length=255)
    content: str
    content_type: Literal["memorials", "knowledge", "note"]


class BlogPostUpdate(BaseModel):
    """블로그 포스트 수정 스키마"""
    name: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    content_type: Optional[Literal["memorials", "knowledge", "note"]] = None


class BlogPostResponse(BaseModel):
    """블로그 포스트 응답 스키마"""
    id: int
    name: str
    title: str
    content: str
    content_type: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class BlogPostListResponse(BaseModel):
    """블로그 포스트 목록 응답 스키마"""
    posts: List[BlogPostResponse]
    total: int


# ==================== Markdown File Schemas ====================

class MarkdownFileCreate(BaseModel):
    """마크다운 파일 생성 스키마"""
    file_name: str
    content: str = ""


class MarkdownFileUpdate(BaseModel):
    """마크다운 파일 수정 스키마"""
    file_name: str
    content: str


class MarkdownFileResponse(BaseModel):
    """마크다운 파일 응답 스키마"""
    file_name: str
    content: str


# ==================== Blog Metadata Schemas ====================

class PostMetadata(BaseModel):
    """포스트 메타데이터 스키마"""
    title: str = "새 포스트"
    excerpt: str = ""
    category: str = ""
    tags: List[str] = []
    author: str = ""
    published: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MetadataUpdate(BaseModel):
    """메타데이터 업데이트 스키마"""
    file_name: str
    metadata: PostMetadata


class MetadataResponse(BaseModel):
    """메타데이터 응답 스키마"""
    posts: dict


# ==================== AI Content Generation Schemas ====================

class AIContentRequest(BaseModel):
    """AI 콘텐츠 생성 요청 스키마"""
    subject: str
    reference_urls: List[str] = []
    additional_prompt: str = ""
    model: str = "gpt-4-1106-preview"


class BlogNewPostRequest(BaseModel):
    """새 블로그 포스트 요청 스키마"""
    title: str = "새 포스트"
    excerpt: str = ""
    category: str = ""
    tags: List[str] = []
    author: str = ""
    content: str = ""
