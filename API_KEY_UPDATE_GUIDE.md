# 🔑 API 키 업데이트 상세 가이드

**작성일**: 2026-03-06  
**대상**: 비개발자도 이해할 수 있는 상세 설명

---

## 🖥️ 현재 작업 환경 이해하기

### 1️⃣ 지금 어디서 작업하고 있나요?

#### 작업 환경 정보
```
📍 위치: e2b.local (샌드박스 클라우드 환경)
👤 사용자: user
🏠 홈 디렉토리: /home/user
📂 프로젝트 디렉토리: /home/user/webapp
```

#### ⚠️ 중요한 이해
**이것은 귀하의 개인 컴퓨터가 아닙니다!**

- 이곳은 **클라우드 샌드박스** 환경입니다
- AI 어시스턴트(저)가 작업하는 **임시 가상 컴퓨터**입니다
- **귀하의 실제 PC/Mac과는 완전히 분리**되어 있습니다

```
[귀하의 컴퓨터] ←→ [인터넷] ←→ [클라우드 샌드박스 (현재 위치)]
                                    └─ /home/user/webapp
```

---

## 📂 프로젝트 구조

### 전체 구조
```
/home/user/webapp/          ← 프로젝트 최상위 폴더
├── .env                    ← ⭐ API 키가 저장된 파일 (여기를 수정해야 함!)
├── .env.example            ← 예제 파일 (수정하면 안 됨)
├── .gitignore              ← Git 제외 목록
├── backend/                ← 백엔드 코드
│   ├── app/
│   │   ├── config.py       ← .env 파일을 읽는 코드
│   │   ├── services/
│   │   │   └── data_collector.py  ← API를 호출하는 코드
│   └── real_data_server.py ← 백엔드 서버 실행 파일
├── frontend/               ← 프론트엔드 코드
│   └── public/
│       └── excel_upload.html
└── data/                   ← 데이터베이스 및 업로드 파일
    ├── bidbot.db
    └── uploads/
```

### .env 파일의 정확한 위치
```
전체 경로: /home/user/webapp/.env
         └─────┬─────┘└──┬──┘└┬┘
               │         │   └─ 파일 이름
               │         └───── 프로젝트 폴더
               └─────────────── 절대 경로
```

---

## 🔍 .env 파일 현재 내용 확인

### 현재 저장된 내용
```env
DATABASE_URL=sqlite:////home/user/webapp/data/bidbot.db
REDIS_URL=redis://localhost:6379/0
PROCUREMENT_API_KEY=1a37dcc24d4168e1966e433f34d421011424a76102dc5146f7cd4ae708ab2313
                    └───────────────────────┬───────────────────────┘
                                    현재 API 키 (64자)
PROCUREMENT_API_BASE_URL=http://apis.data.go.kr/1230000/ScsbidInfoService
APP_NAME=Bid-Bot Clone
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
... (기타 설정들)
```

### 수정해야 할 부분
```
⭐ 3번째 줄: PROCUREMENT_API_KEY=... ← 이 부분만 수정
```

---

## 🔧 API 키 업데이트 방법

### 📋 준비물
1. ✅ 공공데이터포털 계정
2. ✅ 새로 발급받은 API 키 (64자 문자열)
3. ✅ 이 가이드 문서

---

## 🎯 방법 1: 명령어로 직접 수정 (추천)

### Step 1: 현재 API 키 확인
```bash
cd /home/user/webapp
cat .env | grep PROCUREMENT_API_KEY
```

**예상 출력**:
```
PROCUREMENT_API_KEY=1a37dcc24d4168e1966e433f34d421011424a76102dc5146f7cd4ae708ab2313
```

### Step 2: 백업 생성 (안전을 위해)
```bash
cd /home/user/webapp
cp .env .env.backup
echo "✅ 백업 완료: .env.backup"
```

### Step 3: API 키 교체 (한 줄 명령어)
```bash
cd /home/user/webapp
sed -i 's/PROCUREMENT_API_KEY=.*/PROCUREMENT_API_KEY=새로운_API_키_여기에_붙여넣기/' .env
```

**⚠️ 중요**: `새로운_API_키_여기에_붙여넣기` 부분을 실제 새 API 키로 변경하세요!

**예시**:
```bash
# 예: 새 API 키가 abcd1234efgh5678... 이라면
sed -i 's/PROCUREMENT_API_KEY=.*/PROCUREMENT_API_KEY=abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx1234yz5678ab9012cd3456/' .env
```

### Step 4: 변경 확인
```bash
cd /home/user/webapp
cat .env | grep PROCUREMENT_API_KEY
```

**예상 출력**:
```
PROCUREMENT_API_KEY=abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx1234yz5678ab9012cd3456
                    └────────────────────── 새 API 키가 보여야 함
```

### Step 5: 백엔드 서버 재시작
```bash
# 현재 실행 중인 서버 찾기
ps aux | grep real_data_server

# 서버 중지 (PID를 확인한 후)
kill -9 <PID번호>

# 서버 재시작
cd /home/user/webapp/backend
python real_data_server.py &
```

---

## 🎯 방법 2: 텍스트 에디터로 수정

### Step 1: nano 에디터로 열기
```bash
cd /home/user/webapp
nano .env
```

### Step 2: 에디터 화면 설명
```
  GNU nano 6.2                  .env                            

DATABASE_URL=sqlite:////home/user/webapp/data/bidbot.db
REDIS_URL=redis://localhost:6379/0
PROCUREMENT_API_KEY=1a37dcc24d4168e1966e433f34d421011424a76102dc5146f7cd4ae708ab2313
                    ↑ 이 부분을 새 API 키로 변경
PROCUREMENT_API_BASE_URL=http://apis.data.go.kr/1230000/ScsbidInfoService
...

^G Help    ^O Write Out    ^W Where Is    ^K Cut         ^T Execute
^X Exit    ^R Read File    ^\ Replace     ^U Paste       ^J Justify
```

### Step 3: 편집 방법
1. **화살표 키**로 `PROCUREMENT_API_KEY=` 줄로 이동
2. **End 키** 또는 **→ 키**를 눌러 줄 끝으로 이동
3. **Backspace 키**로 기존 API 키 삭제 (64자 모두 삭제)
4. **새 API 키 붙여넣기** (Ctrl+Shift+V 또는 마우스 우클릭 → 붙여넣기)
5. **저장**: `Ctrl + O` → `Enter`
6. **종료**: `Ctrl + X`

### Step 4: 변경 확인
```bash
cat .env | grep PROCUREMENT_API_KEY
```

---

## 🎯 방법 3: Python 스크립트로 안전하게 수정

### 자동화 스크립트 실행
```bash
cd /home/user/webapp
python3 << 'EOF'
import os

# 새 API 키 입력
new_api_key = input("새 API 키를 입력하세요 (64자): ").strip()

if len(new_api_key) != 64:
    print(f"❌ 오류: API 키는 64자여야 합니다. 현재 길이: {len(new_api_key)}")
    exit(1)

# .env 파일 읽기
with open('.env', 'r') as f:
    lines = f.readlines()

# API 키 라인 찾아서 교체
updated = False
for i, line in enumerate(lines):
    if line.startswith('PROCUREMENT_API_KEY='):
        old_key = line.split('=')[1].strip()
        lines[i] = f'PROCUREMENT_API_KEY={new_api_key}\n'
        updated = True
        print(f"✅ API 키 업데이트 완료!")
        print(f"   기존 키: {old_key[:10]}...{old_key[-10:]}")
        print(f"   새 키: {new_api_key[:10]}...{new_api_key[-10:]}")
        break

if not updated:
    print("❌ PROCUREMENT_API_KEY를 찾을 수 없습니다.")
    exit(1)

# .env 파일 저장
with open('.env', 'w') as f:
    f.writelines(lines)

print("\n✅ .env 파일 업데이트 완료!")
print("📝 다음 단계: 백엔드 서버를 재시작하세요.")
EOF
```

---

## 🧪 API 키 변경 확인 및 테스트

### 1단계: .env 파일 확인
```bash
cd /home/user/webapp
echo "=== 현재 API 키 확인 ==="
cat .env | grep PROCUREMENT_API_KEY
```

### 2단계: Python으로 환경 변수 확인
```bash
cd /home/user/webapp
python3 << 'EOF'
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('PROCUREMENT_API_KEY', '')
print(f"✅ API 키 로드 성공")
print(f"   길이: {len(api_key)} 문자")
print(f"   앞 10자: {api_key[:10]}...")
print(f"   뒤 10자: ...{api_key[-10:]}")
EOF
```

### 3단계: API 연결 테스트
```bash
cd /home/user/webapp
python3 << 'EOF'
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PROCUREMENT_API_KEY', '')
base_url = os.getenv('PROCUREMENT_API_BASE_URL', '')

print("🔍 나라장터 API 연결 테스트...")

test_url = f"{base_url}/getBidPblancListInfoServc01"
params = {
    'serviceKey': api_key,
    'type': 'json',
    'pageNo': 1,
    'numOfRows': 1
}

try:
    response = requests.get(test_url, params=params, timeout=10)
    print(f"📡 응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API 연결 성공!")
        data = response.json()
        print(f"📊 응답 데이터: {list(data.keys())}")
    else:
        print(f"❌ API 연결 실패")
        print(f"   응답: {response.text[:200]}")
except Exception as e:
    print(f"❌ 오류: {e}")
EOF
```

---

## 🚀 백엔드 서버 재시작 방법

### 방법 A: 기존 서버 찾아서 재시작
```bash
# 1. 현재 실행 중인 백엔드 서버 찾기
echo "🔍 실행 중인 백엔드 서버 찾기..."
ps aux | grep real_data_server | grep -v grep

# 2. 출력 예시:
# user     8195  0.5  2.1  python real_data_server.py
#          ↑ 이 숫자가 PID (프로세스 ID)

# 3. 서버 중지
kill -9 8195  # ← PID를 여기에 입력

# 4. 서버 재시작
cd /home/user/webapp/backend
nohup python real_data_server.py > server.log 2>&1 &

# 5. 서버 시작 확인
ps aux | grep real_data_server | grep -v grep
echo "✅ 서버가 실행 중입니다!"
```

### 방법 B: 자동화 스크립트
```bash
cd /home/user/webapp
python3 << 'EOF'
import os
import signal
import subprocess
import psutil

print("🔍 기존 백엔드 서버 찾기...")

# 실행 중인 프로세스 찾기
found = False
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = ' '.join(proc.info['cmdline'])
        if 'real_data_server.py' in cmdline:
            print(f"   PID {proc.info['pid']} 찾음!")
            print(f"   종료 중...")
            os.kill(proc.info['pid'], signal.SIGTERM)
            found = True
    except:
        pass

if found:
    print("✅ 기존 서버 종료 완료")
else:
    print("ℹ️  실행 중인 서버 없음")

print("\n🚀 새 서버 시작...")
os.chdir('/home/user/webapp/backend')
subprocess.Popen(['python', 'real_data_server.py'], 
                 stdout=open('server.log', 'w'),
                 stderr=subprocess.STDOUT)

print("✅ 백엔드 서버 재시작 완료!")
print("📝 로그 확인: cat /home/user/webapp/backend/server.log")
EOF
```

---

## 📝 체크리스트

### API 키 업데이트 완료 체크
- [ ] 1. 공공데이터포털에서 새 API 키 발급받음
- [ ] 2. .env 파일 백업 생성 (`cp .env .env.backup`)
- [ ] 3. .env 파일에서 PROCUREMENT_API_KEY 수정
- [ ] 4. 수정 내용 확인 (`cat .env | grep PROCUREMENT_API_KEY`)
- [ ] 5. Python 환경 변수 로드 테스트 통과
- [ ] 6. API 연결 테스트 통과 (200 응답)
- [ ] 7. 백엔드 서버 재시작 완료
- [ ] 8. 서버 로그 확인 (`cat backend/server.log`)

### 문제 해결
- [ ] API 키 길이가 64자인지 확인
- [ ] API 키에 공백이나 특수문자가 없는지 확인
- [ ] .env 파일에 `PROCUREMENT_API_KEY=` 형식이 맞는지 확인
- [ ] 백엔드 서버가 정상 실행 중인지 확인

---

## ❓ 자주 묻는 질문 (FAQ)

### Q1: .env 파일이 내 컴퓨터에 없는데요?
**A**: 맞습니다! `.env` 파일은 **클라우드 샌드박스**에만 있습니다. 귀하의 개인 컴퓨터에는 없습니다.

### Q2: 이 파일을 내 컴퓨터로 다운로드해야 하나요?
**A**: 아니요! 이 파일은 서버에서만 사용됩니다. 다운로드하거나 이메일로 보내면 **보안 위험**이 있습니다.

### Q3: GitHub에 올라가 있나요?
**A**: 아니요! `.gitignore`에 포함되어 있어 GitHub에 절대 업로드되지 않습니다.

### Q4: API 키를 어디서 확인하나요?
**A**: 
1. https://www.data.go.kr/ 접속
2. 로그인
3. 마이페이지 → 인증키 관리
4. 조달청 나라장터 API 찾기

### Q5: API 키 변경 후 바로 적용되나요?
**A**: 아니요! **백엔드 서버를 재시작**해야 새 API 키가 적용됩니다.

### Q6: 실수로 .env 파일을 삭제했어요!
**A**: 백업 파일 복원: `cp .env.backup .env`

### Q7: 여러 개의 .env 파일이 있는데 어느 걸 수정하나요?
**A**: `/home/user/webapp/.env` 파일만 수정하세요. 다른 위치의 `.env` 파일은 건드리지 마세요.

---

## 🆘 문제 발생 시

### 백업 복원
```bash
cd /home/user/webapp
cp .env.backup .env
echo "✅ 백업에서 복원 완료"
```

### 전문가 도움 요청
1. 현재 상태 저장:
```bash
cd /home/user/webapp
cat .env | grep PROCUREMENT_API_KEY > api_key_info.txt
echo "✅ 현재 상태 저장: api_key_info.txt"
```

2. 로그 확인:
```bash
cat /home/user/webapp/backend/server.log
```

3. AI 어시스턴트에게 문의: "API 키 업데이트 중 문제가 발생했습니다. 로그 내용은..."

---

## 📚 관련 문서

- [API_SECURITY_REPORT.md](./API_SECURITY_REPORT.md): API 보안 상세 분석
- [INSTITUTION_AVG_RATE_FEATURE.md](./INSTITUTION_AVG_RATE_FEATURE.md): 발주처 평균 사정율 기능
- [공공데이터포털](https://www.data.go.kr/): API 키 발급

---

**⚠️ 중요 보안 주의사항**
- API 키를 절대 이메일, 메신저, 공개 채팅에 공유하지 마세요
- API 키를 GitHub, GitLab 등에 업로드하지 마세요
- API 키는 반드시 `.env` 파일에만 저장하세요
- 정기적으로 API 키를 갱신하세요 (3~6개월마다)
