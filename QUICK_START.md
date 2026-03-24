# 🚀 빠른 시작 가이드 (Quick Start)

## 📥 1단계: 프로젝트 다운로드

```bash
# Windows PowerShell / Mac Terminal / Linux
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer
```

## 🔧 2단계: 로컬 환경 설정

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 의존성 설치
cd backend
pip install -r requirements.txt
cd ..

# 환경 변수 설정
cp .env.example .env
# .env 파일을 메모장/VS Code로 열어서 API 키 등 수정
```

## 🚀 3단계: 로컬 실행

### 터미널 1 (백엔드):
```bash
cd backend
python real_data_server.py
```

### 터미널 2 (프론트엔드):
```bash
cd frontend/public
python -m http.server 3000
```

### 접속:
- 🌐 프론트엔드: http://localhost:3000/excel_upload.html
- 📚 API 문서: http://localhost:8000/docs
- ✅ Health Check: http://localhost:8000/health

## 🌍 무료 호스팅 옵션

### 🌟 추천: Render.com (무료 750시간/월)
1. https://render.com 접속 → Sign Up (GitHub 연동)
2. New → Web Service
3. GitHub 리포지토리 선택: `mgdwok-stack/KH-BMS`
4. 브랜치: `genspark_ai_developer`
5. Build Command: `cd backend && pip install -r requirements.txt`
6. Start Command: `cd backend && python real_data_server.py`
7. Environment Variables 설정:
   - `DATABASE_URL`: `sqlite:///./data/bidbot.db`
   - `PROCUREMENT_API_KEY`: (당신의 API 키)
   - `DEBUG`: `False`
8. Create Web Service 클릭!

### 대안 1: Railway.app ($5 무료 크레딧)
- https://railway.app → New Project → Deploy from GitHub

### 대안 2: PythonAnywhere (무료 티어)
- https://www.pythonanywhere.com → Web 탭 → Add a new web app

### 대안 3: Fly.io (무료 티어)
- https://fly.io → 터미널에서 `fly launch` 명령어 실행

## 📋 필수 파일 확인

프로젝트에 다음 파일들이 포함되어 있습니다:
- ✅ `backend/requirements.txt` (Python 의존성)
- ✅ `Procfile` (배포 설정)
- ✅ `runtime.txt` (Python 버전)
- ✅ `.env.example` (환경 변수 템플릿)
- ✅ `data/bidbot.db` (샘플 데이터 300건)

## 🔑 환경 변수 (.env 파일)

```ini
DATABASE_URL=sqlite:///./data/bidbot.db
PROCUREMENT_API_KEY=6a63fc31e3729cdf7b858f69c5987ff9a4626b4546556cd94168e31a413f3bbe
PROCUREMENT_API_BASE_URL=http://apis.data.go.kr/1230000/ScsbidInfoService
APP_NAME=Bid-Bot Clone
DEBUG=True  # 배포 시 False로 변경
SECRET_KEY=your-secret-key-here-change-this
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 🐛 문제 해결

### Python 모듈 없음
```bash
pip install -r backend/requirements.txt
```

### 데이터베이스 파일 없음
```bash
mkdir -p data
# bidbot.db는 GitHub에서 자동으로 다운로드됨
```

### CORS 오류
`.env` 파일에서 `ALLOWED_ORIGINS`에 프론트엔드 URL 추가

### 포트 충돌
백엔드 포트 변경: `python real_data_server.py --port 8001`

## 📚 상세 문서

- 📖 **완벽 가이드**: `ANTIGRAVITY_MIGRATION_GUIDE.md`
- 🔑 **API 키 설정**: `API_KEY_UPDATE_GUIDE.md`
- 🔧 **문제 해결**: `API_TROUBLESHOOTING.md`
- 📋 **프로젝트 구조**: `README.md`

## 🔗 유용한 링크

- GitHub: https://github.com/mgdwok-stack/KH-BMS
- Pull Request: https://github.com/mgdwok-stack/KH-BMS/pull/1
- Render.com: https://render.com
- Railway.app: https://railway.app
- PythonAnywhere: https://www.pythonanywhere.com
- Fly.io: https://fly.io

## 💡 팁

1. **로컬 테스트 먼저**: 배포하기 전에 로컬에서 먼저 실행해보세요!
2. **API 키 보안**: `.env` 파일은 절대 GitHub에 업로드하지 마세요! (이미 `.gitignore`에 포함됨)
3. **무료 티어 한도**: 각 플랫폼의 무료 티어 한도를 확인하세요.
4. **데이터베이스**: SQLite는 로컬/개발용, 프로덕션은 PostgreSQL 권장.
5. **로그 확인**: 배포 후 로그를 확인하여 오류를 체크하세요.

---

**작성일**: 2026-03-06  
**버전**: 1.0.0  
**프로젝트**: KH-BMS 입찰 예측 시스템
