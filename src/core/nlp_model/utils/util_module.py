"""
NLP Model Utility Module

LangChain 1.0+ 호환 리뷰 분석 및 응답 생성 유틸리티 함수
with_structured_output() 사용
"""
import os
from typing import Optional, Dict, Any, Tuple

from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableParallel

from .util_prompt import (
    ReviewAnalysis,
    UrgencyAnalysis,
    SimpleResponse,
    DetailedResponse,
    DetailedResponseWithGreeting,
    DetailedResponseWithContact,
    get_analysis_prompt,
    get_urgency_prompt,
    response_prompt_selector,
    get_rag_response_prompt,
    get_simple_response_prompt,
    translate_analysis_result,
)
from ....config import settings

# API 키 설정
os.environ["OPENAI_API_KEY"] = settings.openai_api_key
os.environ["GOOGLE_API_KEY"] = settings.google_api_key


def review_analyzer(
    user_review: str,
    analyzer_prompt_number: int = 0,
    analyzer_temperature: float = 0,
    model_name: str = "gpt-4o",
) -> Dict[str, str]:
    """
    리뷰 분석을 수행하는 모듈 (LangChain 1.0+ with_structured_output)

    Args:
        user_review: 사용자 리뷰 텍스트
        analyzer_prompt_number: 분석 프롬프트 번호 (현재 미사용, 호환성 유지)
        analyzer_temperature: 모델 온도
        model_name: 사용할 OpenAI 모델

    Returns:
        분석 결과 (User_Sentiment, User_Emotion, User_Intention)
    """
    llm = ChatOpenAI(model=model_name, temperature=analyzer_temperature)
    structured_llm = llm.with_structured_output(ReviewAnalysis)

    prompt = get_analysis_prompt()
    chain = prompt | structured_llm

    result = chain.invoke({"review": user_review})

    return {
        "User_Sentiment": result.User_Sentiment,
        "User_Emotion": result.User_Emotion,
        "User_Intention": result.User_Intention,
    }


def norm_responder(
    user_review: str,
    responder_temperature: float = 0,
    model_name: str = "gpt-4o",
) -> str:
    """
    기본 답변모듈 - 프롬프트 없이 단순 응답

    Args:
        user_review: 사용자 리뷰
        responder_temperature: 모델 온도
        model_name: 사용할 모델

    Returns:
        응답 텍스트
    """
    from langchain_core.prompts import ChatPromptTemplate

    llm = ChatOpenAI(model=model_name, temperature=responder_temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Respond to review"),
        ("human", "{review}")
    ])

    try:
        chain = prompt | llm
        response = chain.invoke({"review": user_review})
        return response.content
    except Exception as e:
        print(f"Responding Error: {e}")
        return "Responding Error"


def responder_nocot(
    user_review: str,
    responder_temperature: float = 0,
    User_Sentiment: Optional[str] = None,
    User_Emotion: Optional[str] = None,
    User_Intention: Optional[str] = None,
    model_name: str = "gpt-4o",
) -> Dict[str, Any]:
    """
    Chain Of Thought를 사용하지 않는 답변 모듈 (with_structured_output)
    """
    llm = ChatOpenAI(model=model_name, temperature=responder_temperature)
    structured_llm = llm.with_structured_output(SimpleResponse)

    prompt = response_prompt_selector(4)
    chain = prompt | structured_llm

    try:
        result = chain.invoke({
            "customer_sentiment": User_Sentiment,
            "customer_emotion": User_Emotion,
            "customer_intention": User_Intention,
            "review": user_review,
        })
        return {"Response": result.Response}
    except Exception as e:
        print(f"Responding Error: {e}")
        return {"Response": "Responding Error"}


def responder_basic(
    user_review: str,
    responder_temperature: float = 0,
    User_Sentiment: Optional[str] = None,
    User_Emotion: Optional[str] = None,
    User_Intention: Optional[str] = None,
    rag: bool = False,
    vectorstore_retriever=None,
    model_name: str = "gpt-4o",
) -> Dict[str, Any]:
    """
    기본적인 Basic Responder. RAG기능을 사용할지 결정 가능 (with_structured_output)
    """
    llm = ChatOpenAI(model=model_name, temperature=responder_temperature)
    structured_llm = llm.with_structured_output(DetailedResponse)

    prompt = response_prompt_selector(0, rag=rag)

    if rag and vectorstore_retriever:
        try:
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            chain = (
                RunnableParallel(
                    context=itemgetter("review") | vectorstore_retriever | format_docs,
                    customer_sentiment=itemgetter("customer_sentiment"),
                    customer_emotion=itemgetter("customer_emotion"),
                    customer_intention=itemgetter("customer_intention"),
                    review=itemgetter("review"),
                )
                | prompt
                | structured_llm
            )
            result = chain.invoke({
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
            return result.model_dump()
        except Exception as e:
            print(f"Responding Error: {e}")
            return {"Response": "Responding Error"}
    else:
        try:
            chain = prompt | structured_llm
            result = chain.invoke({
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
            return result.model_dump()
        except Exception as e:
            print(f"Responding Error: {e}")
            return {"Response": "Responding Error"}


def responder_com_name(
    user_review: str,
    responder_temperature: float = 0,
    User_Sentiment: Optional[str] = None,
    User_Emotion: Optional[str] = None,
    User_Intention: Optional[str] = None,
    Company_Name: Optional[str] = None,
    rag: bool = False,
    vectorstore_retriever=None,
    model_name: str = "gpt-4o",
) -> Dict[str, Any]:
    """
    사용자의 정보(회사 이름)를 입력할 수 있는 모듈 (with_structured_output)
    """
    llm = ChatOpenAI(model=model_name, temperature=responder_temperature)
    structured_llm = llm.with_structured_output(DetailedResponseWithGreeting)

    prompt = response_prompt_selector(1, rag=rag)

    if rag and vectorstore_retriever:
        try:
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            chain = (
                RunnableParallel(
                    context=itemgetter("review") | vectorstore_retriever | format_docs,
                    company_name=itemgetter("company_name"),
                    customer_sentiment=itemgetter("customer_sentiment"),
                    customer_emotion=itemgetter("customer_emotion"),
                    customer_intention=itemgetter("customer_intention"),
                    review=itemgetter("review"),
                )
                | prompt
                | structured_llm
            )
            result = chain.invoke({
                "company_name": Company_Name,
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
            return result.model_dump()
        except Exception as e:
            print(f"Responding Error: {e}")
            return {"Response": "Responding Error"}
    else:
        try:
            chain = prompt | structured_llm
            result = chain.invoke({
                "company_name": Company_Name,
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
            return result.model_dump()
        except Exception as e:
            print(f"Responding Error: {e}")
            return {"Response": "Responding Error"}


def responder_cc(
    user_review: str,
    responder_temperature: float = 0,
    User_Sentiment: Optional[str] = None,
    User_Emotion: Optional[str] = None,
    User_Intention: Optional[str] = None,
    Company_Name: Optional[str] = None,
    Contact: Optional[str] = None,
    rag: bool = False,
    vectorstore_retriever=None,
    model_name: str = "gpt-4o",
) -> Dict[str, Any]:
    """
    회사명 + 연락처 포함 응답 (with_structured_output)
    """
    llm = ChatOpenAI(model=model_name, temperature=responder_temperature)
    structured_llm = llm.with_structured_output(DetailedResponseWithGreeting)

    prompt = response_prompt_selector(3, rag=rag)

    if rag and vectorstore_retriever:
        try:
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            chain = (
                RunnableParallel(
                    context=itemgetter("review") | vectorstore_retriever | format_docs,
                    company_name=itemgetter("company_name"),
                    contact=itemgetter("contact"),
                    customer_sentiment=itemgetter("customer_sentiment"),
                    customer_emotion=itemgetter("customer_emotion"),
                    customer_intention=itemgetter("customer_intention"),
                    review=itemgetter("review"),
                )
                | prompt
                | structured_llm
            )
            result = chain.invoke({
                "company_name": Company_Name,
                "contact": Contact,
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
            return result.model_dump()
        except Exception as e:
            print(f"Responding Error: {e}")
            return {"Response": "Responding Error"}
    else:
        try:
            chain = prompt | structured_llm
            result = chain.invoke({
                "company_name": Company_Name,
                "contact": Contact,
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
            return result.model_dump()
        except Exception as e:
            print(f"Responding Error: {e}")
            return {"Response": "Responding Error"}


def responder_cgc(
    user_review: str,
    responder_temperature: float = 0,
    User_Sentiment: Optional[str] = None,
    User_Emotion: Optional[str] = None,
    User_Intention: Optional[str] = None,
    Head: Optional[str] = None,
    Foot: Optional[str] = None,
    model_name: str = "gpt-4o",
) -> Dict[str, Any]:
    """
    인사말/서명 포함 응답 (with_structured_output)
    """
    llm = ChatOpenAI(model=model_name, temperature=responder_temperature)
    structured_llm = llm.with_structured_output(DetailedResponseWithContact)

    prompt = response_prompt_selector(2)
    chain = prompt | structured_llm

    try:
        result = chain.invoke({
            "greeting": Head,
            "contactinfo": Foot,
            "customer_sentiment": User_Sentiment,
            "customer_emotion": User_Emotion,
            "customer_intention": User_Intention,
            "review": user_review,
        })
        return result.model_dump()
    except Exception as e:
        print(f"Responding Error: {e}")
        return {"Response": "Responding Error"}


def review_analyzer_zerocot(
    user_review: str,
    responder_temperature: float = 0,
    analyzer_temperature: float = 0,
    response_model_name: str = "gpt-4o",
    analysis_model_name: str = "gpt-4o",
    Company_Name: Optional[str] = None,
    Contact: Optional[str] = None,
    rag: bool = False,
    vectorstore_retriever=None,
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Zero-shot CoT를 활용한 분석 및 응답 (LangChain 1.0+ with_structured_output)
    """
    print("Analysis Start")

    # 분석 LLM 설정
    analyzer_llm = ChatOpenAI(model=analysis_model_name, temperature=analyzer_temperature)
    structured_analyzer = analyzer_llm.with_structured_output(ReviewAnalysis)

    analyzer_prompt = get_analysis_prompt()
    analyzer_chain = analyzer_prompt | structured_analyzer

    analyzer_result = analyzer_chain.invoke({"review": user_review})

    print("Analyze Level of Urgency")

    # 긴급도 분석
    urgency_llm = ChatOpenAI(model=analysis_model_name, temperature=analyzer_temperature)
    structured_urgency = urgency_llm.with_structured_output(UrgencyAnalysis)

    urgency_prompt = get_urgency_prompt()
    urgency_chain = urgency_prompt | structured_urgency

    urgency_result = urgency_chain.invoke({"review": user_review})

    # 응답 생성
    response_llm = ChatOpenAI(model=response_model_name, temperature=responder_temperature)
    structured_response = response_llm.with_structured_output(SimpleResponse)

    if rag and vectorstore_retriever:
        print("Response: RAG MODE")

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        response_prompt = get_rag_response_prompt()

        response_chain = (
            RunnableParallel(
                context=itemgetter("review") | vectorstore_retriever | format_docs,
                company_name=itemgetter("company_name"),
                contact=itemgetter("contact"),
                sentiment=itemgetter("sentiment"),
                emotion=itemgetter("emotion"),
                intention=itemgetter("intention"),
                review=itemgetter("review"),
            )
            | response_prompt
            | structured_response
        )

        result = response_chain.invoke({
            "company_name": Company_Name,
            "contact": Contact,
            "sentiment": analyzer_result.User_Sentiment,
            "emotion": analyzer_result.User_Emotion,
            "intention": analyzer_result.User_Intention,
            "review": user_review,
        })
    else:
        print("Response: NON-RAG MODE")

        response_prompt = get_simple_response_prompt()
        response_chain = response_prompt | structured_response

        result = response_chain.invoke({
            "sentiment": analyzer_result.User_Sentiment,
            "emotion": analyzer_result.User_Emotion,
            "intention": analyzer_result.User_Intention,
            "review": user_review
        })

    # 결과 한국어 변환
    trans_analyzer_result = translate_analysis_result(analyzer_result, urgency_result)
    print(trans_analyzer_result)

    return trans_analyzer_result, {"Response": result.Response}
