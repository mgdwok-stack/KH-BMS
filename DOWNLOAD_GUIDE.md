# 📥 프로젝트 다운로드 가이드

## 🎯 두 가지 다운로드 방법

---

## ✅ 방법 1: GitHub ZIP 다운로드 (가장 쉬움!) ⭐⭐⭐⭐⭐

### 직접 다운로드 링크 (클릭 한 번!):

```
https://github.com/mgdwok-stack/KH-BMS/archive/refs/heads/genspark_ai_developer.zip
```

**↑ 위 링크를 브라우저 주소창에 복사-붙여넣기 하면 바로 다운로드 시작! ↑**

### 또는 GitHub 웹사이트에서:

1. **GitHub 리포지토리 접속**:
   ```
   https://github.com/mgdwok-stack/KH-BMS
   ```

2. **브랜치 변경**:
   - 상단 왼쪽 "main" 버튼 클릭
   - "genspark_ai_developer" 선택

3. **다운로드**:
   - 초록색 **"Code"** 버튼 클릭
   - **"Download ZIP"** 클릭

4. **압축 풀기**:
   - 다운로드된 `KH-BMS-genspark_ai_developer.zip` 파일
   - 우클릭 → 압축 풀기 (또는 "Extract All")
   - 원하는 폴더에 압축 해제 (예: 바탕화면, 내문서 등)

---

## 📂 방법 2: Git 클론 (개발자용)

### Windows (PowerShell / CMD):

```powershell
# 1. Git 설치 확인 (없으면 https://git-scm.com/ 에서 설치)
git --version

# 2. 원하는 폴더로 이동 (예: 바탕화면)
cd Desktop

# 3. Git 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git

# 4. 프로젝트 폴더로 이동
cd KH-BMS

# 5. 브랜치 전환
git checkout genspark_ai_developer

# 6. 완료! 파일 확인
dir
```

### Mac / Linux (Terminal):

```bash
# 1. Git 설치 확인
git --version

# 2. 원하는 폴더로 이동
cd ~/Desktop

# 3. Git 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git

# 4. 프로젝트 폴더로 이동
cd KH-BMS

# 5. 브랜치 전환
git checkout genspark_ai_developer

# 6. 완료! 파일 확인
ls -la
```

---

## 🗂️ 다운로드 후 폴더 구조

```
KH-BMS-genspark_ai_developer/
│
├── backend/                          # 백엔드 (FastAPI)
│   ├── app/
│   │   ├── main.py                  # API 서버 엔트리포인트
│   │   ├── config.py                # 설정
│   │   ├── database.py              # DB 연결
│   │   ├── api/                     # API 라우터
│   │   │   ├── bids.py              # 입찰 API
│   │   │   ├── predictions.py       # 예측 API
│   │   │   └── analytics.py         # 분석 API
│   │   ├── models/                  # DB 모델
│   │   ├── schemas/                 # Pydantic 스키마
│   │   ├── services/                # 비즈니스 로직
│   │   │   ├── excel_parser.py     # 엑셀 파싱
│   │   │   └── data_collector.py   # 데이터 수집
│   │   └── ml/                      # ML 모델
│   ├── real_data_server.py          # 서버 실행 파일 ⭐
│   └── requirements.txt             # Python 패키지 목록
│
├── frontend/                         # 프론트엔드 (HTML/JS)
│   └── public/
│       ├── index.html               # 메인 페이지
│       ├── excel_upload.html        # 엑셀 업로드 페이지 ⭐
│       ├── styles.css               # 스타일
│       └── scripts.js               # JavaScript
│
├── data/                             # 데이터
│   ├── bidbot.db                    # SQLite DB (샘플 300건)
│   └── uploads/                     # 업로드된 파일
│
├── docs/                             # 문서
│   ├── GOOGLE_CLOUD_DEPLOYMENT.md   # Google Cloud 가이드
│   ├── ANTIGRAVITY_MIGRATION_GUIDE.md # 무료 호스팅 가이드
│   ├── QUICK_START.md               # 빠른 시작
│   └── API_KEY_UPDATE_GUIDE.md      # API 키 설정
│
├── .env.example                      # 환경 변수 템플릿
├── Dockerfile                        # Docker 설정
├── Procfile                          # 배포 설정
├── firebase.json                     # Firebase 설정
└── README.md                         # 프로젝트 설명
```

---

## 📊 다운로드 파일 크기

- **전체 프로젝트**: 약 5~10 MB
- **데이터베이스** (bidbot.db): 약 500 KB
- **백엔드 코드**: 약 2 MB
- **프론트엔드 코드**: 약 500 KB
- **문서**: 약 1 MB

---

## 🚀 다운로드 후 바로 실행하기

### Step 1: Python 가상 환경 설정

**Windows**:
```powershell
# 다운받은 폴더로 이동
cd Desktop\KH-BMS-genspark_ai_developer

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
venv\Scripts\activate

# 의존성 설치
cd backend
pip install -r requirements.txt
```

**Mac/Linux**:
```bash
# 다운받은 폴더로 이동
cd ~/Desktop/KH-BMS-genspark_ai_developer

# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 의존성 설치
cd backend
pip install -r requirements.txt
```

### Step 2: 환경 변수 설정

```bash
# 프로젝트 루트로 이동
cd ..

# .env 파일 생성
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env

# .env 파일 편집 (메모장, VS Code 등)
notepad .env  # Windows
nano .env     # Mac/Linux
```

**.env 파일 내용**:
```ini
DATABASE_URL=sqlite:///./data/bidbot.db
PROCUREMENT_API_KEY=6a63fc31e3729cdf7b858f69c5987ff9a4626b4546556cd94168e31a413f3bbe
PROCUREMENT_API_BASE_URL=http://apis.data.go.kr/1230000/ScsbidInfoService
APP_NAME=Bid-Bot Clone
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Step 3: 실행

**터미널 1 (백엔드)**:
```bash
cd backend
python real_data_server.py
```

**터미널 2 (프론트엔드)**:
```bash
cd frontend/public
python -m http.server 3000
```

**브라우저 접속**:
- 프론트엔드: http://localhost:3000/excel_upload.html
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 🔑 중요 파일 위치

### 실행 파일:
- **백엔드 서버**: `backend/real_data_server.py`
- **엑셀 업로드 페이지**: `frontend/public/excel_upload.html`

### 설정 파일:
- **환경 변수**: `.env` (생성 필요)
- **Python 패키지**: `backend/requirements.txt`
- **Docker 설정**: `Dockerfile`

### 데이터:
- **SQLite DB**: `data/bidbot.db` (샘플 300건 포함)
- **업로드 폴더**: `data/uploads/`

### 문서:
- **빠른 시작**: `QUICK_START.md`
- **Google Cloud 배포**: `GOOGLE_CLOUD_DEPLOYMENT.md`
- **무료 호스팅**: `ANTIGRAVITY_MIGRATION_GUIDE.md`
- **API 키 설정**: `API_KEY_UPDATE_GUIDE.md`

---

## 📚 모든 다운로드 링크

### GitHub:
- **전체 ZIP**: https://github.com/mgdwok-stack/KH-BMS/archive/refs/heads/genspark_ai_developer.zip
- **웹에서 보기**: https://github.com/mgdwok-stack/KH-BMS/tree/genspark_ai_developer
- **Pull Request**: https://github.com/mgdwok-stack/KH-BMS/pull/1
- **Git 클론**: `git clone https://github.com/mgdwok-stack/KH-BMS.git`

### 개별 파일 다운로드 (필요 시):
- **README**: https://github.com/mgdwok-stack/KH-BMS/blob/genspark_ai_developer/README.md
- **QUICK_START**: https://github.com/mgdwok-stack/KH-BMS/blob/genspark_ai_developer/QUICK_START.md
- **Dockerfile**: https://github.com/mgdwok-stack/KH-BMS/blob/genspark_ai_developer/Dockerfile
- **requirements.txt**: https://github.com/mgdwok-stack/KH-BMS/blob/genspark_ai_developer/backend/requirements.txt

---

## 🛠️ Git이 없는 경우

### Git 설치:
- **Windows**: https://git-scm.com/download/win
- **Mac**: `brew install git` 또는 Xcode Command Line Tools
- **Linux**: `sudo apt install git` (Ubuntu/Debian)

### Git 없이 다운로드:
- 위의 **방법 1 (ZIP 다운로드)** 사용 ← **추천!**

---

## ✅ 다운로드 완료 확인

다운로드가 제대로 되었는지 확인:

```bash
# 폴더 이동
cd KH-BMS-genspark_ai_developer

# 주요 파일 확인
ls backend/real_data_server.py     # 백엔드 서버
ls frontend/public/excel_upload.html  # 프론트엔드
ls data/bidbot.db                  # 데이터베이스
ls .env.example                    # 환경 변수 템플릿
ls Dockerfile                      # Docker 설정
ls QUICK_START.md                  # 빠른 시작 가이드

# 모두 존재하면 성공! ✅
```

---

## 🎉 다음 단계

### 1. 로컬 실행 (무료):
- `QUICK_START.md` 파일 참고
- Python 가상 환경 설정
- 백엔드 + 프론트엔드 실행

### 2. Google Cloud 배포:
- `GOOGLE_CLOUD_DEPLOYMENT.md` 참고
- Cloud Run 배포 (무료 2백만 요청/월)

### 3. 다른 무료 호스팅:
- `ANTIGRAVITY_MIGRATION_GUIDE.md` 참고
- Render.com, Railway.app 등

---

## 🆘 문제 해결

### 문제 1: ZIP 파일이 열리지 않음

**해결**:
- Windows: 7-Zip 또는 WinRAR 설치
- Mac: The Unarchiver 설치
- Linux: `unzip KH-BMS-genspark_ai_developer.zip`

### 문제 2: Git 클론이 느림

**해결**:
- ZIP 다운로드 사용 (방법 1)
- 또는 GitHub Desktop 사용: https://desktop.github.com/

### 문제 3: 파일이 안 보임

**확인**:
- 압축을 제대로 풀었는지 확인
- 숨김 파일 표시 활성화 (`.env`, `.git` 등)
- 올바른 브랜치 (`genspark_ai_developer`) 다운로드했는지 확인

---

## 📞 추가 도움

궁금한 점이 있으면:
- GitHub Issues: https://github.com/mgdwok-stack/KH-BMS/issues
- Pull Request: https://github.com/mgdwok-stack/KH-BMS/pull/1
- 문서 참고: `QUICK_START.md`, `GOOGLE_CLOUD_DEPLOYMENT.md`

---

**작성일**: 2026-03-06  
**프로젝트**: KH-BMS 입찰 예측 시스템  
**GitHub**: https://github.com/mgdwok-stack/KH-BMS  
**브랜치**: genspark_ai_developer
