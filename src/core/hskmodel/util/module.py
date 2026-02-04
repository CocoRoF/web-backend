"""
HSK Model Module Functions

LangChain 1.0+ 호환 LLM 기반 분류 모듈
with_structured_output() 사용
"""
import os
import json
from functools import lru_cache
from typing import Dict, List, Optional, Literal

from pydantic import BaseModel, Field, create_model
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser

from ....config import settings

# API 키 설정
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


def item_extracter(
    text: str,
    model: str = "gpt-4o",
    temperature: float = 0,
    print_result: bool = False,
) -> List[str]:
    """
    회사 설명에서 판매 품목 추출

    Args:
        text: 회사 설명 텍스트
        model: 사용할 OpenAI 모델
        temperature: 모델 온도
        print_result: 결과 출력 여부

    Returns:
        추출된 품목 리스트
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "The following are descriptions of specific companies. "
         "Figure out what they sell (or offer) and list them all. "
         "Return the results as a comma seperated list."),
        ("human", "{text}")
    ])

    llm = ChatOpenAI(model=model, temperature=temperature)
    chain = prompt | llm | CommaSeparatedListOutputParser()
    result = chain.invoke({"text": text})

    if print_result:
        print(result)

    return result


class ChapterSimilarity(BaseModel):
    """챕터 유사도 스키마"""
    category: str = Field(description="The name of category")
    relevance: float = Field(
        description="The relevance score of the category between 0.000 and 1.000",
        ge=0.0,
        le=1.0
    )


# 15개 카테고리 상수
CATEGORIES_15 = [
    'Live animals, animal products',
    'Vegetable products',
    'Animals or vegetable fats and oils, prepared foodstuffs',
    'Mineral products',
    'Products of the chemical or allied industries',
    'Plastics and articles thereof, and rubber and articles thereof',
    'Raw hides and skins, leather, furskins and articles thereof',
    'Wood and articles of wood, pulp of wood',
    'Textile and textile articles',
    'Footwear, hats, wigs, articles made of stone, ceramics',
    'Base metals and articles thereof',
    'Machineries, electrical machinery and equipment and parts thereof, sound recorders and reproducers, television and parts thereof',
    'Vehicles, aircraft, vessels and associated transport equipment',
    'Optical, photographic instruments and apparatus, watches, musical instruments',
    'Arms and ammunition, miscellaneous manufactured articles, works of art',
]


@lru_cache(maxsize=4096)
def ChapterSimilarityExtracter(
    text: str,
    model: str = "gpt-4o",
    temperature: float = 0,
) -> Dict[str, any]:
    """
    LLM으로 제품 카테고리 분류 (15개 섹션) - with_structured_output 사용

    Args:
        text: 제품명
        model: 사용할 OpenAI 모델
        temperature: 모델 온도

    Returns:
        카테고리와 관련도
    """
    categories_str = "\n".join(f"- {cat}" for cat in CATEGORIES_15)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         f"You are an expert in categorizing products (or services) based on given categories.\n"
         f"Below is a list of 15 categories and the name of a product (or service).\n"
         f"Please rank the top 1 categories that are most related to that product and provide "
         f"a relevance score between 0.000 and 1.000, rounded to three decimal places.\n\n"
         f"Categories:\n{categories_str}"),
        ("human", "The product (or service): {text}")
    ])

    llm = ChatOpenAI(model=model, temperature=temperature)
    structured_llm = llm.with_structured_output(ChapterSimilarity)
    chain = prompt | structured_llm

    try:
        result = chain.invoke({"text": text})
        return {"category": result.category, "relevance": result.relevance}
    except Exception as e:
        print(f"Error Occur, Please Check. Error: {e}")
        return {"category": "", "relevance": 0.0}


@lru_cache(maxsize=16384)
def LLMSimilarityExtracter(
    text: str,
    model: str = "gpt-4o",
    temperature: float = 0,
    category_list: Optional[str] = None,
) -> Dict[str, any]:
    """
    동적 카테고리로 제품 분류 - with_structured_output 사용

    Args:
        text: 제품명
        model: 사용할 OpenAI 모델
        temperature: 모델 온도
        category_list: JSON 형식의 카테고리 리스트

    Returns:
        카테고리와 관련도
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert in categorizing products (or services) based on given categories.\n"
         "Below is a list of categories and the name of a product (or service).\n"
         "Please rank the top 1 categories that are most related to that product and provide "
         "a relevance score between 0.000 and 1.000, rounded to three decimal places.\n\n"
         "Categories:\n{category_list}"),
        ("human", "The product (or service): {text}")
    ])

    llm = ChatOpenAI(model=model, temperature=temperature)
    structured_llm = llm.with_structured_output(ChapterSimilarity)
    chain = prompt | structured_llm

    try:
        result = chain.invoke({
            "text": text,
            "category_list": category_list,
        })
        return {"category": result.category, "relevance": result.relevance}
    except Exception as e:
        print(f"Error Occur, Please Check. Error: {e}")
        return {"category": "", "relevance": 0.0}


def _create_dynamic_category_schema(categories: List[str]) -> type[BaseModel]:
    """
    동적 카테고리 리스트로 Pydantic 스키마 생성

    Args:
        categories: 카테고리 리스트

    Returns:
        동적으로 생성된 Pydantic BaseModel 클래스
    """
    if not categories:
        return ChapterSimilarity

    # Literal 타입으로 enum-like 제약 생성
    category_literal = Literal[tuple(categories)]  # type: ignore

    DynamicCategorySimilarity = create_model(
        'DynamicCategorySimilarity',
        category=(category_literal, Field(description="The name of category")),
        relevance=(float, Field(
            description="The relevance score between 0.000 and 1.000",
            ge=0.0,
            le=1.0
        )),
    )

    return DynamicCategorySimilarity


@lru_cache(maxsize=8192)
def LLMSimilarityExtracter_OutFunc(
    text: str,
    model: str = "gpt-4o",
    temperature: float = 0,
    category_list: Optional[str] = None,
) -> Dict[str, any]:
    """
    동적 카테고리로 제품 분류 (LangChain 1.0+ with_structured_output)

    이전 function_call 방식에서 with_structured_output 방식으로 마이그레이션

    Args:
        text: 제품명
        model: 사용할 OpenAI 모델
        temperature: 모델 온도
        category_list: JSON 형식의 카테고리 리스트

    Returns:
        카테고리와 관련도
    """
    category_list_parsed = json.loads(category_list) if category_list else []

    # 동적 스키마 생성 (카테고리 리스트가 있으면 Literal로 제약)
    if category_list_parsed:
        # 카테고리가 있으면 동적 스키마 사용
        DynamicSchema = _create_dynamic_category_schema(category_list_parsed)
    else:
        DynamicSchema = ChapterSimilarity

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert in categorizing products (or services) based on given categories.\n"
         "Below is a list of categories and the name of a product (or service).\n"
         "Please rank the top 1 categories that are most related to that product and provide "
         "a relevance score between 0.000 and 1.000, rounded to three decimal places.\n\n"
         "Categories:\n{category_list}"),
        ("human", "The product (or service): {text}")
    ])

    llm = ChatOpenAI(model=model, temperature=temperature)
    structured_llm = llm.with_structured_output(DynamicSchema)
    chain = prompt | structured_llm

    try:
        result = chain.invoke({
            "text": text,
            "category_list": category_list or "",
        })
        # Pydantic 모델이므로 속성으로 접근
        return {
            "category": result.category,
            "relevance": str(result.relevance) if isinstance(result.relevance, (int, float)) else result.relevance
        }
    except Exception as e:
        print(f"Error Occur, Please Check. Error: {e}")
        return {"category": "", "relevance": "0.0"}
