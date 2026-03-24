#!/bin/bash

BASE_URL="https://8001-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai"

echo "==============================================="
echo "🧪 통합 API 테스트"
echo "==============================================="
echo ""

echo "1️⃣ 발주처 목록 조회:"
curl -s "$BASE_URL/api/v1/organizations" | python3 -m json.tool | head -15
echo ""

echo "2️⃣ 경상남도 데이터 조회 (3건):"
curl -s "$BASE_URL/api/v1/organizations/%EA%B2%BD%EC%83%81%EB%82%A8%EB%8F%84?limit=3" | python3 -m json.tool | head -10
echo ""

echo "3️⃣ PQ 전체 통계:"
curl -s "$BASE_URL/api/v1/pq-stats" | python3 -m json.tool | head -15
echo ""

echo "4️⃣ PQ 대표사 목록:"
curl -s "$BASE_URL/api/v1/pq-companies" | python3 -m json.tool | head -15
echo ""

echo "5️⃣ 도화 대표사 분석:"
curl -s "$BASE_URL/api/v1/pq-analysis/%EB%8F%84%ED%99%94?reference_rate=99.9" | python3 -m json.tool | head -20
echo ""

echo "==============================================="
echo "✅ 모든 API 테스트 완료!"
echo "📖 Swagger UI: $BASE_URL/docs"
echo "🌐 웹 데모: $BASE_URL/static/unified.html"
echo "==============================================="
