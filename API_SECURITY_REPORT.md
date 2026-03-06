# 🔐 나라장터 API 키 보안 및 연결 상태 보고서

**작성일**: 2026-03-06  
**프로젝트**: KH-BMS (Bid-Bot Clone)

---

## 📋 요약

### ✅ 보안 상태: **안전**
- API 키는 `.env` 파일에 안전하게 저장되어 있습니다
- `.env` 파일은 Git에 추적되지 않습니다
- `.gitignore`에 포함되어 GitHub에 업로드되지 않습니다

### ⚠️ API 연결 상태: **실패** (500 에러)
- API 키가 만료되었거나 잘못된 것으로 보입니다
- 모든 엔드포인트에서 "Unexpected errors" 응답

---

## 🔍 상세 분석

### 1. API 키 저장 위치

#### 현재 저장 위치
```
/home/user/webapp/.env
```

#### .env 파일 내용
```env
PROCUREMENT_API_KEY=1a37dcc24d4168e1966e433f34d421011424a76102dc5146f7cd4ae708ab2313
PROCUREMENT_API_BASE_URL=http://apis.data.go.kr/1230000/ScsbidInfoService
```

#### API 키 정보
- **길이**: 64자
- **형식**: 16진수 문자열
- **앞 10자**: `1a37dcc24d...`

---

### 2. 보안 검증

#### ✅ .gitignore 확인
```bash
# .gitignore에 포함됨
venv/
env/
.env
.env.local
```

#### ✅ Git 추적 여부
```bash
# 명령: git ls-files | grep -E "^\.env$"
# 결과: (빈 결과) - Git에 추적되지 않음 ✅
```

#### ✅ Git 히스토리 확인
```bash
# 명령: git log --all --full-history -- .env
# 결과: (빈 결과) - 한 번도 커밋되지 않음 ✅
```

#### ✅ GitHub 확인
- `.env` 파일은 GitHub에 업로드되지 않았습니다
- Repository: https://github.com/mgdwok-stack/KH-BMS
- Branch: genspark_ai_developer

---

### 3. API 사용처

#### 백엔드 코드에서의 사용
```python
# backend/app/config.py
PROCUREMENT_API_KEY: str = os.getenv("PROCUREMENT_API_KEY", "")
PROCUREMENT_API_BASE_URL: str = os.getenv("PROCUREMENT_API_BASE_URL", "...")

# backend/app/services/data_collector.py
class DataCollector:
    def __init__(self, db: Session):
        self.api_key = settings.PROCUREMENT_API_KEY
        self.base_url = settings.PROCUREMENT_API_BASE_URL
        
        if not self.api_key:
            logger.warning("PROCUREMENT_API_KEY가 설정되지 않았습니다.")
```

#### 프론트엔드
- ❌ 프론트엔드에서는 API 키를 직접 사용하지 않음 (안전)
- ✅ 백엔드 API를 통해서만 데이터 조회

---

### 4. API 연결 테스트 결과

#### 테스트 1: 기본 엔드포인트
```
URL: http://apis.data.go.kr/1230000/ScsbidInfoService/getBidPblancListInfoServc
응답 코드: 500
응답 내용: Unexpected errors
결과: ❌ 실패
```

#### 테스트 2: 다양한 엔드포인트
```
1. getBidPblancListInfoServc01  → 500 에러
2. getOpengBidInfoServc01       → 500 에러
3. getPblancListInfoServc01     → 500 에러
```

#### 실패 원인 분석
1. **API 키 만료** (가장 가능성 높음)
   - 공공데이터포털의 API 키는 주기적으로 갱신 필요
   - 활용신청 승인 상태 확인 필요
   
2. **API URL 변경**
   - 조달청 API가 업데이트되어 URL이 변경되었을 수 있음
   
3. **서비스 일시 중단**
   - 나라장터 API 서버 점검 중일 수 있음

---

## 🔧 API 키 갱신 방법

### 1. 공공데이터포털 접속
```
https://www.data.go.kr/
```

### 2. 로그인 및 마이페이지 접속
- 마이페이지 → 인증키 관리 → 일반 인증키

### 3. 조달청 나라장터 API 확인
- API명: **조달청_나라장터_입찰정보 서비스**
- 서비스 ID: `1230000/ScsbidInfoService`

### 4. 새 API 키 발급
1. 기존 키 상태 확인
2. 필요시 재발급 요청
3. 승인 대기 (보통 1~2일)
4. 새 키 발급 후 `.env` 파일 업데이트

### 5. .env 파일 업데이트
```bash
cd /home/user/webapp
nano .env

# PROCUREMENT_API_KEY를 새 키로 변경
PROCUREMENT_API_KEY=새로운_64자_API_키
```

### 6. 서버 재시작
```bash
# 백엔드 서버 재시작
cd /home/user/webapp/backend
python real_data_server.py
```

---

## 📊 현재 데이터베이스 상태

### 데이터베이스 경로
```
/home/user/webapp/data/bidbot.db
```

### 저장된 데이터
```
- BidAnnouncement: 300건 (입찰공고)
- BidResult: 266건 (낙찰결과)
- 성공률: 88.7%
```

### 데이터 출처
- ✅ 기존에 수집된 샘플 데이터 (정상 작동)
- ❌ 실시간 API 연동 (현재 실패)

---

## ✅ 보안 권장사항

### 1. 환경 변수 사용 (현재 적용됨 ✅)
```python
# ✅ 좋은 예 (현재 사용 중)
api_key = os.getenv('PROCUREMENT_API_KEY', '')

# ❌ 나쁜 예
api_key = "1a37dcc24d4168e1966e433f34d421011424a76102dc5146f7cd4ae708ab2313"
```

### 2. .gitignore 설정 (현재 적용됨 ✅)
```gitignore
# 민감한 정보 파일
.env
.env.local
.env.*.local

# 데이터베이스 파일
*.db
*.sqlite
```

### 3. .env.example 파일 제공 (현재 적용됨 ✅)
```env
# .env.example (GitHub에 포함 가능)
PROCUREMENT_API_KEY=your_api_key_here
PROCUREMENT_API_BASE_URL=http://apis.data.go.kr/1230000/ScsbidInfoService
```

### 4. 프론트엔드에서 API 키 노출 금지 (현재 적용됨 ✅)
- ✅ 백엔드에서만 API 키 사용
- ✅ 프론트엔드는 백엔드 API를 통해 데이터 조회

### 5. API 키 정기 갱신
- ⚠️ 권장: 3~6개월마다 API 키 갱신
- ⚠️ 공공데이터포털에서 키 상태 정기 확인

---

## 🚀 다음 단계

### 즉시 조치 필요
1. **API 키 갱신** (우선순위: 높음)
   - 공공데이터포털 접속
   - 조달청 나라장터 API 키 상태 확인
   - 필요시 재발급 요청

2. **API 엔드포인트 확인** (우선순위: 중간)
   - 공공데이터포털에서 최신 API 문서 확인
   - URL 및 파라미터 변경사항 확인

### 장기 개선사항
1. **API 키 보안 강화**
   - 환경 변수 암호화 고려
   - AWS Secrets Manager / Azure Key Vault 사용 검토

2. **API 모니터링**
   - API 호출 성공/실패 로그 수집
   - 일일/주간 보고서 자동 생성

3. **백업 API 키**
   - 메인 API 키 실패 시 백업 키로 자동 전환
   - 다중 API 키 관리 시스템

---

## 📝 관련 문서

- [공공데이터포털](https://www.data.go.kr/)
- [조달청 나라장터](https://www.g2b.go.kr/)
- [API 문서](https://www.data.go.kr/data/15000018/openapi.do)

---

## 🔗 참고 링크

- **GitHub Repository**: https://github.com/mgdwok-stack/KH-BMS
- **Branch**: genspark_ai_developer
- **Pull Request**: https://github.com/mgdwok-stack/KH-BMS/pull/1
- **프로젝트 문서**: `/home/user/webapp/`

---

## 📞 문의

API 키 관련 문제 발생 시:
1. 공공데이터포털 고객센터: 1577-5725
2. 조달청 고객센터: 1588-0800
3. 이메일: help@data.go.kr
