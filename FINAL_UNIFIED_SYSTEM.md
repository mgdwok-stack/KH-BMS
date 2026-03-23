# 🎯 입찰 분석 통합 시스템 - 최종 완성

## ✅ 완료된 기능

### 1. 발주처별 통계 시스템
- **데이터베이스 저장 위치**: `/home/user/webapp/data/databases/`
- **포함된 발주처**:
  - 경상남도 (14건, 1개 프로젝트)
  - 경상남도 합천군 (18건, 1개 프로젝트)
  - 충청북도 청주시 (5건, 5개 프로젝트)
  - 한국어촌어항공단 (6건, 1개 프로젝트)

### 2. PQ 대표사 분석 시스템
- **데이터베이스 저장 위치**: `/home/user/webapp/data/bidbot_data.db`
- **분석 데이터**:
  - 총 43건의 PQ 입찰 기록
  - 26개 대표사 통계
  - PQ순위별 투찰 행동 분석

### 3. 통합 API 서버
**단일 포트(8001)에서 모든 기능 제공 (CORS 에러 해결완료)**

#### API 엔드포인트

##### 발주처 관련
- `GET /api/v1/organizations` - 발주처 목록 조회
- `GET /api/v1/organizations/{org_name}?limit=10` - 특정 발주처 입찰 데이터 조회

##### PQ 분석 관련
- `GET /api/v1/pq-stats` - PQ 전체 통계
- `GET /api/v1/pq-companies` - 대표사 목록
- `GET /api/v1/pq-analysis/{company_name}?reference_rate=99.9` - 대표사별 상세 분석

## 🌐 웹 브라우저 테스트

### 메인 통합 웹 페이지
```
https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html
```

**기능**:
1. **발주처별 통계 탭**: 발주처 목록 및 입찰 데이터 조회
2. **PQ 대표사 분석 탭**: 대표사별 PQ순위 및 투찰 행동 분석
3. **전체 개요 탭**: 시스템 전체 통계 및 DB 저장 위치 확인

### Swagger API 문서
```
https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs
```
- 모든 API 엔드포인트를 브라우저에서 직접 테스트 가능
- 자동 생성된 API 문서 및 테스트 인터페이스

## 🧪 API 테스트 예시

### 1. 발주처 목록 조회
```bash
curl https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/api/v1/organizations
```

### 2. 경상남도 데이터 조회
```bash
curl "https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/api/v1/organizations/%EA%B2%BD%EC%83%81%EB%82%A8%EB%8F%84?limit=10"
```

### 3. PQ 전체 통계
```bash
curl https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/api/v1/pq-stats
```

### 4. 도화 대표사 분석
```bash
curl "https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/api/v1/pq-analysis/%EB%8F%84%ED%99%94?reference_rate=99.9"
```

## 📊 분석 결과 예시

### 도화 회사 분석
- **총 입찰**: 4건
- **PQ1위** (2건): 평균 99.3%, 99.9% 이상 50%, 낙찰 1건
- **PQ4위** (1건): 평균 99.3%
- **PQ5위** (1건): 평균 99.54%
- **전략**: 공격적 저가 입찰 (50% 99.9% 미만)

### 건화 회사 분석
- **총 입찰**: 4건
- **PQ1위** (1건): 평균 101.77%, 99.9% 이상 100%, 낙찰 1건
- **전략**: 안정적 고가 입찰

### 삼안 회사 분석
- **총 입찰**: 3건
- **PQ1위** (1건): 평균 107.36%, 99.5% 이상 100%
- **PQ2위** (1건): 평균 99.72%, 99.5% 이상 100%
- **전략**: 안전 + 공격적 입찰 혼합

## 🔧 기술 스택
- **Backend**: FastAPI (Python 3)
- **Database**: SQLite3
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Server**: Uvicorn ASGI
- **Port**: 8001 (통합 서버)

## 📁 파일 구조
```
/home/user/webapp/
├── data/
│   ├── databases/           # 발주처별 SQLite DB
│   │   ├── 경상남도.db
│   │   ├── 경상남도 합천군.db
│   │   ├── 충청북도 청주시.db
│   │   └── 한국어촌어항공단.db
│   └── bidbot_data.db      # PQ 통계 DB
├── static/
│   └── unified.html         # 통합 웹 페이지
├── pq_analysis_api.py       # 통합 API 서버 (발주처 + PQ)
├── build_pq_database.py     # PQ DB 생성 스크립트
├── create_db_by_org.py      # 발주처별 DB 생성
└── test_unified_api.sh      # API 테스트 스크립트
```

## 🎯 주요 해결 사항

### 1. CORS 에러 해결
- **문제**: 웹 페이지에서 두 개의 다른 포트(8000, 8001) API 호출 시 CORS 에러 발생
- **해결**: 단일 API 서버(8001 포트)에 모든 API 통합, `API_BASE = ''` 사용

### 2. 데이터베이스 스키마 호환
- **문제**: 조직 DB의 테이블/컬럼명이 한글로 되어있어 오류 발생
- **해결**: 실제 스키마 확인 후 영문 컬럼명 사용
  - 테이블명: `bids` → `bid_data`
  - 컬럼명: `공고번호` → `pq_no`, `사업명` → `project_name` 등

### 3. 통합 API 서버 구현
- **기능**: 발주처 API + PQ 분석 API를 하나의 서버로 통합
- **이점**: CORS 설정 간소화, 관리 편의성, 사용자 경험 개선

## 🚀 서버 실행 방법
```bash
cd /home/user/webapp
python3 pq_analysis_api.py
```

서버가 시작되면 다음 주소에서 접근 가능:
- 웹 데모: https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html
- API 문서: https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs

## 📝 사용 가이드

### 웹 브라우저에서 사용
1. 통합 웹 페이지 URL을 브라우저에서 열기
2. 상단 탭에서 원하는 기능 선택:
   - **발주처별 통계**: 발주처 선택 → 조회하기
   - **PQ 대표사 분석**: 대표사 선택 → 기준 투찰률 설정 → 분석하기
   - **전체 개요**: 시스템 전체 통계 확인

### API로 직접 호출
Swagger UI (https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs)에서:
1. 원하는 API 엔드포인트 선택
2. "Try it out" 버튼 클릭
3. 파라미터 입력
4. "Execute" 버튼 클릭
5. 결과 확인

## ✨ 완료 날짜
2026-03-20

## 📞 문제 해결
- 모든 CORS 에러 해결 완료
- 단일 포트(8001)로 통합 운영
- 데이터베이스 스키마 호환성 확보
- 웹 브라우저에서 모든 기능 정상 동작 확인

---

**✅ 시스템 정상 동작 중**
