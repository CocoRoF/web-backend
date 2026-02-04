"""
HSK Model Module Functions

LLM 기반 분류 모듈
"""
import os
import json
from functools import lru_cache
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser, JsonOutputParser

from ....config import settings

# API 키 설정
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


def item_extracter(
    text: str,
    model: str = "gpt-4o-2024-05-13",
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
    category: str = Field(description="the name of category")
    relevance: float = Field(description="the relevance score of the category")


@lru_cache(maxsize=4096)
def ChapterSimilarityExtracter(
    text: str,
    model: str = "gpt-4o-2024-05-13",
    temperature: float = 0,
) -> Dict[str, any]:
    """
    LLM으로 제품 카테고리 분류 (15개 섹션)

    Args:
        text: 제품명
        model: 사용할 OpenAI 모델
        temperature: 모델 온도

    Returns:
        카테고리와 관련도
    """
    categories = """'Live animals, animal products',
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
'Arms and ammunition, miscellaneous manufactured articles, works of art'"""

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         f"You are an expert in categorizing products (or services) based on given categories. "
         f"Below is a list of 15 categories and the name of a product (or service). "
         f"Please rank the top 1 categories that are most related to that product and provide "
         f"a relevance score between 0.000 and 1.000, rounded to three decimal places. "
         f"\n\nCategories:\n{categories}"
         f"\n\nFormatting Instruction: {{format_instructions}}"),
        ("human", "the product (or service): {text}")
    ])

    parser = JsonOutputParser(pydantic_object=ChapterSimilarity)
    llm = ChatOpenAI(model=model, temperature=temperature)
    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
        return result
    except Exception as e:
        print(f"Error Occur, Please Check. Error: {e}")
        return {"category": "", "relevance": 0.0}


@lru_cache(maxsize=16384)
def LLMSimilarityExtracter(
    text: str,
    model: str = "gpt-4o-2024-05-13",
    temperature: float = 0,
    category_list: Optional[str] = None,
) -> Dict[str, any]:
    """
    동적 카테고리로 제품 분류

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
         "You are an expert in categorizing products (or services) based on given categories. "
         "Below is a list of categories and the name of a product (or service). "
         "Please rank the top 1 categories that are most related to that product and provide "
         "a relevance score between 0.000 and 1.000, rounded to three decimal places. "
         "\n\nCategories:\n{category_list}"
         "\n\nFormatting Instruction:\n{format_instructions}"),
        ("human", "the product (or service): {text}")
    ])

    parser = JsonOutputParser(pydantic_object=ChapterSimilarity)
    llm = ChatOpenAI(model=model, temperature=temperature)
    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "text": text,
            "category_list": category_list,
            "format_instructions": parser.get_format_instructions()
        })
        return result
    except Exception as e:
        print(f"Error Occur, Please Check. Error: {e}")
        return {"category": "", "relevance": 0.0}


@lru_cache(maxsize=8192)
def LLMSimilarityExtracter_OutFunc(
    text: str,
    model: str = "gpt-4o-2024-05-13",
    temperature: float = 0,
    category_list: Optional[str] = None,
) -> Dict[str, any]:
    """
    OpenAI Function Calling으로 분류

    Args:
        text: 제품명
        model: 사용할 OpenAI 모델
        temperature: 모델 온도
        category_list: JSON 형식의 카테고리 리스트

    Returns:
        카테고리와 관련도
    """
    category_list_conver = json.loads(category_list) if category_list else []

    output_function = [{
        "name": "Categorizer",
        "description": "Cetegorize the product",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": category_list_conver,
                    "description": "The name of category",
                },
                "relevance": {
                    "type": "string",
                    "description": "A string value between '0' and '1', representing the relevance score",
                },
            },
            "required": ["category", "relevance"],
        },
    }]

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert in categorizing products (or services) based on given categories. "
         "Below is a list of categories and the name of a product (or service). "
         "Please rank the top 1 categories that are most related to that product and provide "
         "a relevance score between 0.000 and 1.000, rounded to three decimal places. "
         "\n\nCategories:\n{category_list}"),
        ("human", "the product (or service): {text}")
    ])

    parser = JsonOutputFunctionsParser()
    llm = ChatOpenAI(model=model, temperature=temperature).bind(
        function_call={"name": "Categorizer"},
        functions=output_function
    )
    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "text": text,
            "category_list": category_list,
        })
        return result
    except Exception as e:
        print(f"Error Occur, Please Check. Error: {e}")
        return {"category": "", "relevance": "0.0"}
