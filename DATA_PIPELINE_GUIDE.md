# 데이터 파이프라인 가이드

## 개요

이 문서는 Bid-Bot Clone의 데이터 수집 및 전처리 파이프라인에 대한 상세 가이드입니다.

## 데이터 흐름

```
┌─────────────────────┐
│  조달청 Open API     │
│  - 입찰공고 정보     │
│  - 낙찰결과 정보     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  DataCollector      │
│  - API 호출         │
│  - 응답 파싱        │
│  - 재시도 로직      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  PostgreSQL DB      │
│  - bid_announcements│
│  - bid_results      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  DataProcessor      │
│  - 데이터 정제      │
│  - 특징 추출        │
│  - 학습 데이터 생성 │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AI Model Training  │
│  - DNBP Model       │
│  - LSTM Model       │
└─────────────────────┘
```

## 주요 컴포넌트

### 1. DataCollector (data_collector.py)

조달청 API를 호출하여 데이터를 수집합니다.

**주요 기능:**
- ✅ 입찰공고 정보 수집 (`getDataSetOpnStdBidPblancInfo`)
- ✅ 낙찰결과 정보 수집 (`getDataSetOpnStdScsbidInfo`)
- ✅ API 재시도 로직 (Rate Limit 대응)
- ✅ 데이터 중복 체크
- ✅ 자동 파싱 및 DB 저장

**사용 예시:**
```python
from app.database import SessionLocal
from app.services.data_collector import DataCollector

db = SessionLocal()
collector = DataCollector(db)

# 입찰공고 수집
items = await collector.collect_bid_announcements(
    start_date="20240101",
    end_date="20240331",
    page=1,
    num_of_rows=100
)

# DB 저장
for item in items:
    collector.save_bid_announcement(item)
```

### 2. DataProcessor (data_processor.py)

수집된 데이터를 정제하고 AI 학습을 위한 특징을 추출합니다.

**주요 기능:**
- ✅ 결측치 제거
- ✅ 이상치 탐지 및 처리
- ✅ 사정률 재계산 및 검증
- ✅ 중복 데이터 제거
- ✅ 발주기관/지역/업종별 통계 계산
- ✅ 유사 케이스 탐색
- ✅ 학습 데이터셋 생성

**사용 예시:**
```python
from app.services.data_processor import DataProcessor

db = SessionLocal()
processor = DataProcessor(db)

# 데이터 정제
cleaned_count = processor.clean_bid_results()

# 특징 추출
features = processor.extract_features_for_prediction(bid_announcement)

# 학습 데이터 생성
df = processor.get_training_data(start_date, end_date)
```

### 3. Celery Scheduler (scheduler.py)

주기적으로 데이터를 수집하고 처리합니다.

**스케줄:**
- **매 시간 정각**: 입찰공고 수집
- **매 6시간 30분**: 낙찰결과 수집
- **매일 00:00**: 데이터 정제
- **매주 월요일 01:00**: 데이터 검증

**태스크:**
- `collect_bid_announcements_task`: 입찰공고 수집
- `collect_bid_results_task`: 낙찰결과 수집
- `clean_data_task`: 데이터 정제
- `validate_data_task`: 데이터 검증
- `collect_historical_data_task`: 과거 데이터 일괄 수집 (수동)

## 스크립트 사용법

### 1. 데이터베이스 초기화

```bash
cd /home/user/webapp
python scripts/init_db.py
```

**기능:**
- PostgreSQL 테이블 생성
- 인덱스 자동 생성

### 2. 데이터 수집 테스트

```bash
python scripts/test_data_pipeline.py
```

**기능:**
- API 연동 테스트
- 데이터 저장 테스트
- 데이터 전처리 테스트

### 3. 수동 데이터 수집

#### 최근 데이터 수집
```bash
# 기본: 30일 전 ~ 오늘 (낙찰결과), 오늘 ~ 60일 후 (입찰공고)
python scripts/collect_data.py --mode recent

# 커스텀 기간
python scripts/collect_data.py --mode recent --days-back 90 --days-forward 30
```

#### 과거 데이터 수집
```bash
# 2023년 데이터 수집
python scripts/collect_data.py --mode historical --start-year 2023 --end-year 2023

# 2020~2024년 데이터 수집
python scripts/collect_data.py --mode historical --start-year 2020 --end-year 2024
```

## 데이터 정제 프로세스

### 1. 필수 필드 검증
- `prdprc` (예정가격)
- `basis_prce` (기초금액)
- `sucsfbid_amt` (낙찰금액)

### 2. 기초금액 필터링
- 최소 기초금액: 100만원 (기본값)
- 너무 작은 금액은 학습에서 제외

### 3. 사정률 검증
- 정상 범위: 95% ~ 105%
- 범위 밖 데이터는 이상치로 간주

### 4. 사정률 재계산
```python
사정률 = (예정가격 / 기초금액) × 100
투찰률 = (낙찰금액 / 예정가격) × 100
```

### 5. 중복 제거
- 같은 `bid_ntce_no`가 여러 개인 경우 최신 데이터만 유지

## 특징 추출

AI 예측을 위해 다음 특징들을 추출합니다:

### 기본 특징
- `basis_prce`: 기초금액
- `presmpt_prce`: 추정가격
- `instt_nm`: 발주기관명
- `rgn_nm`: 지역명
- `induty_ty_nm`: 업종명
- `bid_methd_nm`: 입찰방식

### 통계 특징 (과거 365일 기준)

#### 발주기관 통계
- `instt_historical_avg_rate`: 평균 사정률
- `instt_historical_std_rate`: 사정률 표준편차
- `instt_historical_min_rate`: 최소 사정률
- `instt_historical_max_rate`: 최대 사정률
- `instt_historical_count`: 과거 입찰 건수

#### 지역 통계
- `rgn_historical_avg_rate`: 지역 평균 사정률
- `rgn_historical_count`: 지역 입찰 건수

#### 업종 통계
- `induty_historical_avg_rate`: 업종 평균 사정률
- `induty_historical_count`: 업종 입찰 건수

#### 기초금액 구간 통계 (±20%)
- `price_range_avg_rate`: 해당 금액 구간 평균 사정률
- `price_range_count`: 해당 금액 구간 입찰 건수

#### 유사 케이스
- `similar_cases_count`: 유사 입찰 건수
- `similar_cases_avg_rate`: 유사 입찰 평균 사정률
- `similar_cases_std_rate`: 유사 입찰 사정률 표준편차

## Celery 사용법

### 1. Celery Worker 시작

```bash
cd backend
celery -A app.tasks.scheduler worker --loglevel=info
```

### 2. Celery Beat (스케줄러) 시작

```bash
celery -A app.tasks.scheduler beat --loglevel=info
```

### 3. 수동 태스크 실행

```python
from app.tasks.scheduler import collect_bid_announcements_task

# 즉시 실행
result = collect_bid_announcements_task.delay()
print(f"Task ID: {result.id}")

# 결과 확인
print(result.get(timeout=300))  # 5분 타임아웃
```

### 4. Docker Compose로 실행

```bash
docker-compose up -d
```

모든 서비스(PostgreSQL, Redis, Backend, Celery Worker, Celery Beat)가 자동으로 시작됩니다.

## API 응답 구조

### 입찰공고 정보 (getDataSetOpnStdBidPblancInfo)

```json
{
  "response": {
    "body": {
      "items": [
        {
          "bidNtceNo": "공고번호",
          "bidNtceNm": "공고명",
          "insttNm": "공고기관명",
          "basisPrce": "기초금액",
          "presmptPrce": "추정가격",
          "bidMethdNm": "입찰방식",
          "rgnNm": "지역명",
          "indutyTyNm": "업종명"
        }
      ],
      "totalCount": 100
    }
  }
}
```

### 낙찰결과 정보 (getDataSetOpnStdScsbidInfo)

```json
{
  "response": {
    "body": {
      "items": [
        {
          "bidNtceNo": "공고번호",
          "insttNm": "공고기관명",
          "basisPrce": "기초금액",
          "prdprc": "예정가격",
          "prdprcRate": "사정률",
          "sucsfbidAmt": "낙찰금액",
          "sucsfbidRate": "투찰률",
          "opengDt": "개찰일시"
        }
      ],
      "totalCount": 50
    }
  }
}
```

## 에러 처리

### 1. API Rate Limit
- 429 에러 발생 시 10초 대기 후 재시도
- 최대 재시도 횟수: 3회 (설정 가능)

### 2. Timeout
- 기본 타임아웃: 30초
- Exponential Backoff 적용

### 3. 데이터 파싱 에러
- JSON 파싱 실패 시 로그 기록
- 개별 레코드 저장 실패 시 스킵 (전체 중단 없음)

## 모니터링

### 로그 확인

```bash
# Backend 로그
docker-compose logs -f backend

# Celery Worker 로그
docker-compose logs -f celery-worker

# Celery Beat 로그
docker-compose logs -f celery-beat
```

### 데이터베이스 확인

```sql
-- 총 데이터 건수
SELECT 
  (SELECT COUNT(*) FROM bid_announcements) as announcements,
  (SELECT COUNT(*) FROM bid_results) as results;

-- 최근 수집 데이터
SELECT COUNT(*), DATE(created_at) 
FROM bid_results 
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY DATE(created_at) DESC;

-- 사정률 통계
SELECT 
  AVG(prdprc_rate) as avg_rate,
  MIN(prdprc_rate) as min_rate,
  MAX(prdprc_rate) as max_rate,
  STDDEV(prdprc_rate) as std_rate
FROM bid_results
WHERE prdprc_rate IS NOT NULL;
```

## 트러블슈팅

### 문제: API 키 오류
```
해결: .env 파일에 PROCUREMENT_API_KEY 설정 확인
```

### 문제: 데이터베이스 연결 실패
```
해결: 
1. PostgreSQL 실행 확인: docker-compose ps
2. DATABASE_URL 설정 확인
3. 방화벽 확인
```

### 문제: Celery 태스크 실행 안됨
```
해결:
1. Redis 실행 확인
2. Celery Worker 로그 확인
3. celery -A app.tasks.scheduler inspect active
```

## 성능 최적화

### 1. 배치 처리
- 한 번에 100개씩 수집 (페이지 단위)
- DB 커밋은 페이지 단위로

### 2. 인덱싱
- 자주 조회되는 컬럼에 인덱스
- 복합 인덱스 활용

### 3. Connection Pooling
- SQLAlchemy pool_size: 10
- max_overflow: 20

## 다음 단계

Step 2 완료 후, 다음 단계로 진행합니다:

**Step 3: AI 모델 구현**
- DNBP 모델 클래스
- LSTM 모델 클래스
- 앙상블 로직
- 모델 학습 파이프라인

---

**문서 버전**: 1.0  
**최종 수정**: 2026-02-26
