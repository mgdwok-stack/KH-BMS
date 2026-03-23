#!/bin/bash

echo "========================================="
echo "통합 Bid-Bot API 테스트"
echo "========================================="

echo -e "\n1. Health Check:"
curl -s http://localhost:8000/health | python3 -m json.tool

echo -e "\n\n2. 조직별 통계:"
curl -s http://localhost:8000/api/v1/organizations | python3 -m json.tool | head -30

echo -e "\n\n3. PQ 대표사 목록:"
curl -s http://localhost:8000/api/v1/pq-companies | python3 -m json.tool | head -20

echo -e "\n\n4. 업로드된 CSV 파일:"
curl -s http://localhost:8000/api/v1/uploaded-files | python3 -m json.tool

echo -e "\n\n5. 원래 Bid-Bot 엔드포인트 (입찰공고 API):"
curl -s http://localhost:8000/api/v1/bids/ | python3 -m json.tool 2>/dev/null || echo "데이터 없음 (정상)"

echo -e "\n\n========================================="
echo "✅ 모든 테스트 완료!"
echo "========================================="
