"""
NLP Model Utility Module

리뷰 분석 및 응답 생성 유틸리티 함수
"""
import os
from typing import Optional, Dict, Any, Tuple

from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

from .util_prompt import (
    analysis_prompt_selector,
    response_prompt_selector,
    Response_output_selector,
    output_function,
)
from ....config import settings

# API 키 설정
os.environ["OPENAI_API_KEY"] = settings.openai_api_key
os.environ["GOOGLE_API_KEY"] = settings.google_api_key


def review_analyzer(
    user_review: str,
    analyzer_prompt_number: int = 0,
    analyzer_temperature: float = 0,
    model_name: str = "gpt-4-0125-preview",
) -> Dict[str, str]:
    """
    리뷰 분석을 수행하는 모듈

    Args:
        user_review: 사용자 리뷰 텍스트
        analyzer_prompt_number: 분석 프롬프트 번호
        analyzer_temperature: 모델 온도
        model_name: 사용할 OpenAI 모델

    Returns:
        분석 결과 (User_Sentiment, User_Emotion, User_Intention)
    """
    function_prompt = analysis_prompt_selector(prompt_num=analyzer_prompt_number)
    analyzer_prompt = ChatPromptTemplate.from_messages([
        ("system", "As an online hotel manager, analyze customer reviews."),
        ("human", "{analysis}"),
    ])

    analyzer_model = ChatOpenAI(
        model=model_name,
        temperature=analyzer_temperature
    ).bind(function_call={"name": "Describer"}, functions=function_prompt)

    runnable = (
        {"analysis": RunnablePassthrough()}
        | analyzer_prompt
        | analyzer_model
        | JsonOutputFunctionsParser()
    )
    result = runnable.invoke(user_review)
    return result


def norm_responder(
    user_review: str,
    responder_temperature: float = 0,
    model_name: str = "gpt-4-0125-preview",
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
    responder_model = ChatOpenAI(model=model_name, temperature=responder_temperature)
    norm_prompt = ChatPromptTemplate.from_messages([
        ("system", "Respond to review"),
        ("human", "{review}")
    ])

    try:
        responder_chain = norm_prompt | responder_model
        response = responder_chain.invoke({"review": user_review})
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
    model_name: str = "gpt-4-0125-preview",
) -> Dict[str, Any]:
    """
    Chain Of Thought를 사용하지 않는 답변 모듈
    """
    responder_prompt = response_prompt_selector(4)
    responder_model = ChatOpenAI(model=model_name, temperature=responder_temperature)
    responder_function = Response_output_selector(prompt_num=4)

    try:
        response_chain = (
            responder_prompt
            | responder_model.bind(
                function_call={"name": "Responder"},
                functions=responder_function
            )
            | JsonOutputFunctionsParser()
        )
        response = response_chain.invoke({
            "customer_sentiment": User_Sentiment,
            "customer_emotion": User_Emotion,
            "customer_intention": User_Intention,
            "review": user_review,
        })
    except Exception as e:
        print(f"Responding Error: {e}")
        response = {"Response": "Responding Error"}

    return response


def responder_basic(
    user_review: str,
    responder_temperature: float = 0,
    User_Sentiment: Optional[str] = None,
    User_Emotion: Optional[str] = None,
    User_Intention: Optional[str] = None,
    rag: bool = False,
    vectorstore_retriever=None,
    model_name: str = "gpt-4-0125-preview",
) -> Dict[str, Any]:
    """
    기본적인 Basic Responder. RAG기능을 사용할지 결정 가능
    """
    responder_prompt = response_prompt_selector(0, rag=rag)
    responder_model = ChatOpenAI(model=model_name, temperature=responder_temperature)
    responder_function = Response_output_selector(prompt_num=0)

    if rag and vectorstore_retriever:
        try:
            response_chain = (
                {
                    "context": itemgetter("review") | vectorstore_retriever,
                    "customer_sentiment": itemgetter("customer_sentiment"),
                    "customer_emotion": itemgetter("customer_emotion"),
                    "customer_intention": itemgetter("customer_intention"),
                    "review": itemgetter("review"),
                }
                | responder_prompt
                | responder_model.bind(
                    function_call={"name": "Responder"},
                    functions=responder_function
                )
                | JsonOutputFunctionsParser()
            )
            response = response_chain.invoke({
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
        except Exception as e:
            print(f"Responding Error: {e}")
            response = {"Response": "Responding Error"}
    else:
        try:
            response_chain = (
                responder_prompt
                | responder_model.bind(
                    function_call={"name": "Responder"},
                    functions=responder_function
                )
                | JsonOutputFunctionsParser()
            )
            response = response_chain.invoke({
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
        except Exception as e:
            print(f"Responding Error: {e}")
            response = {"Response": "Responding Error"}

    return response


def responder_com_name(
    user_review: str,
    responder_temperature: float = 0,
    User_Sentiment: Optional[str] = None,
    User_Emotion: Optional[str] = None,
    User_Intention: Optional[str] = None,
    Company_Name: Optional[str] = None,
    rag: bool = False,
    vectorstore_retriever=None,
    model_name: str = "gpt-4-0125-preview",
) -> Dict[str, Any]:
    """
    사용자의 정보(회사 이름)를 입력할 수 있는 모듈
    """
    responder_prompt = response_prompt_selector(1, rag=rag)
    responder_model = ChatOpenAI(model=model_name, temperature=responder_temperature)
    responder_function = Response_output_selector(prompt_num=1)

    if rag and vectorstore_retriever:
        try:
            response_chain = (
                {
                    "context": itemgetter("review") | vectorstore_retriever,
                    "company_name": itemgetter("company_name"),
                    "customer_sentiment": itemgetter("customer_sentiment"),
                    "customer_emotion": itemgetter("customer_emotion"),
                    "customer_intention": itemgetter("customer_intention"),
                    "review": itemgetter("review"),
                }
                | responder_prompt
                | responder_model.bind(
                    function_call={"name": "Responder"},
                    functions=responder_function
                )
                | JsonOutputFunctionsParser()
            )
            response = response_chain.invoke({
                "company_name": Company_Name,
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
        except Exception as e:
            print(f"Responding Error: {e}")
            response = {"Response": "Responding Error"}
    else:
        try:
            response_chain = (
                responder_prompt
                | responder_model.bind(
                    function_call={"name": "Responder"},
                    functions=responder_function
                )
                | JsonOutputFunctionsParser()
            )
            response = response_chain.invoke({
                "company_name": Company_Name,
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
        except Exception as e:
            print(f"Responding Error: {e}")
            response = {"Response": "Responding Error"}

    return response


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
    model_name: str = "gpt-4-0125-preview",
) -> Dict[str, Any]:
    """
    회사명 + 연락처 포함 응답
    """
    responder_prompt = response_prompt_selector(3, rag=rag)
    responder_model = ChatOpenAI(model=model_name, temperature=responder_temperature)
    responder_function = Response_output_selector(prompt_num=3)

    if rag and vectorstore_retriever:
        try:
            response_chain = (
                {
                    "context": itemgetter("review") | vectorstore_retriever,
                    "company_name": itemgetter("company_name"),
                    "contact": itemgetter("contact"),
                    "customer_sentiment": itemgetter("customer_sentiment"),
                    "customer_emotion": itemgetter("customer_emotion"),
                    "customer_intention": itemgetter("customer_intention"),
                    "review": itemgetter("review"),
                }
                | responder_prompt
                | responder_model.bind(
                    function_call={"name": "Responder"},
                    functions=responder_function
                )
                | JsonOutputFunctionsParser()
            )
            response = response_chain.invoke({
                "company_name": Company_Name,
                "contact": Contact,
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
        except Exception as e:
            print(f"Responding Error: {e}")
            response = {"Response": "Responding Error"}
    else:
        try:
            response_chain = (
                responder_prompt
                | responder_model.bind(
                    function_call={"name": "Responder"},
                    functions=responder_function
                )
                | JsonOutputFunctionsParser()
            )
            response = response_chain.invoke({
                "company_name": Company_Name,
                "contact": Contact,
                "customer_sentiment": User_Sentiment,
                "customer_emotion": User_Emotion,
                "customer_intention": User_Intention,
                "review": user_review,
            })
        except Exception as e:
            print(f"Responding Error: {e}")
            response = {"Response": "Responding Error"}

    return response


def responder_cgc(
    user_review: str,
    responder_temperature: float = 0,
    User_Sentiment: Optional[str] = None,
    User_Emotion: Optional[str] = None,
    User_Intention: Optional[str] = None,
    Head: Optional[str] = None,
    Foot: Optional[str] = None,
    model_name: str = "gpt-4-0125-preview",
) -> Dict[str, Any]:
    """
    인사말/서명 포함 응답
    """
    responder_prompt = response_prompt_selector(2)
    responder_model = ChatOpenAI(model=model_name, temperature=responder_temperature)
    responder_function = Response_output_selector(prompt_num=2)

    try:
        response_chain = (
            responder_prompt
            | responder_model.bind(
                function_call={"name": "Responder"},
                functions=responder_function
            )
            | JsonOutputFunctionsParser()
        )
        response = response_chain.invoke({
            "greeting": Head,
            "contactinfo": Foot,
            "customer_sentiment": User_Sentiment,
            "customer_emotion": User_Emotion,
            "customer_intention": User_Intention,
            "review": user_review,
        })
    except Exception as e:
        print(f"Responding Error: {e}")
        response = {"Response": "Responding Error"}

    return response


def review_analyzer_zerocot(
    user_review: str,
    responder_temperature: float = 0,
    analyzer_temperature: float = 0,
    response_model_name: str = "gpt-4o-2024-05-13",
    analysis_model_name: str = "gpt-4o-2024-05-13",
    Company_Name: Optional[str] = None,
    Contact: Optional[str] = None,
    rag: bool = False,
    vectorstore_retriever=None,
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Zero-shot CoT를 활용한 분석 및 응답
    """
    print("Analysis Start")

    analyzer_prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze the sentiment, emotion, and intention in the user's review. Step by step."),
        ("human", "{review}"),
    ])

    analyzer_model = ChatOpenAI(
        model=analysis_model_name,
        temperature=analyzer_temperature
    ).bind(
        function_call={"name": "Describer"},
        functions=[output_function(prompt_name="total_extraction")]
    )

    analyzer_chain = (
        {"review": RunnablePassthrough()}
        | analyzer_prompt
        | analyzer_model
        | JsonOutputFunctionsParser()
    )
    analyzer_result = analyzer_chain.invoke({"review": user_review})

    print("Analyze Level of Urgency")

    urgency_prompt = ChatPromptTemplate.from_messages([
        ("system", "As a review manager, assess how urgent it is to respond to a given customer's review."),
        ("human", "{review}"),
    ])

    urgency_model = ChatOpenAI(
        model=analysis_model_name,
        temperature=analyzer_temperature
    ).bind(
        function_call={"name": "Describer"},
        functions=[output_function(prompt_name="urgency_level")]
    )

    urgency_chain = (
        {"review": RunnablePassthrough()}
        | urgency_prompt
        | urgency_model
        | JsonOutputFunctionsParser()
    )
    urgency_result = urgency_chain.invoke({"review": user_review})

    if rag and vectorstore_retriever:
        print("Response: RAG MODE")
        response_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, consider 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention'. "
             "The given 'Responder Name' and 'Contact Information' must be included. "
             "Additionally, use the following pieces of retrieved context to answer the question \n"
             "Context: {context}"),
            ("human",
             "Responder Name:\n{company_name}\n\nContact:\n{contact}\n\n"
             "Customer Sentiment:\n{sentiment}\n\nCustomer Emotion:\n{emotion}\n\n"
             "Customer Intention:\n{intention}\n\nReview:\n{review}")
        ])

        response_model = ChatOpenAI(
            model=response_model_name,
            temperature=responder_temperature
        ).bind(
            function_call={"name": "Describer"},
            functions=[output_function(prompt_name="zero_response")]
        )

        response_chain = (
            {
                "context": itemgetter("review") | vectorstore_retriever,
                "company_name": itemgetter("company_name"),
                "contact": itemgetter("contact"),
                "sentiment": itemgetter("sentiment"),
                "emotion": itemgetter("emotion"),
                "intention": itemgetter("intention"),
                "review": itemgetter("review"),
            }
            | response_prompt
            | response_model
            | JsonOutputFunctionsParser()
        )

        result = response_chain.invoke({
            "company_name": Company_Name,
            "contact": Contact,
            "sentiment": analyzer_result['User_Sentiment'],
            "emotion": analyzer_result['User_Emotion'],
            "intention": analyzer_result['User_Intention'],
            "review": user_review,
        })
    else:
        print("Response: NON-RAG MODE")

        response_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, consider 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention'."),
            ("human",
             "Customer Sentiment:\n{sentiment}\n\nCustomer Emotion:\n{emotion}\n\n"
             "Customer Intention:\n{intention}\n\nReview:\n{review}")
        ])

        response_model = ChatOpenAI(
            model=response_model_name,
            temperature=responder_temperature
        ).bind(
            function_call={"name": "Describer"},
            functions=[output_function(prompt_name="zero_response")]
        )

        response_chain = (
            {
                "sentiment": RunnablePassthrough(),
                "emotion": RunnablePassthrough(),
                "intention": RunnablePassthrough(),
                "review": RunnablePassthrough()
            }
            | response_prompt
            | response_model
            | JsonOutputFunctionsParser()
        )

        result = response_chain.invoke({
            "sentiment": analyzer_result['User_Sentiment'],
            "emotion": analyzer_result['User_Emotion'],
            "intention": analyzer_result['User_Intention'],
            "review": user_review
        })

    # 결과 매핑
    sentiment_mapping = {
        "Positive": "긍정",
        "Neutral": "중립",
        "Negative": "부정",
    }
    emotion_mapping = {
        "Anger": "화남",
        "Disgust": "역겨움",
        "Fear": "공포",
        "Happiness": "행복",
        "Contempt": "조소",
        "Sadness": "슬픔",
        "Surprise": "놀람",
        "Neutral": "중립"
    }
    intention_mapping = {
        "Complaint": "항의",
        "Expressing Dissatisfaction": "불만족 표출",
        "Warning Others": "타인에게 경고",
        "Feedback": "피드백",
        "Sharing Experience": "경험 공유",
        "Expressing Satisfaction": "만족감 표출",
        "Praise": "칭찬",
        "Recommendation": "추천"
    }
    urgency_mapping = {
        "Urgent": "긴급함",
        "Medium": "중간",
        "Not Urgent": "긴급하지않음",
    }

    trans_analyzer_result = {
        'User_Sentiment': sentiment_mapping.get(analyzer_result['User_Sentiment'], analyzer_result['User_Sentiment']),
        'User_Emotion': emotion_mapping.get(analyzer_result['User_Emotion'], analyzer_result['User_Emotion']),
        'User_Intention': intention_mapping.get(analyzer_result['User_Intention'], analyzer_result['User_Intention']),
        'Review_Urgency': urgency_mapping.get(urgency_result.get('Urgency_Level', 'Medium'), 'Medium'),
    }

    print(trans_analyzer_result)

    return trans_analyzer_result, result
