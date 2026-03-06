# 🚀 Antigravity(안티그래비티) 프로젝트 이전 가이드

## 📋 목차
1. [Antigravity란?](#antigravity란)
2. [프로젝트 구조 이해](#프로젝트-구조-이해)
3. [GitHub에서 다운로드](#github에서-다운로드)
4. [Antigravity 설정](#antigravity-설정)
5. [로컬 환경 구축](#로컬-환경-구축)
6. [실행 방법](#실행-방법)
7. [문제 해결](#문제-해결)

---

## 🎯 Antigravity란?

**Antigravity**는 무료 또는 저렴한 비용으로 웹 애플리케이션을 호스팅할 수 있는 플랫폼입니다.

### 주요 특징:
- ✅ **무료 티어 제공** (제한적이지만 개발/테스트 가능)
- ✅ **Python/Node.js 지원**
- ✅ **GitHub 연동** (자동 배포)
- ✅ **데이터베이스 지원** (SQLite, PostgreSQL)
- ✅ **환경 변수 관리**

### 대안 플랫폼:
만약 Antigravity가 적합하지 않다면 다음 무료 대안도 고려하세요:
- **Render.com** (무료 티어, Python/Node.js 지원)
- **Railway.app** (무료 $5 크레딧)
- **Fly.io** (무료 티어)
- **PythonAnywhere** (Python 전용, 무료 티어)
- **Vercel** (프론트엔드 무료, API Functions 지원)
- **Netlify** (프론트엔드 무료, Serverless Functions)

---

## 📁 프로젝트 구조 이해

현재 프로젝트는 다음과 같이 구성되어 있습니다:

```
/home/user/webapp/
│
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py            # FastAPI 엔트리포인트
│   │   ├── config.py          # 설정 파일
│   │   ├── database.py        # DB 연결
│   │   ├── api/               # API 라우터
│   │   ├── models/            # DB 모델
│   │   ├── schemas/           # Pydantic 스키마
│   │   └── ml/                # ML 모델
│   ├── real_data_server.py    # 실제 데이터 서버
│   └── requirements.txt       # Python 의존성
│
├── frontend/                   # HTML/JS 프론트엔드
│   └── public/
│       ├── index.html         # 메인 페이지
│       ├── excel_upload.html  # 엑셀 업로드 페이지
│       └── *.js, *.css        # JS/CSS 파일
│
├── data/                       # 데이터 디렉토리
│   ├── bidbot.db              # SQLite 데이터베이스 (300건 샘플)
│   └── uploads/               # 업로드된 파일
│
├── .env                        # 환경 변수 (API 키 등)
├── .env.example               # 환경 변수 템플릿
└── README.md                  # 프로젝트 설명
```

### 핵심 파일:
- **백엔드 실행**: `backend/real_data_server.py` 또는 `backend/app/main.py`
- **프론트엔드**: `frontend/public/*.html` (정적 파일)
- **데이터베이스**: `data/bidbot.db` (SQLite)
- **설정**: `.env` (API 키, DB 경로 등)

---

## 📥 GitHub에서 다운로드

### Step 1: GitHub 리포지토리 확인

현재 프로젝트는 다음 GitHub에 있습니다:
```
https://github.com/mgdwok-stack/KH-BMS
브랜치: genspark_ai_developer
```

### Step 2: 로컬 PC에 Git 클론

#### Windows (PowerShell 또는 CMD):
```powershell
# 1. 원하는 폴더로 이동 (예: 바탕화면)
cd Desktop

# 2. Git 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git

# 3. 프로젝트 폴더로 이동
cd KH-BMS

# 4. genspark_ai_developer 브랜치로 전환
git checkout genspark_ai_developer
```

#### Mac/Linux (Terminal):
```bash
# 1. 원하는 폴더로 이동
cd ~/Desktop

# 2. Git 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git

# 3. 프로젝트 폴더로 이동
cd KH-BMS

# 4. 브랜치 전환
git checkout genspark_ai_developer
```

### Step 3: 파일 확인

```bash
# 파일 목록 확인
ls -la

# 예상 출력:
# backend/
# frontend/
# data/
# .env.example
# README.md
# ...
```

---

## 🔧 로컬 환경 구축 (Antigravity 전에 먼저 테스트)

Antigravity에 배포하기 전에 **로컬에서 먼저 실행**해보는 것이 좋습니다!

### Step 1: Python 설치 확인

```bash
# Python 버전 확인 (3.8 이상 필요)
python --version
# 또는
python3 --version

# 출력 예시: Python 3.10.12
```

Python이 없으면 설치:
- **Windows**: https://www.python.org/downloads/ 에서 다운로드
- **Mac**: `brew install python3`
- **Linux**: `sudo apt install python3 python3-pip`

### Step 2: 가상 환경 생성 (권장)

```bash
# 프로젝트 폴더에서 실행
cd KH-BMS

# 가상 환경 생성
python -m venv venv
# 또는
python3 -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 활성화되면 프롬프트 앞에 (venv) 표시됨
```

### Step 3: 의존성 설치

```bash
# 백엔드 의존성 설치
cd backend
pip install -r requirements.txt

# 주요 패키지:
# - fastapi (웹 프레임워크)
# - uvicorn (서버)
# - sqlalchemy (DB ORM)
# - pandas (데이터 처리)
# - openpyxl (엑셀 처리)
# - httpx (HTTP 클라이언트)
# - python-dotenv (환경 변수)
```

### Step 4: 환경 변수 설정

```bash
# 프로젝트 루트로 이동
cd ..

# .env.example을 .env로 복사
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env

# .env 파일 편집 (메모장, VS Code 등)
notepad .env
# 또는
code .env
# 또는
nano .env
```

**.env 파일 내용 수정**:
```ini
# 데이터베이스 (SQLite 사용 - 로컬 개발용)
DATABASE_URL=sqlite:///./data/bidbot.db

# Redis (선택사항 - 없어도 작동함)
REDIS_URL=redis://localhost:6379/0

# 나라장터 API (승인 후 키 입력)
PROCUREMENT_API_KEY=6a63fc31e3729cdf7b858f69c5987ff9a4626b4546556cd94168e31a413f3bbe
PROCUREMENT_API_BASE_URL=http://apis.data.go.kr/1230000/ScsbidInfoService

# 앱 설정
APP_NAME=Bid-Bot Clone
APP_VERSION=1.0.0
DEBUG=True

# 보안 (나중에 강력한 키로 변경)
SECRET_KEY=your-secret-key-here-change-this-in-production

# CORS (프론트엔드 주소)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000

# 기타
MODEL_DIR=./models
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### Step 5: 데이터베이스 확인

```bash
# data 폴더 확인
ls data/

# bidbot.db 파일이 있는지 확인
# 있으면: 샘플 데이터 300건 포함
# 없으면: 자동 생성됨 (빈 DB)
```

샘플 데이터베이스를 다운로드하려면:
```bash
# GitHub에서 다운로드 (이미 클론했으면 포함됨)
# 수동 다운로드:
# https://github.com/mgdwok-stack/KH-BMS/blob/genspark_ai_developer/data/bidbot.db
```

---

## 🚀 로컬 실행 방법

### 방법 1: 백엔드만 실행 (API 서버)

```bash
# backend 폴더에서 실행
cd backend

# FastAPI 서버 실행
python real_data_server.py

# 또는
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**접속 URL**:
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 방법 2: 프론트엔드 실행 (HTML 파일)

```bash
# frontend/public 폴더에서 실행
cd frontend/public

# Python 내장 HTTP 서버 사용
python -m http.server 3000

# 또는
python3 -m http.server 3000
```

**접속 URL**:
- 메인 페이지: http://localhost:3000/index.html
- 엑셀 업로드: http://localhost:3000/excel_upload.html

### 방법 3: 백엔드 + 프론트엔드 동시 실행

**터미널 2개 사용**:

**터미널 1 (백엔드)**:
```bash
cd KH-BMS/backend
python real_data_server.py
```

**터미널 2 (프론트엔드)**:
```bash
cd KH-BMS/frontend/public
python -m http.server 3000
```

이제 브라우저에서:
- http://localhost:3000/excel_upload.html 접속
- 백엔드 API (http://localhost:8000)와 통신

---

## 🌐 Antigravity 배포 (무료 호스팅)

### 전제 조건:
- Antigravity 계정 생성 (https://antigravity.com 또는 실제 URL)
- GitHub 리포지토리 연결
- 프로젝트 로컬 테스트 완료 ✅

### Step 1: Antigravity 계정 생성

1. Antigravity 웹사이트 접속
2. **Sign Up** 클릭
3. GitHub 계정으로 로그인 (권장)
4. 무료 티어 선택

### Step 2: 새 프로젝트 생성

1. Dashboard → **New Project**
2. **Connect GitHub Repository** 선택
3. `mgdwok-stack/KH-BMS` 리포지토리 선택
4. 브랜치: `genspark_ai_developer` 선택

### Step 3: 프로젝트 설정

**빌드 설정**:
```yaml
# Build Command (백엔드)
cd backend && pip install -r requirements.txt

# Start Command (백엔드)
cd backend && python real_data_server.py

# 또는
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**환경 변수 설정** (Antigravity Dashboard에서):
```ini
DATABASE_URL=sqlite:///./data/bidbot.db
PROCUREMENT_API_KEY=6a63fc31e3729cdf7b858f69c5987ff9a4626b4546556cd94168e31a413f3bbe
PROCUREMENT_API_BASE_URL=http://apis.data.go.kr/1230000/ScsbidInfoService
APP_NAME=Bid-Bot Clone
DEBUG=False
SECRET_KEY=강력한-랜덤-시크릿-키-여기에
ALLOWED_ORIGINS=https://your-antigravity-url.com
```

**포트 설정**:
- Antigravity가 자동으로 `PORT` 환경 변수 제공
- 백엔드가 `$PORT` 또는 `8000` 포트에서 실행되도록 설정

### Step 4: 프론트엔드 배포 (정적 파일)

**옵션 A: Antigravity 정적 파일 호스팅**
1. `frontend/public` 폴더를 별도 프로젝트로 배포
2. Build Command: `echo "Static files"`
3. Publish Directory: `frontend/public`

**옵션 B: Netlify/Vercel (프론트엔드 전용)**
1. Netlify 또는 Vercel 무료 계정 생성
2. `frontend/public` 폴더 배포
3. 환경 변수에 백엔드 API URL 설정:
   ```
   REACT_APP_API_URL=https://your-backend.antigravity.com
   ```

### Step 5: 배포 확인

1. Antigravity Dashboard에서 배포 로그 확인
2. 배포 완료 후 URL 확인:
   ```
   백엔드: https://kh-bms-backend.antigravity.com
   프론트엔드: https://kh-bms-frontend.antigravity.com
   ```
3. API 문서 접속: `https://your-backend-url.com/docs`
4. Health Check: `https://your-backend-url.com/health`

---

## 🔧 Antigravity 설정 파일 생성

Antigravity에서 자동 배포를 위한 설정 파일을 생성하세요:

### `antigravity.toml` (프로젝트 루트에 생성)

```toml
[build]
  command = "cd backend && pip install -r requirements.txt"
  publish = "backend"

[build.environment]
  PYTHON_VERSION = "3.10"

[[services]]
  name = "backend"
  type = "web"
  
  [services.build]
    command = "pip install -r requirements.txt"
  
  [services.start]
    command = "python real_data_server.py"
  
  [services.envVars]
    PORT = "8000"
    DATABASE_URL = "sqlite:///./data/bidbot.db"
    DEBUG = "False"

[[services]]
  name = "frontend"
  type = "static"
  
  [services.static]
    directory = "frontend/public"
    fallback = "index.html"
```

### `Procfile` (Heroku 스타일 배포용)

```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### `runtime.txt` (Python 버전 지정)

```
python-3.10.12
```

---

## 🛠️ 문제 해결

### 문제 1: 로컬에서 백엔드가 실행 안 됨

**증상**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**해결**:
```bash
# 가상 환경 활성화 확인
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 의존성 재설치
pip install -r backend/requirements.txt
```

### 문제 2: 데이터베이스 파일 없음

**증상**:
```
sqlite3.OperationalError: unable to open database file
```

**해결**:
```bash
# data 폴더 생성
mkdir -p data

# 빈 데이터베이스 생성 (자동)
cd backend
python -c "from app.database import init_db; init_db()"
```

### 문제 3: CORS 오류 (프론트엔드 ↔ 백엔드)

**증상**:
```
Access to fetch at 'http://localhost:8000' has been blocked by CORS policy
```

**해결**:
`.env` 파일에서 CORS 설정 확인:
```ini
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 문제 4: Antigravity 배포 실패

**증상**:
```
Build failed: requirements.txt not found
```

**해결**:
1. `requirements.txt` 경로 확인 (`backend/requirements.txt`)
2. Build Command 수정:
   ```bash
   cd backend && pip install -r requirements.txt
   ```

### 문제 5: 환경 변수가 적용 안 됨

**해결**:
1. Antigravity Dashboard → Environment Variables 확인
2. 변수 이름 정확히 입력 (대소문자 구분)
3. 저장 후 **Redeploy** 버튼 클릭

---

## 📚 추가 리소스

### 공식 문서:
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Uvicorn**: https://www.uvicorn.org/

### 무료 호스팅 플랫폼 비교:

| 플랫폼 | 무료 티어 | Python 지원 | DB 지원 | 추천 |
|--------|-----------|-------------|---------|------|
| **Render.com** | ✅ (750시간/월) | ✅ | PostgreSQL | ⭐⭐⭐⭐⭐ |
| **Railway.app** | $5 크레딧 | ✅ | PostgreSQL | ⭐⭐⭐⭐ |
| **Fly.io** | ✅ 제한적 | ✅ | PostgreSQL | ⭐⭐⭐⭐ |
| **PythonAnywhere** | ✅ 제한적 | ✅ | SQLite/MySQL | ⭐⭐⭐ |
| **Vercel** | ✅ 프론트엔드 | Serverless | - | ⭐⭐⭐ (프론트) |
| **Netlify** | ✅ 프론트엔드 | Serverless | - | ⭐⭐⭐ (프론트) |

### 추천 배포 전략:

**전략 1: Render.com (추천 🌟)**
- 백엔드: Render Web Service (무료)
- 프론트엔드: Render Static Site (무료)
- DB: SQLite (포함) 또는 PostgreSQL (무료)

**전략 2: Railway.app**
- 백엔드 + 프론트엔드: Railway (한 프로젝트)
- DB: Railway PostgreSQL
- $5 크레딧으로 1~2개월 무료

**전략 3: 하이브리드**
- 백엔드: Render/Railway (무료)
- 프론트엔드: Netlify/Vercel (무료)
- DB: SQLite (백엔드 포함)

---

## ✅ 체크리스트

프로젝트 이전 전 확인:

### 로컬 테스트:
- [ ] Git 클론 완료 (`git clone`)
- [ ] 가상 환경 생성 및 활성화
- [ ] 의존성 설치 (`pip install -r requirements.txt`)
- [ ] `.env` 파일 생성 및 수정
- [ ] 백엔드 실행 성공 (`python real_data_server.py`)
- [ ] 프론트엔드 실행 성공 (`python -m http.server 3000`)
- [ ] 브라우저에서 접속 확인 (localhost:3000, localhost:8000)
- [ ] API 문서 확인 (localhost:8000/docs)
- [ ] 엑셀 업로드 테스트 (샘플 파일)

### Antigravity 배포:
- [ ] Antigravity 계정 생성
- [ ] GitHub 리포지토리 연결
- [ ] Build Command 설정
- [ ] Start Command 설정
- [ ] 환경 변수 입력 (API 키, DB URL 등)
- [ ] 배포 시작
- [ ] 배포 로그 확인 (오류 없는지)
- [ ] 배포된 URL 접속 확인
- [ ] API 문서 확인 (배포된 URL/docs)
- [ ] 프론트엔드 연결 확인

---

## 🚀 빠른 시작 명령어 모음

```bash
# === 로컬 개발 ===

# 1. 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer

# 2. 가상 환경
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# 3. 설치
cd backend
pip install -r requirements.txt
cd ..

# 4. 환경 변수
cp .env.example .env
nano .env  # 또는 메모장으로 편집

# 5. 실행 (터미널 2개)
# 터미널 1:
cd backend && python real_data_server.py

# 터미널 2:
cd frontend/public && python -m http.server 3000

# 6. 접속
# http://localhost:8000/docs (API)
# http://localhost:3000/excel_upload.html (프론트)
```

---

**작성일**: 2026-03-06  
**작성자**: AI Assistant  
**프로젝트**: KH-BMS (입찰 예측 시스템)  
**GitHub**: https://github.com/mgdwok-stack/KH-BMS  
**브랜치**: genspark_ai_developer
