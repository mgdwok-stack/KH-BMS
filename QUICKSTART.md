# Bid-Bot Clone - Quick Start Guide

## 🎯 빠른 시작 (5분 안에!)

### 1. 사전 요구사항 확인
```bash
docker --version    # Docker 20.10+
docker-compose --version  # Docker Compose 1.29+
```

### 2. 프로젝트 클론 및 환경 설정
```bash
# 환경 변수 파일 생성
cp .env.example .env

# .env 파일 편집 (필수!)
# PROCUREMENT_API_KEY=your_api_key_here
```

### 3. 전체 스택 실행 (한 줄 명령어!)
```bash
docker-compose up --build -d
```

### 4. 서비스 확인
- 🌐 **프론트엔드**: http://localhost:3000
- 🔧 **백엔드 API**: http://localhost:8000
- 📖 **API 문서**: http://localhost:8000/docs

---

## 📋 단계별 가이드

### Step 1: 데이터베이스 초기화
```bash
# 데이터베이스 테이블 생성
docker-compose exec backend python scripts/init_db.py
```

### Step 2: 데이터 수집
```bash
# 최근 데이터 수집 (최근 60일)
docker-compose exec backend python scripts/collect_data.py --mode recent

# 과거 데이터 수집 (특정 기간)
docker-compose exec backend python scripts/collect_data.py \
  --mode historical \
  --start-year 2023 \
  --start-month 1 \
  --end-year 2024 \
  --end-month 12
```

### Step 3: AI 모델 학습
```bash
# 모델 학습 (최소 1,000건 데이터 필요)
docker-compose exec backend python scripts/train_models.py

# 학습 결과 확인
# - models/dnbp_model.h5
# - models/lstm_model.h5
```

### Step 4: 프론트엔드 접속
브라우저에서 http://localhost:3000 접속

---

## 🔧 개발 모드 (로컬 환경)

### Backend 개발
```bash
cd backend

# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 초기화
python scripts/init_db.py

# 개발 서버 실행 (hot-reload 지원)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend 개발
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행 (hot-reload 지원)
npm run dev

# 브라우저에서 http://localhost:3000 자동 오픈
```

### Celery Worker 개발
```bash
cd backend

# Worker 실행
celery -A app.tasks.scheduler worker --loglevel=info

# Beat 스케줄러 실행 (별도 터미널)
celery -A app.tasks.scheduler beat --loglevel=info
```

---

## 📊 주요 기능 사용법

### 1. 입찰공고 조회
1. 프론트엔드 접속: http://localhost:3000
2. **"입찰공고"** 메뉴 클릭
3. 필터 설정 (지역, 공고기관, 입찰상태)
4. 입찰공고 클릭하여 상세 정보 확인

### 2. AI 예측 사용
1. 입찰공고 상세 페이지 접속
2. **"AI 예측 결과"** 섹션 확인
3. 예측 사정률, 추천 투찰금액 확인
4. DNBP, LSTM 개별 예측 결과 비교

### 3. 분석 대시보드
1. **"대시보드"** 메뉴 클릭
2. 전체 통계 카드 확인
3. 사정률 분포 히스토그램 확인
4. 일별 입찰 트렌드 차트 확인

### 4. 발주기관 분석
1. **"분석"** 메뉴 클릭
2. **"발주기관 분석"** 탭 클릭
3. 발주기관명 입력 (예: 국방부)
4. 월별 추이, 금액대별 분포 확인

---

## 🐛 문제 해결

### 문제 1: Docker 컨테이너가 시작되지 않음
```bash
# 로그 확인
docker-compose logs backend
docker-compose logs frontend

# 컨테이너 재시작
docker-compose restart
```

### 문제 2: 데이터베이스 연결 오류
```bash
# PostgreSQL 상태 확인
docker-compose ps postgres

# PostgreSQL 재시작
docker-compose restart postgres

# 데이터베이스 초기화
docker-compose exec backend python scripts/init_db.py
```

### 문제 3: 프론트엔드가 백엔드에 연결되지 않음
```bash
# 백엔드 API 상태 확인
curl http://localhost:8000/health

# CORS 설정 확인 (.env 파일)
ALLOWED_ORIGINS=http://localhost:3000

# Docker 네트워크 확인
docker network inspect bidbot-network
```

### 문제 4: AI 모델이 학습되지 않음
```bash
# 데이터 개수 확인 (최소 1,000건 필요)
docker-compose exec postgres psql -U bidbot -d bidbot_db -c "SELECT COUNT(*) FROM bid_results;"

# 데이터 수집 실행
docker-compose exec backend python scripts/collect_data.py --mode recent

# 모델 학습 재시도
docker-compose exec backend python scripts/train_models.py
```

---

## 📈 성능 최적화 팁

### 1. 데이터베이스 인덱스
```sql
-- 자주 조회되는 컬럼에 인덱스 생성
CREATE INDEX idx_bid_announcement_instt_nm ON bid_announcements(instt_nm);
CREATE INDEX idx_bid_announcement_rgn_nm ON bid_announcements(rgn_nm);
CREATE INDEX idx_bid_result_opengdt ON bid_results(opengdt);
```

### 2. Redis 캐싱
```python
# 캐싱 활성화 (backend/app/config.py)
REDIS_CACHE_TTL = 3600  # 1시간
```

### 3. 프론트엔드 빌드 최적화
```bash
# 프로덕션 빌드
cd frontend
npm run build

# 빌드 결과물 확인
ls -lh dist/
```

---

## 🚀 프로덕션 배포

### Docker Compose 프로덕션 설정
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    environment:
      - DEBUG=False
      - ALLOWED_ORIGINS=https://your-domain.com
    restart: always

  frontend:
    environment:
      - VITE_API_BASE_URL=https://api.your-domain.com/api/v1
    restart: always
```

### 배포 명령어
```bash
# 프로덕션 모드로 실행
docker-compose -f docker-compose.prod.yml up --build -d

# SSL 인증서 설정 (Let's Encrypt)
docker-compose exec nginx certbot --nginx -d your-domain.com
```

---

## 📞 지원 및 문의

### 문서
- **API 문서**: http://localhost:8000/docs
- **프로젝트 README**: [README.md](README.md)
- **아키텍처 문서**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **데이터베이스 스키마**: [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)

### 추가 가이드
- **데이터 파이프라인**: [DATA_PIPELINE_GUIDE.md](DATA_PIPELINE_GUIDE.md)
- **Step 1 요약**: [STEP1_SUMMARY.md](STEP1_SUMMARY.md)
- **Step 2 요약**: [STEP2_SUMMARY.md](STEP2_SUMMARY.md)
- **Step 3 요약**: [STEP3_SUMMARY.md](STEP3_SUMMARY.md)
- **Step 4 요약**: [STEP4_SUMMARY.md](STEP4_SUMMARY.md)

---

**Happy Bidding! 🎯**
