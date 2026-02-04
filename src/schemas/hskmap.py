"""
HSKMap Pydantic Schemas
"""
from typing import Optional, Any
from pydantic import BaseModel


class HSKRequest(BaseModel):
    """HS 코드 매칭 요청 스키마"""
    desc: str
    isic_code: Optional[str] = None


class HSKResponse(BaseModel):
    """HS 코드 매칭 응답 스키마"""
    isic_map: Any
    response: Any
    final_code: Any
