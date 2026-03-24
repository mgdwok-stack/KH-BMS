# SSH 서버로 프로젝트 이전 완벽 가이드

## 📋 목차
1. [현재 상태 요약](#현재-상태-요약)
2. [이전 방법 선택](#이전-방법-선택)
3. [방법 1: GitHub + DB 백업 (권장)](#방법-1-github--db-백업-권장)
4. [방법 2: 직접 전송 (SCP/rsync)](#방법-2-직접-전송-scprsync)
5. [SSH 서버 환경 설정](#ssh-서버-환경-설정)
6. [서버에서 실행](#서버에서-실행)
7. [개발 워크플로우](#개발-워크플로우)
8. [문제 해결](#문제-해결)

---

## 현재 상태 요약

### 프로젝트 정보
- **위치**: `/home/user/webapp`
- **저장소**: https://github.com/mgdwok-stack/KH-BMS
- **브랜치**: `genspark_ai_developer`
- **최신 커밋**: `abfc329` (docs: SSH 서버 이전 빠른 가이드 추가)

### 데이터베이스 파일 (총 6.3 MB)
```
152K    data/bidbot.db              # 원본 입찰봇 DB
4.9M    data/bidbot_data.db         # PQ 통계 DB (17,461 records, 261 companies)
236K    data/databases/경상남도 합천군.db    # 918 records
584K    data/databases/경상남도.db           # 2,534 records
368K    data/databases/충청북도 청주시.db    # 1,470 records
116K    data/databases/한국어촌어항공단.db   # 381 records
```

### CSV 파일
- **위치**: `data/upload_files/`
- **개수**: 19개 CSV 파일

---

## 이전 방법 선택

### 방법 1: GitHub + DB 백업 ⭐ (권장)
**장점**: 
- 코드와 DB 분리 관리
- 버전 관리 활용
- 팀 협업 용이
- 이후 개발 편리

**단점**: 
- 2단계 작업 필요

**추천 상황**: 
- 계속 개발할 예정
- 여러 서버에 배포 필요
- 팀 협업 필요

### 방법 2: 직접 전송 (SCP/rsync)
**장점**: 
- 한 번에 모든 파일 전송
- 단순하고 직관적

**단점**: 
- 버전 관리 어려움
- 대용량 파일 전송 시간 소요

**추천 상황**: 
- 일회성 배포
- 빠른 테스트 필요
- Git 사용 불편

---

## 방법 1: GitHub + DB 백업 (권장)

### 1단계: 미완료 작업 커밋

```bash
# 샌드박스에서 실행
cd /home/user/webapp

# 로컬 개발 가이드 추가
git add LOCAL_DEVELOPMENT_GUIDE.md SSH_SERVER_MIGRATION_GUIDE.md
git commit -m "docs: SSH 서버 이전 가이드 추가"
git push origin genspark_ai_developer
```

### 2단계: 데이터베이스 백업 파일 생성

```bash
# 샌드박스에서 실행
cd /home/user/webapp

# DB 및 CSV 백업
tar -czf kh_bms_data_backup.tar.gz \
    data/bidbot.db \
    data/bidbot_data.db \
    data/databases/ \
    data/upload_files/

# 백업 파일 크기 확인
ls -lh kh_bms_data_backup.tar.gz
```

### 3단계: 백업 파일 전송

#### 옵션 A: 임시 파일 공유 서비스 사용 (가장 간단)

```bash
# transfer.sh 사용 (무료, 14일 보관)
curl --upload-file kh_bms_data_backup.tar.gz https://transfer.sh/kh_bms_data.tar.gz

# 출력된 URL 복사 (예: https://transfer.sh/xxxxx/kh_bms_data.tar.gz)
```

#### 옵션 B: Google Drive / Dropbox 사용

1. 샌드박스에서 백업 파일 다운로드:
   ```bash
   # 다른 터미널에서 (로컬 PC)
   scp user@sandbox:/home/user/webapp/kh_bms_data_backup.tar.gz ./
   ```

2. 수동으로 클라우드에 업로드

3. SSH 서버에서 다운로드

#### 옵션 C: 직접 SCP로 SSH 서버에 전송

```bash
# 샌드박스에서 직접 SSH 서버로 전송
scp kh_bms_data_backup.tar.gz your_user@your_server_ip:/path/to/destination/
```

### 4단계: SSH 서버에 클론 및 복원

```bash
# SSH 서버에 접속
ssh your_user@your_server_ip

# 프로젝트 디렉토리 생성
mkdir -p ~/projects
cd ~/projects

# GitHub에서 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer

# 백업 파일 다운로드 (transfer.sh 사용한 경우)
wget https://transfer.sh/xxxxx/kh_bms_data.tar.gz -O kh_bms_data_backup.tar.gz

# 또는 클라우드에서 다운로드
# wget "https://drive.google.com/uc?export=download&id=FILE_ID" -O kh_bms_data_backup.tar.gz

# 백업 복원
tar -xzf kh_bms_data_backup.tar.gz

# 파일 확인
ls -lh data/*.db
ls -lh data/databases/*.db
ls data/upload_files/ | wc -l
```

---

## 방법 2: 직접 전송 (SCP/rsync)

### 옵션 A: SCP 사용

```bash
# 샌드박스에서 실행
cd /home/user

# 전체 프로젝트 압축 (불필요한 파일 제외)
tar -czf kh_bms_full.tar.gz \
    --exclude='webapp/.git' \
    --exclude='webapp/__pycache__' \
    --exclude='webapp/*.pyc' \
    --exclude='webapp/venv' \
    --exclude='webapp/.venv' \
    webapp/

# SSH 서버로 전송
scp kh_bms_full.tar.gz your_user@your_server_ip:/path/to/destination/

# SSH 서버에서
cd /path/to/destination/
tar -xzf kh_bms_full.tar.gz
cd webapp
```

### 옵션 B: rsync 사용 (더 빠름)

```bash
# 샌드박스에서 실행
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='.venv' \
    /home/user/webapp/ \
    your_user@your_server_ip:/path/to/destination/webapp/
```

---

## SSH 서버 환경 설정

### 1단계: 필수 패키지 설치

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

#### CentOS/RHEL
```bash
sudo yum install -y python3 python3-pip git curl
```

### 2단계: Python 가상환경 생성

```bash
cd ~/projects/KH-BMS  # 또는 webapp/

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt
```

### 3단계: 환경 변수 설정 (선택사항)

```bash
# .env 파일 생성
cat > .env << 'EOF'
# 서버 설정
HOST=0.0.0.0
PORT=8000

# 데이터베이스 경로
DB_PATH=data/bidbot_data.db
ORG_DB_DIR=data/databases

# API 키 (필요시)
# API_KEY=your_api_key_here
EOF
```

### 4단계: 방화벽 설정

#### Ubuntu/Debian (UFW)
```bash
sudo ufw allow 8000/tcp
sudo ufw status
```

#### CentOS/RHEL (firewalld)
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

---

## 서버에서 실행

### 개발 모드로 실행

```bash
cd ~/projects/KH-BMS  # 프로젝트 디렉토리로 이동
source venv/bin/activate  # 가상환경 활성화

# 서버 실행
python3 unified_server.py
```

**접속 URL**:
- Web UI: `http://your_server_ip:8000/static/complete_integrated_system.html`
- API Docs: `http://your_server_ip:8000/docs`

### 프로덕션 모드로 실행 (systemd 서비스)

#### 1. 서비스 파일 생성

```bash
sudo nano /etc/systemd/system/kh-bms.service
```

#### 2. 서비스 파일 내용

```ini
[Unit]
Description=KH-BMS Bid Analysis System
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/projects/KH-BMS
Environment="PATH=/home/your_username/projects/KH-BMS/venv/bin"
ExecStart=/home/your_username/projects/KH-BMS/venv/bin/python3 unified_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. 서비스 활성화 및 시작

```bash
# 서비스 등록
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start kh-bms

# 부팅 시 자동 시작 설정
sudo systemctl enable kh-bms

# 상태 확인
sudo systemctl status kh-bms

# 로그 확인
sudo journalctl -u kh-bms -f
```

#### 4. 서비스 관리 명령어

```bash
# 서비스 중지
sudo systemctl stop kh-bms

# 서비스 재시작
sudo systemctl restart kh-bms

# 서비스 상태 확인
sudo systemctl status kh-bms
```

---

## 개발 워크플로우

### 로컬 PC에서 개발 (권장)

```bash
# 1. 로컬 PC에 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer

# 2. 가상환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. DB 복원 (백업 파일 다운로드 후)
tar -xzf kh_bms_data_backup.tar.gz

# 4. 로컬에서 실행 및 테스트
python unified_server.py

# 5. 코드 수정 후 커밋
git add .
git commit -m "feat: 새로운 기능 추가"
git push origin genspark_ai_developer

# 6. SSH 서버에서 업데이트
ssh your_user@your_server_ip
cd ~/projects/KH-BMS
git pull origin genspark_ai_developer
sudo systemctl restart kh-bms
```

### SSH 서버에서 직접 개발

```bash
# 1. SSH 접속
ssh your_user@your_server_ip

# 2. 프로젝트 디렉토리 이동
cd ~/projects/KH-BMS
source venv/bin/activate

# 3. 코드 편집 (vim, nano 등)
vim unified_server.py

# 4. 테스트
python unified_server.py

# 5. 커밋 및 푸시
git add .
git commit -m "fix: 버그 수정"
git push origin genspark_ai_developer
```

---

## 검증 체크리스트

### 파일 구조 확인
```bash
cd ~/projects/KH-BMS
tree -L 2 -I 'venv|__pycache__|*.pyc'
```

**예상 출력**:
```
.
├── backend/
├── data/
│   ├── bidbot.db
│   ├── bidbot_data.db
│   ├── databases/
│   └── upload_files/
├── static/
│   └── complete_integrated_system.html
├── unified_server.py
├── pq_stats_analyzer.py
├── requirements.txt
└── README.md
```

### Python 환경 확인
```bash
python3 --version  # ≥ Python 3.8
pip list | grep -E "fastapi|uvicorn|pandas|sqlite"
```

### 데이터베이스 확인
```bash
# DB 파일 존재 확인
ls -lh data/*.db data/databases/*.db

# PQ 통계 확인
sqlite3 data/bidbot_data.db "SELECT COUNT(*) FROM Company_PQ_Stats;"
# 예상: 17461

sqlite3 data/bidbot_data.db "SELECT COUNT(DISTINCT 대표사) FROM Company_PQ_Stats;"
# 예상: 261
```

### 서버 동작 확인
```bash
# 헬스 체크
curl http://localhost:8000/health

# PQ 회사 목록
curl http://localhost:8000/api/v1/pq-companies | jq '.companies | length'
# 예상: 261

# 조직 목록
curl http://localhost:8000/api/v1/organizations | jq '.organizations | length'
# 예상: 4
```

### 웹 UI 접속 테스트
브라우저에서 접속:
- `http://your_server_ip:8000/static/complete_integrated_system.html`
- 7개 탭 모두 정상 작동 확인

---

## 문제 해결

### 1. 포트 8000 이미 사용 중
```bash
# 포트 사용 프로세스 확인
sudo lsof -i :8000
# 또는
sudo netstat -tlnp | grep 8000

# 프로세스 종료
sudo kill -9 <PID>

# 또는 다른 포트로 실행
python3 unified_server.py --port 8001
```

### 2. Python 버전 부족
```bash
# Python 3.8+ 필요
python3 --version

# 업그레이드 (Ubuntu)
sudo apt install python3.10
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

### 3. 의존성 설치 오류
```bash
# 시스템 패키지 먼저 설치
sudo apt install -y python3-dev build-essential

# pip 업그레이드
pip install --upgrade pip setuptools wheel

# 다시 설치
pip install -r requirements.txt
```

### 4. DB 파일 없음
```bash
# 백업에서 복원
tar -xzf kh_bms_data_backup.tar.gz

# 또는 CSV에서 재구축
cd ~/projects/KH-BMS
python3 pq_stats_analyzer.py build
```

### 5. 권한 오류
```bash
# 디렉토리 권한 설정
chmod -R 755 ~/projects/KH-BMS
chmod -R 644 ~/projects/KH-BMS/data/*.db
```

### 6. 외부 접속 불가
```bash
# 방화벽 확인
sudo ufw status
sudo firewall-cmd --list-ports

# 서버가 0.0.0.0으로 바인딩되었는지 확인
netstat -tlnp | grep 8000
# 0.0.0.0:8000 이어야 함 (127.0.0.1:8000이면 외부 접속 불가)
```

---

## 📝 요약

### 추천 방법: GitHub + DB 백업

**샌드박스에서**:
1. `git push` 로 코드 푸시
2. `tar -czf kh_bms_data_backup.tar.gz data/` 로 DB 백업
3. `curl --upload-file kh_bms_data_backup.tar.gz https://transfer.sh/` 로 업로드

**SSH 서버에서**:
1. `git clone` 및 `git checkout genspark_ai_developer`
2. `python3 -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `wget <transfer.sh URL>` 로 DB 다운로드
5. `tar -xzf kh_bms_data_backup.tar.gz`
6. `python3 unified_server.py`
7. systemd 서비스 등록 (선택사항)

### 주요 URL
- **GitHub 저장소**: https://github.com/mgdwok-stack/KH-BMS
- **PR**: https://github.com/mgdwok-stack/KH-BMS/pull/1
- **브랜치**: `genspark_ai_developer`
- **Web UI**: `http://SERVER_IP:8000/static/complete_integrated_system.html`
- **API Docs**: `http://SERVER_IP:8000/docs`

### 데이터 규모
- **PQ 통계**: 17,461 레코드, 261개 대표사
- **발주처**: 4개 (경상남도, 합천군, 청주시, 한국어촌어항공단)
- **CSV 파일**: 19개
- **총 DB 크기**: 6.3 MB

---

## 추가 리소스

- `LOCAL_DEVELOPMENT_GUIDE.md`: 로컬 PC 개발 환경 설정 가이드
- `QUICK_TRANSFER_GUIDE.md`: 빠른 이전 가이드
- `PROJECT_TRANSFER_GUIDE.md`: 상세 프로젝트 이전 가이드
- `REQUIREMENTS_VERIFICATION.md`: 요구사항 검증 문서

---

**작성일**: 2026-03-24  
**버전**: 2.0.0  
**최종 업데이트**: SSH 서버 이전 완벽 가이드
