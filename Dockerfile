# Python 3.10 slim 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사
COPY backend/requirements.txt .

# Python 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 코드 복사
COPY backend/ ./backend/
COPY data/ ./data/

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# 포트 노출
EXPOSE 8080

# 백엔드 서버 실행 (Cloud Run용)
CMD cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
