# Step 2 완료: 데이터 파이프라인 구현 (조달청 API 연동)

## ✅ 완료된 작업

### 1. DataCollector 서비스 (`data_collector.py`)

조달청 나라장터 Open API와 연동하여 실시간 데이터를 수집합니다.

#### 핵심 기능

**✅ 입찰공고 정보 수집**
```python
async def collect_bid_announcements(
    start_date, end_date, page, num_of_rows
) -> List[Dict]
```
- API: `getDataSetOpnStdBidPblancInfo`
- 수집 데이터: 공고번호, 공고명, 기관명, 기초금액, 지역, 업종 등
- 자동 페이지네이션 지원

**✅ 낙찰결과 정보 수집**
```python
async def collect_bid_results(
    start_date, end_date, page, num_of_rows
) -> List[Dict]
```
- API: `getDataSetOpnStdScsbidInfo`
- 수집 데이터: 예정가격, 사정률, 낙찰금액, 투찰률 등
- **AI 학습의 핵심 데이터셋**

**✅ 고급 기능**
- **재시도 로직**: 최대 3회 재시도 (Exponential Backoff)
- **Rate Limit 대응**: 429 에러 시 10초 대기
- **타임아웃 처리**: 기본 30초
- **중복 체크**: `bid_ntce_no` 기준 자동 중복 제거
- **데이터 검증**: 필수 필드 검증 및 타입 변환

#### 데이터 파싱 및 변환
```python
_parse_int(value)      # 문자열 → 정수 (콤마 제거)
_parse_float(value)    # 문자열 → 실수
_parse_datetime(value) # YYYYMMDD[HHmmss] → datetime
```

### 2. DataProcessor 서비스 (`data_processor.py`)

수집된 raw 데이터를 정제하고 AI 학습에 적합한 형태로 변환합니다.

#### 핵심 기능

**✅ 데이터 정제 (`clean_bid_results`)**

1. **필수 필드 검증**
   - `prdprc`, `basis_prce`, `sucsfbid_amt` NULL 체크
   - 누락 데이터 식별 및 로깅

2. **기초금액 필터링**
   - 최소 기초금액: 100만원 (기본값)
   - 너무 작은 금액은 학습 데이터에서 제외

3. **사정률 검증 및 재계산**
   ```python
   사정률 = (예정가격 / 기초금액) × 100
   투찰률 = (낙찰금액 / 예정가격) × 100
   ```
   - 정상 범위: 95% ~ 105%
   - 기존 사정률과 차이가 크면 재계산값으로 업데이트

4. **중복 데이터 제거**
   - 같은 `bid_ntce_no`가 여러 개인 경우
   - 최신 데이터만 유지, 나머지 삭제

**✅ 특징 추출 (`extract_features_for_prediction`)**

AI 예측을 위한 다양한 특징을 자동으로 추출합니다.

| 특징 카테고리 | 추출 항목 | 설명 |
|--------------|-----------|------|
| **기본 정보** | basis_prce, presmpt_prce | 기초금액, 추정가격 |
| **메타 정보** | instt_nm, rgn_nm, induty_ty_nm | 발주기관, 지역, 업종 |
| **발주기관 통계** | avg_rate, std_rate, count | 과거 평균 사정률, 표준편차, 건수 |
| **지역 통계** | rgn_avg_rate, rgn_count | 지역별 평균 사정률, 건수 |
| **업종 통계** | induty_avg_rate, induty_count | 업종별 평균 사정률, 건수 |
| **금액 구간 통계** | price_range_avg_rate | ±20% 구간 평균 사정률 |
| **유사 케이스** | similar_cases_count, avg_rate | 유사 입찰 건수 및 평균 |

**유사 케이스 탐색 조건:**
- 같은 발주기관
- 같은 지역
- 같은 업종
- 유사한 기초금액 (±30%)
- 최근 365일 이내

**✅ 학습 데이터 생성**

```python
# DNBP/LSTM 모델 학습용 DataFrame
df = processor.get_training_data(
    start_date, end_date, min_basis_price
)

# LSTM 시계열 데이터 생성
X, y = processor.get_time_series_data(
    instt_nm, rgn_nm, lookback_days, sequence_length
)
```

### 3. Celery Task Scheduler (`scheduler.py`)

주기적인 데이터 수집 및 처리를 자동화합니다.

#### 스케줄 구성

| 태스크 | 스케줄 | 설명 |
|--------|--------|------|
| `collect_bid_announcements_task` | **매 시간 정각** | 입찰공고 수집 (오늘 ~ 60일 후) |
| `collect_bid_results_task` | **매 6시간 30분** | 낙찰결과 수집 (30일 전 ~ 오늘) |
| `clean_data_task` | **매일 00:00** | 데이터 정제 및 검증 |
| `validate_data_task` | **매주 월요일 01:00** | 데이터 통계 및 검증 리포트 |

#### 수동 실행 태스크

```python
# 과거 데이터 일괄 수집 (예: 2023년 전체)
collect_historical_data_task.delay("20230101", "20231231")

# 즉시 수집 실행
trigger_immediate_collection()
```

#### Celery 설정

```python
broker = Redis (redis://localhost:6379/0)
result_backend = Redis
timezone = 'Asia/Seoul'
task_time_limit = 30분
task_soft_time_limit = 25분
```

### 4. 유틸리티 스크립트

#### `init_db.py` - 데이터베이스 초기화

```bash
python scripts/init_db.py
```

**기능:**
- PostgreSQL 테이블 자동 생성
- 인덱스 자동 생성
- 데이터베이스 연결 검증

#### `test_data_pipeline.py` - API 연동 테스트

```bash
python scripts/test_data_pipeline.py
```

**기능:**
- 입찰공고 API 테스트
- 낙찰결과 API 테스트
- DB 저장 테스트
- 데이터 전처리 테스트
- 샘플 데이터 출력

#### `collect_data.py` - 수동 데이터 수집

```bash
# 최근 데이터 수집 (30일 전 ~ 오늘, 오늘 ~ 60일 후)
python scripts/collect_data.py --mode recent

# 커스텀 기간
python scripts/collect_data.py --mode recent \
    --days-back 90 --days-forward 30

# 과거 데이터 대량 수집 (2023년 전체)
python scripts/collect_data.py --mode historical \
    --start-year 2023 --end-year 2023
```

### 5. 문서화

**✅ DATA_PIPELINE_GUIDE.md**
- 데이터 흐름 다이어그램
- 주요 컴포넌트 상세 설명
- API 사용법 및 예시
- 스크립트 사용법
- 데이터 정제 프로세스
- 특징 추출 상세
- Celery 설정 및 사용법
- 에러 처리 및 모니터링
- 트러블슈팅 가이드

## 📊 핵심 구현 내용

### 데이터 흐름

```
조달청 Open API
    ↓
[DataCollector]
    ├─ collect_bid_announcements() → bid_announcements 테이블
    └─ collect_bid_results() → bid_results 테이블
    ↓
[DataProcessor]
    ├─ clean_bid_results() → 데이터 정제
    ├─ extract_features_for_prediction() → 특징 추출
    └─ get_training_data() → 학습 DataFrame 생성
    ↓
[AI Model Training] (다음 단계)
```

### 데이터 정제 파이프라인

```python
1. 필수 필드 검증 (NULL 체크)
   ↓
2. 기초금액 필터링 (최소 100만원)
   ↓
3. 사정률 검증 (95% ~ 105% 범위)
   ↓
4. 사정률/투찰률 재계산
   ↓
5. 중복 데이터 제거 (최신 데이터만 유지)
   ↓
깨끗한 학습 데이터셋
```

### 특징 추출 전략

**다층 통계 분석:**
1. **발주기관 레벨**: 해당 기관의 과거 패턴
2. **지역 레벨**: 지역별 입찰 특성
3. **업종 레벨**: 업종별 경향
4. **금액 레벨**: 유사 금액대 분석
5. **케이스 레벨**: 다중 조건 유사 케이스

## 🎯 성능 및 안정성

### API 호출 최적화
- ✅ 비동기 처리 (httpx AsyncClient)
- ✅ Connection Pooling
- ✅ 재시도 로직 (Exponential Backoff)
- ✅ Rate Limit 대응 (429 에러 처리)

### 데이터베이스 최적화
- ✅ 배치 커밋 (페이지 단위)
- ✅ 인덱스 활용 (복합 인덱스)
- ✅ 중복 체크 최적화 (쿼리 최소화)

### 에러 처리
- ✅ 개별 레코드 저장 실패 시 스킵 (전체 중단 없음)
- ✅ 상세 로깅 (DEBUG, INFO, ERROR 레벨)
- ✅ 예외 복구 (try-except-finally 패턴)

## 📦 생성된 파일

```
✅ backend/app/services/
   ├── __init__.py
   ├── data_collector.py      # 조달청 API 연동 (14KB)
   └── data_processor.py      # 데이터 전처리 (15KB)

✅ backend/app/tasks/
   ├── __init__.py
   └── scheduler.py           # Celery 스케줄러 (10KB)

✅ scripts/
   ├── init_db.py             # DB 초기화
   ├── test_data_pipeline.py  # API 테스트
   └── collect_data.py        # 수동 데이터 수집

✅ DATA_PIPELINE_GUIDE.md     # 데이터 파이프라인 가이드 (7KB)
```

## 🚀 사용 방법

### 1. 환경 설정

```bash
# .env 파일에 API 키 설정
PROCUREMENT_API_KEY=your_api_key_here
```

### 2. 데이터베이스 초기화

```bash
python scripts/init_db.py
```

### 3. 데이터 수집 테스트

```bash
python scripts/test_data_pipeline.py
```

### 4. Docker Compose 실행

```bash
# 모든 서비스 시작 (PostgreSQL, Redis, Backend, Celery)
docker-compose up -d

# 로그 확인
docker-compose logs -f celery-worker
```

### 5. 수동 데이터 수집

```bash
# 최근 30일 데이터 수집
python scripts/collect_data.py --mode recent

# 2023년 데이터 수집
python scripts/collect_data.py --mode historical \
    --start-year 2023 --end-year 2023
```

## 📈 예상 데이터 규모

| 데이터 | 추정 건수 | 비고 |
|--------|-----------|------|
| **입찰공고 (연간)** | ~100,000건 | 매일 300건 내외 |
| **낙찰결과 (연간)** | ~50,000건 | 입찰공고의 약 50% |
| **학습 데이터 (2년)** | ~100,000건 | 정제 후 약 100,000건 |

## 🔄 Git Commit 정보

```bash
commit 9d25605
Date: 2026-02-26

feat: 데이터 파이프라인 구현 (조달청 API 연동 및 전처리)

- DataCollector 서비스 구현
- DataProcessor 서비스 구현
- Celery Task Scheduler 구현
- 유틸리티 스크립트 추가
- 문서화 (DATA_PIPELINE_GUIDE.md)
```

## 🎯 다음 단계: Step 3 - AI 모델 구현

Step 2에서 구축한 데이터 파이프라인을 기반으로 AI 모델을 구현합니다:

### DNBP 모델 (Deep learning Network to predict Budget Price)
1. 15개 가상 예비가격 생성
2. 최적화된 6개 노드(a, g, h, i, j, k) 선택
3. 딥러닝 신경망으로 상위 4개 추첨 확률 예측
4. 4개 평균으로 예정가격 사정률 도출

### LSTM 모델 (Long Short-Term Memory)
1. 시계열 데이터로 발주기관별 패턴 학습
2. 과거 N일간의 사정률 시퀀스 입력
3. 다음 사정률 예측

### 앙상블 로직
1. DNBP와 LSTM 예측값 가중 평균
2. 최종 추천 투찰금액 산출

---

**Step 2 완료! 🎉**

조달청 Open API와 연동하여 실시간 데이터를 수집하고, 정제하고, AI 학습에 적합한 형태로 변환하는 완전한 데이터 파이프라인이 구축되었습니다. 이제 AI 모델 학습을 위한 데이터가 준비되었습니다!
