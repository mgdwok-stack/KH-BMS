# 실제 입찰 데이터 분석 가이드

## 📊 현재 상태

### 데이터베이스 통계
- **총 입찰 공고**: 200건
- **낙찰 결과**: 172건 (성공률 86%)
- **평균 기초금액**: 5.27B KRW
- **평균 사정률**: 100.21%
- **사정률 범위**: 95% ~ 105%

### 지역별 분석
| 지역 | 공고 수 | 평균 기초금액 | 평균 사정률 |
|------|---------|--------------|------------|
| 전북 | 15 | 5.94B KRW | 101.19% |
| 제주 | 15 | 5.08B KRW | 99.75% |
| 충북 | 15 | 4.19B KRW | 100.60% |
| 서울 | 14 | 6.25B KRW | 99.02% |

### 업종별 분석
| 업종 | 공고 수 | 평균 기초금액 | 평균 사정률 |
|------|---------|--------------|------------|
| 산림사업 | 24 | 5.36B KRW | 100.34% |
| 조경공사 | 23 | 5.73B KRW | 101.09% |
| 문화재수리공사 | 22 | 4.96B KRW | 100.00% |
| 전기공사 | 22 | 5.06B KRW | 99.95% |

---

## 🚀 서버 실행 방법

### 1. 데이터베이스 초기화 (처음 한 번만)
```bash
cd /home/user/webapp/backend
python scripts/init_db.py
```

### 2. 샘플 데이터 생성 (또는 실제 API 수집)
```bash
# 방법 A: 샘플 데이터 생성 (빠름, 테스트용)
python scripts/generate_sample_data.py

# 방법 B: 실제 API에서 수집 (조달청 API 키 필요)
python scripts/collect_data.py --mode recent --days 7
python scripts/collect_data.py --mode historical --start-date 2024-12-01 --end-date 2024-12-31
```

### 3. 데이터 분석
```bash
python scripts/analyze_real_data.py
```

### 4. API 서버 실행
```bash
cd /home/user/webapp/backend
python real_data_server.py
```

서버 접속:
- **API Root**: http://localhost:8000/
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API 엔드포인트

### 1. 입찰 공고 목록
```bash
GET /api/v1/bids/?page=1&page_size=20

# 필터링
GET /api/v1/bids/?region=서울&industry=토목건축공사
GET /api/v1/bids/?min_price=1000000000&max_price=5000000000
```

**응답 예시:**
```json
{
  "total": 200,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "bid_ntce_no": "202410000-00",
      "bid_ntce_nm": "행정안전부 시설물유지관리",
      "ntce_instt_nm": "행정안전부",
      "dminstt_nm": "강원",
      "industry_ty_nm": "시설물유지관리",
      "basis_prc": 9060000000.0,
      "basis_prc_display": "9.06B KRW",
      "ntce_dt": "20241201120000",
      "bid_status": "개찰완료"
    }
  ]
}
```

### 2. 입찰 공고 상세
```bash
GET /api/v1/bids/202410000-00
```

**응답 예시:**
```json
{
  "announcement": {
    "id": 1,
    "bid_ntce_no": "202410000-00",
    "bid_ntce_nm": "행정안전부 시설물유지관리",
    "ntce_instt_nm": "행정안전부",
    "dminstt_nm": "강원",
    "industry_ty_nm": "시설물유지관리",
    "basis_prc": 9060000000.0,
    "basis_prc_display": "9.06B KRW",
    "ntce_dt": "20241201120000",
    "bid_clse_dt": "20241215140000",
    "opng_dt": "20241216100000",
    "bid_status": "개찰완료"
  },
  "result": {
    "prdprc_rate": 98.83,
    "prdprc": 8953638000.0,
    "prdprc_display": "8.95B KRW",
    "sucbid_prc": 8169714342.0,
    "sucbid_prc_display": "8.17B KRW",
    "sucbid_rate": 91.26,
    "opng_dt": "20241216100000"
  }
}
```

### 3. 전체 통계
```bash
GET /api/v1/analytics/summary
```

**응답 예시:**
```json
{
  "total_stats": {
    "total_announcements": 200,
    "total_results": 172,
    "success_rate": 86.0,
    "avg_basis_prc": 5265885000.0,
    "avg_basis_prc_display": "5.27B KRW"
  },
  "prediction_rate_stats": {
    "avg_prdprc_rate": 100.21,
    "min_prdprc_rate": 95.0,
    "max_prdprc_rate": 105.0,
    "range": 10.0
  }
}
```

### 4. 지역별 통계
```bash
GET /api/v1/analytics/regional
```

**응답 예시:**
```json
{
  "regions": [
    {
      "region": "전북",
      "count": 15,
      "avg_basis_prc": 5943466667.0,
      "avg_basis_prc_display": "5.94B KRW",
      "avg_prdprc_rate": 101.19
    }
  ]
}
```

### 5. 업종별 통계
```bash
GET /api/v1/analytics/industry
```

### 6. 기관별 통계
```bash
GET /api/v1/analytics/institution
```

---

## 🔑 조달청 API 키 설정

### API 키 발급
1. https://www.data.go.kr/ 접속
2. 회원가입 / 로그인
3. **"조달청_입찰공고정보서비스"** 신청
4. 승인 후 **일반 인증키** 복사

### API 키 입력
```bash
# .env 파일에 추가
echo "PROCUREMENT_API_KEY=1a37dcc24d4168e1966e..." >> /home/user/webapp/.env
```

### 실제 데이터 수집
```bash
cd /home/user/webapp/backend

# 최근 7일 데이터 수집
python scripts/collect_data.py --mode recent --days 7

# 특정 기간 데이터 수집
python scripts/collect_data.py --mode historical \
  --start-date 2024-01-01 \
  --end-date 2024-12-31
```

---

## 📈 데이터 분석 예시

### Python 스크립트로 분석
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import BidAnnouncement, BidResult

engine = create_engine('sqlite:////home/user/webapp/data/bidbot.db')
Session = sessionmaker(bind=engine)
session = Session()

# 전체 공고 수
total = session.query(BidAnnouncement).count()
print(f"Total announcements: {total}")

# 평균 사정률
avg_rate = session.query(func.avg(BidResult.prdprc_rate)).scalar()
print(f"Average prediction rate: {avg_rate:.2f}%")

# 서울 지역 공고
seoul_bids = session.query(BidAnnouncement).filter(
    BidAnnouncement.dminstt_nm == '서울'
).all()
```

### SQL로 직접 분석
```bash
sqlite3 /home/user/webapp/data/bidbot.db

# 사정률 분포
SELECT 
  ROUND(prdprc_rate, 0) as rate,
  COUNT(*) as count
FROM bid_results
GROUP BY ROUND(prdprc_rate, 0)
ORDER BY rate;

# 기관별 평균 사정률
SELECT 
  a.ntce_instt_nm,
  COUNT(*) as count,
  ROUND(AVG(r.prdprc_rate), 2) as avg_rate
FROM bid_announcements a
JOIN bid_results r ON a.bid_ntce_no = r.bid_ntce_no
GROUP BY a.ntce_instt_nm
ORDER BY count DESC
LIMIT 10;
```

---

## 🎯 다음 단계

### 1. AI 모델 학습
```bash
# TODO: 모델 학습 스크립트 작성
python scripts/train_dnbp_model.py
python scripts/train_lstm_model.py
python scripts/train_ensemble_model.py
```

### 2. 예측 API 구현
- DNBP 모델 예측
- LSTM 모델 예측
- 앙상블 예측
- 신뢰도 계산

### 3. 프론트엔드 연동
- React 대시보드 연동
- 실시간 차트 업데이트
- 필터링 UI 개선

### 4. 자동화
- Celery 스케줄러 설정
- 매일 자동 데이터 수집
- 모델 재학습 파이프라인

---

## 📝 참고 자료

- **프로젝트 문서**: `/home/user/webapp/docs/`
- **API 문서**: http://localhost:8000/docs
- **데이터베이스**: `/home/user/webapp/data/bidbot.db`
- **로그**: `/home/user/webapp/logs/`

---

**마지막 업데이트**: 2026-02-26
**버전**: 1.0.0
