# 📥 샌드박스 파일 다운로드 완벽 가이드

## 🎯 다운로드 방법 (3가지)

---

## ✅ 방법 1: GitHub에서 다운로드 (가장 쉬움! ⭐⭐⭐⭐⭐)

**추천 이유**:
- ✅ 모든 코드와 설정 파일이 포함
- ✅ 클릭 한 번으로 다운로드
- ✅ 가장 최신 버전
- ✅ 총 151개 파일 (1.8MB)

### 다운로드 링크:
```
https://github.com/mgdwok-stack/KH-BMS/archive/refs/heads/genspark_ai_developer.zip
```

### 포함된 파일:
- ✅ 백엔드 코드 (`backend/`)
- ✅ 프론트엔드 코드 (`frontend/`)
- ✅ 데이터베이스 (`data/bidbot.db`) - 432 KB
- ✅ 모든 문서 (`.md` 파일들)
- ✅ 설정 파일 (`.env.example`, `Dockerfile`, 등)
- ✅ Git 히스토리 제외 (깔끔함)

### 다운로드 후:
1. ZIP 파일 압축 해제
2. 폴더명: `KH-BMS-genspark_ai_developer`
3. `QUICK_START.md` 파일 참고하여 실행

---

## 📦 방법 2: 개별 파일 다운로드 (GitHub 웹)

특정 파일만 필요한 경우:

### 중요 파일 직접 다운로드:

#### 데이터베이스:
```
https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/data/bidbot.db
```
- 크기: 432 KB
- 포함: 300개 입찰공고 + 266개 낙찰결과

#### 통합 대시보드:
```
https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/frontend/public/index.html
```

#### 엑셀 업로드 페이지:
```
https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/frontend/public/excel_upload.html
```

#### 백엔드 서버:
```
https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/backend/real_data_server.py
```

#### 환경 변수 템플릿:
```
https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/.env.example
```

#### Python 패키지 목록:
```
https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/backend/requirements.txt
```

---

## 🖥️ 방법 3: Git Clone (개발자용)

### Windows (PowerShell):
```powershell
# 원하는 폴더로 이동
cd Desktop

# Git 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git

# 폴더 이동
cd KH-BMS

# 브랜치 전환
git checkout genspark_ai_developer

# 파일 확인
dir
```

### Mac/Linux (Terminal):
```bash
# 원하는 폴더로 이동
cd ~/Desktop

# Git 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git

# 폴더 이동
cd KH-BMS

# 브랜치 전환
git checkout genspark_ai_developer

# 파일 확인
ls -la
```

---

## 📊 다운로드 파일 크기 및 내용

### 전체 프로젝트:
- **압축 파일**: 약 1.8 MB
- **압축 해제 후**: 약 5~10 MB
- **파일 수**: 151개

### 주요 파일 크기:
| 파일 | 크기 | 설명 |
|------|------|------|
| `data/bidbot.db` | 432 KB | SQLite 데이터베이스 |
| `frontend/public/index.html` | 23 KB | 통합 대시보드 |
| `frontend/public/excel_upload.html` | 28 KB | 엑셀 업로드 |
| `backend/real_data_server.py` | 5 KB | 서버 실행 파일 |
| 모든 `.md` 문서 | 약 500 KB | 가이드 문서 |
| 백엔드 코드 | 약 2 MB | Python 코드 |
| 프론트엔드 코드 | 약 500 KB | HTML/CSS/JS |

---

## 🗂️ 다운로드 후 폴더 구조

```
KH-BMS-genspark_ai_developer/
│
├── backend/                          # 백엔드 (FastAPI)
│   ├── app/
│   │   ├── main.py                  # API 엔트리포인트
│   │   ├── api/                     # API 라우터
│   │   ├── models/                  # DB 모델
│   │   ├── services/                # 비즈니스 로직
│   │   └── routes/                  # 라우트
│   ├── real_data_server.py          # 서버 실행 ⭐
│   └── requirements.txt             # Python 패키지
│
├── frontend/public/                  # 프론트엔드
│   ├── index.html                   # 통합 대시보드 ⭐
│   ├── excel_upload.html            # 엑셀 업로드 ⭐
│   ├── dashboard.html               # (기존)
│   └── dashboard_v2.html            # (기존)
│
├── data/
│   ├── bidbot.db                    # SQLite DB ⭐
│   └── uploads/                     # 업로드 폴더
│
├── docs/                             # 문서
│   ├── QUICK_START.md               # 빠른 시작 ⭐
│   ├── DOWNLOAD_GUIDE.md            # 다운로드 가이드 ⭐
│   ├── GOOGLE_CLOUD_DEPLOYMENT.md   # Google Cloud
│   └── ...                          # 기타 문서들
│
├── .env.example                      # 환경 변수 템플릿 ⭐
├── Dockerfile                        # Docker 설정
├── Procfile                          # 배포 설정
├── firebase.json                     # Firebase 설정
├── runtime.txt                       # Python 버전
└── README.md                         # 프로젝트 설명 ⭐
```

---

## 🚀 다운로드 후 바로 실행하기

### Step 1: 압축 해제
- ZIP 파일 다운로드 후 압축 해제
- 폴더명: `KH-BMS-genspark_ai_developer`

### Step 2: Python 환경 설정
```bash
# 프로젝트 폴더로 이동
cd KH-BMS-genspark_ai_developer

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
```

### Step 3: 환경 변수 설정
```bash
# .env 파일 생성
# Windows:
copy .env.example .env
# Mac/Linux:
cp .env.example .env

# .env 파일 편집 (메모장, VS Code 등)
notepad .env  # Windows
nano .env     # Mac/Linux
```

### Step 4: 실행 (터미널 2개 필요)

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

### Step 5: 브라우저 접속
- **통합 대시보드**: http://localhost:3000/index.html
- **엑셀 업로드**: http://localhost:3000/excel_upload.html
- **API 문서**: http://localhost:8000/docs

---

## 🔑 샌드박스 전용 파일 (GitHub에 없는 것들)

다음 파일들은 샌드박스에만 있고 GitHub에는 포함되지 않습니다:

### 제외된 파일:
- ❌ `.git/` - Git 히스토리 (용량 큼)
- ❌ `venv/` - Python 가상 환경 (재생성 가능)
- ❌ `__pycache__/` - Python 캐시 (자동 생성)
- ❌ `logs/` - 로그 파일 (재생성 가능)
- ❌ `node_modules/` - Node 패키지 (재설치 가능)
- ❌ `.env` - 환경 변수 (보안상 제외, `.env.example` 제공)

### 포함된 중요 파일:
- ✅ `data/bidbot.db` - 샘플 데이터베이스
- ✅ `data/uploads/` - 업로드 폴더 (빈 폴더)
- ✅ 모든 소스 코드
- ✅ 모든 설정 파일
- ✅ 모든 문서

---

## 📥 추가 다운로드 옵션

### GitHub Desktop 사용 (GUI):
1. GitHub Desktop 설치: https://desktop.github.com/
2. File → Clone Repository
3. URL 입력: `https://github.com/mgdwok-stack/KH-BMS.git`
4. 브랜치 변경: `genspark_ai_developer`

### GitHub CLI 사용:
```bash
# GitHub CLI 설치
# Windows: winget install GitHub.cli
# Mac: brew install gh
# Linux: apt install gh

# 리포지토리 클론
gh repo clone mgdwok-stack/KH-BMS

# 브랜치 전환
cd KH-BMS
git checkout genspark_ai_developer
```

---

## 🆘 문제 해결

### Q1: ZIP 파일이 다운로드 안 됨
**A**: 브라우저를 변경하거나 다음 도구 사용:
- Windows: Edge, Chrome
- Mac: Safari, Chrome
- Linux: Firefox, Chrome

### Q2: 압축이 안 풀림
**A**: 
- Windows: 7-Zip 설치 (https://www.7-zip.org/)
- Mac: The Unarchiver 설치
- Linux: `unzip` 또는 `tar` 명령어

### Q3: Git이 없음
**A**: 
- 방법 1 (ZIP) 사용하거나
- Git 설치: https://git-scm.com/

### Q4: 데이터베이스가 비어있음
**A**: GitHub에서 다시 다운로드하면 샘플 데이터(300건) 포함됨

### Q5: Python 패키지 설치 실패
**A**:
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 의존성 재설치
pip install -r backend/requirements.txt
```

---

## 🔗 모든 다운로드 링크 요약

### GitHub:
| 항목 | 링크 |
|------|------|
| **전체 ZIP** | https://github.com/mgdwok-stack/KH-BMS/archive/refs/heads/genspark_ai_developer.zip |
| **웹에서 보기** | https://github.com/mgdwok-stack/KH-BMS/tree/genspark_ai_developer |
| **Git 클론** | `git clone https://github.com/mgdwok-stack/KH-BMS.git` |

### 개별 파일:
| 파일 | 링크 |
|------|------|
| **데이터베이스** | https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/data/bidbot.db |
| **통합 대시보드** | https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/frontend/public/index.html |
| **엑셀 업로드** | https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/frontend/public/excel_upload.html |
| **서버 실행 파일** | https://github.com/mgdwok-stack/KH-BMS/raw/genspark_ai_developer/backend/real_data_server.py |

### 문서:
| 문서 | 링크 |
|------|------|
| **빠른 시작** | https://github.com/mgdwok-stack/KH-BMS/blob/genspark_ai_developer/QUICK_START.md |
| **다운로드 가이드** | https://github.com/mgdwok-stack/KH-BMS/blob/genspark_ai_developer/DOWNLOAD_GUIDE.md |
| **Google Cloud** | https://github.com/mgdwok-stack/KH-BMS/blob/genspark_ai_developer/GOOGLE_CLOUD_DEPLOYMENT.md |

---

## ✅ 다운로드 체크리스트

- [ ] GitHub에서 ZIP 다운로드 또는 Git 클론
- [ ] 압축 해제 (폴더: `KH-BMS-genspark_ai_developer`)
- [ ] Python 설치 확인 (`python --version`)
- [ ] 가상 환경 생성 (`python -m venv venv`)
- [ ] 가상 환경 활성화
- [ ] 의존성 설치 (`pip install -r backend/requirements.txt`)
- [ ] `.env` 파일 생성 (`.env.example` 복사)
- [ ] 백엔드 실행 (`python real_data_server.py`)
- [ ] 프론트엔드 실행 (`python -m http.server 3000`)
- [ ] 브라우저 접속 (http://localhost:3000/index.html)

---

## 🎉 완료!

이제 샌드박스의 모든 파일을 다운받아 로컬에서 실행할 수 있습니다!

**추천 방법**: 
1. GitHub ZIP 다운로드 (가장 쉬움)
2. QUICK_START.md 참고하여 실행
3. 통합 대시보드에서 모든 기능 확인

---

**작성일**: 2026-03-06  
**프로젝트**: KH-BMS 입찰 예측 시스템  
**GitHub**: https://github.com/mgdwok-stack/KH-BMS  
**브랜치**: genspark_ai_developer
