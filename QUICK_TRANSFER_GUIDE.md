# ⚡ SSH 서버 이전 빠른 가이드

## 🚀 가장 쉬운 방법 (추천)

### 📦 1단계: 샌드박스에서 DB 백업 다운로드

```bash
# 이미 생성된 백업 파일 다운로드
# 파일 위치: /home/user/db_backup_20260323.tar.gz (4.2MB)
```

**다운로드 방법**:
1. 샌드박스 터미널에서 실행:
   ```bash
   curl --upload-file /home/user/db_backup_20260323.tar.gz https://transfer.sh/db_backup.tar.gz
   ```
2. 출력된 URL 복사 (예: `https://transfer.sh/xxxxx/db_backup.tar.gz`)

---

### 🖥️ 2단계: SSH 서버에서 프로젝트 설정

```bash
# SSH 서버 접속
ssh your-user@your-server-ip

# 1. GitHub에서 코드 클론
cd ~
mkdir -p projects
cd projects
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer

# 2. Python 환경 설정
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. DB 파일 다운로드 및 압축 해제
wget https://transfer.sh/xxxxx/db_backup.tar.gz
tar -xzf db_backup.tar.gz

# 4. 서버 실행
python3 unified_server.py
```

---

### ✅ 3단계: 검증

```bash
# 다른 터미널에서
curl http://localhost:8000/health

# 브라우저에서 접속
# http://your-server-ip:8000/static/complete_integrated_system.html
```

---

## 📋 필수 설치 (SSH 서버)

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

### CentOS/RHEL
```bash
sudo yum install -y python3 python3-pip git curl
```

---

## 🔥 방화벽 설정

```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp
sudo ufw reload

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## 🎯 자동 시작 설정 (선택사항)

```bash
# systemd 서비스 생성
sudo tee /etc/systemd/system/bidbot.service > /dev/null << SERVICE
[Unit]
Description=Bid-Bot Unified Server
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python3 unified_server.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable bidbot
sudo systemctl start bidbot
sudo systemctl status bidbot
```

---

## 🚨 문제 해결

### 포트 이미 사용 중
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Python 버전 오류
```bash
python3 --version  # 3.8 이상 필요
```

### DB 파일 없음
```bash
# CSV 파일이 있으면 DB 재생성 가능
python3 pq_stats_analyzer.py build
```

---

## 📞 상세 가이드

전체 이전 가이드는 `PROJECT_TRANSFER_GUIDE.md` 참고

---

**현재 상태**:
- ✅ 코드: GitHub 푸시 완료
- ✅ DB 백업: `/home/user/db_backup_20260323.tar.gz` (4.2MB)
- ✅ 커밋: 636ab04
- ✅ PR: https://github.com/mgdwok-stack/KH-BMS/pull/1
