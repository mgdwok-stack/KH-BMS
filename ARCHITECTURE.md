# Bid-Bot Clone: System Architecture

## 시스템 개요

Bid-Bot Clone은 조달청 공공데이터를 기반으로 딥러닝(DNBP, LSTM)을 활용하여 최적의 낙찰하한가와 사정률을 예측하는 AI 입찰 분석 솔루션입니다.

## 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                    (React Dashboard)                         │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                        │
│                      (FastAPI)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Bids API     │  │ Predictions  │  │ Analytics    │      │
│  │ /api/v1/bids │  │ API          │  │ API          │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│  Data Collection │ │  AI Prediction│ │  Database    │
│  Service         │ │  Service      │ │  Layer       │
│                  │ │               │ │              │
│ ┌──────────────┐ │ │ ┌──────────┐ │ │ PostgreSQL   │
│ │ Celery Worker│ │ │ │ DNBP     │ │ │              │
│ │              │ │ │ │ Model    │ │ │ ┌──────────┐ │
│ │ Scheduler    │ │ │ └──────────┘ │ │ │ bid_     │ │
│ │ (APScheduler)│ │ │              │ │ │ announce-│ │
│ └──────────────┘ │ │ ┌──────────┐ │ │ │ ments    │ │
│         ▲        │ │ │ LSTM     │ │ │ └──────────┘ │
│         │        │ │ │ Model    │ │ │              │
│         │        │ │ └──────────┘ │ │ ┌──────────┐ │
│         │        │ │              │ │ │ bid_     │ │
│         │        │ │ ┌──────────┐ │ │ │ results  │ │
│    ┌────┴─────┐  │ │ │ Ensemble │ │ │ └──────────┘ │
│    │  Redis   │  │ │ │ Logic    │ │ │              │
│    │  Queue   │  │ │ └──────────┘ │ │ ┌──────────┐ │
│    └──────────┘  │ │              │ │ │ predict- │ │
└──────────────────┘ └──────────────┘ │ │ ions     │ │
            │                          │ └──────────┘ │
            ▼                          └──────────────┘
┌─────────────────────────────────────┐
│   External Data Source              │
│   조달청 나라장터 Open API           │
│                                     │
│  - getDataSetOpnStdBidPblancInfo   │
│    (입찰공고정보)                    │
│  - getDataSetOpnStdScsbidInfo      │
│    (낙찰정보)                        │
└─────────────────────────────────────┘
```

## 시스템 컴포넌트

### 1. Frontend Layer (React)

#### 주요 컴포넌트
- **Dashboard**: 전체 입찰 현황 대시보드
- **BidList**: 입찰공고 목록 및 필터링
- **BidDetail**: 입찰공고 상세 정보 및 AI 예측 결과
- **Analytics**: 통계 분석 및 시각화
- **UserSettings**: 사용자 설정 및 필터 관리

#### 기술 스택
- React 18+ with Hooks
- Redux Toolkit (상태 관리)
- Recharts (데이터 시각화)
- TailwindCSS (스타일링)
- Axios (HTTP 클라이언트)

### 2. Backend Layer (FastAPI)

#### API 엔드포인트 구조

```
/api/v1/
├── bids/
│   ├── GET /                      # 입찰공고 목록 조회
│   ├── GET /{bid_id}              # 입찰공고 상세 조회
│   ├── GET /search                # 입찰공고 검색
│   └── GET /filters               # 필터 옵션 조회
│
├── predictions/
│   ├── POST /predict              # 사정률 예측 요청
│   ├── GET /{prediction_id}       # 예측 결과 조회
│   ├── GET /history               # 예측 이력 조회
│   └── GET /accuracy              # 예측 정확도 조회
│
├── analytics/
│   ├── GET /trends                # 사정률 트렌드 분석
│   ├── GET /institutions          # 발주기관별 통계
│   └── GET /regions               # 지역별 통계
│
└── users/
    ├── GET /preferences           # 사용자 설정 조회
    └── PUT /preferences           # 사용자 설정 수정
```

#### 서비스 레이어
- **DataCollector**: 조달청 API 데이터 수집
- **DataProcessor**: 데이터 전처리 및 정제
- **Predictor**: AI 모델 예측 서비스
- **AnalyticsService**: 통계 분석 서비스

### 3. Data Collection Layer

#### Celery Task Scheduler
주기적으로 조달청 API를 호출하여 데이터를 수집하고 DB에 저장

**주요 작업**:
1. **입찰공고 수집** (매 시간마다)
   - API: `getDataSetOpnStdBidPblancInfo`
   - 신규 공고 확인 및 DB 저장
   - 기존 공고 상태 업데이트

2. **낙찰결과 수집** (매 6시간마다)
   - API: `getDataSetOpnStdScsbidInfo`
   - 개찰 완료된 공고의 결과 데이터 수집
   - AI 모델 학습 데이터셋 업데이트

3. **데이터 정제** (매일 자정)
   - 결측치 제거
   - 이상치 탐지 및 처리
   - 중복 데이터 제거

### 4. AI/ML Layer

#### DNBP 모델 (Deep learning Network to predict Budget Price)

**목적**: 복수예비가격 산출 로직을 딥러닝으로 모방

**구조**:
```python
Input Layer: 6 nodes (최적화된 예비가격 구간 a, g, h, i, j, k)
    ↓
Hidden Layer 1: 64 nodes (ReLU activation)
    ↓
Hidden Layer 2: 32 nodes (ReLU activation)
    ↓
Hidden Layer 3: 16 nodes (ReLU activation)
    ↓
Output Layer: 15 nodes (Softmax - 15개 예비가격 확률 분포)
    ↓
Top 4 Selection: 상위 4개 추출
    ↓
Average: 4개의 평균 → 예정가격 사정률
```

**학습 데이터**:
- Input: 기초금액 기준 생성된 15개 가상 예비가격 중 6개 선택
- Output: 실제 추첨된 4개의 예비가격 번호
- Loss Function: Categorical Crossentropy
- Optimizer: Adam

**예측 프로세스**:
1. 기초금액(basis_prce) 입력
2. 예가범위(±2% 또는 ±3%) 기준으로 15개 가상 예비가격 생성
3. 최적화된 6개 노드(a, g, h, i, j, k) 값 추출
4. DNBP 모델로 15개 중 상위 4개 확률 예측
5. 상위 4개의 평균값 계산 → 예정가격 사정률

#### LSTM 모델 (Long Short-Term Memory)

**목적**: 시계열 패턴을 학습하여 발주기관별/지역별 사정률 예측

**구조**:
```python
Input Layer: Sequence of past N bid results (시계열 데이터)
    ↓
LSTM Layer 1: 128 units (return_sequences=True)
    ↓
Dropout: 0.2
    ↓
LSTM Layer 2: 64 units
    ↓
Dropout: 0.2
    ↓
Dense Layer 1: 32 units (ReLU activation)
    ↓
Output Layer: 1 unit (Linear - 사정률 예측)
```

**학습 데이터**:
- Input: 과거 N일간의 입찰 결과 시퀀스 (사정률, 발주기관, 지역, 업종 등)
- Output: 다음 입찰의 사정률
- Loss Function: Mean Squared Error (MSE)
- Optimizer: Adam

**특징 엔지니어링**:
- 발주기관별 과거 평균 사정률
- 지역별 과거 평균 사정률
- 업종별 과거 평균 사정률
- 기초금액 구간별 평균 사정률
- 시간적 트렌드 (월별, 분기별)

#### 앙상블 로직

**목적**: DNBP와 LSTM의 예측을 결합하여 최종 사정률 도출

**방법**: 가중 평균 (Weighted Average)

```python
final_rate = (dnbp_rate × w1) + (lstm_rate × w2)

# 기본 가중치
w1 = 0.6  # DNBP (복수예비가격 로직 중심)
w2 = 0.4  # LSTM (시계열 패턴 중심)

# 동적 가중치 조정
if similar_cases_count > 100:
    # 유사 케이스가 많으면 LSTM 가중치 증가
    w2 += 0.1
    w1 -= 0.1
```

**최종 추천 투찰금액 계산**:
```python
predicted_prdprc = basis_prce × (final_rate / 100)
recommended_bid_amt = predicted_prdprc × 0.87745  # 일반적인 낙찰하한율
```

### 5. Database Layer

#### PostgreSQL 스키마
- **bid_announcements**: 입찰공고 정보 (약 10만+ 레코드/년)
- **bid_results**: 낙찰결과 정보 (약 5만+ 레코드/년, 학습 데이터)
- **predictions**: AI 예측 결과 (무제한)
- **user_preferences**: 사용자 설정 (사용자당 1 레코드)

#### 인덱싱 전략
- 조회 성능 최적화를 위한 복합 인덱스
- 시계열 데이터는 날짜 기준 인덱스
- 발주기관, 지역, 업종 등 필터링 컬럼 인덱스

## 데이터 흐름

### 1. 데이터 수집 흐름
```
[조달청 API]
    ↓ HTTP Request (Celery Task)
[DataCollector Service]
    ↓ Parse & Validate
[DataProcessor Service]
    ↓ Clean & Transform
[PostgreSQL Database]
    ↓ Query for Training
[AI Model Training]
```

### 2. 예측 요청 흐름
```
[User Request]
    ↓ POST /api/v1/predictions/predict
[FastAPI Endpoint]
    ↓ Load Bid Announcement
[Predictor Service]
    ├─→ [DNBP Model] → dnbp_rate
    ├─→ [LSTM Model] → lstm_rate
    └─→ [Ensemble Logic] → final_rate
        ↓ Calculate
    [Prediction Result]
        ↓ Save to DB
    [Return to User]
```

### 3. 대시보드 조회 흐름
```
[User Browser]
    ↓ GET Request
[React Dashboard]
    ↓ API Call
[FastAPI Endpoint]
    ↓ Query with Filters
[PostgreSQL Database]
    ↓ Return Data
[Analytics Service] (if needed)
    ↓ Process & Aggregate
[JSON Response]
    ↓ Render
[Charts & Tables]
```

## 보안 설계

### 1. API 보안
- **API Key 관리**: 환경 변수로 관리, 코드에 하드코딩 금지
- **Rate Limiting**: API 호출 빈도 제한 (조달청 API 정책 준수)
- **CORS 설정**: 허용된 도메인만 접근 가능

### 2. 데이터 보안
- **민감 정보 암호화**: 사용자 정보는 암호화 저장
- **SQL Injection 방지**: SQLAlchemy ORM 사용
- **환경 변수 분리**: `.env` 파일로 설정 관리

### 3. 인증/인가 (향후 구현)
- JWT 토큰 기반 인증
- 사용자별 접근 권한 관리

## 성능 최적화

### 1. 캐싱 전략
- **Redis 캐시**: 자주 조회되는 데이터 캐싱
- **결과 캐싱**: 동일한 입찰공고에 대한 예측은 재사용

### 2. 쿼리 최적화
- **인덱스 활용**: 모든 필터 컬럼에 인덱스
- **N+1 문제 방지**: Eager Loading 사용
- **페이지네이션**: 대량 데이터 조회 시 필수

### 3. 비동기 처리
- **Celery Task Queue**: 무거운 작업은 백그라운드 처리
- **FastAPI Async**: I/O 바운드 작업은 비동기 처리

## 모니터링 & 로깅

### 1. 로깅
- **Application Log**: 모든 주요 이벤트 로깅
- **Error Log**: 에러 발생 시 상세 정보 기록
- **Performance Log**: API 응답 시간 측정

### 2. 모니터링 (향후 구현)
- **Prometheus**: 메트릭 수집
- **Grafana**: 대시보드 시각화
- **Sentry**: 에러 추적

## 배포 전략

### 1. Docker 컨테이너화
- 모든 서비스를 Docker 컨테이너로 패키징
- Docker Compose로 로컬 개발 환경 구축

### 2. CI/CD (향후 구현)
- GitHub Actions: 자동화된 테스트 및 배포
- Docker Hub: 이미지 저장소

### 3. 프로덕션 배포 (향후 구현)
- AWS ECS / Kubernetes
- Load Balancer
- Auto Scaling

## 확장 가능성

### 1. 수평 확장
- FastAPI 서버: 다중 인스턴스 실행 가능
- Celery Worker: 워커 수 증가로 처리량 향상
- PostgreSQL: Read Replica로 읽기 성능 향상

### 2. 기능 확장
- 실시간 알림 기능 (WebSocket)
- 모바일 앱 (React Native)
- 더 많은 AI 모델 추가 (Transformer, Attention Mechanism)

## 개발 로드맵

### Phase 1: MVP (현재)
- ✅ 프로젝트 구조 설계
- ✅ 데이터베이스 스키마 설계
- ⏳ 조달청 API 연동
- ⏳ DNBP 모델 구현
- ⏳ LSTM 모델 구현
- ⏳ 기본 API 엔드포인트 구현
- ⏳ 기본 React 대시보드 구현

### Phase 2: 고도화
- 예측 정확도 향상
- 사용자 인증/인가 시스템
- 알림 기능
- 고급 필터링 및 검색

### Phase 3: 프로덕션
- 성능 최적화
- 보안 강화
- 모니터링 시스템
- 프로덕션 배포

## 결론

Bid-Bot Clone은 조달청 공공데이터와 AI 기술을 결합하여 입찰 과정의 투명성과 효율성을 높이는 솔루션입니다. DNBP와 LSTM 모델의 앙상블을 통해 높은 정확도의 사정률 예측을 제공하며, 직관적인 UI/UX로 사용자 경험을 극대화합니다.
