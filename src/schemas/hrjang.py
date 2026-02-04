"""
HRJang Pydantic Schemas
"""
from datetime import datetime
from pydantic import BaseModel, Field


class HrCommentCreate(BaseModel):
    """댓글 생성 스키마"""
    userid: str = Field(..., max_length=10)
    password: str = Field(..., max_length=20)
    title: str = Field(..., max_length=15)
    comment: str = Field(..., max_length=1000)


class HrCommentDelete(BaseModel):
    """댓글 삭제 스키마"""
    id: int
    password: str


class HrCommentResponse(BaseModel):
    """댓글 응답 스키마"""
    id: int
    userid: str
    password: str
    title: str
    comment: str
    time: datetime
    
    model_config = {"from_attributes": True}


class HrCommentListResponse(BaseModel):
    """댓글 목록 응답 스키마"""
    comments: list[HrCommentResponse]
    total: int
