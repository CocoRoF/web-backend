"""
HRJang API Router

댓글 관련 API 엔드포인트
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..models import HrComment
from ..schemas.hrjang import (
    HrCommentCreate,
    HrCommentDelete,
    HrCommentResponse,
    HrCommentListResponse,
)

router = APIRouter()


@router.post("/comment", response_model=dict)
async def create_comment(
    data: HrCommentCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """새 댓글 생성"""
    comment = HrComment(
        userid=data.userid,
        password=data.password,
        title=data.title,
        comment=data.comment,
        time=datetime.now(),
    )
    db.add(comment)
    await db.commit()

    return {"message": "Success"}


@router.get("/comments", response_model=HrCommentListResponse)
async def get_comments(db: AsyncSession = Depends(get_async_db)):
    """댓글 목록 조회"""
    result = await db.execute(
        select(HrComment).order_by(HrComment.time.desc())
    )
    comments = result.scalars().all()

    return HrCommentListResponse(comments=comments, total=len(comments))


@router.get("/comments/{comment_id}", response_model=HrCommentResponse)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """특정 댓글 조회"""
    result = await db.execute(
        select(HrComment).where(HrComment.id == comment_id)
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@router.put("/comments/{comment_id}", response_model=HrCommentResponse)
async def update_comment(
    comment_id: int,
    data: HrCommentCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """댓글 수정"""
    result = await db.execute(
        select(HrComment).where(HrComment.id == comment_id)
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # 비밀번호 확인
    if comment.password != data.password:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    # 업데이트
    comment.userid = data.userid
    comment.title = data.title
    comment.comment = data.comment

    await db.commit()
    await db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    data: HrCommentDelete,
    db: AsyncSession = Depends(get_async_db),
):
    """댓글 삭제 (비밀번호 확인)"""
    result = await db.execute(
        select(HrComment).where(HrComment.id == comment_id)
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # 비밀번호 확인
    if comment.password != data.password:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    await db.delete(comment)
    await db.commit()

    return {"message": "삭제되었습니다."}


# Django 호환 엔드포인트
@router.post("/delcomment/")
async def delete_comment_legacy(
    data: HrCommentDelete,
    db: AsyncSession = Depends(get_async_db),
):
    """댓글 삭제 (레거시 - POST 메서드)"""
    result = await db.execute(
        select(HrComment).where(HrComment.id == data.id)
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # 비밀번호 확인
    if comment.password != data.password:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    await db.delete(comment)
    await db.commit()

    return {"message": "삭제되었습니다."}
