"""
HSK Code Matching Model

Django에서 마이그레이션된 HS 코드 매칭 핵심 로직
"""
import json
from pathlib import Path
from typing import Tuple, List, Dict, Any

from .util.tools import (
    MapHS, 
    get_similarities, 
    get_similarities_cache, 
    Chapter_selector, 
    code_ten_extracter, 
    final_hsten_extractor, 
    final_hsten_extractor_noisic
)
from .util.module import (
    item_extracter, 
    ChapterSimilarityExtracter, 
    LLMSimilarityExtracter, 
    LLMSimilarityExtracter_OutFunc
)

# 데이터 파일 경로
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

CHAPTER_PATH = DATA_DIR / "chapter_dict.json"
HEADER_PATH = DATA_DIR / "header_dict.json"
HS10_PATH = DATA_DIR / "hs10_dict_5.json"
MAPDICT_PATH = DATA_DIR / "map_dict.json"

# 데이터 로드 (지연 로딩)
_chap_dict = None
_head_dict = None
_hs10_dict = None
_isic_map_dict = None


def _load_data():
    """데이터 파일 로드"""
    global _chap_dict, _head_dict, _hs10_dict, _isic_map_dict
    
    if _chap_dict is None:
        if CHAPTER_PATH.exists():
            with open(CHAPTER_PATH, 'r', encoding='utf-8') as f:
                _chap_dict = json.load(f)
        else:
            _chap_dict = {}
            
    if _head_dict is None:
        if HEADER_PATH.exists():
            with open(HEADER_PATH, 'r', encoding='utf-8') as f:
                _head_dict = json.load(f)
        else:
            _head_dict = {}
            
    if _hs10_dict is None:
        if HS10_PATH.exists():
            with open(HS10_PATH, 'r', encoding='utf-8') as f:
                _hs10_dict = json.load(f)
        else:
            _hs10_dict = {}
            
    if _isic_map_dict is None:
        if MAPDICT_PATH.exists():
            with open(MAPDICT_PATH, 'r', encoding='utf-8') as f:
                _isic_map_dict = json.load(f)
        else:
            _isic_map_dict = {}


def get_descriptions(data: Dict, key: str) -> List[str]:
    """딕셔너리에서 설명 추출"""
    descriptions = []
    for item in data.get(key, []):
        for k, v in item.items():
            descriptions.append(v)
    return descriptions


def get_code_by_description(data: Dict, key: str, description: str) -> str | None:
    """설명으로 코드 조회"""
    for item in data.get(key, []):
        for k, v in item.items():
            if v == description:
                return k
    return None


def isic_map(isic: str) -> Dict[str, Any]:
    """ISIC 코드를 HS 코드로 매핑"""
    _load_data()
    
    try:
        result_total = sorted(set(_isic_map_dict[isic]))
        result_hs02 = sorted(set(item[:2] for item in result_total))
        result_hs04 = sorted(set(item[:4] for item in result_total))
    except KeyError:
        result_total = None
        result_hs02 = None
        result_hs04 = None

    return {"Total": result_total, "HS02": result_hs02, "HS04": result_hs04}


def hscode_matching_model(
    ISIC_code: str, 
    Desc: str
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[str]]:
    """
    HS 코드 매칭 모델 실행
    
    Args:
        ISIC_code: ISIC 코드 (빈 문자열이면 ISIC 없이 매칭)
        Desc: 제품/회사 설명
        
    Returns:
        Tuple of (isic_data, result_list, final_result)
    """
    _load_data()
    
    result_list = []
    item_list = item_extracter(Desc)
    
    print(f"{len(item_list)} Items Remain")
    
    progress = 0
    for item in item_list:
        progress += 1
        temp_dict = {}
        temp_dict["Item_Name"] = item
        
        # 첫 번째 레벨: 섹션 분류
        first_chapter_relevance_emb = get_similarities_cache(
            item, 
            example="chapter", 
            result_key="Emb_Section", 
            result_value="Emb_Section_Relevance"
        )
        temp_dict["Contents"] = first_chapter_relevance_emb
        
        first_chapter_relevance_llm = ChapterSimilarityExtracter(item)
        temp_dict["Contents"]["LLM_Section"] = first_chapter_relevance_llm["category"]
        temp_dict["Contents"]["LLM_Section_Relevance"] = first_chapter_relevance_llm["relevance"]
        
        # 두 번째 레벨: 챕터 분류
        emb_chapter_list = Chapter_selector(first_chapter_relevance_emb["Emb_Section"])
        second_result_emb = get_similarities_cache(
            item, 
            text_list=emb_chapter_list, 
            result_key="Emb_Chapter", 
            result_value="Emb_Chapter_Relevance"
        )
        temp_dict["Contents"]["Emb_Chapter"] = second_result_emb["Emb_Chapter"]
        temp_dict["Contents"]["Emb_Chapter_Relevance"] = second_result_emb["Emb_Chapter_Relevance"]
        emb_code_02 = _chap_dict.get(second_result_emb["Emb_Chapter"], "00")
        temp_dict["Contents"]["Emb_HS02"] = emb_code_02
        
        llm_chapter_list = Chapter_selector(first_chapter_relevance_llm["category"])
        category_list_str = "[" + ", ".join(f'"{i}"' for i in llm_chapter_list) + "]"
        second_result_llm = LLMSimilarityExtracter(item, category_list=category_list_str)
        temp_dict["Contents"]["LLM_Chapter"] = second_result_llm["category"]
        temp_dict["Contents"]["LLM_Chapter_Relevance"] = second_result_llm["relevance"]
        llm_code_02 = _chap_dict.get(second_result_llm["category"], "00")
        temp_dict["Contents"]["LLM_HS02"] = llm_code_02
        
        # 세 번째 레벨: 헤더 분류
        emb_header_list = get_descriptions(_head_dict, emb_code_02)
        third_result_emb = get_similarities_cache(
            item, 
            text_list=emb_header_list, 
            result_key="header", 
            result_value="header_relevance"
        )
        temp_dict["Contents"]["Emb_Heading"] = third_result_emb["header"]
        temp_dict["Contents"]["Emb_Heading_Relevance"] = third_result_emb["header_relevance"]
        emb_code_04 = get_code_by_description(_head_dict, emb_code_02, third_result_emb['header'])
        temp_dict["Contents"]["Emb_HS04"] = emb_code_04
        
        llm_header_list = get_descriptions(_head_dict, llm_code_02)
        header_list_str = "[" + ", ".join(f'"{i}"' for i in llm_header_list) + "]"
        third_result_llm = LLMSimilarityExtracter_OutFunc(item, category_list=header_list_str)
        temp_dict["Contents"]["LLM_Heading"] = third_result_llm["category"]
        temp_dict["Contents"]["LLM_Heading_Relevance"] = third_result_llm["relevance"]
        llm_code_04 = get_code_by_description(_head_dict, llm_code_02, third_result_llm['category'])
        temp_dict["Contents"]["LLM_HS04"] = llm_code_04
        
        # 네 번째 레벨: HS10 코드 추출
        try:
            hs10_data_emb = _hs10_dict[emb_code_04]
        except (KeyError, TypeError):
            hs10_data_emb = code_ten_extracter(emb_code_04) if emb_code_04 else []
            if emb_code_04 and emb_code_04 not in _hs10_dict:
                _hs10_dict[emb_code_04] = hs10_data_emb
                # 파일 저장 (선택적)
                try:
                    with open(HS10_PATH, 'w', encoding='utf-8') as f:
                        json.dump(_hs10_dict, f, ensure_ascii=False, indent=4)
                except Exception:
                    pass
                    
        if hs10_data_emb:
            emb_hs10_list = list(set([
                list(item_data.values())[0]['HS_10_kor'] 
                for item_data in hs10_data_emb
            ]))
            final_result_emb = get_similarities_cache(
                item, 
                text_list=emb_hs10_list, 
                result_key="hs10_desc", 
                result_value="hs10_desc_relevance"
            )
            temp_dict["Contents"]["Emb_HS10"] = final_result_emb['hs10_desc']
            temp_dict["Contents"]["Emb_HS10_Relevance"] = final_result_emb['hs10_desc_relevance']
            emb_hs10_result_list = [
                list(item_data.keys())[0] 
                for item_data in hs10_data_emb 
                if list(item_data.values())[0]['HS_10_kor'] == final_result_emb['hs10_desc']
            ]
            temp_dict["Contents"]["Emb_HS10_List"] = emb_hs10_result_list
        
        try:
            hs10_data_llm = _hs10_dict[llm_code_04]
        except (KeyError, TypeError):
            hs10_data_llm = code_ten_extracter(llm_code_04) if llm_code_04 else []
            if llm_code_04 and llm_code_04 not in _hs10_dict:
                _hs10_dict[llm_code_04] = hs10_data_llm
                try:
                    with open(HS10_PATH, 'w', encoding='utf-8') as f:
                        json.dump(_hs10_dict, f, ensure_ascii=False, indent=4)
                except Exception:
                    pass
                    
        if hs10_data_llm:
            llm_hs10_list = list(set([
                list(item_data.values())[0]['HS_10_kor'] 
                for item_data in hs10_data_llm
            ]))
            llm_hs10_list_str = "[" + ", ".join(f'"{i}"' for i in llm_hs10_list) + "]"
            final_result_llm = LLMSimilarityExtracter_OutFunc(item, category_list=llm_hs10_list_str)
            temp_dict["Contents"]["LLM_HS10"] = final_result_llm['category']
            temp_dict["Contents"]["LLM_HS10_Relevance"] = final_result_llm['relevance']
            llm_hs10_result_list = [
                list(item_data.keys())[0] 
                for item_data in hs10_data_llm 
                if list(item_data.values())[0]['HS_10_kor'] == final_result_llm['category']
            ]
            temp_dict["Contents"]["LLM_HS10_List"] = llm_hs10_result_list
        
        pro_percent = progress / len(item_list)
        print(f"Progress: {pro_percent:.2%}")
        result_list.append(temp_dict)
    
    # 최종 결과 추출
    if ISIC_code == "":
        isic_data = {"Total": [], "HS02": [], "HS04": []}
        final_result = final_hsten_extractor_noisic(result_list)
    else:
        isic_data = isic_map(ISIC_code)
        final_result = final_hsten_extractor(isic_data, result_list)
    
    return isic_data, result_list, final_result
