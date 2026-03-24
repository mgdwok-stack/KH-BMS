# 🎯 PQ 통계 분석 시스템 - 실행 완료 보고서

## ✅ 시스템 개요

CSV 파일에서 PQ(사전심사) 입찰 데이터를 분석하여 **대표사별 투찰 행동 패턴**을 분석하는 시스템이 완성되었습니다.

---

## 📊 주요 기능

### 1. **데이터 전처리 (완료)**
- CSV 파일에서 `PQ공고 NO.`, `업체명`, `PQ점수`, `추정예가` 추출
- 공고별 **PQ순위** 자동 계산 (PQ점수 기준 내림차순)
- 컨소시엄 `업체명`에서 **대표사** 추출 ('+' 기준 첫 번째)
- SQLite 데이터베이스 `bidbot_data.db` 생성

### 2. **데이터베이스 구조**
```sql
Table: Company_PQ_Stats
Columns:
  - 공고번호 (TEXT)
  - 대표사 (TEXT)
  - 업체명 (TEXT)
  - PQ점수 (REAL)
  - PQ순위 (INTEGER)
  - 투찰률 (REAL) -- 추정예가
  - 기초금액, 예정금액, 예가
  - 낙찰여부 (TEXT: 'O' or 'X')
  - 공고일자, 사업명, 발주처
```

### 3. **통계 분석 기능 (완료)**
각 대표사에 대해:
- **PQ순위별 그룹 분석**
  - 참여 횟수
  - 평균/최소/최대/중앙값 투찰률
  - 기준 투찰률(예: 99.9%) 이상/미만 비율
  - 낙찰 건수

- **전략적 인사이트 자동 생성**
  - 1순위일 때: 고가 vs. 저가 입찰 전략 판별
  - 2순위일 때: 경쟁적 vs. 안전한 입찰 전략 판별

---

## 🚀 실행 방법

### **CLI 방식 (터미널)**
```bash
cd /home/user/webapp

# 1. 데이터베이스 생성
python3 build_pq_database.py

# 2. 특정 회사 분석
python3 -c "
from analyze_pq_company import analyze_company_bidding
analyze_company_bidding('도화', reference_rate=99.9)
"
```

### **API 방식 (웹 서버)**
```bash
# 서버 실행
python3 pq_analysis_api.py

# 또는 백그라운드 실행
nohup python3 pq_analysis_api.py > pq_api.log 2>&1 &
```

---

## 🌐 API 엔드포인트

### **Base URL**
- **로컬**: `http://localhost:8001`
- **공개 URL**: `https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai`

### **엔드포인트 목록**

#### 1. PQ 전체 통계
```http
GET /api/v1/pq-stats
```
- 총 입찰 기록 수
- 등록된 대표사 목록 및 참여 횟수
- PQ순위별 전체 통계 (평균/최소/최대 투찰률)

#### 2. 대표사 목록 조회
```http
GET /api/v1/pq-companies
```
- 데이터베이스에 등록된 모든 대표사
- 각 대표사별 입찰 참여 횟수

#### 3. 대표사 상세 분석
```http
GET /api/v1/pq-analysis/{company_name}?reference_rate=99.9
```
- 특정 대표사의 PQ순위별 투찰 행동 분석
- 기준 투찰률 이상/미만 비율
- 전략적 인사이트

**예시**:
```bash
curl "http://localhost:8001/api/v1/pq-analysis/도화?reference_rate=99.9"
curl "http://localhost:8001/api/v1/pq-analysis/건화?reference_rate=99.9"
curl "http://localhost:8001/api/v1/pq-analysis/삼안?reference_rate=99.5"
```

---

## 📈 실행 결과 예시

### **도화 회사 분석 결과**
```
🏢 회사명: 도화
📊 총 입찰: 4건
📈 기준 투찰률: 99.9%

【PQ순위별 상세 분석】
  ▶ PQ순위 1위 (총 2건)
     평균 투찰률: 99.3% (범위: 98.59% ~ 100.0%)
     99.9% 이상: 1건 (50.0%)
     99.9% 미만: 1건 (50.0%)
     🏆 낙찰: 1건

  ▶ PQ순위 4위 (총 1건)
     평균 투찰률: 99.3%
     99.9% 이상: 0건 (0.0%)
     99.9% 미만: 1건 (100.0%)

  ▶ PQ순위 5위 (총 1건)
     평균 투찰률: 99.54%
     99.9% 이상: 0건 (0.0%)
     99.9% 미만: 1건 (100.0%)

【💡 전략적 인사이트】
  • 공격적 낙찰 전략 (저가 입찰, 50%가 99.9% 미만)
```

### **건화 회사 분석 결과**
```
🏢 회사명: 건화
📊 총 입찰: 4건

【PQ순위별 평균 투찰률】
  • PQ1위: 101.77% (1건)
  • PQ4위: 100.5% (1건)
  • PQ5위: 101.56% (1건)
  • PQ6위: 100.71% (1건)

【💡 전략적 인사이트】
  • 적극적 낙찰 전략 (안정적 고가 입찰, 100%가 99.9% 이상)
```

### **삼안 회사 분석 결과**
```
🏢 회사명: 삼안
📊 총 입찰: 3건

【PQ순위별 분석】
  • PQ1위: 평균 107.36% - 99.5% 이상 100.0% (1/1)
  • PQ2위: 평균 99.72% - 99.5% 이상 100.0% (1/1)
  • PQ3위: 평균 100.54% - 99.5% 이상 100.0% (1/1)

【💡 인사이트】
  • 적극적 낙찰 전략 (안정적 고가 입찰, 100%가 99.5% 이상)
  • 안전한 입찰 (평균 99.72%, 99.5% 이상)
```

---

## 📂 파일 구조

```
/home/user/webapp/
├── data/
│   ├── bidbot_data.db          # PQ 통계 SQLite 데이터베이스 (43건)
│   ├── upload_files/
│   │   ├── 25년10월.CSV        # 입력 CSV (24건)
│   │   └── 25년11월.CSV        # 입력 CSV (19건)
│   └── databases/               # 발주처별 DB (기존)
│
├── build_pq_database.py         # DB 생성 스크립트
├── pq_analysis_api.py           # PQ 분석 API 서버 ✅ 실행 중
└── PQ_ANALYSIS_SUMMARY.md       # 본 문서
```

---

## 🎯 핵심 성과

✅ **43건의 입찰 데이터** 분석 완료  
✅ **26개 대표사** 등록 및 분석 가능  
✅ **PQ순위별 투찰 행동 패턴** 자동 분석  
✅ **전략적 인사이트** 자동 생성  
✅ **RESTful API** 제공 (Swagger UI 포함)  
✅ **공개 URL** 접근 가능  

---

## 🔗 접속 정보

### **Swagger UI (대화형 API 문서)**
```
https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs
```

### **Health Check**
```
https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/health
```

---

## 📊 등록된 대표사 TOP 10

1. **건화** - 4건
2. **도화** - 4건
3. **삼안** - 3건
4. 건일 - 2건
5. 대영 - 2건
6. 동명 - 2건
7. 서영 - 2건
8. 수성 - 2건
9. 아라 - 2건
10. 유신 - 2건

---

## 💡 사용 예시

### **Python에서 API 호출**
```python
import requests

base_url = "https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai"

# 도화 회사 분석
response = requests.get(f"{base_url}/api/v1/pq-analysis/도화?reference_rate=99.9")
data = response.json()

print(f"회사명: {data['company_name']}")
print(f"총 입찰: {data['total_bids']}건")

for rank in data['rank_analysis']:
    print(f"PQ{rank['rank']}위: 평균 {rank['avg_rate']}%")
```

### **curl로 API 호출**
```bash
# 전체 통계
curl "https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/api/v1/pq-stats"

# 건화 회사 분석
curl "https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/api/v1/pq-analysis/건화?reference_rate=99.9"
```

---

## ✅ 테스트 완료

- ✅ CSV 데이터 전처리
- ✅ SQLite 데이터베이스 생성
- ✅ PQ순위 계산
- ✅ 대표사 추출
- ✅ 통계 분석 기능
- ✅ 인사이트 자동 생성
- ✅ RESTful API 서버
- ✅ 공개 URL 접근
- ✅ Swagger UI 문서화

---

## 🎉 결론

**PQ 통계 분석 시스템이 완벽하게 구현되어 실행 중입니다!**

이제 Swagger UI(`/docs`)를 통해 직접 API를 테스트하거나,  
Python/curl 등으로 API를 호출하여 대표사별 투찰 행동 분석 결과를 확인할 수 있습니다.

---

**작성일**: 2026-03-19  
**API 버전**: 1.0.0  
**상태**: ✅ 운영 중
