# 🚀 Google 클라우드 플랫폼 배포 가이드

## 🤔 Google Antigravity란?

**참고**: Python에서 `import antigravity`를 실행하면 XKCD 만화가 열리는 이스터에그입니다! 😊

하지만 Google에서 제공하는 **무료/저렴한 개발 플랫폼**은 다음과 같습니다:

---

## 🎯 Google 클라우드 옵션

### 1. Google Cloud Platform (GCP) - App Engine ⭐⭐⭐⭐⭐

**무료 할당량**:
- ✅ 28 frontend instance hours/일 (매일 무료)
- ✅ 9 backend instance hours/일
- ✅ 1GB 무료 저장소
- ✅ 데이터베이스: Cloud SQL 또는 Firestore

**장점**:
- Google의 강력한 인프라
- 자동 스케일링
- Python/FastAPI 완벽 지원
- 무료 SSL 인증서

**단점**:
- 초기 설정이 복잡
- 신용카드 등록 필요 (무료 할당량 초과 시에만 과금)
- 무료 할당량 초과 시 비용 발생

---

### 2. Google Cloud Run 🚀

**무료 할당량**:
- ✅ 2백만 요청/월
- ✅ 180,000 vCPU-초/월
- ✅ 360,000 GiB-초/월
- ✅ 1GB 무료 저장소

**장점**:
- Docker 컨테이너 기반 (유연함)
- 사용한 만큼만 과금
- 완전 관리형 (Serverless)
- 빠른 배포

**단점**:
- Docker 이미지 작성 필요
- Cold Start 지연 가능

---

### 3. Firebase Hosting + Cloud Functions

**무료 할당량**:
- ✅ 10GB 호스팅 저장소
- ✅ 125,000 Cloud Functions 호출/월
- ✅ Firebase Realtime Database 무료 티어

**장점**:
- 프론트엔드 호스팅 최적화
- Firebase 생태계 (인증, DB 등)
- CDN 자동 제공
- 설정 간단

**단점**:
- 백엔드는 Cloud Functions로 제한
- FastAPI 전체를 실행하기 어려움

---

## 📋 추천: Google Cloud Run (컨테이너 배포)

이 방법이 가장 **무료 할당량이 넉넉하고**, **FastAPI를 그대로 사용**할 수 있습니다!

---

## 🔧 Google Cloud Run 배포 가이드

### 전제 조건:
1. Google 계정 (Gmail)
2. Google Cloud 프로젝트 생성
3. `gcloud` CLI 설치 (선택사항, 웹 콘솔도 가능)

---

### Step 1: Google Cloud Console 설정

1. **Google Cloud Console 접속**
   ```
   https://console.cloud.google.com/
   ```

2. **새 프로젝트 생성**
   - 좌측 상단 프로젝트 선택 → **새 프로젝트**
   - 프로젝트 이름: `kh-bms-project`
   - 생성 클릭

3. **결제 계정 연결** (무료 할당량 사용 위해 필요)
   - 신용카드 등록 (무료 할당량 초과 시에만 과금)
   - $300 무료 크레딧 제공 (90일간)

4. **Cloud Run API 활성화**
   - 좌측 메뉴 → **API 및 서비스** → **라이브러리**
   - "Cloud Run API" 검색 → 활성화
   - "Container Registry API" 검색 → 활성화
   - "Cloud Build API" 검색 → 활성화

---

### Step 2: Dockerfile 생성

프로젝트 루트에 `Dockerfile` 생성:

```dockerfile
# Python 3.10 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY backend/requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 코드 복사
COPY backend/ ./backend/
COPY data/ ./data/

# 포트 설정 (Cloud Run은 PORT 환경 변수 사용)
ENV PORT=8080

# 백엔드 서버 실행
CMD cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

### Step 3: .dockerignore 생성

```
.git
.env
.env.example
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv/
*.egg-info/
.DS_Store
frontend/
*.md
logs/
*.log
```

---

### Step 4: Cloud Run 배포 (웹 콘솔 사용)

#### 방법 A: 웹 콘솔에서 직접 배포

1. **Cloud Run 콘솔 접속**
   ```
   https://console.cloud.google.com/run
   ```

2. **서비스 만들기** 클릭

3. **소스 선택**
   - **"GitHub에서 지속적으로 배포"** 선택
   - GitHub 계정 연결
   - 리포지토리 선택: `mgdwok-stack/KH-BMS`
   - 브랜치: `genspark_ai_developer`
   - Dockerfile 위치: `/Dockerfile`

4. **서비스 구성**
   ```
   서비스 이름: kh-bms-backend
   리전: asia-northeast3 (서울)
   인증: 인증되지 않은 호출 허용 (공개 API)
   컨테이너 포트: 8080
   ```

5. **환경 변수 설정**
   - `DATABASE_URL`: `sqlite:///./data/bidbot.db`
   - `PROCUREMENT_API_KEY`: `6a63fc31e3729cdf7b858f69c5987ff9a4626b4546556cd94168e31a413f3bbe`
   - `PROCUREMENT_API_BASE_URL`: `http://apis.data.go.kr/1230000/ScsbidInfoService`
   - `APP_NAME`: `Bid-Bot Clone`
   - `DEBUG`: `False`
   - `SECRET_KEY`: (강력한 시크릿 키 생성)

6. **만들기** 클릭

7. **배포 완료** 후 URL 확인:
   ```
   https://kh-bms-backend-xxxxxxxxxx-an.a.run.app
   ```

#### 방법 B: gcloud CLI 사용 (로컬 터미널)

```bash
# 1. gcloud CLI 설치 (아직 안 했다면)
# Windows: https://cloud.google.com/sdk/docs/install
# Mac: brew install google-cloud-sdk
# Linux: curl https://sdk.cloud.google.com | bash

# 2. 로그인
gcloud auth login

# 3. 프로젝트 설정
gcloud config set project kh-bms-project

# 4. 프로젝트 폴더로 이동
cd KH-BMS

# 5. Cloud Run 배포
gcloud run deploy kh-bms-backend \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "DATABASE_URL=sqlite:///./data/bidbot.db,PROCUREMENT_API_KEY=6a63fc31e3729cdf7b858f69c5987ff9a4626b4546556cd94168e31a413f3bbe,DEBUG=False"

# 6. 배포 완료 후 URL 확인
# Service URL: https://kh-bms-backend-xxxxxxxxxx-an.a.run.app
```

---

### Step 5: 프론트엔드 배포 (Firebase Hosting)

#### Firebase Hosting 설정

1. **Firebase Console 접속**
   ```
   https://console.firebase.google.com/
   ```

2. **프로젝트 추가** → `kh-bms-project` 선택 (Google Cloud와 연동)

3. **Hosting 활성화**

4. **Firebase CLI 설치**
   ```bash
   npm install -g firebase-tools
   ```

5. **Firebase 로그인**
   ```bash
   firebase login
   ```

6. **프로젝트 초기화**
   ```bash
   cd KH-BMS
   firebase init hosting

   # 질문 답변:
   # - Public directory: frontend/public
   # - Configure as SPA: No
   # - Overwrite index.html: No
   ```

7. **배포**
   ```bash
   firebase deploy --only hosting
   ```

8. **URL 확인**
   ```
   https://kh-bms-project.web.app
   ```

---

### Step 6: 프론트엔드에서 백엔드 URL 연결

`frontend/public/excel_upload.html` 파일에서 API URL 수정:

```javascript
// 기존:
const API_URL = 'http://localhost:8000';

// 변경:
const API_URL = 'https://kh-bms-backend-xxxxxxxxxx-an.a.run.app';
```

재배포:
```bash
firebase deploy --only hosting
```

---

## 💰 비용 추정

### 무료 할당량 (매월):
- Cloud Run: 2백만 요청 무료
- Firebase Hosting: 10GB 전송 무료
- Cloud Build: 120 빌드 분 무료

### 예상 비용:
- **소규모 사용 (월 1000명 방문)**: $0 (무료 할당량 내)
- **중규모 사용 (월 10,000명 방문)**: $5~$10
- **대규모 사용 (월 100,000명 방문)**: $50~$100

---

## 🔧 필수 파일 추가

### 1. `Dockerfile` 생성 (위 참고)

### 2. `.dockerignore` 생성 (위 참고)

### 3. `firebase.json` 생성

```json
{
  "hosting": {
    "public": "frontend/public",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "/api/**",
        "function": "api"
      }
    ],
    "headers": [
      {
        "source": "**",
        "headers": [
          {
            "key": "Access-Control-Allow-Origin",
            "value": "*"
          }
        ]
      }
    ]
  }
}
```

### 4. `.firebaserc` 생성

```json
{
  "projects": {
    "default": "kh-bms-project"
  }
}
```

---

## 🛠️ 문제 해결

### 문제 1: Docker 빌드 실패

**증상**:
```
ERROR: failed to solve: failed to compute cache key
```

**해결**:
```bash
# Dockerfile 경로 확인
ls -la Dockerfile

# Docker 데몬 실행 확인
docker --version
```

### 문제 2: Cloud Run 배포 실패

**증상**:
```
ERROR: (gcloud.run.deploy) User does not have permission
```

**해결**:
```bash
# 권한 확인
gcloud projects get-iam-policy kh-bms-project

# Cloud Run Admin 역할 추가 (필요 시)
gcloud projects add-iam-policy-binding kh-bms-project \
  --member="user:your-email@gmail.com" \
  --role="roles/run.admin"
```

### 문제 3: 환경 변수 적용 안 됨

**해결**:
```bash
# Cloud Run 콘솔에서 환경 변수 재확인
# 또는 gcloud 명령어로 업데이트
gcloud run services update kh-bms-backend \
  --region asia-northeast3 \
  --set-env-vars "KEY=VALUE"
```

---

## 📚 참고 문서

- **Cloud Run 공식 문서**: https://cloud.google.com/run/docs
- **Firebase Hosting**: https://firebase.google.com/docs/hosting
- **Docker 공식 문서**: https://docs.docker.com/
- **gcloud CLI**: https://cloud.google.com/sdk/gcloud

---

## ✅ 체크리스트

### Google Cloud 설정:
- [ ] Google Cloud 계정 생성
- [ ] 프로젝트 생성 (`kh-bms-project`)
- [ ] 결제 계정 연결 ($300 무료 크레딧)
- [ ] Cloud Run API 활성화
- [ ] Container Registry API 활성화
- [ ] Cloud Build API 활성화

### 파일 준비:
- [ ] `Dockerfile` 생성
- [ ] `.dockerignore` 생성
- [ ] `firebase.json` 생성 (프론트엔드용)
- [ ] `.firebaserc` 생성 (프론트엔드용)

### 배포:
- [ ] 백엔드 Cloud Run 배포
- [ ] 프론트엔드 Firebase Hosting 배포
- [ ] API URL 연결 확인
- [ ] 테스트 (엑셀 업로드 등)

---

## 🚀 빠른 시작 명령어

```bash
# === Google Cloud Run 배포 ===

# 1. 프로젝트 클론 (이미 했다면 생략)
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer

# 2. Dockerfile 생성 (위 내용 복사)
nano Dockerfile

# 3. gcloud 로그인
gcloud auth login
gcloud config set project kh-bms-project

# 4. Cloud Run 배포
gcloud run deploy kh-bms-backend \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated

# 5. Firebase 배포 (프론트엔드)
firebase login
firebase init hosting
firebase deploy --only hosting
```

---

**작성일**: 2026-03-06  
**작성자**: AI Assistant  
**프로젝트**: KH-BMS 입찰 예측 시스템
