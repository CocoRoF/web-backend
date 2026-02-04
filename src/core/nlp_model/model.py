"""
Review Responder Model

리뷰 분석 및 응답 생성 핵심 클래스
"""
import os
from typing import Optional, List, Dict, Any

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from .utils.util_module import (
    review_analyzer,
    norm_responder,
    responder_nocot,
    responder_basic,
    responder_com_name,
    responder_cc,
    responder_cgc,
    review_analyzer_zerocot,
)
from ...config import settings


class ReviewResponder:
    """
    리뷰 분석 및 응답 생성 클래스
    
    Django에서 마이그레이션된 ReviewResponder 클래스
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        analyzer_prompt_number: int = 0,
        analyzer_temperature: float = 0,
        responder_temperature: float = 0,
        responder_name: Optional[str] = None,
        header: Optional[str] = None,
        footer: Optional[str] = None,
        contact: Optional[str] = None,
        rag: bool = False,
        memory: bool = False,
        rag_list: Optional[List[str]] = None,
        analysis_model_name: str = "gpt-4-0125-preview",
        nocot: bool = False,
        model_name: str = "gpt-4-0125-preview",
    ):
        self.api_key = api_key or settings.openai_api_key
        self.analyzer_prompt_number = analyzer_prompt_number
        self.analyzer_temperature = analyzer_temperature
        self.responder_temperature = responder_temperature
        self.responder_name = responder_name
        self.header = header
        self.footer = footer
        self.rag = rag
        self.rag_list = rag_list
        self.retriever = None
        self.memory = memory
        self.contact = contact
        self.analysis_model_name = analysis_model_name
        self.nocot = nocot
        self.model_name = model_name

        # API 키 설정
        os.environ["OPENAI_API_KEY"] = self.api_key
        
        # RAG 설정
        if self.rag and self.rag_list:
            self.vectorstore = FAISS.from_texts(
                self.rag_list, 
                embedding=OpenAIEmbeddings()
            )
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 5, "score_threshold": 0.4},
            )
        
        # 분석 결과 저장
        self.review_sentiment: Optional[str] = None
        self.review_emotion: Optional[str] = None
        self.review_intention: Optional[str] = None

    def Analysis(self, review_text: str, value_return: bool = False) -> Optional[Dict[str, Any]]:
        """
        리뷰 감성/감정/의도 분석
        
        Args:
            review_text: 분석할 리뷰 텍스트
            value_return: 결과 반환 여부
            
        Returns:
            분석 결과 (value_return=True인 경우)
        """
        result = review_analyzer(
            review_text,
            self.analyzer_prompt_number,
            self.analyzer_temperature,
            self.analysis_model_name,
        )
        self.review_sentiment = result["User_Sentiment"]
        self.review_emotion = result["User_Emotion"]
        self.review_intention = result["User_Intention"]

        if value_return:
            return result
        return None

    def Response(
        self,
        review_text: str,
        method: str = "RAAM",
        review_sentiment: Optional[str] = None,
        review_emotion: Optional[str] = None,
        review_intention: Optional[str] = None,
    ) -> str:
        """
        리뷰 응답 생성
        
        Args:
            review_text: 리뷰 텍스트
            method: 응답 메서드 ("normal", "RAAM", "nocot" 등)
            review_sentiment: 감성 (제공하지 않으면 자동 분석)
            review_emotion: 감정 (제공하지 않으면 자동 분석)
            review_intention: 의도 (제공하지 않으면 자동 분석)
            
        Returns:
            생성된 응답 텍스트
        """
        if method == "normal":
            response = norm_responder(
                review_text, 
                self.responder_temperature, 
                model_name=self.model_name
            )

        elif method == "RAAM":
            if (
                review_sentiment is None
                or review_emotion is None
                or review_intention is None
            ):
                self.Analysis(review_text)
                review_sentiment = review_sentiment or self.review_sentiment
                review_emotion = review_emotion or self.review_emotion
                review_intention = review_intention or self.review_intention

            if self.responder_name:
                if self.header and self.footer:
                    response = responder_cgc(
                        review_text,
                        self.responder_temperature,
                        review_sentiment,
                        review_emotion,
                        review_intention,
                        self.header,
                        self.footer,
                        self.model_name,
                    )
                elif self.contact:
                    response = responder_cc(
                        review_text,
                        self.responder_temperature,
                        review_sentiment,
                        review_emotion,
                        review_intention,
                        self.responder_name,
                        self.contact,
                        self.rag,
                        self.retriever,
                        self.model_name,
                    )
                else:
                    response = responder_com_name(
                        review_text,
                        self.responder_temperature,
                        review_sentiment,
                        review_emotion,
                        review_intention,
                        self.responder_name,
                        self.rag,
                        self.retriever,
                        self.model_name,
                    )
            else:
                response = responder_basic(
                    review_text,
                    self.responder_temperature,
                    review_sentiment,
                    review_emotion,
                    review_intention,
                    self.rag,
                    self.retriever,
                    self.model_name,
                )

        elif method == "nocot":
            if (
                review_sentiment is None
                or review_emotion is None
                or review_intention is None
            ):
                self.Analysis(review_text)
                review_sentiment = review_sentiment or self.review_sentiment
                review_emotion = review_emotion or self.review_emotion
                review_intention = review_intention or self.review_intention

            response = responder_nocot(
                review_text,
                self.responder_temperature,
                review_sentiment,
                review_emotion,
                review_intention,
                self.model_name,
            )

        else:
            response = norm_responder(
                review_text, 
                self.responder_temperature, 
                model_name=self.model_name
            )

        # 응답이 딕셔너리인 경우 Final_Response 또는 Response 추출
        if isinstance(response, dict):
            return response.get("Final_Response", response.get("Response", str(response)))
        
        return response
    
    def get_response(
        self,
        review_text: str,
        analysis_model: str = "RAAM",
        method: str = "normal",
        responder_name: Optional[str] = None,
        contact: Optional[str] = None,
        retrieval: Optional[str] = None,
    ) -> str:
        """
        간편 응답 생성 메서드
        
        Args:
            review_text: 리뷰 텍스트
            analysis_model: 분석 모델 타입
            method: 응답 메서드
            responder_name: 응답자 이름
            contact: 연락처 정보
            retrieval: RAG 컨텍스트
            
        Returns:
            생성된 응답 텍스트
        """
        # 임시로 속성 업데이트
        if responder_name:
            self.responder_name = responder_name
        if contact:
            self.contact = contact
            
        # RAG 설정
        if retrieval:
            self.rag = True
            self.rag_list = [retrieval]
            self.vectorstore = FAISS.from_texts(
                self.rag_list, 
                embedding=OpenAIEmbeddings()
            )
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 5, "score_threshold": 0.4},
            )
        
        return self.Response(review_text, method=method)
