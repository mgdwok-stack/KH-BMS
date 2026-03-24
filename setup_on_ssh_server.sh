#!/bin/bash

###############################################################################
# KH-BMS SSH 서버 자동 설치 스크립트
# 
# 사용법:
#   1. 이 스크립트를 SSH 서버로 복사
#   2. chmod +x setup_on_ssh_server.sh
#   3. ./setup_on_ssh_server.sh
#
# 작성: 2026-03-24
###############################################################################

set -e  # 오류 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 단계별 진행 표시
print_step() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  $1${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

###############################################################################
# 1단계: 시스템 요구사항 확인
###############################################################################
print_step "1단계: 시스템 요구사항 확인"

# OS 확인
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    log_info "OS: $NAME $VERSION"
else
    log_warning "OS 정보를 확인할 수 없습니다."
fi

# Python 버전 확인
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    log_info "Python 버전: $PYTHON_VERSION"
    
    # Python 3.8 이상 확인
    REQUIRED_VERSION="3.8"
    if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
        log_error "Python 3.8 이상이 필요합니다. 현재: $PYTHON_VERSION"
        exit 1
    fi
else
    log_error "Python3이 설치되어 있지 않습니다."
    echo "설치 명령:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    exit 1
fi

# Git 확인
if ! command -v git &> /dev/null; then
    log_error "Git이 설치되어 있지 않습니다."
    echo "설치 명령:"
    echo "  Ubuntu/Debian: sudo apt install git"
    echo "  CentOS/RHEL:   sudo yum install git"
    exit 1
fi
log_success "Git 설치 확인"

# curl 확인
if ! command -v curl &> /dev/null; then
    log_warning "curl이 설치되어 있지 않습니다."
    echo "설치 명령:"
    echo "  Ubuntu/Debian: sudo apt install curl"
    echo "  CentOS/RHEL:   sudo yum install curl"
fi

###############################################################################
# 2단계: 프로젝트 디렉토리 설정
###############################################################################
print_step "2단계: 프로젝트 디렉토리 설정"

# 프로젝트 디렉토리 확인
DEFAULT_PROJECT_DIR="$HOME/projects/KH-BMS"
read -p "프로젝트 설치 경로 (기본: $DEFAULT_PROJECT_DIR): " PROJECT_DIR
PROJECT_DIR=${PROJECT_DIR:-$DEFAULT_PROJECT_DIR}

log_info "프로젝트 경로: $PROJECT_DIR"

# 디렉토리가 이미 존재하는 경우
if [[ -d "$PROJECT_DIR" ]]; then
    log_warning "디렉토리가 이미 존재합니다: $PROJECT_DIR"
    read -p "기존 디렉토리를 삭제하고 다시 설치하시겠습니까? (y/N): " CONFIRM
    if [[ "$CONFIRM" == "y" || "$CONFIRM" == "Y" ]]; then
        rm -rf "$PROJECT_DIR"
        log_info "기존 디렉토리 삭제됨"
    else
        log_error "설치 취소"
        exit 1
    fi
fi

# 부모 디렉토리 생성
mkdir -p "$(dirname "$PROJECT_DIR")"

###############################################################################
# 3단계: GitHub에서 클론
###############################################################################
print_step "3단계: GitHub 저장소 클론"

REPO_URL="https://github.com/mgdwok-stack/KH-BMS.git"
BRANCH="genspark_ai_developer"

log_info "저장소: $REPO_URL"
log_info "브랜치: $BRANCH"

git clone "$REPO_URL" "$PROJECT_DIR"
cd "$PROJECT_DIR"
git checkout "$BRANCH"

log_success "프로젝트 클론 완료"

###############################################################################
# 4단계: Python 가상환경 설정
###############################################################################
print_step "4단계: Python 가상환경 설정"

log_info "가상환경 생성 중..."
python3 -m venv venv

log_info "가상환경 활성화..."
source venv/bin/activate

log_info "pip 업그레이드..."
pip install --upgrade pip

log_info "의존성 패키지 설치..."
pip install -r requirements.txt

log_success "가상환경 설정 완료"

###############################################################################
# 5단계: 데이터베이스 복원
###############################################################################
print_step "5단계: 데이터베이스 복원"

echo "데이터베이스 백업 파일을 복원해야 합니다."
echo ""
echo "방법 1: transfer.sh URL 사용 (권장)"
echo "  샌드박스에서:"
echo "    curl --upload-file kh_bms_data_backup.tar.gz https://transfer.sh/kh_bms_data.tar.gz"
echo "  그 후 생성된 URL을 입력하세요."
echo ""
echo "방법 2: 로컬 파일 경로"
echo "  이미 백업 파일을 다운로드한 경우 파일 경로를 입력하세요."
echo ""
read -p "백업 파일 URL 또는 경로 (엔터: 나중에 수동 복원): " BACKUP_SOURCE

if [[ -n "$BACKUP_SOURCE" ]]; then
    if [[ "$BACKUP_SOURCE" =~ ^https?:// ]]; then
        # URL에서 다운로드
        log_info "백업 파일 다운로드 중..."
        wget "$BACKUP_SOURCE" -O kh_bms_data_backup.tar.gz
        BACKUP_FILE="kh_bms_data_backup.tar.gz"
    elif [[ -f "$BACKUP_SOURCE" ]]; then
        # 로컬 파일 사용
        BACKUP_FILE="$BACKUP_SOURCE"
    else
        log_error "파일을 찾을 수 없습니다: $BACKUP_SOURCE"
        BACKUP_FILE=""
    fi
    
    if [[ -n "$BACKUP_FILE" ]]; then
        log_info "백업 파일 압축 해제 중..."
        tar -xzf "$BACKUP_FILE"
        log_success "데이터베이스 복원 완료"
        
        # 파일 확인
        log_info "복원된 DB 파일:"
        ls -lh data/*.db 2>/dev/null || true
        ls -lh data/databases/*.db 2>/dev/null || true
    fi
else
    log_warning "데이터베이스 복원을 건너뛰었습니다."
    echo ""
    echo "나중에 수동으로 복원하려면:"
    echo "  1. 백업 파일을 다운로드"
    echo "  2. cd $PROJECT_DIR"
    echo "  3. tar -xzf kh_bms_data_backup.tar.gz"
    echo ""
fi

###############################################################################
# 6단계: 환경 변수 설정
###############################################################################
print_step "6단계: 환경 변수 설정 (선택사항)"

read -p ".env 파일을 생성하시겠습니까? (y/N): " CREATE_ENV
if [[ "$CREATE_ENV" == "y" || "$CREATE_ENV" == "Y" ]]; then
    cat > .env << 'EOF'
# 서버 설정
HOST=0.0.0.0
PORT=8000

# 데이터베이스 경로
DB_PATH=data/bidbot_data.db
ORG_DB_DIR=data/databases

# API 키 (필요시 설정)
# API_KEY=your_api_key_here
EOF
    log_success ".env 파일 생성 완료"
fi

###############################################################################
# 7단계: 서버 테스트
###############################################################################
print_step "7단계: 서버 테스트"

echo "서버를 테스트로 실행하시겠습니까?"
read -p "테스트 실행 (y/N): " TEST_RUN

if [[ "$TEST_RUN" == "y" || "$TEST_RUN" == "Y" ]]; then
    log_info "서버 시작 중... (Ctrl+C로 중지)"
    python3 unified_server.py &
    SERVER_PID=$!
    
    # 서버 시작 대기
    sleep 5
    
    # 헬스 체크
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "서버가 정상적으로 실행 중입니다!"
        
        # 기본 정보 출력
        echo ""
        echo "접속 URL:"
        echo "  Web UI:   http://$(hostname -I | awk '{print $1}'):8000/static/complete_integrated_system.html"
        echo "  API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
        echo ""
        
        # 서버 중지
        read -p "엔터를 눌러 테스트 서버를 중지하세요..."
        kill $SERVER_PID
        log_info "테스트 서버 중지됨"
    else
        log_error "서버 시작 실패"
        kill $SERVER_PID 2>/dev/null || true
    fi
fi

###############################################################################
# 8단계: systemd 서비스 설정 (선택사항)
###############################################################################
print_step "8단계: systemd 서비스 설정 (선택사항)"

read -p "systemd 서비스를 생성하시겠습니까? (y/N): " CREATE_SERVICE
if [[ "$CREATE_SERVICE" == "y" || "$CREATE_SERVICE" == "Y" ]]; then
    SERVICE_FILE="/etc/systemd/system/kh-bms.service"
    
    log_info "서비스 파일 생성 중..."
    
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=KH-BMS Bid Analysis System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python3 unified_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    log_info "서비스 등록 중..."
    sudo systemctl daemon-reload
    sudo systemctl enable kh-bms
    sudo systemctl start kh-bms
    
    sleep 2
    
    if sudo systemctl is-active --quiet kh-bms; then
        log_success "systemd 서비스 활성화 완료"
        echo ""
        echo "서비스 관리 명령:"
        echo "  상태 확인: sudo systemctl status kh-bms"
        echo "  시작:     sudo systemctl start kh-bms"
        echo "  중지:     sudo systemctl stop kh-bms"
        echo "  재시작:   sudo systemctl restart kh-bms"
        echo "  로그:     sudo journalctl -u kh-bms -f"
    else
        log_error "서비스 시작 실패"
        echo "로그 확인: sudo journalctl -u kh-bms -n 50"
    fi
fi

###############################################################################
# 완료
###############################################################################
print_step "설치 완료!"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  KH-BMS 설치가 완료되었습니다!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "프로젝트 경로: $PROJECT_DIR"
echo ""
echo "다음 단계:"
echo "  1. 데이터베이스 복원 (아직 안 했다면):"
echo "     cd $PROJECT_DIR"
echo "     tar -xzf kh_bms_data_backup.tar.gz"
echo ""
echo "  2. 서버 실행:"
echo "     cd $PROJECT_DIR"
echo "     source venv/bin/activate"
echo "     python3 unified_server.py"
echo ""
echo "  3. 방화벽 설정 (필요시):"
echo "     Ubuntu/Debian: sudo ufw allow 8000/tcp"
echo "     CentOS/RHEL:   sudo firewall-cmd --permanent --add-port=8000/tcp && sudo firewall-cmd --reload"
echo ""
echo "접속 URL:"
echo "  Web UI:   http://$(hostname -I | awk '{print $1}'):8000/static/complete_integrated_system.html"
echo "  API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "문서:"
echo "  - SSH_SERVER_MIGRATION_GUIDE.md: 상세 이전 가이드"
echo "  - LOCAL_DEVELOPMENT_GUIDE.md: 로컬 개발 가이드"
echo "  - README.md: 프로젝트 소개"
echo ""
log_success "모든 작업이 완료되었습니다!"
