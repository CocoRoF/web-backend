"""
NLP Model Prompt Utilities

프롬프트 및 출력 함수 정의
"""
from typing import List, Dict, Any

from langchain.prompts import ChatPromptTemplate


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


def analysis_prompt_selector(prompt_num: int) -> List[Dict[str, Any]]:
    """
    분석 함수 정의 선택
    """
    function_list = [
        [{
            "name": "Describer",
            "description": "Analyze the following Review",
            "parameters": {
                "type": "object",
                "properties": {
                    "User_Sentiment": {
                        "type": "string",
                        "enum": ["Positive", "Neutral", "Negative"],
                        "description": "Sentiment Analysis of the 'Review'",
                    },
                    "User_Emotion": {
                        "type": "string",
                        "enum": ["Anger", "Disgust", "Fear", "Happiness", "Contempt", "Sadness", "Surprise"],
                        "description": "Emotion Analysis of the 'Review'",
                    },
                    "User_Intention": {
                        "type": "string",
                        "enum": ["Complaint", "Expressing Dissatisfaction", "Warning Others", "Feedback",
                                "Sharing Experience", "Expressing Satisfaction", "Praise", "Recommendation"],
                        "description": "Intention Analysis of the 'Review'",
                    },
                },
                "required": ["User_Sentiment", "User_Emotion", "User_Intention"],
            },
        }],
    ]

    return function_list[prompt_num] if prompt_num < len(function_list) else function_list[0]


def Response_output_selector(prompt_num: int) -> List[Dict[str, Any]]:
    """
    응답 출력 함수 선택
    """
    base_response = {
        "name": "Responder",
        "description": "Respond appropriately to the following customer 'Reviews'",
        "parameters": {
            "type": "object",
            "properties": {
                "Responding_to_Customer_Sentiment": {"type": "string", "description": "Responding to Customer Sentiment"},
                "Sentiment_Reason": {"type": "string", "description": "The reason for the sentiment response"},
                "Responding_to_Customer_Emotion": {"type": "string", "description": "Responding to Customer Emotion"},
                "Emotion_Reason": {"type": "string", "description": "The reason for the emotion response"},
                "Responding_to_Customer_Intention": {"type": "string", "description": "Responding to Customer Intention"},
                "Intention_Reason": {"type": "string", "description": "The reason for the intention response"},
                "Final_Response": {"type": "string", "description": "The Final Generated Response"},
            },
            "required": ["Responding_to_Customer_Sentiment", "Sentiment_Reason",
                        "Responding_to_Customer_Emotion", "Emotion_Reason",
                        "Responding_to_Customer_Intention", "Intention_Reason", "Final_Response"],
        },
    }

    if prompt_num == 4:
        return [{
            "name": "Responder",
            "description": "Respond appropriately to the following customer 'Reviews'",
            "parameters": {
                "type": "object",
                "properties": {
                    "Response": {"type": "string", "description": "Response to Customer Review"},
                },
                "required": ["Response"],
            },
        }]

    if prompt_num in [1, 2, 3]:
        base_response["parameters"]["properties"]["Greeting"] = {"type": "string", "description": "Greeting Message"}
        base_response["parameters"]["required"].insert(0, "Greeting")

    if prompt_num == 2:
        base_response["parameters"]["properties"]["Contact_Information"] = {"type": "string", "description": "Contact Information"}
        base_response["parameters"]["required"].append("Contact_Information")

    return [base_response]


def output_function(prompt_name: str = None) -> Dict[str, Any]:
    """
    OpenAI Function 정의 반환
    """
    functions = {
        "sentiment": {
            "name": "Describer",
            "description": "Analyze the following Review",
            "parameters": {
                "type": "object",
                "properties": {
                    "User_Sentiment": {"type": "string", "enum": ["Positive", "Neutral", "Negative"]},
                },
                "required": ["User_Sentiment"],
            },
        },
        "emotion": {
            "name": "Describer",
            "description": "Analyze the following Review",
            "parameters": {
                "type": "object",
                "properties": {
                    "User_Emotion": {"type": "string", "enum": ["Anger", "Disgust", "Fear", "Happiness", "Contempt", "Sadness", "Surprise"]},
                },
                "required": ["User_Emotion"],
            },
        },
        "intention": {
            "name": "Describer",
            "description": "Analyze the following Review",
            "parameters": {
                "type": "object",
                "properties": {
                    "User_Intention": {"type": "string", "enum": ["Complaint", "Expressing Dissatisfaction", "Warning Others", "Feedback", "Sharing Experience", "Expressing Satisfaction", "Praise", "Recommendation"]},
                },
                "required": ["User_Intention"],
            },
        },
        "response": {
            "name": "Describer",
            "description": "Respond appropriately to the following customer 'Reviews'.",
            "parameters": {
                "type": "object",
                "properties": {"Response": {"type": "string"}},
                "required": ["Response"],
            },
        },
        "urgency_level": {
            "name": "Describer",
            "description": "Determine how urgent a given customer's 'Review' is.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Urgency_Level": {"type": "string", "enum": ["Urgent", "Medium", "Not Urgent"]},
                },
                "required": ["Urgency_Level"],
            },
        },
        "zero_response": {
            "name": "Describer",
            "description": "Respond appropriately to the following customer 'Reviews'",
            "parameters": {
                "type": "object",
                "properties": {"Response": {"type": "string", "description": "Response to Customer Review"}},
                "required": ["Response"],
            },
        },
        "total_extraction": {
            "name": "Describer",
            "description": "Analyze the following Review",
            "parameters": {
                "type": "object",
                "properties": {
                    "User_Sentiment": {"type": "string", "enum": ["Positive", "Neutral", "Negative"]},
                    "User_Emotion": {"type": "string", "enum": ["Anger", "Disgust", "Fear", "Happiness", "Contempt", "Sadness", "Surprise", "Neutral"]},
                    "User_Intention": {"type": "string", "enum": ["Complaint", "Expressing Dissatisfaction", "Warning Others", "Feedback", "Sharing Experience", "Expressing Satisfaction", "Praise", "Recommendation"]},
                },
                "required": ["User_Sentiment", "User_Emotion", "User_Intention"],
            },
        },
    }

    if prompt_name not in functions:
        raise ValueError(f"Invalid prompt_name: {prompt_name}. Choose from {list(functions.keys())}")

    return functions[prompt_name]
