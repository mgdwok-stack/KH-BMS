# 🚀 SSH 서버 이전 빠른 시작 가이드

단 **5단계**로 SSH 서버에 프로젝트를 이전할 수 있습니다!

---

## 📦 현재 상태

- **백업 파일 크기**: 4.2 MB
- **백업 파일 위치**: `/home/user/webapp/kh_bms_data_backup.tar.gz`
- **GitHub 저장소**: https://github.com/mgdwok-stack/KH-BMS
- **브랜치**: `genspark_ai_developer`

---

## 🎯 방법 1: 자동 스크립트 사용 (가장 간단!)

### 단계 1: 백업 파일 업로드 (샌드박스에서)

```bash
cd /home/user/webapp
curl --upload-file kh_bms_data_backup.tar.gz https://transfer.sh/kh_bms_data.tar.gz
```

📝 **출력된 URL을 복사하세요** (예: `https://transfer.sh/xxxxx/kh_bms_data.tar.gz`)

### 단계 2: 설치 스크립트 다운로드 (SSH 서버에서)

```bash
ssh your_user@your_server_ip
wget https://raw.githubusercontent.com/mgdwok-stack/KH-BMS/genspark_ai_developer/setup_on_ssh_server.sh
chmod +x setup_on_ssh_server.sh
```

### 단계 3: 스크립트 실행

```bash
./setup_on_ssh_server.sh
```

스크립트가 자동으로:
- ✅ 시스템 요구사항 확인
- ✅ GitHub에서 프로젝트 클론
- ✅ Python 가상환경 생성
- ✅ 의존성 패키지 설치
- ✅ 데이터베이스 복원
- ✅ 서버 테스트
- ✅ systemd 서비스 생성 (선택사항)

### 단계 4: 방화벽 설정 (필요시)

```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 단계 5: 완료! 🎉

브라우저에서 접속:
- **Web UI**: `http://your_server_ip:8000/static/complete_integrated_system.html`
- **API Docs**: `http://your_server_ip:8000/docs`

---

## 🛠️ 방법 2: 수동 설치 (단계별)

### 단계 1: 백업 파일 준비 (샌드박스)

```bash
cd /home/user/webapp
curl --upload-file kh_bms_data_backup.tar.gz https://transfer.sh/kh_bms_data.tar.gz
# URL 복사!
```

### 단계 2: 프로젝트 클론 (SSH 서버)

```bash
ssh your_user@your_server_ip
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer
```

### 단계 3: 가상환경 설정

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 단계 4: 데이터베이스 복원

```bash
# transfer.sh에서 다운로드
wget https://transfer.sh/xxxxx/kh_bms_data.tar.gz -O kh_bms_data_backup.tar.gz

# 압축 해제
tar -xzf kh_bms_data_backup.tar.gz

# 확인
ls -lh data/*.db
ls -lh data/databases/*.db
```

### 단계 5: 서버 실행

```bash
python3 unified_server.py
```

---

## 🔥 방법 3: 초고속 (이미 환경 갖춰진 경우)

```bash
# SSH 서버에서 한 번에 실행
ssh your_user@your_server_ip << 'ENDSSH'
cd ~/projects
git clone https://github.com/mgdwok-stack/KH-BMS.git && cd KH-BMS
git checkout genspark_ai_developer
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
wget YOUR_TRANSFER_SH_URL -O kh_bms_data_backup.tar.gz
tar -xzf kh_bms_data_backup.tar.gz
python3 unified_server.py
ENDSSH
```

---

## 📊 설치 후 검증

### 1. 헬스 체크
```bash
curl http://localhost:8000/health
```

**예상 출력**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "databases": {
    "original_bidbot": true,
    "pq_stats": true
  },
  "organization_databases": 4
}
```

### 2. PQ 회사 수 확인
```bash
curl -s http://localhost:8000/api/v1/pq-companies | jq '.companies | length'
```

**예상**: `261`

### 3. 조직 수 확인
```bash
curl -s http://localhost:8000/api/v1/organizations | jq '.organizations | length'
```

**예상**: `4`

### 4. DB 레코드 수 확인
```bash
sqlite3 data/bidbot_data.db "SELECT COUNT(*) FROM Company_PQ_Stats;"
```

**예상**: `17461`

---

## 🎨 웹 UI 테스트

브라우저에서 `http://your_server_ip:8000/static/complete_integrated_system.html` 접속 후:

- ✅ **대시보드 탭**: 통계 표시
- ✅ **실시간 입찰공고 탭**: 공고 목록
- ✅ **과거 입찰결과 탭**: 결과 조회
- ✅ **엑셀 분석 탭**: XLS 업로드
- ✅ **PQ 점수 분석 탭**: 261개 회사 목록, 분석 기능
- ✅ **발주처별 예가 분석 탭**: 4개 발주처 목록, 데이터 조회
- ✅ **CSV 업로드 탭**: CSV 업로드, DB 업데이트 버튼

---

## 🚦 서비스로 실행 (선택사항)

### systemd 서비스 생성

```bash
sudo nano /etc/systemd/system/kh-bms.service
```

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

### 서비스 시작

```bash
sudo systemctl daemon-reload
sudo systemctl enable kh-bms
sudo systemctl start kh-bms
sudo systemctl status kh-bms
```

---

## 🔧 문제 해결

### 포트 8000 이미 사용 중
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Python 버전 부족
```bash
python3 --version  # 3.8 이상 필요
# 업그레이드 (Ubuntu)
sudo apt install python3.10
```

### 의존성 설치 오류
```bash
sudo apt install python3-dev build-essential
pip install --upgrade pip
pip install -r requirements.txt
```

### 외부 접속 안 됨
```bash
# 방화벽 확인
sudo ufw status
sudo ufw allow 8000/tcp

# 서버 바인딩 확인
netstat -tlnp | grep 8000
# 0.0.0.0:8000 이어야 함
```

---

## 📚 추가 문서

- **`SSH_SERVER_MIGRATION_GUIDE.md`**: 상세 이전 가이드 (10,000자)
- **`LOCAL_DEVELOPMENT_GUIDE.md`**: 로컬 PC 개발 환경 설정
- **`REQUIREMENTS_VERIFICATION.md`**: 요구사항 검증 문서

---

## 🎁 요약

| 항목 | 내용 |
|-----|------|
| 백업 파일 | `kh_bms_data_backup.tar.gz` (4.2 MB) |
| GitHub | https://github.com/mgdwok-stack/KH-BMS |
| 브랜치 | `genspark_ai_developer` |
| Web UI | `http://SERVER_IP:8000/static/complete_integrated_system.html` |
| API Docs | `http://SERVER_IP:8000/docs` |
| PQ 회사 | 261개 (17,461 레코드) |
| 발주처 | 4개 (5,304 레코드) |
| CSV 파일 | 19개 |

---

**작성일**: 2026-03-24  
**예상 소요 시간**: 10~15분  
**난이도**: ⭐⭐☆☆☆ (쉬움)
