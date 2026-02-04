"""
LawChaser Pydantic Schemas
"""
from datetime import date
from typing import Optional, Any
from pydantic import BaseModel


class LawListRequest(BaseModel):
    """법률 목록 요청 스키마"""
    lsId: str


class LawOldNewRequest(BaseModel):
    """구/신 조문 요청 스키마"""
    lsiSeq: str
    lsId: str


class ArticleCherserRequest(BaseModel):
    """기사 조회 요청 스키마"""
    input_date: str


class LawListResponse(BaseModel):
    """법률 목록 응답 스키마"""
    law_name: str
    lsi_seq: str
    anc_yd: date
    anc_no: int
    ef_yd: date
    unk_var_1: Optional[str] = None
    unk_var_2: Optional[str] = None
    classify: Optional[str] = None
    
    model_config = {"from_attributes": True}


class LawOldNewResponse(BaseModel):
    """구/신 조문 응답 스키마"""
    old: str
    new: str
    
    model_config = {"from_attributes": True}


class ArticleResponse(BaseModel):
    """기사 응답 스키마"""
    data: Any
