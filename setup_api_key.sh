#!/bin/bash
# 안전한 API 키 설정 스크립트

echo "================================================"
echo "🔐 Bid-Bot Clone - 안전한 API 키 설정"
echo "================================================"
echo ""

# API 키 입력받기 (입력 시 화면에 표시되지 않음)
echo "조달청(나라장터) API 키를 입력하세요:"
echo "(입력하는 동안 화면에 표시되지 않습니다)"
read -s API_KEY

# 입력 확인
echo ""
echo "API 키가 입력되었습니다. (보안을 위해 표시하지 않습니다)"
echo ""

# .env 파일 백업
if [ -f .env ]; then
    cp .env .env.backup
    echo "✅ 기존 .env 파일 백업 완료 (.env.backup)"
fi

# API 키를 .env 파일에 안전하게 저장
if [ -f .env ]; then
    # 기존 파일에서 PROCUREMENT_API_KEY 라인만 교체
    sed -i "s/^PROCUREMENT_API_KEY=.*/PROCUREMENT_API_KEY=${API_KEY}/" .env
    echo "✅ API 키가 .env 파일에 저장되었습니다"
else
    # .env 파일이 없으면 생성
    cp .env.example .env
    sed -i "s/^PROCUREMENT_API_KEY=.*/PROCUREMENT_API_KEY=${API_KEY}/" .env
    echo "✅ .env 파일 생성 및 API 키 저장 완료"
fi

# 파일 권한 설정 (소유자만 읽기/쓰기 가능)
chmod 600 .env
echo "✅ .env 파일 권한 설정 완료 (600 - 소유자만 접근 가능)"

# .gitignore 확인
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "✅ .env 파일이 .gitignore에 추가되었습니다"
fi

echo ""
echo "================================================"
echo "✅ API 키 설정 완료!"
echo "================================================"
echo ""
echo "다음 단계:"
echo "1. 백엔드 서버 재시작: python demo_server.py"
echo "2. 데이터 수집: python scripts/collect_data.py --mode recent"
echo "3. AI 모델 학습: python scripts/train_models.py"
echo ""
echo "⚠️ 보안 팁:"
echo "- .env 파일은 절대 Git에 커밋하지 마세요"
echo "- API 키는 다른 사람과 공유하지 마세요"
echo "- 정기적으로 API 키를 변경하세요"
echo ""
