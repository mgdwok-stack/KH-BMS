# 🔐 안전한 API 키 설정 가이드

## 📋 개요

조달청(나라장터) API 키를 안전하게 설정하여 실제 입찰 데이터를 수집하는 방법입니다.

---

## 🎯 API 키 발급받기

### 1. 공공데이터포털 회원가입
1. **공공데이터포털** 접속: https://www.data.go.kr/
2. 회원가입 (무료)
3. 로그인

### 2. API 신청
1. 검색창에 **"조달청 입찰공고"** 검색
2. **"조달청_입찰공고정보서비스"** 선택
3. **"활용신청"** 버튼 클릭
4. 이용목적 작성 (예: 입찰 데이터 분석)
5. 신청 완료

### 3. API 키 확인
1. 마이페이지 > 오픈API > 개발계정
2. **일반 인증키(Encoding)** 복사
3. 예시: `AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`

---

## 🔒 방법 1: 자동 스크립트 사용 (추천 ⭐)

### 실행 방법
```bash
cd /home/user/webapp
./setup_api_key.sh
```

### 장점
- ✅ API 키가 화면에 표시되지 않음
- ✅ 파일 권한 자동 설정 (600)
- ✅ .gitignore 자동 추가
- ✅ 기존 .env 파일 자동 백업

---

## 🔒 방법 2: 수동 설정

### Step 1: .env 파일 생성
```bash
cd /home/user/webapp
cp .env.example .env
```

### Step 2: 안전하게 편집
```bash
# nano 에디터 사용 (화면에 표���됨 - 주의!)
nano .env

# 또는 vim 사용
vim .env
```

### Step 3: API 키 입력
```bash
# 이 부분을 수정
PROCUREMENT_API_KEY=여기에_실제_API_키_입력
```

### Step 4: 파일 권한 설정
```bash
# 소유자만 읽기/쓰기 가능하도록 설정
chmod 600 .env

# 권한 확인
ls -la .env
# 출력 예: -rw------- 1 user user 1234 Feb 26 10:00 .env
```

### Step 5: Git 제외 확인
```bash
# .gitignore에 .env 추가되어 있는지 확인
cat .gitignore | grep ".env"

# 없으면 추가
echo ".env" >> .gitignore
```

---

## 🔒 방법 3: 환경 변수로 직접 설정 (임시)

### 현재 세션에만 적용 (재시작 시 사라짐)
```bash
export PROCUREMENT_API_KEY="여기에_실제_API_키_입력"

# 확인 (처음 몇 글자만 표시)
echo ${PROCUREMENT_API_KEY:0:10}...
```

### Python 스크립트에서 바로 사용
```bash
PROCUREMENT_API_KEY="여기에_실제_API_키" python scripts/collect_data.py --mode recent
```

---

## ✅ API 키 설정 확인

### 1. .env 파일 확인 (보안 - 일부만 표시)
```bash
# API 키의 처음 10자만 표시
grep PROCUREMENT_API_KEY .env | cut -d'=' -f2 | cut -c1-10
```

### 2. Python에서 확인
```bash
cd /home/user/webapp/backend
python -c "
import os
from dotenv import load_dotenv
load_dotenv('../.env')
key = os.getenv('PROCUREMENT_API_KEY')
if key and len(key) > 10:
    print(f'✅ API 키 설정 완료: {key[:10]}...{key[-4:]}')
else:
    print('❌ API 키가 설정되지 않았습니다')
"
```

### 3. API 연결 테스트
```bash
cd /home/user/webapp/backend
python scripts/test_data_pipeline.py
```

---

## 🔐 보안 베스트 프랙티스

### ✅ 해야 할 것
1. **파일 권한 설정**
   ```bash
   chmod 600 .env
   ```

2. **.gitignore에 추가**
   ```bash
   echo ".env" >> .gitignore
   echo ".env.local" >> .gitignore
   echo ".env.*.local" >> .gitignore
   ```

3. **환경별 분리**
   ```bash
   .env.development  # 개발용
   .env.production   # 운영용
   .env.test         # 테스트용
   ```

4. **정기적 교체**
   - 3-6개월마다 API 키 재발급

### ❌ 하지 말아야 할 것
1. **.env 파일을 Git에 커밋**
   ```bash
   # 절대 하지 마세요!
   git add .env  # ❌
   ```

2. **API 키를 코드에 직접 하드코딩**
   ```python
   # 나쁜 예 ❌
   API_KEY = "AbCdEf123456..."
   
   # 좋은 예 ✅
   API_KEY = os.getenv('PROCUREMENT_API_KEY')
   ```

3. **API 키를 로그에 출력**
   ```python
   # 나쁜 예 ❌
   print(f"API Key: {API_KEY}")
   
   # 좋은 예 ✅
   print(f"API Key: {API_KEY[:10]}...")
   ```

4. **API 키를 다른 사람과 공유**
   - 이메일, 메신저, 화면 캡처에 API 키 포함 금지

---

## 🚀 API 키 설정 후 실행

### Step 1: 데이터베이스 초기화
```bash
cd /home/user/webapp/backend
python scripts/init_db.py
```

### Step 2: 데이터 수집 테스트
```bash
# 최근 데이터 소량 수집 (테스트)
python scripts/collect_data.py --mode recent

# 성공 시 출력:
# ✅ 입찰공고 10건 수집 완료
# ✅ 낙찰결과 8건 수집 완료
```

### Step 3: 전체 데이터 수집
```bash
# 과거 1년치 데이터 수집
python scripts/collect_data.py --mode historical --start-year 2024 --start-month 1 --end-year 2024 --end-month 12
```

### Step 4: AI 모델 학습
```bash
# 최소 1,000건 이상 데이터 필요
python scripts/train_models.py
```

### Step 5: 백엔드 서버 재시작
```bash
# 데모 서버 종료
pkill -f demo_server.py

# 실제 서버 실행 (API 키 포함)
cd /home/user/webapp/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔍 문제 해결

### 문제 1: API 키가 작동하지 않음
```bash
# API 키 형식 확인
# - 길이: 보통 40-80자
# - 특수문자 없음 (영문, 숫자만)
# - 공백 없음

# 테스트
curl "http://apis.data.go.kr/1230000/ScsbidInfoService/getDataSetOpnStdBidPblancInfo?serviceKey=여기에_API_키&pageNo=1&numOfRows=10"
```

### 문제 2: 권한 오류
```bash
# .env 파일 권한 확인
ls -la .env

# 권한 재설정
chmod 600 .env
```

### 문제 3: API 키가 로드되지 않음
```bash
# .env 파일 위치 확인
pwd
ls -la .env

# Python에서 재확인
python -c "
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.env')
print(f'📁 .env 파일 위치: {env_path.absolute()}')
print(f'📄 파일 존재: {env_path.exists()}')

load_dotenv()
key = os.getenv('PROCUREMENT_API_KEY')
print(f'🔑 API 키 로드: {'✅' if key else '❌'}')
"
```

---

## 📊 API 사용량 모니터링

### 공공데이터포털에서 확인
1. 로그인 > 마이페이지
2. 오픈API > 활용통계
3. 일일 사용량 확인

### 사용량 제한
- **일반 계정**: 하루 1,000 ~ 10,000건
- **프리미엄 계정**: 무제한 (신청 필요)

### 제한 초과 시
```bash
# 에러 메시지 예:
# "SERVICE_KEY_IS_NOT_REGISTERED_ERROR"
# "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR"

# 해결 방법:
# 1. 다음 날까지 대기
# 2. 프리미엄 계정 신청
# 3. 수집 간격 조정 (Celery 스케줄러)
```

---

## 🎯 요약

### 가장 안전한 방법 (추천 순서)

1. **🥇 자동 스크립트**
   ```bash
   ./setup_api_key.sh
   ```

2. **🥈 수동 설정 + 권한 설정**
   ```bash
   nano .env
   chmod 600 .env
   ```

3. **🥉 환경 변수 (임시)**
   ```bash
   export PROCUREMENT_API_KEY="..."
   ```

### 핵심 보안 원칙
- ✅ 파일 권한: `chmod 600 .env`
- ✅ Git 제외: `.env` in `.gitignore`
- ✅ 정기 교체: 3-6개월
- ❌ Git 커밋 금지
- ❌ 코드 하드코딩 금지
- ❌ 공유 금지

---

**API 키 설정 후 실제 입찰 데이터를 수집하고 AI 예측을 시작하세요!** 🚀
