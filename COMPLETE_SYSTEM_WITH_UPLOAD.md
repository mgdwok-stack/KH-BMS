# 🎉 입찰 분석 통합 시스템 - 최종 완성 (CSV 업로드 기능 포함)

## ✅ 전체 시스템 기능

### 1. 🏢 발주처별 통계
- 발주처 목록 조회
- 발주처별 입찰 데이터 상세 조회
- 4개 발주처, 총 43건 데이터

### 2. 📊 PQ 대표사 분석
- PQ 전체 통계
- 대표사별 상세 분석
- 26개 대표사, 43건 PQ 기록
- PQ순위별 투찰 행동 패턴 분석

### 3. 📤 CSV 파일 업로드 (NEW!)
- 웹 브라우저에서 직접 CSV 업로드
- 업로드된 파일 자동 저장
- 파일 목록 및 관리
- 업로드 시간, 파일 크기 정보 표시

### 4. 📈 전체 시스템 개요
- 시스템 전체 통계
- 데이터베이스 위치 정보
- 파일 구조 안내

---

## 🌐 웹 브라우저에서 사용

### 메인 통합 웹 페이지
```
https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html
```

### 사용 가능한 4개 탭
1. **🏢 발주처별 통계**: 발주처 선택 → 입찰 데이터 조회
2. **📊 PQ 대표사 분석**: 대표사 선택 → 투찰 행동 분석
3. **📤 CSV 업로드**: 파일 선택 → 업로드 → 자동 저장
4. **📈 전체 개요**: 시스템 전체 현황 확인

---

## 📤 CSV 업로드 사용 방법

### Step 1: CSV 업로드 탭 선택
웹 페이지 상단에서 "📤 CSV 업로드" 탭 클릭

### Step 2: 파일 업로드
1. **"📁 CSV 파일 선택"** 버튼 클릭
2. 컴퓨터에서 CSV 파일 선택 (.csv 또는 .CSV)
3. 자동으로 업로드 시작
4. 성공 메시지 확인:
   ```
   ✅ 파일 업로드 성공! N건의 데이터가 업로드되었습니다.
   ```

### Step 3: 업로드된 파일 확인
- **"파일 목록 새로고침"** 버튼 클릭
- 업로드된 파일 목록 표시:
  - 파일명
  - 파일 크기 (KB)
  - 업로드 시간

### 현재 업로드된 파일
- `25년10월.CSV` (4.42 KB) - 2025년 10월 입찰 데이터
- `25년11월.CSV` (3.15 KB) - 2025년 11월 입찰 데이터

---

## 🔌 새로 추가된 API 엔드포인트

### 1. CSV 파일 업로드
```http
POST /api/v1/upload-csv
Content-Type: multipart/form-data

Parameters:
- file: CSV 파일 (required)
```

**응답 예시**:
```json
{
  "success": true,
  "message": "✅ 파일 업로드 성공! 24건의 데이터가 업로드되었습니다.",
  "filename": "25년10월.CSV",
  "records_count": 24
}
```

### 2. 업로드된 파일 목록
```http
GET /api/v1/uploaded-files
```

**응답 예시**:
```json
{
  "files": [
    {
      "filename": "25년10월.CSV",
      "size": 4527,
      "uploaded_at": "2026-03-19T07:33:58.801991"
    },
    {
      "filename": "25년11월.CSV",
      "size": 3223,
      "uploaded_at": "2026-03-19T07:33:09.337166"
    }
  ],
  "total": 2
}
```

### 3. 업로드된 파일 처리
```http
POST /api/v1/process-uploaded-files
```

**기능**:
- 업로드된 CSV 파일들을 처리
- 발주처별 DB 생성
- PQ 통계 DB 업데이트

---

## 📊 데이터 흐름

```
[사용자] 
  ↓ CSV 업로드
[웹 브라우저]
  ↓ POST /api/v1/upload-csv
[통합 API 서버 (8001)]
  ↓ 파일 저장
[data/upload_files/]
  ↓ 처리 요청
[DB 생성 스크립트]
  ↓
[SQLite 데이터베이스]
  ↓ 조회/분석
[웹 UI 표시]
```

---

## 🗂️ 파일 저장 위치

### 1. 업로드된 CSV 파일
```
/home/user/webapp/data/upload_files/
├── 25년10월.CSV (4.42 KB)
└── 25년11월.CSV (3.15 KB)
```

### 2. 발주처별 데이터베이스
```
/home/user/webapp/data/databases/
├── 경상남도.db (14건)
├── 경상남도 합천군.db (18건)
├── 충청북도 청주시.db (5건)
└── 한국어촌어항공단.db (6건)
```

### 3. PQ 통계 데이터베이스
```
/home/user/webapp/data/bidbot_data.db
- 26개 대표사
- 43건 PQ 입찰 기록
```

---

## 🔧 기술 스택

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **SQLite3**: 경량 데이터베이스
- **Pandas**: 데이터 분석 및 처리
- **python-multipart**: 파일 업로드 지원

### Frontend
- **HTML5**: 구조
- **CSS3**: 스타일링 (Gradient, Card layout)
- **JavaScript (Vanilla)**: 동적 기능
- **Fetch API**: 비동기 HTTP 요청

---

## 🧪 테스트 방법

### 웹 브라우저에서 테스트
1. 웹 페이지 열기: https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html
2. "📤 CSV 업로드" 탭 클릭
3. "📁 CSV 파일 선택" 버튼 클릭
4. 테스트 CSV 파일 선택 (data/upload_files/ 디렉토리의 파일 사용 가능)
5. 업로드 완료 메시지 확인
6. "파일 목록 새로고침" 클릭하여 파일 확인

### API 직접 테스트 (curl)

#### 파일 목록 조회
```bash
curl https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/api/v1/uploaded-files
```

#### CSV 업로드
```bash
curl -X POST \
  https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/api/v1/upload-csv \
  -F "file=@/path/to/your/file.csv"
```

---

## 💡 주요 개선 사항

### 이전 시스템 (backend/ 디렉토리)
- 별도의 백엔드/프론트엔드 구조
- 복잡한 설정 및 실행
- 엑셀 파서 서비스 분리

### 현재 통합 시스템
✅ **단일 API 서버** (포트 8001)
✅ **통합 웹 UI** (4개 탭)
✅ **CORS 에러 해결** (단일 도메인)
✅ **간단한 CSV 업로드**
✅ **실시간 파일 관리**

---

## 🔍 CSV 파일 형식

업로드 가능한 CSV 형식:
- 인코딩: CP949 (한글 지원)
- 구분자: 쉼표(,)
- 필수 컬럼:
  - `PQ공고 NO.`: 공고 번호
  - `업체명`: 입찰 참여 업체
  - `PQ점수`: PQ 평가 점수
  - `추정예가`: 예상 입찰가

---

## 🎯 향후 개선 계획

### Phase 1 (완료 ✅)
- ✅ 발주처별 통계 조회
- ✅ PQ 대표사 분석
- ✅ CSV 파일 업로드
- ✅ 통합 웹 UI

### Phase 2 (계획)
- 📋 엑셀 (.xlsx) 파일 지원
- 🔄 자동 DB 업데이트
- 📊 고급 통계 차트
- 📥 분석 결과 다운로드

### Phase 3 (계획)
- 🤖 AI 예측 모델 통합
- 📈 실시간 데이터 업데이트
- 👥 사용자 인증 및 권한
- 📱 모바일 최적화

---

## 📝 관련 문서

### 사용자 가이드
- `WEB_USAGE_GUIDE.md` - 웹 브라우저 상세 사용법
- `SYSTEM_STATUS.md` - 시스템 현재 상태
- `EXCEL_UPLOAD_GUIDE.md` - 원래 엑셀 업로드 시스템 설명

### 기술 문서
- `FINAL_UNIFIED_SYSTEM.md` - 통합 시스템 개요
- `PQ_ANALYSIS_SUMMARY.md` - PQ 분석 상세
- `ORGANIZATION_DB_GUIDE.md` - 발주처 DB 가이드

---

## 🚀 서버 실행 방법

```bash
cd /home/user/webapp

# 서버 시작
python3 pq_analysis_api.py

# 백그라운드 실행
nohup python3 pq_analysis_api.py > server.log 2>&1 &
```

서버 접속:
- 웹 UI: https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/static/unified.html
- API 문서: https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs
- Health Check: https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/health

---

## ✨ 최종 완성 기능 요약

| 기능 | 상태 | 설명 |
|------|------|------|
| 발주처 통계 | ✅ | 4개 발주처, 43건 데이터 |
| PQ 분석 | ✅ | 26개 대표사 분석 |
| CSV 업로드 | ✅ | 웹에서 직접 업로드 |
| 파일 관리 | ✅ | 목록 조회, 정보 표시 |
| 통합 UI | ✅ | 4개 탭, 반응형 디자인 |
| API 문서 | ✅ | Swagger 자동 생성 |
| CORS 해결 | ✅ | 단일 서버 통합 |

---

**✅ 모든 기능이 완벽하게 동작합니다!**

**최종 업데이트**: 2026-03-20
**버전**: v2.0.0 (CSV 업로드 기능 포함)
**상태**: 운영 중 🟢
