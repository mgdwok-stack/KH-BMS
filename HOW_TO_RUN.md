# 🚀 Bid-Bot Clone - 실행 가이드

## ✅ 서버 실행 완료!

현재 **Bid-Bot Clone API 데모 서버**가 실행 중입니다!

---

## 🌐 서비스 접속 정보

### 공개 URL
```
https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai
```

### 주요 엔드포인트

| 엔드포인트 | 설명 | URL |
|-----------|------|-----|
| 📖 **API 문서 (Swagger)** | 대화형 API 문서 | [/docs](https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/docs) |
| 📝 **API 문서 (ReDoc)** | 깔끔한 API 문서 | [/redoc](https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/redoc) |
| 💚 **헬스 체크** | 서버 상태 확인 | [/health](https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/health) |
| 🎯 **루트** | 기본 정보 | [/](https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/) |

---

## 🧪 API 테스트

### 1. 브라우저에서 테스트

아래 링크를 클릭하여 바로 접속하세요:

1. **API 문서 보기**: 
   👉 https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/docs

2. **서버 상태 확인**:
   👉 https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/health

3. **데모 데이터 보기**:
   👉 https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/api/v1/demo

### 2. curl로 테스트

```bash
# 서버 상태 확인
curl https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/health

# 데모 데이터 조회
curl https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/api/v1/demo

# 분석 요약 조회
curl https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/api/v1/analytics/summary
```

### 3. Python으로 테스트

```python
import requests

# API 기본 URL
BASE_URL = "https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai"

# 서버 상태 확인
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 데모 데이터 조회
response = requests.get(f"{BASE_URL}/api/v1/demo")
print(response.json())
```

---

## 📊 데모 데이터 예시

### 입찰공고 샘플
```json
{
  "id": 1,
  "bid_ntce_no": "20260001234-00",
  "bid_ntce_nm": "청사 건물 유지보수 공사",
  "instt_nm": "행정안전부",
  "rgn_nm": "서울",
  "basis_prce": 1000000000
}
```

### AI 예측 샘플
```json
{
  "final_predicted_rate": 99.52,
  "predicted_prdprc": 995200000,
  "recommended_bid_amt": 872993044,
  "dnbp_predicted_rate": 99.54,
  "lstm_predicted_rate": 99.48
}
```

---

## 🔧 완전한 기능 활성화

현재는 **데모 모드**로 실행 중입니다. 완전한 기능을 사용하려면:

### 방법 1: Docker Compose (권장)

```bash
# 1. 환경 변수 설정
cp .env.example .env
# PROCUREMENT_API_KEY를 실제 API 키로 변경

# 2. Docker Compose 실행
docker-compose up --build -d

# 3. 서비스 접속
# PostgreSQL: localhost:5432
# Redis: localhost:6379
# Backend: localhost:8000
# Frontend: localhost:3000
```

### 방법 2: 로컬 개발 환경

```bash
# Backend 실행
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend 실행 (별도 터미널)
cd frontend
npm install
npm run dev
```

---

## 📖 API 문서 사용법

### Swagger UI에서 API 테스트하기

1. **API 문서 열기**: https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/docs

2. **엔드포인트 선택**: 테스트하고 싶은 API 클릭

3. **"Try it out" 클릭**: 우측 상단 버튼

4. **파라미터 입력**: 필요한 파라미터 입력

5. **"Execute" 클릭**: 요청 실행

6. **결과 확인**: Response body에서 결과 확인

---

## 🎯 주요 API 엔드포인트

### 1. 입찰공고 API
```
GET  /api/v1/bids/              # 목록 조회
GET  /api/v1/bids/{bid_id}       # 상세 조회
GET  /api/v1/bids/search/filters # 필터 옵션
GET  /api/v1/bids/results/       # 낙찰결과
```

### 2. AI 예측 API
```
POST /api/v1/predictions/predict          # 예측 실행
GET  /api/v1/predictions/{id}             # 예측 조회
GET  /api/v1/predictions/                 # 예측 목록
GET  /api/v1/predictions/stats/summary    # 통계
GET  /api/v1/predictions/accuracy/report  # 정확도
```

### 3. 분석 API
```
GET /api/v1/analytics/summary              # 대시보드 요약
GET /api/v1/analytics/trends               # 트렌드 분석
GET /api/v1/analytics/institution/{name}   # 발주기관 분석
GET /api/v1/analytics/histogram            # 히스토그램
```

---

## 💡 다음 단계

### 1. 데이터 수집
```bash
# 데이터베이스 초기화
python scripts/init_db.py

# 데이터 수집 (최근 60일)
python scripts/collect_data.py --mode recent
```

### 2. AI 모델 학습
```bash
# 모델 학습 (최소 1,000건 데이터 필요)
python scripts/train_models.py
```

### 3. Frontend 실행
```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

---

## 🐛 문제 해결

### 서버가 실행되지 않는 경우
```bash
# 프로세스 확인
ps aux | grep python

# 포트 확인
lsof -i :8000

# 로그 확인
tail -f /tmp/demo_server.log
```

### API 호출이 실패하는 경우
```bash
# 서버 상태 확인
curl https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/health

# 네트워크 확인
ping 8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai
```

---

## 📞 추가 문서

- **README.md** - 프로젝트 전체 개요
- **QUICKSTART.md** - 빠른 시작 가이드
- **ARCHITECTURE.md** - 시스템 아키텍처
- **PROJECT_COMPLETION.md** - 프로젝트 완료 보고서

---

## ✨ 현재 상태

✅ **API 서버 실행 중** (데모 모드)  
✅ **공개 URL 접속 가능**  
✅ **API 문서 확인 가능**  
⏳ **PostgreSQL 설정 필요** (완전한 기능 사용)  
⏳ **Frontend 빌드 필요** (UI 사용)  

---

**서버 URL**: https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai  
**API 문서**: https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/docs  

**Happy Testing! 🎯**
