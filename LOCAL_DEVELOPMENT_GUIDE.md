# 💻 로컬 PC 개발 가이드

## 🎯 왜 로컬 PC에서 개발해야 하나요?

### 로컬 PC의 장점
- ✅ **무제한 저장공간** - 하드디스크 용량만큼 사용
- ✅ **빠른 속도** - 네트워크 지연 없음
- ✅ **IDE 사용** - VS Code, PyCharm 등 강력한 도구
- ✅ **안정성** - 세션 종료 걱정 없음
- ✅ **오프라인 작업** - 인터넷 없어도 개발 가능
- ✅ **디버깅 편리** - 브레이크포인트, 변수 감시 등

### SSH 서버는 언제?
- 🚀 **배포** - 실제 서비스 운영
- 👥 **공유** - 팀원과 테스트 서버 공유
- 🔄 **CI/CD** - 자동 배포 파이프라인

---

## 🖥️ 로컬 PC 환경 설정

### Windows 사용자

#### 1. Git 설치
- 다운로드: https://git-scm.com/download/win
- 설치 후 Git Bash 실행

#### 2. Python 설치
- 다운로드: https://www.python.org/downloads/
- 설치 시 "Add Python to PATH" 체크

#### 3. VS Code 설치 (선택)
- 다운로드: https://code.visualstudio.com/
- Python Extension 설치

#### 4. 프로젝트 클론
```bash
# Git Bash 또는 PowerShell에서
cd C:\Users\YourName\Documents
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer

# Python 가상환경
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python unified_server.py
```

브라우저: `http://localhost:8000/static/complete_integrated_system.html`

---

### macOS 사용자

#### 1. Homebrew 설치 (없는 경우)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Git & Python 설치
```bash
brew install git python@3.11
```

#### 3. 프로젝트 클론
```bash
cd ~/Documents
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer

# Python 가상환경
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python3 unified_server.py
```

브라우저: `http://localhost:8000/static/complete_integrated_system.html`

---

### Linux 사용자

#### 1. Git & Python 설치
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip

# CentOS/RHEL
sudo yum install -y git python3 python3-pip
```

#### 2. 프로젝트 클론
```bash
cd ~/projects
git clone https://github.com/mgdwok-stack/KH-BMS.git
cd KH-BMS
git checkout genspark_ai_developer

# Python 가상환경
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python3 unified_server.py
```

브라우저: `http://localhost:8000/static/complete_integrated_system.html`

---

## 📁 DB 파일 복원

### 방법 1: GitHub에서 다운로드 (DB가 Git에 있는 경우)
```bash
# 이미 클론했다면 자동으로 포함됨
git lfs pull  # Git LFS 사용 시
```

### 방법 2: 별도 다운로드 (DB가 Git에 없는 경우)

#### Windows
```powershell
# PowerShell에서
cd C:\Users\YourName\Documents\KH-BMS
Invoke-WebRequest -Uri "https://transfer.sh/xxxxx/db_backup.tar.gz" -OutFile "db_backup.tar.gz"

# 압축 해제 (Git Bash에서)
tar -xzf db_backup.tar.gz
```

#### macOS/Linux
```bash
cd ~/Documents/KH-BMS  # 또는 ~/projects/KH-BMS
wget https://transfer.sh/xxxxx/db_backup.tar.gz
tar -xzf db_backup.tar.gz
```

### 방법 3: CSV에서 DB 재생성
```bash
# CSV 파일이 있다면
python3 pq_stats_analyzer.py build

# 발주처별 DB 생성
python3 create_db_by_org.py "경상남도"
python3 create_db_by_org.py "경상남도 합천군"
python3 create_db_by_org.py "충청북도 청주시"
python3 create_db_by_org.py "한국어촌어항공단"
```

---

## 🔧 VS Code 추천 설정

### 추천 확장 프로그램
```
- Python (Microsoft)
- Pylance
- Python Debugger
- GitLens
- SQLite Viewer
```

### 설정 파일 (.vscode/settings.json)
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true
    }
}
```

### 디버그 설정 (.vscode/launch.json)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "unified_server:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

---

## 🔄 개발 워크플로우

### 1. 로컬에서 개발
```bash
# 가상환경 활성화
source venv/bin/activate  # Windows: venv\Scripts\activate

# 서버 실행 (자동 재시작)
uvicorn unified_server:app --reload --host 0.0.0.0 --port 8000

# 또는
python3 unified_server.py
```

### 2. 브라우저 테스트
- UI: http://localhost:8000/static/complete_integrated_system.html
- API: http://localhost:8000/docs

### 3. 코드 수정
- VS Code 또는 좋아하는 에디터 사용
- 파일 저장 시 서버 자동 재시작 (--reload 옵션)

### 4. Git 커밋
```bash
git add .
git commit -m "feat: 새로운 기능 추가"
git push origin genspark_ai_developer
```

### 5. SSH 서버 배포 (필요 시)
```bash
# SSH 서버에서
cd ~/projects/KH-BMS
git pull origin genspark_ai_developer
source venv/bin/activate
python3 unified_server.py
```

---

## 🐛 디버깅 팁

### VS Code 디버거 사용
1. 브레이크포인트 설정 (코드 왼쪽 클릭)
2. F5 누르기
3. 변수 값 확인, 단계별 실행

### 로그 확인
```python
# unified_server.py에 로깅 추가
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/test")
async def test():
    logger.debug("디버그 메시지")
    logger.info("정보 메시지")
    return {"status": "ok"}
```

### DB 직접 확인
```bash
# SQLite 명령어
sqlite3 data/bidbot_data.db

# SQL 실행
sqlite> SELECT COUNT(*) FROM Company_PQ_Stats;
sqlite> SELECT * FROM Company_PQ_Stats LIMIT 5;
sqlite> .quit
```

---

## 📊 프로젝트 구조

```
KH-BMS/
├── .vscode/              # VS Code 설정
├── backend/              # 백엔드 코드
│   ├── app/
│   │   ├── api/         # API 라우터
│   │   ├── models/      # 데이터 모델
│   │   └── services/    # 비즈니스 로직
│   └── data/            # 원본 DB
├── data/                # 로컬 DB 및 CSV
│   ├── bidbot.db
│   ├── bidbot_data.db
│   ├── databases/       # 발주처별 DB
│   └── upload_files/    # CSV 파일
├── static/              # 웹 UI
│   └── complete_integrated_system.html
├── venv/                # Python 가상환경 (Git 제외)
├── unified_server.py    # 메인 서버
├── pq_stats_analyzer.py # PQ 분석
├── create_db_by_org.py  # 발주처 DB 생성
├── requirements.txt     # Python 의존성
└── .gitignore           # Git 제외 파일
```

---

## 🚀 성능 최적화

### 개발 환경
```bash
# 자동 재시작 활성화
uvicorn unified_server:app --reload

# 로그 레벨 조정
uvicorn unified_server:app --log-level debug
```

### 프로덕션 환경
```bash
# 워커 프로세스 사용
uvicorn unified_server:app --workers 4

# Gunicorn 사용
gunicorn unified_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 🔐 보안 주의사항

### .env 파일 사용
```bash
# .env 파일 생성
cat > .env << ENVEOF
GOVERNMENT_API_KEY=your_api_key
SECRET_KEY=your_secret_key
DB_PATH=data/bidbot.db
ENVEOF

# .gitignore에 추가
echo ".env" >> .gitignore
```

### 민감 정보 관리
- API 키는 절대 Git에 커밋하지 마세요
- `.env` 파일은 로컬에만 보관
- GitHub에는 `.env.example` 업로드

---

## 📞 도움말

### 문제 발생 시
1. 가상환경 활성화 확인
2. 의존성 재설치: `pip install -r requirements.txt`
3. 포트 충돌 확인: 8000 포트 사용 중인지 확인
4. DB 파일 확인: `ls -lh data/*.db`

### 추가 자료
- FastAPI 문서: https://fastapi.tiangolo.com/
- SQLAlchemy 문서: https://www.sqlalchemy.org/
- Python 가상환경: https://docs.python.org/3/library/venv.html

---

**로컬 PC에서 편하게 개발하세요! 🎉**
