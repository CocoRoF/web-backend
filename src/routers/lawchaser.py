"""
LawChaser API Router

법률 관련 API 엔드포인트
"""
import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..models import LawListCrawledData, LawOldNewCrawledData
from ..schemas.lawchaser import (
    LawListRequest,
    LawOldNewRequest,
    ArticleCherserRequest,
    LawListResponse,
    LawOldNewResponse,
)

router = APIRouter()

# 기사 데이터 캐시 (앱 시작시 로드)
_article_cache: dict = {}


def load_article_data():
    """기사 데이터 로드"""
    global _article_cache
    
    # CSV 파일 경로 (환경에 맞게 조정)
    csv_path = Path(__file__).parent.parent / "data" / "article_gpt.csv"
    
    if csv_path.exists():
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            _article_cache = df.to_dict("index")
        except Exception:
            pass


# 앱 시작시 데이터 로드 시도
load_article_data()


@router.post("/lawlist/", response_model=List[LawListResponse])
async def get_law_list(
    request: LawListRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """법률 목록 조회"""
    result = await db.execute(
        select(LawListCrawledData)
        .where(LawListCrawledData.ls_id == request.lsId)
    )
    laws = result.scalars().all()
    
    return laws


@router.post("/oldnew/", response_model=List[LawOldNewResponse])
async def get_law_oldnew(
    request: LawOldNewRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """구/신 조문 비교 조회"""
    result = await db.execute(
        select(LawOldNewCrawledData)
        .where(
            LawOldNewCrawledData.lsi_seq == request.lsiSeq,
            LawOldNewCrawledData.ls_id == request.lsId,
        )
        .order_by(LawOldNewCrawledData.oldnew_sequence)
    )
    laws = result.scalars().all()
    
    return laws


@router.post("/artchaser/")
async def get_article(request: ArticleCherserRequest):
    """기사 조회"""
    global _article_cache
    
    if not _article_cache:
        load_article_data()
    
    if request.input_date not in _article_cache:
        return {"Response": "No_Data_Exist"}
    
    return _article_cache[request.input_date]
