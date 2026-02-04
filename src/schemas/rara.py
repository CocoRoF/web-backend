"""
Rara Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ==================== Request Schemas ====================

class RaraBasicRequest(BaseModel):
    """기본 AI 응답 요청 스키마"""
    model: str = Field(..., max_length=30)
    inputText: str = Field(..., max_length=5000)
    analysis_model: Optional[str] = Field(None, max_length=30)
    response_method: str = Field(..., max_length=20)
    user_rating: Optional[int] = None


class RaraCustomRequest(BaseModel):
    """커스텀 AI 응답 요청 스키마"""
    model: str = Field(..., max_length=30)
    inputText: str = Field(..., max_length=5000)
    responder_name: Optional[str] = Field(None, max_length=50)
    contact: Optional[str] = Field(None, max_length=1000)
    retrieval: Optional[str] = Field(None, max_length=100000)
    response_method: str = Field(..., max_length=20)
    analysis_model: Optional[str] = Field(None, max_length=30)
    user_rating: Optional[int] = None


class RaraRatingRequest(BaseModel):
    """평점 저장 요청 스키마"""
    model: str
    inputText: str
    response: str
    analysis_model: Optional[str] = None
    response_method: str
    user_rating: int


class RaraSurveyRequest(BaseModel):
    """설문 저장 요청 스키마"""
    name: str = Field(..., max_length=30)
    organization: str = Field(..., max_length=30)
    contact: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=50)
    dataidx: int
    select_value: int


# ==================== Response Schemas ====================

class RaraBasicResponse(BaseModel):
    """기본 AI 응답 스키마"""
    Response: str


class RaraCustomResponse(BaseModel):
    """커스텀 AI 응답 스키마"""
    Response: str
    Custom_Response: Optional[str] = None


class RaraModelResponse(BaseModel):
    """Rara 모델 응답 스키마"""
    id: int
    model: str
    analysis_model: Optional[str]
    response_method: str
    responder_name: Optional[str]
    contact: Optional[str]
    input_text: str
    response: Optional[str]
    user_rating: Optional[int]
    time: datetime

    model_config = {"from_attributes": True}


class SuccessResponse(BaseModel):
    """성공 응답 스키마"""
    message: str = "Success"
