# Bid-Bot Clone: AI 입찰 분석 솔루션

## 프로젝트 개요
대한민국 조달청 나라장터 오픈 API를 활용하여 딥러닝(DNBP, LSTM)으로 최적의 낙찰하한가와 사정률을 예측하는 AI 입찰 분석 솔루션입니다.

## 핵심 기능
- 📊 조달청 공공데이터 실시간 수집 및 저장
- 🤖 DNBP(Deep learning Network to predict Budget Price) 모델 기반 예측
- 📈 LSTM 시계열 분석을 통한 사정률 패턴 학습
- 🎯 앙상블 기법을 활용한 최적 투찰금액 추천
- 📱 직관적인 대시보드 UI/UX

## 기술 스택
### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Task Queue**: Celery + Redis
- **API Client**: httpx

### AI/ML
- **Framework**: TensorFlow 2.x / PyTorch 2.x
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn

### Frontend
- **Framework**: React 18+
- **State Management**: Redux Toolkit
- **Charts**: Recharts
- **Styling**: TailwindCSS
- **Build Tool**: Vite

### DevOps
- **Container**: Docker & Docker Compose
- **API Documentation**: OpenAPI (Swagger)

## 프로젝트 구조
```
bid-bot-clone/
├── backend/                    # Python 백엔드
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 애플리케이션 엔트리포인트
│   │   ├── config.py          # 환경 설정
│   │   ├── database.py        # DB 연결 설정
│   │   ├── models/            # SQLAlchemy 모델
│   │   │   ├── __init__.py
│   │   │   ├── bid.py         # 입찰공고 모델
│   │   │   └── result.py      # 낙찰결과 모델
│   │   ├── schemas/           # Pydantic 스키마
│   │   │   ├── __init__.py
│   │   │   ├── bid.py
│   │   │   └── prediction.py
│   │   ├── api/               # API 라우터
│   │   │   ├── __init__.py
│   │   │   ├── bids.py        # 입찰 관련 엔드포인트
│   │   │   └── predictions.py # 예측 엔드포인트
│   │   ├── services/          # 비즈니스 로직
│   │   │   ├── __init__.py
│   │   │   ├── data_collector.py  # 조달청 API 연동
│   │   │   ├── data_processor.py  # 데이터 전처리
│   │   │   └── predictor.py       # AI 예측 서비스
│   │   ├── ml/                # 머신러닝 모델
│   │   │   ├── __init__.py
│   │   │   ├── dnbp_model.py      # DNBP 모델
│   │   │   ├── lstm_model.py      # LSTM 모델
│   │   │   ├── ensemble.py        # 앙상블 로직
│   │   │   └── trainer.py         # 모델 학습
│   │   └── tasks/             # Celery 태스크
│   │       ├── __init__.py
│   │       └── scheduler.py   # 데이터 수집 스케줄러
│   ├── tests/                 # 테스트 코드
│   ├── alembic/               # DB 마이그레이션
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React 프론트엔드
│   ├── public/
│   ├── src/
│   │   ├── components/        # 재사용 컴포넌트
│   │   │   ├── Dashboard/
│   │   │   ├── BidList/
│   │   │   ├── PredictionCard/
│   │   │   └── Charts/
│   │   ├── pages/             # 페이지 컴포넌트
│   │   │   ├── Home.jsx
│   │   │   ├── BidDetail.jsx
│   │   │   └── Analytics.jsx
│   │   ├── services/          # API 호출
│   │   │   └── api.js
│   │   ├── store/             # Redux 스토어
│   │   ├── utils/             # 유틸리티 함수
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── ml_notebooks/              # Jupyter 노트북 (실험/분석)
│   ├── data_exploration.ipynb
│   ├── dnbp_experiment.ipynb
│   └── lstm_training.ipynb
│
├── scripts/                   # 유틸리티 스크립트
│   ├── init_db.py            # DB 초기화
│   └── seed_data.py          # 샘플 데이터 생성
│
├── docker-compose.yml         # Docker 컴포즈 설정
├── .env.example              # 환경변수 예시
├── .gitignore
└── README.md
```

## 데이터베이스 스키마

### 1. bid_announcements (입찰공고 정보)
- 조달청 API의 입찰공고 데이터를 저장
- 기초금액, 추정가격, 입찰방식 등 입찰 기본 정보

### 2. bid_results (낙찰결과 정보)
- 개찰 후 낙찰가격, 투찰률, 사정률 등 결과 데이터
- DNBP/LSTM 모델 학습의 핵심 데이터셋

### 3. predictions (예측 결과)
- AI 모델이 생성한 예측 사정률 및 추천 투찰금액
- 사용자별 예측 이력 관리

### 4. user_preferences (사용자 설정)
- 사용자별 지역, 업종, 면허 필터링 설정

## 설치 및 실행

### 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 필요한 값들을 설정하세요
```

### Docker를 이용한 실행
```bash
docker-compose up -d
```

### 로컬 개발 환경

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API 문서
백엔드 서버 실행 후 다음 URL에서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 주요 API 엔드포인트
- `GET /api/v1/bids` - 입찰공고 목록 조회
- `GET /api/v1/bids/{bid_id}` - 입찰공고 상세 조회
- `POST /api/v1/predictions/predict` - 사정률 예측
- `GET /api/v1/analytics/trends` - 통계 및 트렌드 분석

## 조달청 API 연동
- **서비스명**: 조달청_나라장터 공공데이터개방표준서비스
- **API KEY**: 공공데이터포털에서 발급 필요
- **주요 엔드포인트**:
  - `getDataSetOpnStdBidPblancInfo`: 입찰공고정보
  - `getDataSetOpnStdScsbidInfo`: 낙찰정보

## AI 모델 아키텍처

### DNBP 모델
1. 기초금액 기준 ±2~3% 범위에서 15개 가상 예비가격 생성
2. 최적화된 6개 입력 노드 선택 (a, g, h, i, j, k)
3. 딥러닝 신경망으로 상위 4개 추첨 확률 예측
4. 4개 사정률의 산술평균으로 예정가격 사정률 도출

### LSTM 모델
1. 시계열 입찰 데이터로 발주기관별/지역별 패턴 학습
2. 과거 N일간의 사정률 추이를 입력으로 다음 사정률 예측

### 앙상블
- DNBP와 LSTM의 예측값을 가중 평균하여 최종 추천 사정률 산출
- 가중치는 검증 데이터셋에서 최적화

## 라이선스
MIT License

## 기여 방법
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 개발자
- Full-Stack & AI Engineer

## 참고 자료
- [조달청 나라장터](https://www.g2b.go.kr)
- [공공데이터포털](https://www.data.go.kr)
