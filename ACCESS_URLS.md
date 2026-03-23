# 🌐 통합 Bid-Bot 시스템 - 접속 URL

## 메인 서버
**포트**: 8000  
**기본 URL**: https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai

---

## 📱 웹 인터페이스

### 1. 원래 프론트엔드 (React/TypeScript)
**URL**: https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/app/index.html

**기능**:
- 대시보드
- 입찰 관리
- Excel 업로드 및 분석
- 원래 3월 초에 만든 모든 기능

**관련 페이지**:
- Dashboard: `/app/dashboard.html`
- Excel Upload: `/app/excel_upload.html`
- Test: `/app/test.html`

---

### 2. 새로운 통합 UI (어제/오늘 작업)
**URL**: https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/index.html

**기능**:
- 📊 전체 개요
- 📋 입찰 공고
- 🤖 AI 예측
- 🏢 조직별 통계
- 🏆 PQ 분석
- 📤 CSV 업로드
- 📊 Excel 업로드

---

### 3. 로컬 보안 버전 (데이터가 로컬에만 저장)
**URL**: https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/local_secure.html

**특징**:
- CSV 파일이 서버에 업로드되지 않음
- 모든 데이터가 브라우저에만 저장
- SQLite DB를 로컬 파일로 다운로드 가능

---

### 4. 기존 통합 UI (PQ + CSV)
**URL**: https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html

**기능**:
- 발주처별 통계
- PQ 대표사 분석
- CSV 업로드
- 전체 개요

---

## 📡 API 엔드포인트

### API 문서
- **Swagger UI**: https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs
- **ReDoc**: https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/redoc

### 주요 API

#### 원래 Bid-Bot API (3월 초)
- `GET /api/v1/bids/` - 입찰 공고 목록
- `POST /api/v1/bids/` - 새 공고 등록
- `POST /api/v1/predictions/predict` - AI 예측
- `GET /api/v1/analytics/overview` - 분석 통계
- `POST /api/v1/excel/upload` - Excel 업로드
- `GET /api/v1/excel/uploads` - Excel 파일 목록

#### PQ 분석 API (어제/오늘)
- `GET /api/v1/pq-stats` - PQ 전체 통계
- `GET /api/v1/pq-companies` - PQ 대표사 목록
- `GET /api/v1/pq-analysis/{company}` - 대표사 분석

#### 조직별 통계 API (어제/오늘)
- `GET /api/v1/organizations` - 조직 목록
- `GET /api/v1/organizations/{org_name}` - 조직 데이터

#### CSV 업로드 API (어제/오늘)
- `POST /api/v1/upload-csv` - CSV 업로드 및 DB 생성
- `GET /api/v1/uploaded-files` - 업로드된 파일 목록

---

## 🗂️ 파일 위치

### 프론트엔드
- **원래 Frontend**: `/home/user/webapp/frontend/public/`
  - `index.html` - 메인 페이지
  - `dashboard.html` - 대시보드
  - `excel_upload.html` - Excel 업로드

- **새 UI**: `/home/user/webapp/static/`
  - `index.html` - 통합 UI (새로 만든 것)
  - `unified.html` - 기존 통합 UI
  - `local_secure.html` - 로컬 보안 버전
  - `test.html` - API 테스트

### 백엔드
- **통합 서버**: `/home/user/webapp/unified_server.py`
- **원래 Backend**: `/home/user/webapp/backend/app/`

### 데이터베이스
- **원래 Bid-Bot DB**: `/home/user/webapp/backend/data/bidbot.db`
- **PQ 통계 DB**: `/home/user/webapp/data/bidbot_data.db`
- **조직별 DB**: `/home/user/webapp/data/databases/*.db`

---

## ✅ 어떤 것을 사용해야 하나?

### 상황별 추천:

1. **원래 시스템 그대로 사용하고 싶다면**:
   → https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/app/index.html

2. **모든 기능을 한 곳에서 보고 싶다면**:
   → https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/index.html

3. **데이터를 서버에 올리고 싶지 않다면**:
   → https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/local_secure.html

4. **PQ 분석과 CSV만 사용하고 싶다면**:
   → https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html

---

## 🔧 서버 재시작

```bash
cd /home/user/webapp
kill $(lsof -ti :8000)
python3 unified_server.py
```

---

**업데이트**: 2026-03-20 08:34  
**상태**: ✅ 모든 시스템 정상 작동
