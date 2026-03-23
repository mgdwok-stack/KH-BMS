# 🎯 통합 입찰 분석 시스템 - 완전 가이드

## ✅ 시스템 개요

**발주처별 통계**와 **PQ 대표사 분석**을 하나의 웹 인터페이스에서 제공하는 통합 시스템입니다.

---

## 💾 데이터베이스 저장 위치

### 1. 발주처별 DB (4개 파일)

```
📍 위치: /home/user/webapp/data/databases/
```

**파일 목록:**
- `경상남도.db` - 14건, 1개 프로젝트
- `경상남도 합천군.db` - 18건, 1개 프로젝트
- `충청북도 청주시.db` - 5건, 1개 프로젝트
- `한국어촌어항공단.db` - 6건, 6개 프로젝트

**총 43건의 발주처별 입찰 데이터**

**테이블 구조:**
```sql
CREATE TABLE bid_data (
    id INTEGER PRIMARY KEY,
    pq_no TEXT,
    announcement_date TEXT,
    project_name TEXT,
    organization TEXT,
    bid_type TEXT,
    base_amount TEXT,
    estimated_price TEXT,
    estimated_rate REAL,
    company_name TEXT,
    pq_score REAL,
    bid_amount TEXT,
    predicted_rate REAL,
    is_winner TEXT
);
```

### 2. PQ 통계 DB (1개 파일)

```
📍 위치: /home/user/webapp/data/bidbot_data.db
```

**내용:**
- 26개 대표사
- 43건 PQ 입찰 분석 데이터
- PQ순위별 투찰 행동 패턴
- 전략적 인사이트

**테이블 구조:**
```sql
CREATE TABLE Company_PQ_Stats (
    id INTEGER PRIMARY KEY,
    공고번호 TEXT,
    대표사 TEXT,
    업체명 TEXT,
    PQ점수 REAL,
    PQ순위 INTEGER,
    투찰률 REAL,
    기초금액 TEXT,
    예정금액 TEXT,
    예가 REAL,
    낙찰여부 TEXT,
    공고일자 TEXT,
    사업명 TEXT,
    발주처 TEXT,
    created_at TIMESTAMP
);
```

---

## 🌐 웹 인터페이스 접속

### 🎯 통합 웹 페이지 (추천!)

```
https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html
```

**3개의 탭으로 구성:**

#### [탭 1] 🏢 발주처별 통계
- 발주처 목록 카드 (4개 발주처)
- 발주처 선택 및 데이터 조회
- 테이블 형식으로 입찰 내역 표시
- 기초금액, 예정금액, 낙찰여부 등 상세 정보

#### [탭 2] 📊 PQ 대표사 분석
- PQ 전체 통계 (43건, 26개 대표사)
- 대표사 선택 드롭다운
- 기준 투찰률 조정 (기본 99.9%)
- PQ순위별 상세 분석
- 전략적 인사이트 자동 생성

#### [탭 3] 📈 전체 개요
- 시스템 전체 통계
- DB 저장 위치 정보
- 발주처 + PQ 통합 요약

---

## 🔧 API 서버 정보

### 서버 1: 발주처별 API (포트 8000)

**Base URL:** `http://localhost:8000`

**엔드포인트:**
- `GET /api/v1/organizations` - 발주처 목록
- `GET /api/v1/organizations/{org_name}` - 발주처별 데이터
- `GET /api/v1/organizations/{org_name}/stats` - 발주처 통계
- `POST /api/v1/create-db/{org_name}` - DB 생성
- `GET /api/v1/check-updates` - CSV 변경 확인
- `POST /api/v1/update-all-databases` - 전체 DB 업데이트

**Swagger UI:** `https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs`

### 서버 2: PQ 분석 API (포트 8001)

**Base URL:** `http://localhost:8001`

**엔드포인트:**
- `GET /api/v1/pq-stats` - PQ 전체 통계
- `GET /api/v1/pq-companies` - 대표사 목록
- `GET /api/v1/pq-analysis/{company_name}` - 대표사 분석

**Swagger UI:** `https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs`

---

## 📊 데이터 현황

### 발주처별 통계
- **총 발주처:** 4개
- **총 입찰 건수:** 43건
- **총 프로젝트:** 9개

**발주처 목록:**
1. 경상남도 - 14건
2. 경상남도 합천군 - 18건
3. 충청북도 청주시 - 5건
4. 한국어촌어항공단 - 6건

### PQ 대표사 통계
- **총 대표사:** 26개
- **총 입찰 기록:** 43건
- **PQ 순위 범위:** 1위 ~ 14위

**TOP 10 대표사:**
1. 건화 - 4건
2. 도화 - 4건
3. 삼안 - 3건
4. 건일 - 2건
5. 대영 - 2건
6. 동명 - 2건
7. 서영 - 2건
8. 수성 - 2건
9. 아라 - 2건
10. 유신 - 2건

---

## 💡 사용 예시

### 웹 브라우저에서

1. **통합 페이지 접속**
   ```
   https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html
   ```

2. **발주처별 통계 조회**
   - [탭 1] 클릭
   - "발주처 불러오기" 버튼 클릭
   - 원하는 발주처 선택
   - "조회하기" 버튼 클릭

3. **PQ 대표사 분석**
   - [탭 2] 클릭
   - "통계 불러오기" 버튼 클릭
   - 대표사 선택 (예: 도화, 건화)
   - "분석하기" 버튼 클릭

### Python으로 API 호출

```python
import requests

# 발주처 목록 조회
org_response = requests.get('http://localhost:8000/api/v1/organizations')
organizations = org_response.json()
print(f"발주처 수: {len(organizations)}")

# 특정 발주처 데이터 조회
org_data = requests.get('http://localhost:8000/api/v1/organizations/경상남도?limit=5')
print(org_data.json())

# PQ 대표사 분석
pq_response = requests.get('http://localhost:8001/api/v1/pq-analysis/도화?reference_rate=99.9')
analysis = pq_response.json()
print(f"회사명: {analysis['company_name']}")
print(f"총 입찰: {analysis['total_bids']}건")
```

### curl로 API 호출

```bash
# 발주처 목록
curl "http://localhost:8000/api/v1/organizations"

# 경상남도 데이터
curl "http://localhost:8000/api/v1/organizations/경상남도?limit=10"

# PQ 통계
curl "http://localhost:8001/api/v1/pq-stats"

# 도화 회사 분석
curl "http://localhost:8001/api/v1/pq-analysis/도화?reference_rate=99.9"
```

---

## 🔄 데이터 업데이트

### CSV 파일 업로드 위치

```
/home/user/webapp/data/upload_files/
```

새로운 CSV 파일을 이 폴더에 업로드하면 자동으로 감지됩니다.

### 수동 업데이트

```bash
# CLI로 업데이트
python3 auto_update_dbs.py

# 또는 강제 업데이트
python3 auto_update_dbs.py --force
```

### API로 업데이트

```bash
# 변경 사항 확인
curl "http://localhost:8000/api/v1/check-updates"

# 전체 DB 업데이트
curl -X POST "http://localhost:8000/api/v1/update-all-databases"
```

---

## 📁 프로젝트 구조

```
/home/user/webapp/
├── data/
│   ├── databases/              # 발주처별 DB
│   │   ├── 경상남도.db
│   │   ├── 경상남도 합천군.db
│   │   ├── 충청북도 청주시.db
│   │   └── 한국어촌어항공단.db
│   ├── bidbot_data.db         # PQ 통계 DB
│   └── upload_files/          # CSV 업로드 폴더
│       ├── 25년10월.CSV
│       └── 25년11월.CSV
│
├── static/
│   ├── index.html             # PQ 분석 페이지
│   └── unified.html           # 통합 페이지 ⭐
│
├── org_db_server.py           # 발주처 API 서버
├── pq_analysis_api.py         # PQ 분석 API 서버
├── create_db_by_org.py        # 발주처 DB 생성
├── pq_stats_analyzer.py       # PQ 통계 분석
└── auto_update_dbs.py         # 자동 업데이트
```

---

## 🎯 주요 기능

### ✅ 발주처별 분석
- CSV에서 발주처별 데이터 추출
- SQLite DB 자동 생성
- 사업명, 기초금액, 예정금액, 낙찰업체 관리
- 통계 정보 제공

### ✅ PQ 대표사 분석
- PQ공고별 순위 자동 계산
- 컨소시엄에서 대표사 추출
- PQ순위별 투찰 행동 패턴 분석
- 기준 투찰률 이상/미만 비율
- 전략적 인사이트 자동 생성

### ✅ 통합 웹 인터페이스
- 3개 탭으로 구성된 직관적 UI
- 실시간 데이터 조회
- 반응형 디자인 (모바일 지원)
- 테이블/카드 형식 시각화

### ✅ 자동화
- CSV 변경 감지 (MD5 해시)
- 자동 DB 업데이트
- API를 통한 원격 업데이트

---

## 🚀 실행 방법

### 서버 시작

```bash
# 발주처 API 서버 (포트 8000)
python3 org_db_server.py &

# PQ 분석 API 서버 (포트 8001)
python3 pq_analysis_api.py &
```

### 서버 상태 확인

```bash
# Health check
curl http://localhost:8000/health
curl http://localhost:8001/health
```

---

## 📖 추가 문서

- `ORGANIZATION_DB_GUIDE.md` - 발주처 DB 상세 가이드
- `PQ_ANALYSIS_SUMMARY.md` - PQ 분석 요약
- `AUTO_UPDATE_GUIDE.md` - 자동 업데이트 가이드
- `WEB_DEMO_READY.md` - 웹 데모 사용법

---

## 🎊 결론

**모든 기능이 하나의 통합 웹 페이지에서 동작합니다!**

지금 바로 접속하세요:
```
https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html
```

**DB 저장 위치:**
- 발주처 DB: `/home/user/webapp/data/databases/*.db`
- PQ 통계 DB: `/home/user/webapp/data/bidbot_data.db`

---

**작성일:** 2026-03-19  
**버전:** 2.0.0 (통합 버전)  
**상태:** ✅ 운영 중
