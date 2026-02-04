"""
NLP Model Prompt Utilities

LangChain 1.0+ 호환 프롬프트 및 Pydantic 스키마 정의
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


# ============================================================================
# Pydantic Schemas for Structured Output (LangChain 1.0+ with_structured_output)
# ============================================================================

class ReviewAnalysis(BaseModel):
    """리뷰 분석 결과 스키마"""
    User_Sentiment: Literal["Positive", "Neutral", "Negative"] = Field(
        description="Sentiment Analysis of the 'Review'"
    )
    User_Emotion: Literal[
        "Anger", "Disgust", "Fear", "Happiness", "Contempt", "Sadness", "Surprise", "Neutral"
    ] = Field(
        description="Emotion Analysis of the 'Review'"
    )
    User_Intention: Literal[
        "Complaint", "Expressing Dissatisfaction", "Warning Others", "Feedback",
        "Sharing Experience", "Expressing Satisfaction", "Praise", "Recommendation"
    ] = Field(
        description="Intention Analysis of the 'Review'"
    )


class UrgencyAnalysis(BaseModel):
    """긴급도 분석 스키마"""
    Urgency_Level: Literal["Urgent", "Medium", "Not Urgent"] = Field(
        description="The urgency level of responding to this review"
    )


class SimpleResponse(BaseModel):
    """간단한 응답 스키마"""
    Response: str = Field(description="Response to Customer Review")


class DetailedResponse(BaseModel):
    """상세 응답 스키마 (Chain of Thought 포함)"""
    Responding_to_Customer_Sentiment: str = Field(
        description="Responding to Customer Sentiment"
    )
    Sentiment_Reason: str = Field(
        description="The reason for the sentiment response"
    )
    Responding_to_Customer_Emotion: str = Field(
        description="Responding to Customer Emotion"
    )
    Emotion_Reason: str = Field(
        description="The reason for the emotion response"
    )
    Responding_to_Customer_Intention: str = Field(
        description="Responding to Customer Intention"
    )
    Intention_Reason: str = Field(
        description="The reason for the intention response"
    )
    Final_Response: str = Field(
        description="The Final Generated Response"
    )


class DetailedResponseWithGreeting(BaseModel):
    """인사말 포함 상세 응답 스키마"""
    Greeting: str = Field(description="Greeting Message")
    Responding_to_Customer_Sentiment: str = Field(
        description="Responding to Customer Sentiment"
    )
    Sentiment_Reason: str = Field(
        description="The reason for the sentiment response"
    )
    Responding_to_Customer_Emotion: str = Field(
        description="Responding to Customer Emotion"
    )
    Emotion_Reason: str = Field(
        description="The reason for the emotion response"
    )
    Responding_to_Customer_Intention: str = Field(
        description="Responding to Customer Intention"
    )
    Intention_Reason: str = Field(
        description="The reason for the intention response"
    )
    Final_Response: str = Field(
        description="The Final Generated Response"
    )


class DetailedResponseWithContact(BaseModel):
    """인사말 및 연락처 포함 상세 응답 스키마"""
    Greeting: str = Field(description="Greeting Message")
    Contact_Information: str = Field(description="Contact Information")
    Responding_to_Customer_Sentiment: str = Field(
        description="Responding to Customer Sentiment"
    )
    Sentiment_Reason: str = Field(
        description="The reason for the sentiment response"
    )
    Responding_to_Customer_Emotion: str = Field(
        description="Responding to Customer Emotion"
    )
    Emotion_Reason: str = Field(
        description="The reason for the emotion response"
    )
    Responding_to_Customer_Intention: str = Field(
        description="Responding to Customer Intention"
    )
    Intention_Reason: str = Field(
        description="The reason for the intention response"
    )
    Final_Response: str = Field(
        description="The Final Generated Response"
    )


# ============================================================================
# Schema Selectors
# ============================================================================

def get_analysis_schema() -> type[ReviewAnalysis]:
    """리뷰 분석 스키마 반환"""
    return ReviewAnalysis


def get_urgency_schema() -> type[UrgencyAnalysis]:
    """긴급도 분석 스키마 반환"""
    return UrgencyAnalysis


def get_response_schema(prompt_num: int) -> type[BaseModel]:
    """
    응답 스키마 선택

    Args:
        prompt_num: 프롬프트 번호 (0-4)

    Returns:
        해당하는 Pydantic 스키마 클래스
    """
    schema_map = {
        0: DetailedResponse,
        1: DetailedResponseWithGreeting,
        2: DetailedResponseWithContact,
        3: DetailedResponseWithGreeting,
        4: SimpleResponse,
    }
    return schema_map.get(prompt_num, DetailedResponse)


# ============================================================================
# Prompt Templates
# ============================================================================

def get_analysis_prompt() -> ChatPromptTemplate:
    """리뷰 분석용 프롬프트 반환"""
    return ChatPromptTemplate.from_messages([
        ("system", "As an online hotel manager, analyze customer reviews."),
        ("human", "{review}"),
    ])


def get_urgency_prompt() -> ChatPromptTemplate:
    """긴급도 분석용 프롬프트 반환"""
    return ChatPromptTemplate.from_messages([
        ("system", "As a review manager, assess how urgent it is to respond to a given customer's review."),
        ("human", "{review}"),
    ])


def response_prompt_selector(prompt_num: int, rag: bool = False) -> ChatPromptTemplate:
    """
    응답 프롬프트 선택

    Args:
        prompt_num: 프롬프트 번호 (0-4)
        rag: RAG 모드 여부

    Returns:
        ChatPromptTemplate
    """
    prompts = {
        (0, False): ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, it is important to keep 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention' in mind.\n\n"
             "Your answer must follow this 'Format' below.\nFormat:\n"
             "(Responding to Customer Sentiment) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n"
             "(Responding to Customer Emotion) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n"
             "(Responding to Customer Intention) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n\n"
             "The Final Generated Response to that Customer Review = Your Final Response"),
            ("human",
             "Customer Sentiment:\n{customer_sentiment}\n\nCustomer Emotion:\n{customer_emotion}\n\n"
             "Customer Intention:\n{customer_intention}\n\nReview:\n{review}"),
        ]),
        (0, True): ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, it is important to keep 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention' in mind.\n\n"
             "Use the following pieces of retrieved context to answer the question.\n\nContext: {context}\n\n"
             "Your answer must follow this 'Format' below.\nFormat:\n"
             "(Responding to Customer Sentiment) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n"
             "(Responding to Customer Emotion) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n"
             "(Responding to Customer Intention) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n\n"
             "The Final Generated Response to that Customer Review = Your Final Response"),
            ("human",
             "Customer Sentiment:\n{customer_sentiment}\n\nCustomer Emotion:\n{customer_emotion}\n\n"
             "Customer Intention:\n{customer_intention}\n\nReview:\n{review}"),
        ]),
        (1, False): ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, it is important to keep 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention' in mind.\n\n"
             "Your answer must follow this 'Format' below.\nFormat:\n"
             "\"(Greetings including company name)\"\n"
             "(Responding to Customer Sentiment) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n"
             "(Responding to Customer Emotion) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n"
             "(Responding to Customer Intention) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n\n"
             "The Final Generated Response to that Customer Review = Your Final Response"),
            ("human",
             "Company name:\n{company_name}\n\nCustomer Sentiment:\n{customer_sentiment}\n\n"
             "Customer Emotion:\n{customer_emotion}\n\nCustomer Intention:\n{customer_intention}\n\nReview:\n{review}"),
        ]),
        (1, True): ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, it is important to keep 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention' in mind.\n\n"
             "Use the following pieces of retrieved context to answer the question.\n\nContext: {context}\n\n"
             "Your answer must follow this 'Format' below.\nFormat:\n"
             "\"(Greetings including company name)\"\n"
             "(Responding to Customer Sentiment) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n"
             "(Responding to Customer Emotion) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n"
             "(Responding to Customer Intention) + \"(The sentence in the customer review that is the reason for generating that response.)\"\n\n"
             "The Final Generated Response to that Customer Review = Your Final Response"),
            ("human",
             "Company name:\n{company_name}\n\nCustomer Sentiment:\n{customer_sentiment}\n\n"
             "Customer Emotion:\n{customer_emotion}\n\nCustomer Intention:\n{customer_intention}\n\nReview:\n{review}"),
        ]),
        (2, False): ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, it is important to keep 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention' in mind.\n\n"
             "The given 'Greeting' and 'Contact Information' message must be included.\n\n"
             "The Final Response must be generated."),
            ("human",
             "Greeting:\n{greeting}\n\nContact Information:\n{contactinfo}\n\n"
             "Customer Sentiment:\n{customer_sentiment}\n\nCustomer Emotion:\n{customer_emotion}\n\n"
             "Customer Intention:\n{customer_intention}\n\nReview:\n{review}"),
        ]),
        (3, False): ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, it is important to keep 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention' in mind. "
             "Consider the contacts information."),
            ("human",
             "Company name:\n{company_name}\n\nContact:\n{contact}\n\n"
             "Customer Sentiment:\n{customer_sentiment}\n\nCustomer Emotion:\n{customer_emotion}\n\n"
             "Customer Intention:\n{customer_intention}\n\nReview:\n{review}"),
        ]),
        (3, True): ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, it is important to keep 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention' in mind.\n\n"
             "Consider the contacts information.\n\n"
             "Use the following pieces of retrieved context to answer the question.\n\nContext: {context}"),
            ("human",
             "Company name:\n{company_name}\n\nContact:\n{contact}\n\n"
             "Customer Sentiment:\n{customer_sentiment}\n\nCustomer Emotion:\n{customer_emotion}\n\n"
             "Customer Intention:\n{customer_intention}\n\nReview:\n{review}"),
        ]),
        (4, False): ChatPromptTemplate.from_messages([
            ("system",
             "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
             "When composing your reply, it is important to keep 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention' in mind."),
            ("human",
             "Customer Sentiment:\n{customer_sentiment}\n\nCustomer Emotion:\n{customer_emotion}\n\n"
             "Customer Intention:\n{customer_intention}\n\nReview:\n{review}"),
        ]),
    }

    return prompts.get((prompt_num, rag), prompts[(0, False)])


def get_rag_response_prompt() -> ChatPromptTemplate:
    """RAG 응답용 프롬프트 반환"""
    return ChatPromptTemplate.from_messages([
        ("system",
         "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
         "When composing your reply, consider 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention'. "
         "The given 'Responder Name' and 'Contact Information' must be included. "
         "Additionally, use the following pieces of retrieved context to answer the question.\n"
         "Context: {context}"),
        ("human",
         "Responder Name:\n{company_name}\n\nContact:\n{contact}\n\n"
         "Customer Sentiment:\n{sentiment}\n\nCustomer Emotion:\n{emotion}\n\n"
         "Customer Intention:\n{intention}\n\nReview:\n{review}")
    ])


def get_simple_response_prompt() -> ChatPromptTemplate:
    """간단 응답용 프롬프트 반환"""
    return ChatPromptTemplate.from_messages([
        ("system",
         "As a marketing manager managing online customer reviews, write a response to the following 'Review'.\n\n"
         "When composing your reply, consider 'Customer Sentiment', 'Customer Emotion' and 'Customer Intention'."),
        ("human",
         "Customer Sentiment:\n{sentiment}\n\nCustomer Emotion:\n{emotion}\n\n"
         "Customer Intention:\n{intention}\n\nReview:\n{review}")
    ])


# ============================================================================
# Result Mappings (Korean translations)
# ============================================================================

SENTIMENT_MAPPING = {
    "Positive": "긍정",
    "Neutral": "중립",
    "Negative": "부정",
}

EMOTION_MAPPING = {
    "Anger": "화남",
    "Disgust": "역겨움",
    "Fear": "공포",
    "Happiness": "행복",
    "Contempt": "조소",
    "Sadness": "슬픔",
    "Surprise": "놀람",
    "Neutral": "중립"
}

INTENTION_MAPPING = {
    "Complaint": "항의",
    "Expressing Dissatisfaction": "불만족 표출",
    "Warning Others": "타인에게 경고",
    "Feedback": "피드백",
    "Sharing Experience": "경험 공유",
    "Expressing Satisfaction": "만족감 표출",
    "Praise": "칭찬",
    "Recommendation": "추천"
}

URGENCY_MAPPING = {
    "Urgent": "긴급함",
    "Medium": "중간",
    "Not Urgent": "긴급하지않음",
}


def translate_analysis_result(analysis: ReviewAnalysis, urgency: Optional[UrgencyAnalysis] = None) -> dict:
    """
    분석 결과를 한국어로 변환

    Args:
        analysis: 리뷰 분석 결과
        urgency: 긴급도 분석 결과 (선택)

    Returns:
        한국어로 번역된 분석 결과 딕셔너리
    """
    result = {
        'User_Sentiment': SENTIMENT_MAPPING.get(analysis.User_Sentiment, analysis.User_Sentiment),
        'User_Emotion': EMOTION_MAPPING.get(analysis.User_Emotion, analysis.User_Emotion),
        'User_Intention': INTENTION_MAPPING.get(analysis.User_Intention, analysis.User_Intention),
    }

    if urgency:
        result['Review_Urgency'] = URGENCY_MAPPING.get(urgency.Urgency_Level, urgency.Urgency_Level)

    return result
