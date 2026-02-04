"""
HSKMap API Router

HS 코드 매칭 관련 API 엔드포인트
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..models import HSKModel
from ..schemas.hskmap import HSKRequest, HSKResponse

router = APIRouter()


@router.post("/basic/", response_model=HSKResponse)
async def hskmap_basic(
    request: HSKRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """HS 코드 매칭 모델 호출"""
    try:
        # HSK 모델 임포트
        from ..core.hskmodel.model import hscode_matching_model
        
        # 모델 실행
        result_isic, result, final_result = hscode_matching_model(
            request.isic_code or "",
            request.desc,
        )
        
        # DB 저장 (선택적)
        hsk_record = HSKModel(
            desc=request.desc,
            isic_code=request.isic_code,
            time=datetime.now(),
        )
        db.add(hsk_record)
        await db.commit()
        
        return HSKResponse(
            isic_map=result_isic,
            response=result,
            final_code=final_result,
        )
        
    except ImportError:
        # 모델이 없는 경우 기본 응답
        return HSKResponse(
            isic_map={},
            response={"message": "HSK model not loaded"},
            final_code="",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
