"""
HSK Model Tools

임베딩, 유사도 계산, 웹 크롤링 등 유틸리티 함수
"""
import os
import re
import json
from typing import Dict, List, Optional, Union, Any

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

from ....config import settings

# API 키 설정
os.environ["OPENAI_API_KEY"] = settings.openai_api_key

# 임베딩 캐시
embedding_cache: Dict[str, List[float]] = {}


def get_embedding(text: str) -> List[float]:
    """
    OpenAI 임베딩 생성

    Args:
        text: 임베딩할 텍스트

    Returns:
        임베딩 벡터
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


def MapHS(data: Union[pd.DataFrame, List[Dict]]) -> Union[pd.DataFrame, List[Dict]]:
    """
    HS 코드 매핑

    Args:
        data: DataFrame 또는 딕셔너리 리스트

    Returns:
        HS 코드가 매핑된 데이터
    """
    from pathlib import Path

    map_dict_path = Path(__file__).parent.parent / "data" / "map_dict.json"

    if not map_dict_path.exists():
        return data

    with open(map_dict_path, 'r', encoding='utf-8') as f:
        loaded_dict = json.load(f)

    if isinstance(data, pd.DataFrame):
        print("Received a DataFrame")
        a = 0
        for idx in data.index:
            code = str(data.loc[idx, "CODE"])
            try:
                data.at[idx, "HS_Map"] = loaded_dict[code]
                data.at[idx, "HS_Map_02"] = sorted(set([item[:2] for item in data.loc[idx, "HS_Map"]]))
                data.at[idx, "HS_Map_04"] = sorted(set([item[:4] for item in data.loc[idx, "HS_Map"]]))
                a += 1
            except Exception as e:
                data.at[idx, "HS_Map"] = np.nan
                data.at[idx, "HS_Map_02"] = np.nan
                data.at[idx, "HS_Map_04"] = np.nan
                print(f"No Data {idx}, error: {e}")

        print(f"Done. Success = {a}, Fail = {len(data)-a}")
        return data

    elif isinstance(data, list):
        print("Received a JSON-like dictionary")
        a = 0
        for n in range(len(data)):
            code = str(data[n]["CODE"])
            try:
                data[n]["HS_Map"] = loaded_dict[code]
                data[n]["HS_Map_02"] = sorted(set([item[:2] for item in data[n]["HS_Map"]]))
                data[n]["HS_Map_04"] = sorted(set([item[:4] for item in data[n]["HS_Map"]]))
                a += 1
            except Exception as e:
                data[n]["HS_Map"] = []
                data[n]["HS_Map_02"] = []
                data[n]["HS_Map_04"] = []
                print(f"No Data {n}, error: {e}")

        return data
    else:
        raise ValueError("Unsupported type")


def get_similarities(
    text: str,
    text_list: Optional[List[str]] = None,
    example: Optional[str] = None,
    top_n: int = 1
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    코사인 유사도 계산
    """
    if example == "chapter":
        text_list = [
            "Live animals, animal products",
            "Vegetable products",
            "Animals or vegetable fats and oils, prepared foodstuffs",
            "Mineral products",
            "Products of the chemical or allied industries",
            "Plastics and articles thereof, and rubber and articles thereof",
            "Raw hides and skins, leather, furskins and articles thereof",
            "Wood and articles of wood, pulp of wood",
            "Textile and textile articles",
            "Footwear, hats, wigs, articles made of stone, ceramics",
            "Base metals and articles thereof",
            "Machineries, electrical machinery and equipment and parts thereof, sound recorders and reproducers, television and parts thereof",
            "Vehicles, aircraft, vessels and associated transport equipment",
            "Optical, photographic instruments and apparatus, watches, musical instruments",
            "Arms and ammunition, miscellaneous manufactured articles, works of art"
        ]

    if text_list is None and example is None:
        print("No Text_List and Example. Need at least one arguments")
        return None

    reference_embedding = get_embedding(text)
    similarities = []

    for category in text_list:
        category_embedding = get_embedding(category)
        similarity = cosine_similarity([reference_embedding], [category_embedding])[0][0]
        similarities.append((category, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_n_list = similarities[:top_n]

    if top_n == 1:
        return {"category": top_n_list[0][0], "relevance": round(top_n_list[0][1], 3)}
    else:
        return [{"category": cat, "relevance": round(sim, 3)} for cat, sim in top_n_list]


def get_similarities_cache(
    text: str,
    text_list: Optional[List[str]] = None,
    example: Optional[str] = None,
    top_n: int = 1,
    result_key: str = "category",
    result_value: str = "relevance"
) -> Dict[str, Any]:
    """
    캐싱된 유사도 계산
    """
    global embedding_cache

    if example == "chapter":
        text_list = [
            "Live animals, animal products",
            "Vegetable products",
            "Animals or vegetable fats and oils, prepared foodstuffs",
            "Mineral products",
            "Products of the chemical or allied industries",
            "Plastics and articles thereof, and rubber and articles thereof",
            "Raw hides and skins, leather, furskins and articles thereof",
            "Wood and articles of wood, pulp of wood",
            "Textile and textile articles",
            "Footwear, hats, wigs, articles made of stone, ceramics",
            "Base metals and articles thereof",
            "Machineries, electrical machinery and equipment and parts thereof, sound recorders and reproducers, television and parts thereof",
            "Vehicles, aircraft, vessels and associated transport equipment",
            "Optical, photographic instruments and apparatus, watches, musical instruments",
            "Arms and ammunition, miscellaneous manufactured articles, works of art"
        ]

    if text_list is None and example is None:
        print("No Text_List and Example. Need at least one arguments")
        return {}

    # 레퍼런스 임베딩
    if text in embedding_cache:
        reference_embedding = embedding_cache[text]
    else:
        reference_embedding = get_embedding(text)
        embedding_cache[text] = reference_embedding

    # 카테고리 임베딩
    category_embeddings = []
    for category in text_list:
        if category in embedding_cache:
            category_embedding = embedding_cache[category]
        else:
            category_embedding = get_embedding(category)
            embedding_cache[category] = category_embedding
        category_embeddings.append(category_embedding)

    similarities = cosine_similarity([reference_embedding], category_embeddings)[0]

    sorted_indices = np.argsort(similarities)[::-1]
    top_n_indices = sorted_indices[:top_n]
    top_n_list = [(text_list[i], similarities[i]) for i in top_n_indices]

    if top_n == 1:
        return {result_key: top_n_list[0][0], result_value: round(top_n_list[0][1], 3)}
    else:
        return [{result_key: cat, result_value: round(sim, 3)} for cat, sim in top_n_list]


def Chapter_selector(category_name: str) -> List[str]:
    """
    카테고리별 챕터 목록 반환
    """
    section_list = [
        "Live animals, animal products",
        "Vegetable products",
        "Animals or vegetable fats and oils, prepared foodstuffs",
        "Mineral products",
        "Products of the chemical or allied industries",
        "Plastics and articles thereof, and rubber and articles thereof",
        "Raw hides and skins, leather, furskins and articles thereof",
        "Wood and articles of wood, pulp of wood",
        "Textile and textile articles",
        "Footwear, hats, wigs, articles made of stone, ceramics",
        "Base metals and articles thereof",
        "Machineries, electrical machinery and equipment and parts thereof, sound recorders and reproducers, television and parts thereof",
        "Vehicles, aircraft, vessels and associated transport equipment",
        "Optical, photographic instruments and apparatus, watches, musical instruments",
        "Arms and ammunition, miscellaneous manufactured articles, works of art"
    ]

    chapter_mapping = {
        section_list[0]: [
            "Live Animals",
            "Meat and edible meat offal",
            "Fish and crustaceans, molluscs and other aquatic invertebrates",
            "Dairy produce; birds' eggs; natural honey; edible products of animal origin, not elsewhere specified or included",
            "Products of animal origin, not elsewhere specified or included",
        ],
        section_list[1]: [
            "Live trees and other plants; bulbs, roots and the like; cut flowers and ornamental foliage",
            "Edible vegetables and certain roots and tubers",
            "Edible fruit and nuts; peel of citrus fruits or melons",
            "Coffee, tea, mate and spices",
            "Cereals",
            "Products of the milling industry; malt; starches; inulin; wheat gluten",
            "Oil seeds and oleaginous fruits; miscellaneous grains, seeds and fruit; industrial or medicinal plants; straw and fodder",
            "Lac; gums, resins and other vegetable saps and extracts",
            "Vegetable plaiting materials; vegetable products not elsewhere specified or included"
        ],
        section_list[2]: [
            "Animal or vegetable fats and oil and their cleavage products; prepared edible fats; animal or vegetable waxes",
            "Preparations of meat, of fish or of crustaceans, molluscs or other aquatic invertebrates",
            "Sugars and sugar confectionery",
            "Cocoa and cocoa preparations",
            "Preparations of cereals, flour, starch or milk; pastry cooks' products",
            "Preparations of vegetables, fruit, nuts or other parts of plants",
            "Miscellaneous edible preparations",
            "Beverages, spirits and vinegar",
            "Residues and waste from the food industries; prepared animal fodder",
            "Tobacco and manufactured tobacco substitutes"
        ],
        section_list[3]: [
            "Salt; sulphur, earths and stones; plastering materials, lime and cement",
            "Ores, slag and ash",
            "Mineral fuels, mineral oils and products of their distillation; bituminous substances; mineral waxes"
        ],
        section_list[4]: [
            "Inorganic chemicals; organic or inorganic compounds of precious metals, of rare-earth metals, of radioactive elements or of isotopes",
            "Organic chemicals",
            "Pharmaceutical products",
            "Fertilizers",
            "Tanning or dyeing extracts; tannins and their derivatives; dyes, pigments and other colouring matter, paints and varnishes; putty and other mastics; inks",
            "Essential oils and resinoids; perfumery, cosmetic or toilet preparations",
            "Soap, organic surface-active agents, washing preparations, lubricating preparations, artificial waxes, prepared waxes, polishing or scouring preparations, candles and similar articles, modelling pastes, 'dental waxes' and dental preparations with a basis",
            "Albuminoidal substances; modified starches; glues; enzymes",
            "Explosives; pyrotechnic products; matches; pyrophoric alloys; certain combustible preparations",
            "Photographic or cinematographic goods",
            "Miscellaneous chemical products",
        ],
        section_list[5]: [
            "Plastics and articles thereof",
            "Rubber and articles thereof",
        ],
        section_list[6]: [
            "Raw hides and skins (other than furskins) and leather",
            "Articles of leather; saddlery and harness; travel goods, handbags and similar containers; articles of animal gut (other than silk-worm gut)",
            "Furskins and artificial fur, manufactures thereof"
        ],
        section_list[7]: [
            "Wood and Articles of wood; wood charcoal",
            "Cork and articles of cork",
            "Manufactures of straw, of esparto or of other plaiting materials; basket-ware and wickerwork",
            "Pulp of wood or of other fibrous cellulosic material; recovered (waste and scrap) paper or paperboard",
            "Paper and paperboard; articles of paper pulp, of paper or of paperboard",
            "Printed books, newspapers, pictures and other products of the printing industry; manuscripts, typescripts and plans",
        ],
        section_list[8]: [
            "Silk",
            "Wool, fine or coarse animal hair; horse hair yarn and woven fabric",
            "Cotton",
            "Other vegetable textile fibres; paper yarn and woven fabrics of paper yarn",
            "Man-made filaments",
            "Man-made staple fibres",
            "Wadding, felt and non-wovens; special yarns; twine, cordage, ropes and cables and articles thereof",
            "Carpets and other textile floor coverings",
            "Special woven fabrics; tufted textile fabrics; lace; tapestries; trimmings; embroidery",
            "Impregnated, coated, covered or laminated textile fabrics; textile articles of a kind suitable for industrial use",
            "Knitted or crocheted fabrics",
            "Articles of apparel and clothing accessories knitted or crocheted",
            "Articles of apparel and clothing accessories, not knitted or crocheted",
            "Other made up textile articles; sets; worn clothing and worn textile articles; rags"
        ],
        section_list[9]: [
            "Footwear, gaiters and the like; parts of such articles",
            "Headgear and parts thereof",
            "Umbrellas, sun umbrellas, walking-sticks, seat-sticks, whips, riding-crops and parts thereof",
            "Prepared feathers and down and articles made of feathers or of down; artificial flowers; articles of human hair",
            "Articles of stone, plaster, cement, asbestos, mica or similar materials",
            "Ceramic products",
            "Glass and glassware",
            "Natural or cultured pearls, precious or semi-precious stones, precious metals, metals clad with precious metal and articles thereof; immitation jewellery; coin"
        ],
        section_list[10]: [
            "Iron and steel",
            "Articles of iron or steel",
            "Copper and articles thereof",
            "Nickel and articles thereof",
            "Aluminium and articles thereof",
            "Lead and articles thereof",
            "Zinc and articles thereof",
            "Tin and articles thereof",
            "Other base metals; cermets; articles thereof",
            "Tools, implements, cutlery, spoons and forks, of base metal; parts thereof of base metal",
            "Miscellaneous articles of base metal"
        ],
        section_list[11]: [
            "Nuclear reactors, boilers, machinery and mechanical appliances; parts thereof",
            "Electrical machinery and equipment and parts thereof; sound recorders and reproducers, television image and sound recorders and reproducers, and parts and accessories of such articles"
        ],
        section_list[12]: [
            "Railway or tramway locomotives, rolling-stock and parts thereof; railway or tramway track fixtures and fittings and parts thereof; mechanical (including electro-mechanical) traffic signalling equipment of all kinds",
            "Vehicles other than railway or tramway rolling-stock, and parts and accessories thereof",
            "Aircraft, spacecraft, and parts thereof",
            "Ships, boats and floating structures",
        ],
        section_list[13]: [
            "Optical, photographic, cinematographic, measuring, checking, precision, medical or surgical instruments and apparatus; parts and accessories thereof",
            "Clocks and watches and parts thereof",
            "Musical instruments; parts and accessories of such articles"
        ],
        section_list[14]: [
            "Arms and ammunition; parts and accessories thereof",
            "Furniture; bedding, mattresses, mattress supports, cushions and similar stuffed furnishings; lamps and lighting fittings, not elsewhere specified or included; illuminated signs, illuminated name-plates and the like; prefabricated buildings",
            "Toys, games and sports requisites; parts and accessories thereof",
            "Miscellaneous manufactured articles",
            "Works of art, collectors' pieces and antiques"
        ],
    }

    return chapter_mapping.get(category_name, [])


def code_ten_extracter(code_four: str) -> List[Dict[str, Any]]:
    """
    KITA 웹사이트에서 HS10 코드 크롤링
    """
    if not code_four:
        return []

    data = []

    for idx in range(1, 10):
        previous_length = len(data)
        url = f"https://fta.kita.net/hsCode?pageIndex={idx}&mnSn=207&scGbn=hskCd&scKwrd={code_four}"

        try:
            result = requests.get(url, timeout=10)
            result.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")
            return data

        soup = BeautifulSoup(result.text, 'html.parser')
        tbody = soup.find('tbody', id="hskCodeTbody")

        if tbody is None:
            print("Error: Could not find tbody element.")
            return data

        rows = tbody.find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                key = cells[0].text.strip()
                key_four = key[:4]
                value1 = cells[1].text.strip()
                value1 = re.sub(r'제\d+류\s*', '', value1)
                value2 = cells[2].text.strip()
                value3 = cells[3].text.strip()

                if key_four == code_four:
                    data.append({
                        key: {
                            'HS_2_kor': value1,
                            'HS_4_kor': value2,
                            'HS_10_kor': value3
                        }
                    })

        if previous_length == len(data):
            break

    return data


def final_hsten_extractor(
    isic_data: Dict[str, Any],
    data_list: List[Dict[str, Any]]
) -> List[str]:
    """
    최종 HS10 코드 추출 (ISIC 포함)
    """
    final_hs10_code_list = []

    try:
        isic_02 = isic_data.get("HS02", [])
        isic_04 = isic_data.get("HS04", [])
    except (KeyError, TypeError):
        isic_02 = []
        isic_04 = []

    # 여러 조건으로 반복 시도
    conditions = [
        lambda c, e4, e10: c[:4] in isic_04 and c in e10,
        lambda c, e4, e10: c[:4] in isic_04 and c[:4] == e4,
        lambda c, e4, e10: c[:2] in isic_02,
        lambda c, e4, e10: c[:4] == e4,
        lambda c, e4, e10: True,
    ]

    for condition in conditions:
        for data in data_list:
            contents = data.get("Contents", {})

            try:
                llm_10_list = contents.get("LLM_HS10_List", [])
            except:
                continue

            emb_10_list = contents.get("Emb_HS10_List", [])
            emb_4 = contents.get("Emb_HS04")

            for code_10 in llm_10_list:
                if condition(code_10, emb_4, emb_10_list):
                    final_hs10_code_list.append(code_10)

        final_hs10_code_list = list(set(final_hs10_code_list))
        if len(final_hs10_code_list) >= len(data_list):
            return final_hs10_code_list

    return final_hs10_code_list


def final_hsten_extractor_noisic(data_list: List[Dict[str, Any]]) -> List[str]:
    """
    최종 HS10 코드 추출 (ISIC 없음)
    """
    final_hs10_code_list = []

    # 여러 조건으로 반복 시도
    for data in data_list:
        contents = data.get("Contents", {})

        try:
            llm_10_list = contents.get("LLM_HS10_List", [])
            emb_10_list = contents.get("Emb_HS10_List", [])
        except:
            continue

        for code_10 in llm_10_list:
            if code_10 in emb_10_list:
                final_hs10_code_list.append(code_10)

    final_hs10_code_list = list(set(final_hs10_code_list))
    if len(final_hs10_code_list) >= len(data_list):
        return final_hs10_code_list

    # 두 번째 조건
    for data in data_list:
        contents = data.get("Contents", {})

        try:
            llm_10_list = contents.get("LLM_HS10_List", [])
            emb_4 = contents.get("Emb_HS04")
        except:
            continue

        for code_10 in llm_10_list:
            if code_10[:4] == emb_4:
                final_hs10_code_list.append(code_10)

    final_hs10_code_list = list(set(final_hs10_code_list))
    if len(final_hs10_code_list) >= len(data_list):
        return final_hs10_code_list

    # 세 번째 조건
    for data in data_list:
        contents = data.get("Contents", {})

        try:
            llm_10_list = contents.get("LLM_HS10_List", [])
            emb_2 = contents.get("Emb_HS02")
        except:
            continue

        for code_10 in llm_10_list:
            if code_10[:2] == emb_2:
                final_hs10_code_list.append(code_10)

    final_hs10_code_list = list(set(final_hs10_code_list))
    if len(final_hs10_code_list) >= len(data_list):
        return final_hs10_code_list

    # 모든 코드 추가
    for data in data_list:
        contents = data.get("Contents", {})

        try:
            llm_10_list = contents.get("LLM_HS10_List", [])
        except:
            continue

        for code_10 in llm_10_list:
            final_hs10_code_list.append(code_10)

    return list(set(final_hs10_code_list))
