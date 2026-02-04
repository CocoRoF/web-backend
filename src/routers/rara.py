"""
Rara API Router

AI 리뷰 분석 및 응답 관련 API 엔드포인트
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..models import RaraModel, RaraSurvey
from ..schemas.rara import (
    RaraBasicRequest,
    RaraCustomRequest,
    RaraRatingRequest,
    RaraSurveyRequest,
    RaraBasicResponse,
    RaraCustomResponse,
    SuccessResponse,
)

router = APIRouter()


@router.post("/basic/", response_model=RaraBasicResponse)
async def basic_response(
    request: RaraBasicRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """기본 AI 응답 생성"""
    try:
        from ..core.nlp_model.model import ReviewResponder
        
        # ReviewResponder 인스턴스 생성
        responder = ReviewResponder()
        
        # response_method에 따른 처리
        if request.response_method == "basic":
            response = responder.get_response(
                request.inputText,
                request.analysis_model or "RAAM",
                "basic",
            )
        elif request.response_method == "normal":
            response = responder.get_response(
                request.inputText,
                request.analysis_model or "RAAM",
                "normal",
            )
        else:
            # nocot 모드
            response = responder.get_response(
                request.inputText,
                request.analysis_model or "RAAM",
                "nocot",
            )
        
        # DB 저장
        rara_record = RaraModel(
            model=request.model,
            analysis_model=request.analysis_model,
            response_method=request.response_method,
            input_text=request.inputText,
            response=response,
            user_rating=request.user_rating,
            time=datetime.now(),
        )
        db.add(rara_record)
        await db.commit()
        
        return RaraBasicResponse(Response=response)
        
    except ImportError:
        # NLP 모델이 없는 경우 기본 응답
        return RaraBasicResponse(
            Response="NLP 모델이 로드되지 않았습니다. 모델을 설정해 주세요."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/custom/", response_model=RaraCustomResponse)
async def custom_response(
    request: RaraCustomRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """커스텀 AI 응답 생성"""
    try:
        from ..core.nlp_model.model import ReviewResponder
        
        responder = ReviewResponder()
        
        # response_method에 따른 처리
        if request.response_method == "custom":
            # 커스텀 응답만
            custom_resp = responder.get_response(
                request.inputText,
                request.analysis_model or "RAAM",
                "custom",
                responder_name=request.responder_name,
                contact=request.contact,
                retrieval=request.retrieval,
            )
            
            return RaraCustomResponse(Response=custom_resp)
            
        elif request.response_method in ["final", "multi"]:
            # 일반 응답 + 커스텀 응답
            normal_resp = responder.get_response(
                request.inputText,
                request.analysis_model or "RAAM",
                "normal",
            )
            custom_resp = responder.get_response(
                request.inputText,
                request.analysis_model or "RAAM",
                "custom",
                responder_name=request.responder_name,
                contact=request.contact,
                retrieval=request.retrieval,
            )
            
            # DB 저장
            rara_record = RaraModel(
                model=request.model,
                analysis_model=request.analysis_model,
                response_method=request.response_method,
                responder_name=request.responder_name,
                contact=request.contact,
                retrieval=request.retrieval,
                input_text=request.inputText,
                response=normal_resp,
                user_rating=request.user_rating,
                time=datetime.now(),
            )
            db.add(rara_record)
            await db.commit()
            
            return RaraCustomResponse(Response=normal_resp, Custom_Response=custom_resp)
        
        else:
            return RaraCustomResponse(Response="Invalid response_method")
            
    except ImportError:
        return RaraCustomResponse(
            Response="NLP 모델이 로드되지 않았습니다."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rating/", response_model=SuccessResponse)
async def save_rating(
    request: RaraRatingRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """평점 저장"""
    # 매칭되는 레코드 찾기
    result = await db.execute(
        select(RaraModel).where(
            and_(
                RaraModel.model == request.model,
                RaraModel.input_text == request.inputText,
                RaraModel.response == request.response,
                RaraModel.response_method == request.response_method,
            )
        )
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # 평점 업데이트
    record.user_rating = request.user_rating
    await db.commit()
    
    return SuccessResponse()


@router.post("/survey/", response_model=SuccessResponse)
async def save_survey(
    request: RaraSurveyRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """설문 저장"""
    survey = RaraSurvey(
        name=request.name,
        organization=request.organization,
        contact=request.contact,
        email=request.email,
        dataidx=request.dataidx,
        select_value=request.select_value,
        time=datetime.now(),
    )
    db.add(survey)
    await db.commit()
    
    return SuccessResponse()
