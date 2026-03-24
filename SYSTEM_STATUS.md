# 🎯 입찰 분석 통합 시스템 - 현재 상태

## ✅ 시스템 운영 상태
- **상태**: 정상 운영 중 ✅
- **서버**: pq_analysis_api.py (PID: 3375)
- **포트**: 8001
- **업데이트**: 2026-03-20

---

## 📂 데이터베이스 현황

### 1. 발주처별 SQLite DB
**위치**: `/home/user/webapp/data/databases/`

| 발주처 | 파일명 | 레코드 수 | 프로젝트 수 |
|--------|--------|-----------|-------------|
| 경상남도 | 경상남도.db | 14건 | 1개 |
| 경상남도 합천군 | 경상남도 합천군.db | 18건 | 1개 |
| 충청북도 청주시 | 충청북도 청주시.db | 5건 | 5개 |
| 한국어촌어항공단 | 한국어촌어항공단.db | 6건 | 1개 |
| **합계** | | **43건** | **8개** |

### 2. PQ 통계 DB
**위치**: `/home/user/webapp/data/bidbot_data.db`
- 대표사: 26개
- PQ 입찰 기록: 43건
- PQ순위: 1위~14위

---

## 🌐 웹 접근 URL

### 메인 통합 웹 페이지
```
https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html
```
**기능**:
- 🏢 발주처별 통계 (조회 및 분석)
- 📊 PQ 대표사 분석 (투찰 행동 패턴)
- 📈 전체 개요 (시스템 통계)

### Swagger API 문서
```
https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs
```
**기능**:
- API 문서 자동 생성
- 브라우저에서 직접 API 테스트
- Request/Response 예시

---

## 🔌 API 엔드포인트

### 발주처 관련
| Method | Endpoint | 설명 | 상태 |
|--------|----------|------|------|
| GET | `/api/v1/organizations` | 발주처 목록 | ✅ |
| GET | `/api/v1/organizations/{org_name}` | 발주처 입찰 데이터 | ✅ |

### PQ 분석 관련
| Method | Endpoint | 설명 | 상태 |
|--------|----------|------|------|
| GET | `/api/v1/pq-stats` | PQ 전체 통계 | ✅ |
| GET | `/api/v1/pq-companies` | 대표사 목록 | ✅ |
| GET | `/api/v1/pq-analysis/{company_name}` | 대표사 상세 분석 | ✅ |

### 기타
| Method | Endpoint | 설명 | 상태 |
|--------|----------|------|------|
| GET | `/` | 루트 (HTML 데모) | ✅ |
| GET | `/health` | 헬스 체크 | ✅ |
| GET | `/docs` | API 문서 | ✅ |

---

## 🧪 테스트 결과

### 최근 테스트 (2026-03-20)
- ✅ 발주처 목록 조회: 4개 발주처 정상 반환
- ✅ 경상남도 데이터: 14건 정상 조회
- ✅ PQ 전체 통계: 43건, 26개 대표사
- ✅ PQ 대표사 분석: 도화, 건화, 삼안 등 정상 분석
- ✅ 웹 페이지: 모든 탭 정상 동작
- ✅ CORS: 에러 없음 (단일 서버 통합)

---

## 🔧 해결된 이슈

### Issue #1: CORS 에러
- **문제**: 웹 페이지에서 8000, 8001 두 포트 접근 시 CORS 에러
- **해결**: 단일 API 서버(8001)로 통합, `API_BASE = ''` 사용
- **상태**: ✅ 해결

### Issue #2: 데이터베이스 테이블명 불일치
- **문제**: API 코드에서 `bids` 테이블 사용, 실제는 `bid_data`
- **해결**: 실제 스키마 확인 후 `bid_data` 사용
- **상태**: ✅ 해결

### Issue #3: 컬럼명 불일치
- **문제**: 한글 컬럼명(`공고번호`) 사용 시 오류
- **해결**: 영문 컬럼명(`pq_no`) 사용
- **상태**: ✅ 해결

---

## 📊 주요 분석 결과

### TOP 3 대표사 (참여 건수)
1. **건화**: 4건
2. **도화**: 4건  
3. **삼안**: 3건

### PQ1위 평균 투찰률
- **도화**: 99.3% (공격적 저가)
- **건화**: 101.77% (안정적 고가)
- **삼안**: 107.36% (공격적 고가)

### 낙찰 패턴
- PQ1위에서 낙찰률이 가장 높음
- 고가 입찰 전략이 안정적
- 저가 입찰 전략은 위험하지만 효과적

---

## 📝 관련 문서

### 사용자 가이드
- `WEB_USAGE_GUIDE.md` - 웹 브라우저 사용 가이드
- `FINAL_UNIFIED_SYSTEM.md` - 시스템 전체 개요
- `UNIFIED_SYSTEM_GUIDE.md` - 통합 시스템 가이드

### 기술 문서
- `PQ_ANALYSIS_SUMMARY.md` - PQ 분석 상세 설명
- `ORGANIZATION_DB_GUIDE.md` - 발주처 DB 가이드
- `pq_analysis_api.py` - API 서버 소스 코드

### 데이터 파일
- `upload_files/25년10월.CSV` - 2025년 10월 CSV 원본
- `upload_files/25년11월.CSV` - 2025년 11월 CSV 원본

---

## 🚀 서버 재시작 방법

```bash
cd /home/user/webapp

# 기존 서버 종료
lsof -ti:8001 | xargs kill -9 2>/dev/null

# 서버 시작
python3 pq_analysis_api.py
```

---

## 💾 백업 권장사항

### 중요 파일
1. `/home/user/webapp/data/databases/*.db` - 발주처별 DB
2. `/home/user/webapp/data/bidbot_data.db` - PQ 통계 DB
3. `/home/user/webapp/upload_files/*.CSV` - 원본 CSV
4. `/home/user/webapp/pq_analysis_api.py` - API 서버

### 백업 명령어
```bash
cd /home/user/webapp
tar -czf backup_$(date +%Y%m%d).tar.gz data/ upload_files/ *.py static/
```

---

## 📞 연락처 및 지원

### 문제 발생 시
1. 서버 로그 확인
2. API 문서(/docs) 확인
3. 브라우저 개발자 도구(F12) 확인

### 시스템 상태 확인
```bash
# 서버 프로세스 확인
ps aux | grep pq_analysis_api

# 포트 확인
lsof -i:8001

# DB 파일 확인
ls -lh data/databases/
ls -lh data/bidbot_data.db
```

---

**✅ 모든 시스템이 정상 운영 중입니다!**

**최종 업데이트**: 2026-03-20
**시스템 버전**: v1.0.0
**상태**: 운영 중 🟢
