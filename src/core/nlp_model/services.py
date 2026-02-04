"""
Blog Content Generation Services

LangChain 1.0+ 호환 AI 기반 블로그 콘텐츠 생성 서비스
"""
import os
from typing import List, AsyncGenerator, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from ...config import settings

# API 키 설정
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


async def generate_blog_content_stream(
    subject: str,
    reference_urls: Optional[List[str]] = None,
    additional_prompt: str = "",
    model: str = "gpt-4o",
) -> AsyncGenerator[str, None]:
    """
    AI 블로그 콘텐츠 스트리밍 생성 (LangChain 1.0+ 호환)

    Args:
        subject: 블로그 주제
        reference_urls: 참조 URL 목록
        additional_prompt: 추가 프롬프트
        model: 사용할 모델

    Yields:
        생성된 콘텐츠 청크
    """
    # 참조 컨텍스트 구성
    context = ""
    if reference_urls:
        try:
            import httpx
            from bs4 import BeautifulSoup

            for url in reference_urls[:3]:  # 최대 3개 URL
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, timeout=10)
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # 메인 콘텐츠 추출
                        for script in soup(["script", "style", "nav", "footer", "header"]):
                            script.decompose()

                        text = soup.get_text(separator='\n', strip=True)
                        context += f"\n\n--- Reference from {url} ---\n{text[:2000]}"
                except Exception:
                    continue
        except ImportError:
            pass

    # 프롬프트 구성
    system_prompt = """You are an expert technical blog writer.
Write a comprehensive, well-structured blog post in Markdown format.
Include:
- A compelling title with # heading
- An introduction
- Main sections with ## headings
- Code examples where appropriate
- A conclusion
- Use proper Markdown formatting

The blog should be informative, engaging, and SEO-friendly.
Write in Korean if the subject is in Korean, otherwise in English."""

    if context:
        system_prompt += f"\n\nReference Context:\n{context}"

    if additional_prompt:
        system_prompt += f"\n\nAdditional Instructions: {additional_prompt}"

    # LLM 호출 (LangChain 1.0+ 스트리밍 방식)
    llm = ChatOpenAI(
        model=model,
        temperature=0.7,
        streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Write a blog post about: {subject}")
    ])

    chain = prompt | llm

    # LangChain 1.0+ astream 사용
    async for chunk in chain.astream({"subject": subject}):
        if hasattr(chunk, 'content') and chunk.content:
            yield chunk.content


async def generate_blog_content(
    subject: str,
    reference_urls: Optional[List[str]] = None,
    additional_prompt: str = "",
    model: str = "gpt-4o",
) -> str:
    """
    AI 블로그 콘텐츠 일괄 생성 (비스트리밍)

    Args:
        subject: 블로그 주제
        reference_urls: 참조 URL 목록
        additional_prompt: 추가 프롬프트
        model: 사용할 모델

    Returns:
        생성된 전체 블로그 콘텐츠
    """
    content_parts = []
    async for chunk in generate_blog_content_stream(
        subject=subject,
        reference_urls=reference_urls,
        additional_prompt=additional_prompt,
        model=model,
    ):
        content_parts.append(chunk)

    return "".join(content_parts)
