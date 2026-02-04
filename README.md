# FastAPI Backend

Django REST Framework에서 마이그레이션된 FastAPI 백엔드 프로젝트입니다.

## 🚀 시작하기

### 필수 요구사항
- Python 3.11+
- PostgreSQL
- uv (Python package manager)

### 설치

1. **uv 설치** (설치되어 있지 않은 경우)
```bash
pip install uv
```

2. **가상환경 생성 및 의존성 설치**
```bash
# 프로젝트 디렉토리로 이동
cd workspace

# uv로 가상환경 생성
uv venv

# 의존성 설치
uv sync
```

3. **환경변수 설정**
```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 편집하여 실제 값 입력
```

4. **데이터베이스 마이그레이션**
```bash
# 가상환경 활성화
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Alembic 마이그레이션 실행
alembic upgrade head
```

5. **서버 실행**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 프로젝트 구조

```
workspace/
├── pyproject.toml          # 프로젝트 설정 및 의존성
├── alembic.ini             # Alembic 마이그레이션 설정
├── .env.example            # 환경변수 예시
├── README.md               # 이 파일
├── src/
│   ├── main.py             # FastAPI 앱 진입점
│   ├── config.py           # 설정 관리
│   ├── database.py         # 데이터베이스 연결
│   ├── dependencies.py     # 의존성 주입
│   ├── core/               # 핵심 모듈 (NLP, HSK 등)
│   │   ├── hskmodel/       # HS 코드 매칭 모델
│   │   └── nlp_model/      # NLP 모델
│   ├── models/             # SQLAlchemy 모델
│   ├── schemas/            # Pydantic 스키마
│   ├── routers/            # API 라우터
│   │   ├── blog.py
│   │   ├── hrjang.py
│   │   ├── hskmap.py
│   │   ├── lawchaser.py
│   │   └── rara.py
│   └── services/           # 비즈니스 로직
├── data/                   # 데이터 파일
│   ├── blog_posts/         # 블로그 마크다운 파일
│   └── hskmodel/           # HS 코드 데이터
├── media/                  # 업로드된 미디어 파일
├── static/                 # 정적 파일
├── migrations/             # Alembic 마이그레이션
└── tests/                  # 테스트 파일
```

## 🔌 API 엔드포인트

### Health Check
- `GET /health` - 서버 상태 확인

### Blog API (`/api/blog`)
- `POST /api/blog/image/upload/` - 이미지 업로드
- `POST /api/blog/post/` - 블로그 포스트 생성
- `GET /api/blog/post/{pk}` - 특정 포스트 조회
- `GET /api/blog/post/list/` - 포스트 목록
- `GET /api/blog/contents/` - 마크다운 콘텐츠 조회
- `POST /api/blog/new-post/` - 새 포스트 생성
- `GET /api/blog/ai-generate-stream/` - AI 콘텐츠 생성 (SSE)

### HRJang API (`/api/hrjang`)
- `POST /api/hrjang/comment` - 댓글 생성
- `GET /api/hrjang/comments` - 댓글 목록
- `DELETE /api/hrjang/comments/{id}` - 댓글 삭제

### HSKMap API (`/api/hskmap`)
- `POST /api/hskmap/basic/` - HS 코드 매칭

### LawChaser API (`/api/lawchaser`)
- `POST /api/lawchaser/lawlist/` - 법률 목록 조회
- `POST /api/lawchaser/oldnew/` - 구/신조문 비교
- `POST /api/lawchaser/artchaser/` - 기사 조회

### Rara API (`/api/rara`)
- `POST /api/rara/basic/` - 기본 AI 응답
- `POST /api/rara/custom/` - 커스텀 AI 응답
- `POST /api/rara/rating/` - 평점 저장
- `POST /api/rara/survey/` - 설문 저장

## 📖 API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 개발

### 린팅 및 포맷팅
```bash
# Ruff로 린팅
ruff check src/

# 자동 수정
ruff check src/ --fix

# 타입 체크
mypy src/
```

### 테스트
```bash
# 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src
```

## 📄 라이선스

MIT License
