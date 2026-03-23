# 🚀 SSH 서버로 프로젝트 이전 완벽 가이드

## 📊 프로젝트 현황

### 프로젝트 정보
- **프로젝트명**: KH-BMS (입찰 분석 시스템)
- **총 크기**: 42MB
- **파일 수**: 374개
- **디렉토리 수**: 138개
- **GitHub**: https://github.com/mgdwok-stack/KH-BMS

### 주요 구성
```
/home/user/webapp/
├── backend/               # FastAPI 백엔드
│   ├── app/
│   └── data/
├── frontend/              # 프론트엔드 (있을 경우)
├── data/                  # 데이터베이스 및 CSV 파일
│   ├── bidbot.db         # 입찰 공고/결과 DB (152KB)
│   ├── bidbot_data.db    # PQ 통계 DB (4.9MB)
│   ├── databases/        # 발주처별 DB (4개)
│   └── upload_files/     # CSV 파일 (19개)
├── static/               # 정적 파일 (HTML/CSS/JS)
├── unified_server.py     # 통합 서버
├── pq_stats_analyzer.py  # PQ 분석기
├── create_db_by_org.py   # 발주처 DB 생성기
└── requirements.txt      # Python 의존성
```

---

## 🎯 이전 방법 (3가지 옵션)

### ✅ 방법 1: GitHub를 통한 이전 (추천) 🌟

**장점**: 
- 가장 안전하고 깔끔
- Git 히스토리 유지
- 버전 관리 계속 가능

**단점**: 
- DB 파일이 크면 Git LFS 필요

#### Step 1: 샌드박스에서 최종 커밋 & 푸시

```bash
cd /home/user/webapp

# 모든 변경사항 커밋
git add -A
git commit -m "feat: SSH 서버 이전 전 최종 커밋"
git push origin genspark_ai_developer

# 현재 상태 확인
git status
git log --oneline -5
```

#### Step 2: SSH 서버에서 클론

```bash
# SSH 서버 접속
ssh your-user@your-server-ip

# 프로젝트 디렉토리 생성
mkdir -p ~/projects
cd ~/projects

# GitHub에서 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS

# 개발 브랜치 체크아웃
git checkout genspark_ai_developer
```

#### Step 3: 환경 설정

```bash
# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# 디렉토리 권한 설정
chmod -R 755 .
chmod +x *.py
```

#### Step 4: DB 파일 복원 (옵션)

**방법 A: Git LFS 사용** (DB 파일이 Git에 있는 경우)
```bash
git lfs pull
```

**방법 B: 별도 전송** (DB 파일이 Git에 없는 경우)
```bash
# 샌드박스에서 DB 압축
cd /home/user/webapp
tar -czf db_backup.tar.gz data/*.db data/databases/*.db

# SSH 서버로 전송 (아래 방법 2 참고)
```

---

### ✅ 방법 2: SCP/RSYNC를 통한 직접 전송

**장점**: 
- 모든 파일 그대로 전송 (DB 포함)
- 빠르고 직접적

**단점**: 
- 샌드박스에서 SSH 서버로 직접 접근 필요

#### Step 1: 샌드박스에서 전체 압축

```bash
cd /home/user
tar -czf webapp_backup.tar.gz \
  --exclude='webapp/.git' \
  --exclude='webapp/venv' \
  --exclude='webapp/__pycache__' \
  --exclude='webapp/.pytest_cache' \
  --exclude='webapp/node_modules' \
  webapp/

# 압축 결과 확인
ls -lh webapp_backup.tar.gz
```

#### Step 2: SSH 서버로 전송

**옵션 A: SCP 사용**
```bash
# 샌드박스에서 실행
scp webapp_backup.tar.gz your-user@your-server-ip:~/

# 또는 포트 지정
scp -P 22 webapp_backup.tar.gz your-user@your-server-ip:~/
```

**옵션 B: RSYNC 사용** (더 효율적)
```bash
# 샌드박스에서 실행
rsync -avz --progress \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='__pycache__' \
  /home/user/webapp/ \
  your-user@your-server-ip:~/projects/webapp/
```

#### Step 3: SSH 서버에서 압축 해제

```bash
# SSH 서버 접속
ssh your-user@your-server-ip

# 압축 해제
cd ~
tar -xzf webapp_backup.tar.gz
mv webapp ~/projects/webapp
cd ~/projects/webapp

# Git 재초기화 (필요시)
git init
git remote add origin https://github.com/mgdwok-stack/KH-BMS.git
git fetch origin
git checkout -b genspark_ai_developer origin/genspark_ai_developer
```

---

### ✅ 방법 3: 중간 저장소 활용 (샌드박스에서 SSH 접근 불가 시)

**장점**: 
- 샌드박스에서 직접 SSH 접근 불필요
- 대용량 파일 전송 가능

**단점**: 
- 추가 단계 필요

#### Step 1: 파일을 클라우드 스토리지에 업로드

**옵션 A: Google Drive / Dropbox**
```bash
# 샌드박스에서 압축
cd /home/user
tar -czf webapp_backup_$(date +%Y%m%d).tar.gz webapp/

# 다운로드 링크를 브라우저에서 복사
# (샌드박스에서 직접 다운로드)
```

**옵션 B: GitHub Release 사용**
```bash
# 샌드박스에서
cd /home/user/webapp
tar -czf ../webapp_backup.tar.gz \
  --exclude='.git' \
  --exclude='venv' \
  .

# GitHub Release에 업로드 (gh CLI 또는 웹 UI)
gh release create v1.0.0 ../webapp_backup.tar.gz
```

**옵션 C: 임시 파일 공유 서비스**
```bash
# 샌드박스에서 압축 후
# transfer.sh 사용
curl --upload-file webapp_backup.tar.gz https://transfer.sh/webapp_backup.tar.gz

# URL을 받아서 SSH 서버에서 다운로드
```

#### Step 2: SSH 서버에서 다운로드

```bash
# SSH 서버에서
cd ~/projects

# transfer.sh에서 다운로드
wget https://transfer.sh/xxxxx/webapp_backup.tar.gz

# 또는 GitHub Release에서
wget https://github.com/mgdwok-stack/KH-BMS/releases/download/v1.0.0/webapp_backup.tar.gz

# 압축 해제
tar -xzf webapp_backup.tar.gz
cd webapp
```

---

## 🔧 SSH 서버 환경 설정

### 1. 시스템 의존성 설치

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl

# CentOS/RHEL
sudo yum install -y python3 python3-pip git curl
```

### 2. Python 가상환경 생성

```bash
cd ~/projects/webapp
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# .env 파일 생성 (필요시)
cat > .env << 'ENVEOF'
# API Keys
GOVERNMENT_API_KEY=your_api_key_here

# Database
DB_PATH=data/bidbot.db
PQ_DB_PATH=data/bidbot_data.db

# Server
HOST=0.0.0.0
PORT=8000
ENVEOF
```

### 4. 방화벽 설정 (포트 오픈)

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 8000/tcp
sudo ufw reload

# CentOS/RHEL (Firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 5. 서비스 자동 시작 설정 (systemd)

```bash
# systemd 서비스 파일 생성
sudo nano /etc/systemd/system/bidbot.service

# 내용:
[Unit]
Description=Bid-Bot Unified Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user/projects/webapp
Environment="PATH=/home/your-user/projects/webapp/venv/bin"
ExecStart=/home/your-user/projects/webapp/venv/bin/python3 unified_server.py
Restart=always

[Install]
WantedBy=multi-user.target

# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable bidbot
sudo systemctl start bidbot
sudo systemctl status bidbot
```

---

## 🧪 이전 후 검증

### 1. 기본 검증

```bash
cd ~/projects/webapp

# Git 상태 확인
git status
git remote -v

# Python 환경 확인
source venv/bin/activate
python3 --version
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|pandas)"

# DB 파일 확인
ls -lh data/*.db
ls -lh data/databases/*.db
ls data/upload_files/*.CSV | wc -l
```

### 2. 서버 실행 테스트

```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 시작
python3 unified_server.py

# 다른 터미널에서 health check
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/pq-companies | jq 'length'
curl http://localhost:8000/api/v1/organizations
```

### 3. 데이터 무결성 검증

```bash
# DB 레코드 수 확인
python3 << 'PYEOF'
import sqlite3

# PQ 통계 DB
conn = sqlite3.connect('data/bidbot_data.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM Company_PQ_Stats")
print(f"PQ 통계 레코드: {cursor.fetchone()[0]}건")
cursor.execute("SELECT COUNT(DISTINCT `대표사`) FROM Company_PQ_Stats")
print(f"대표사 수: {cursor.fetchone()[0]}개")
conn.close()

# 발주처 DB
import os
org_dbs = [f for f in os.listdir('data/databases') if f.endswith('.db')]
print(f"발주처 DB 수: {len(org_dbs)}개")
for db in org_dbs:
    conn = sqlite3.connect(f'data/databases/{db}')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bid_data")
    count = cursor.fetchone()[0]
    print(f"  - {db}: {count}건")
    conn.close()
PYEOF
```

### 4. 웹 UI 접근 테스트

```bash
# SSH 서버 IP 확인
hostname -I

# 브라우저에서 접속
# http://your-server-ip:8000/static/complete_integrated_system.html
# http://your-server-ip:8000/docs
```

---

## 🚨 문제 해결

### 문제 1: 포트 이미 사용 중

```bash
# 포트 8000 사용 중인 프로세스 확인
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# 프로세스 종료
sudo kill -9 <PID>

# 또는 다른 포트 사용
PORT=8001 python3 unified_server.py
```

### 문제 2: 의존성 설치 실패

```bash
# Python 버전 확인 (3.8 이상 필요)
python3 --version

# pip 업그레이드
pip install --upgrade pip setuptools wheel

# 개별 패키지 설치
pip install fastapi uvicorn sqlalchemy pandas
```

### 문제 3: DB 파일 없음

```bash
# DB 파일 재생성
python3 pq_stats_analyzer.py build

# 발주처 DB 생성
python3 create_db_by_org.py "경상남도"
python3 create_db_by_org.py "경상남도 합천군"
python3 create_db_by_org.py "충청북도 청주시"
python3 create_db_by_org.py "한국어촌어항공단"
```

### 문제 4: 권한 오류

```bash
# 프로젝트 디렉토리 소유권 변경
sudo chown -R $USER:$USER ~/projects/webapp

# 실행 권한 부여
chmod +x ~/projects/webapp/*.py
chmod -R 755 ~/projects/webapp
```

---

## 📝 체크리스트

### 이전 전 (샌드박스)
- [ ] Git 최종 커밋 & 푸시
- [ ] DB 파일 백업
- [ ] CSV 파일 백업
- [ ] requirements.txt 최신화
- [ ] 환경 변수 문서화

### 이전 중
- [ ] 프로젝트 파일 전송 (Git/SCP/클라우드)
- [ ] DB 파일 전송
- [ ] CSV 파일 전송

### 이전 후 (SSH 서버)
- [ ] Git 클론 또는 압축 해제
- [ ] Python 가상환경 생성
- [ ] 의존성 설치
- [ ] DB 파일 확인
- [ ] 서버 실행 테스트
- [ ] API 동작 확인
- [ ] 웹 UI 접근 확인
- [ ] 방화벽 설정
- [ ] systemd 서비스 설정 (선택)

---

## 🎯 권장 작업 순서

### 최종 추천: GitHub + 별도 DB 전송

```bash
# === 샌드박스에서 ===

# 1. Git 커밋 & 푸시
cd /home/user/webapp
git add -A
git commit -m "feat: SSH 서버 이전 준비"
git push origin genspark_ai_developer

# 2. DB 파일 압축
tar -czf ~/db_backup.tar.gz data/*.db data/databases/*.db data/upload_files/*.CSV

# 3. DB 파일을 임시 저장소에 업로드 (transfer.sh)
curl --upload-file ~/db_backup.tar.gz https://transfer.sh/db_backup.tar.gz
# URL 저장: https://transfer.sh/xxxxx/db_backup.tar.gz


# === SSH 서버에서 ===

# 1. GitHub에서 코드 클론
cd ~/projects
git clone https://github.com/mgdwok-stack/KH-BMS.git webapp
cd webapp
git checkout genspark_ai_developer

# 2. Python 환경 설정
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. DB 파일 다운로드 & 압축 해제
wget https://transfer.sh/xxxxx/db_backup.tar.gz
tar -xzf db_backup.tar.gz

# 4. 서버 실행
python3 unified_server.py

# 5. 검증
curl http://localhost:8000/health
```

---

## 📞 도움이 필요하면

1. **GitHub Issues**: https://github.com/mgdwok-stack/KH-BMS/issues
2. **문서 참고**: 
   - `MANUAL_DB_UPDATE_IMPLEMENTATION.md`
   - `REQUIREMENTS_VERIFICATION.md`
   - `FINAL_SUMMARY.md`

---

**작성일**: 2026-03-23  
**버전**: 1.0  
**대상**: SSH 서버 이전
