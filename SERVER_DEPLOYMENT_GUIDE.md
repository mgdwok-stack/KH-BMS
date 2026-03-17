# 🚀 GitHub → 개인 서버 배포 + 로컬 PC 개발 완벽 가이드

## 🎯 목표

1. **개인 서버**: GitHub 코드를 서버에 배포하여 24시간 운영
2. **로컬 PC**: VS Code 등으로 편하게 개발
3. **GitHub**: 중간 저장소로 버전 관리

---

## 📋 전체 워크플로우

```
┌─────────────┐     Git Push     ┌──────────┐    Git Pull    ┌──────────────┐
│  로컬 PC    │ ────────────────→ │  GitHub  │ ────────────→ │  개인 서버   │
│  (개발)     │                   │ (저장소) │               │  (24시간)    │
└─────────────┘                   └──────────┘               └──────────────┘
     ↓                                                              ↓
 VS Code로                                                    자동 실행
 코드 작성                                                    (systemd)
```

---

## 🖥️ Part 1: 개인 서버에 배포하기

### 전제 조건:
- ✅ 개인 서버 (Linux 권장: Ubuntu, CentOS 등)
- ✅ SSH 접속 가능
- ✅ Python 3.8 이상 설치
- ✅ Git 설치

---

### Step 1: 서버에 SSH 접속

```bash
# Windows (PowerShell):
ssh username@your-server-ip
# 예: ssh ubuntu@192.168.1.100

# Mac/Linux (Terminal):
ssh username@your-server-ip
```

---

### Step 2: 서버에 프로젝트 클론

```bash
# 1. 프로젝트 디렉토리로 이동 (또는 생성)
cd ~
mkdir -p projects
cd projects

# 2. GitHub에서 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS

# 3. 브랜치 전환
git checkout genspark_ai_developer

# 4. 파일 확인
ls -la
```

---

### Step 3: Python 환경 설정 (서버)

```bash
# 1. 가상 환경 생성
python3 -m venv venv

# 2. 가상 환경 활성화
source venv/bin/activate

# 3. 의존성 설치
cd backend
pip install -r requirements.txt
cd ..

# 4. 환경 변수 설정
cp .env.example .env
nano .env
# API 키 등 수정 후 저장 (Ctrl+X, Y, Enter)
```

---

### Step 4: 서버에서 자동 실행 설정 (systemd)

#### 백엔드 서비스 파일 생성:

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/kh-bms-backend.service
```

**파일 내용**:
```ini
[Unit]
Description=KH-BMS Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/projects/KH-BMS/backend
Environment="PATH=/home/ubuntu/projects/KH-BMS/venv/bin"
ExecStart=/home/ubuntu/projects/KH-BMS/venv/bin/python real_data_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 프론트엔드 서비스 파일 생성:

```bash
sudo nano /etc/systemd/system/kh-bms-frontend.service
```

**파일 내용**:
```ini
[Unit]
Description=KH-BMS Frontend (HTTP Server)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/projects/KH-BMS/frontend/public
ExecStart=/usr/bin/python3 -m http.server 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 서비스 시작:

```bash
# systemd 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start kh-bms-backend
sudo systemctl start kh-bms-frontend

# 부팅 시 자동 시작
sudo systemctl enable kh-bms-backend
sudo systemctl enable kh-bms-frontend

# 상태 확인
sudo systemctl status kh-bms-backend
sudo systemctl status kh-bms-frontend

# 로그 확인
sudo journalctl -u kh-bms-backend -f
```

---

### Step 5: 방화벽 설정 (포트 열기)

```bash
# UFW 사용 (Ubuntu):
sudo ufw allow 8000/tcp  # 백엔드
sudo ufw allow 3000/tcp  # 프론트엔드
sudo ufw reload

# firewalld 사용 (CentOS):
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

---

### Step 6: Nginx 리버스 프록시 설정 (선택사항, 권장)

```bash
# Nginx 설치
sudo apt install nginx  # Ubuntu
sudo yum install nginx  # CentOS

# 설정 파일 생성
sudo nano /etc/nginx/sites-available/kh-bms
```

**Nginx 설정**:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 또는 서버 IP

    # 프론트엔드
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 백엔드 API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API 문서
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Nginx 활성화**:
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/kh-bms /etc/nginx/sites-enabled/

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 💻 Part 2: 로컬 PC에서 개발하기

### Step 1: 로컬 PC에 Git 클론

#### Windows (PowerShell):
```powershell
# 1. 원하는 폴더로 이동 (예: 문서)
cd Documents

# 2. Git 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS

# 3. 브랜치 전환
git checkout genspark_ai_developer
```

#### Mac/Linux (Terminal):
```bash
# 1. 원하는 폴더로 이동
cd ~/Documents

# 2. Git 클론
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS

# 3. 브랜치 전환
git checkout genspark_ai_developer
```

---

### Step 2: VS Code로 프로젝트 열기

```bash
# VS Code 설치 후:
code .
```

또는 VS Code 실행 → File → Open Folder → `KH-BMS` 선택

---

### Step 3: 로컬 개발 환경 설정

```bash
# 1. 가상 환경 생성
python -m venv venv

# 2. 가상 환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 의존성 설치
cd backend
pip install -r requirements.txt
cd ..

# 4. 환경 변수 설정
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```

---

### Step 4: VS Code 확장 프로그램 설치 (권장)

추천 확장:
- ✅ **Python** (Microsoft) - Python 지원
- ✅ **Pylance** - Python 언어 서버
- ✅ **GitLens** - Git 기능 강화
- ✅ **Live Server** - HTML 실시간 미리보기
- ✅ **Prettier** - 코드 포맷팅
- ✅ **Material Icon Theme** - 아이콘 테마

---

### Step 5: 로컬에서 테스트 실행

**VS Code 터미널 2개 사용**:

**터미널 1 (백엔드)**:
```bash
cd backend
python real_data_server.py
```

**터미널 2 (프론트엔드)**:
```bash
cd frontend/public
python -m http.server 3000
```

**브라우저 접속**:
- http://localhost:3000/index.html
- http://localhost:8000/docs

---

## 🔄 Part 3: 개발 → 배포 워크플로우

### 일상적인 개발 순서:

#### 1. 로컬 PC에서 코드 수정

```bash
# VS Code에서 코드 편집
# 예: frontend/public/index.html 수정
```

#### 2. 로컬에서 테스트

```bash
# 백엔드 + 프론트엔드 실행
# 브라우저에서 테스트
```

#### 3. Git 커밋 및 푸시

```bash
# 변경 사항 확인
git status

# 스테이징
git add .

# 커밋
git commit -m "feat: 새로운 기능 추가"

# 푸시
git push origin genspark_ai_developer
```

#### 4. 서버에서 업데이트

**방법 A: 수동 업데이트**
```bash
# SSH로 서버 접속
ssh username@your-server-ip

# 프로젝트 폴더로 이동
cd ~/projects/KH-BMS

# Git Pull
git pull origin genspark_ai_developer

# 서비스 재시작
sudo systemctl restart kh-bms-backend
sudo systemctl restart kh-bms-frontend

# 상태 확인
sudo systemctl status kh-bms-backend
```

**방법 B: 자동 배포 스크립트**
```bash
# 서버에 배포 스크립트 생성
nano ~/deploy-kh-bms.sh
```

**스크립트 내용**:
```bash
#!/bin/bash

echo "🚀 KH-BMS 배포 시작..."

# 프로젝트 디렉토리로 이동
cd ~/projects/KH-BMS

# Git Pull
echo "📥 GitHub에서 최신 코드 가져오기..."
git pull origin genspark_ai_developer

# 가상 환경 활성화
source venv/bin/activate

# 의존성 업데이트 (필요 시)
# pip install -r backend/requirements.txt

# 서비스 재시작
echo "🔄 서비스 재시작..."
sudo systemctl restart kh-bms-backend
sudo systemctl restart kh-bms-frontend

# 상태 확인
echo "✅ 서비스 상태 확인..."
sudo systemctl status kh-bms-backend --no-pager
sudo systemctl status kh-bms-frontend --no-pager

echo "🎉 배포 완료!"
```

**스크립트 실행 권한**:
```bash
chmod +x ~/deploy-kh-bms.sh
```

**사용**:
```bash
~/deploy-kh-bms.sh
```

---

## 🤖 Part 4: GitHub Actions 자동 배포 (고급)

### GitHub Actions 워크플로우 생성

`.github/workflows/deploy.yml` 파일 생성:

```yaml
name: Deploy to Server

on:
  push:
    branches:
      - genspark_ai_developer

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy to Server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd ~/projects/KH-BMS
            git pull origin genspark_ai_developer
            source venv/bin/activate
            pip install -r backend/requirements.txt
            sudo systemctl restart kh-bms-backend
            sudo systemctl restart kh-bms-frontend
```

**GitHub Secrets 설정**:
1. GitHub 리포지토리 → Settings → Secrets → Actions
2. New repository secret 클릭
3. 추가:
   - `SERVER_HOST`: 서버 IP
   - `SERVER_USER`: SSH 사용자명
   - `SSH_PRIVATE_KEY`: SSH 개인키

---

## 🔒 보안 설정

### 1. SSH 키 기반 인증 (비밀번호 없이)

```bash
# 로컬 PC에서 SSH 키 생성
ssh-keygen -t rsa -b 4096

# 공개키를 서버에 복사
ssh-copy-id username@your-server-ip

# 이제 비밀번호 없이 접속 가능
ssh username@your-server-ip
```

### 2. .env 파일 보안

```bash
# 서버에서 .env 파일 권한 설정
chmod 600 ~/projects/KH-BMS/.env

# 소유자만 읽기/쓰기 가능
```

### 3. 방화벽 설정

```bash
# SSH만 허용하고 나머지는 Nginx로
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS (SSL)
sudo ufw enable
```

---

## 📊 서버 모니터링

### 서비스 상태 확인

```bash
# 실시간 로그 확인
sudo journalctl -u kh-bms-backend -f

# 최근 로그 확인
sudo journalctl -u kh-bms-backend -n 50

# 서비스 상태
sudo systemctl status kh-bms-backend
```

### 시스템 리소스 확인

```bash
# CPU, 메모리 사용량
htop

# 디스크 사용량
df -h

# 프로세스 확인
ps aux | grep python
```

---

## 🆘 문제 해결

### 문제 1: 서비스가 시작 안 됨

```bash
# 로그 확인
sudo journalctl -u kh-bms-backend -n 100

# 권한 문제 확인
ls -la ~/projects/KH-BMS/

# 수동 실행 테스트
cd ~/projects/KH-BMS/backend
source ../venv/bin/activate
python real_data_server.py
```

### 문제 2: 포트가 이미 사용 중

```bash
# 포트 사용 프로세스 확인
sudo lsof -i :8000
sudo lsof -i :3000

# 프로세스 종료
sudo kill -9 <PID>
```

### 문제 3: Git Pull 충돌

```bash
# 로컬 변경사항 무시하고 Pull
git fetch origin
git reset --hard origin/genspark_ai_developer
```

---

## ✅ 전체 워크플로우 요약

### 개발 순서:

1. **로컬 PC**: VS Code로 코드 수정
2. **로컬 PC**: `git add . && git commit -m "메시지"`
3. **로컬 PC**: `git push origin genspark_ai_developer`
4. **서버**: `~/deploy-kh-bms.sh` 실행 (또는 자동 배포)
5. **확인**: 브라우저에서 서버 IP 접속

### 서버 접속:
- **HTTP**: http://your-server-ip:3000
- **API**: http://your-server-ip:8000/docs
- **Nginx 사용 시**: http://your-domain.com

---

## 🔗 추가 리소스

### 서버 관리 도구:
- **PM2** (Node.js): https://pm2.keymetrics.io/
- **Supervisor** (Python): http://supervisord.org/
- **Docker**: https://www.docker.com/

### 클라우드 서버:
- **AWS EC2**: https://aws.amazon.com/ec2/
- **DigitalOcean**: https://www.digitalocean.com/
- **Vultr**: https://www.vultr.com/
- **Linode**: https://www.linode.com/

---

## 📋 체크리스트

### 서버 설정:
- [ ] SSH 접속 확인
- [ ] Git 클론 완료
- [ ] Python 가상 환경 설정
- [ ] 의존성 설치
- [ ] .env 파일 설정
- [ ] systemd 서비스 생성
- [ ] 서비스 시작 및 활성화
- [ ] 방화벽 포트 열기
- [ ] Nginx 설정 (선택)

### 로컬 PC 설정:
- [ ] Git 클론 완료
- [ ] VS Code 설치
- [ ] Python 가상 환경 설정
- [ ] 의존성 설치
- [ ] .env 파일 설정
- [ ] 로컬 테스트 성공

### 배포 준비:
- [ ] 배포 스크립트 작성
- [ ] SSH 키 기반 인증 설정
- [ ] Git 푸시 테스트
- [ ] 서버 배포 테스트

---

**작성일**: 2026-03-06  
**프로젝트**: KH-BMS 입찰 예측 시스템  
**GitHub**: https://github.com/mgdwok-stack/KH-BMS
