"""
SQLAlchemy Models

데이터베이스 모델 정의
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Boolean, 
    ForeignKey, func
)
from sqlalchemy.orm import relationship

from ..database import Base


# ==================== Blog Models ====================

class BlogImage(Base):
    """블로그 이미지 모델"""
    __tablename__ = "blog_blogimage"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    image = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())


class BlogPost(Base):
    """블로그 포스트 모델"""
    __tablename__ = "blog_blogpost"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False)  # memorials, knowledge, note
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ==================== HRJang Models ====================

class HrComment(Base):
    """HR 댓글 모델"""
    __tablename__ = "hrjang_hrcommentmodel"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userid = Column(String(10), nullable=False)
    password = Column(String(20), nullable=False)
    title = Column(String(15), nullable=False)
    comment = Column(String(1000), nullable=False)
    time = Column(DateTime, nullable=False)


# ==================== HSKMap Models ====================

class HSKModel(Base):
    """HS 코드 매칭 모델"""
    __tablename__ = "hskmap_hskmodel"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    desc = Column(String(10000), nullable=False)
    isic_code = Column(String(10), nullable=True)
    time = Column(DateTime, nullable=False)


# ==================== LawChaser Models ====================

class LawListCrawledData(Base):
    """법률 목록 크롤링 데이터"""
    __tablename__ = "lawchaser_lawlistcrawleddata"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ls_id = Column(String(10), nullable=False)
    law_name = Column(String(30), nullable=False)
    lsi_seq = Column(String(10), nullable=False)
    anc_yd = Column(Date, nullable=False)  # 공포일
    anc_no = Column(Integer, nullable=False)  # 공포번호
    ef_yd = Column(Date, nullable=False)  # 시행일
    unk_var_1 = Column(String(10), nullable=True)
    unk_var_2 = Column(String(10), nullable=True)
    classify = Column(String(10), nullable=True)


class LawOldNewCrawledData(Base):
    """법률 구/신 조문 크롤링 데이터"""
    __tablename__ = "lawchaser_lawoldnewcrawleddata"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lsi_seq = Column(String(10), nullable=False)
    ls_id = Column(String(10), nullable=False)
    oldnew_sequence = Column(Integer, nullable=False)
    old = Column(String(1000), nullable=False)
    new = Column(String(1000), nullable=False)


# ==================== Rara Models ====================

class RaraModel(Base):
    """Rara AI 응답 모델"""
    __tablename__ = "rara_raramodel"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model = Column(String(30), nullable=False)
    analysis_model = Column(String(30), nullable=True)
    response_method = Column(String(20), nullable=False)
    responder_name = Column(String(50), nullable=True)
    contact = Column(String(1000), nullable=True)
    retrieval = Column(String(100000), nullable=True)
    input_text = Column(String(5000), nullable=False)
    response = Column(String(100000), nullable=True)
    user_rating = Column(Integer, nullable=True)
    time = Column(DateTime, nullable=False)


class RaraSurvey(Base):
    """Rara 설문 모델"""
    __tablename__ = "rara_rarasurvey"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    organization = Column(String(30), nullable=False)
    contact = Column(String(50), nullable=True)
    email = Column(String(50), nullable=True)
    dataidx = Column(Integer, nullable=False)
    select_value = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False)
