#!/bin/bash
echo "============================================"
echo "🧪 전체 API 테스트"
echo "============================================"

BASE_URL="http://localhost:8000"

echo ""
echo "1️⃣ Health Check..."
curl -s "$BASE_URL/health" | jq '.status'

echo ""
echo "2️⃣ PQ Companies (처음 3개)..."
curl -s "$BASE_URL/api/v1/pq-companies" | jq '.[0:3] | .[] | {company_name, total_participation, win_count}'

echo ""
echo "3️⃣ PQ Analysis (건화)..."
curl -s "$BASE_URL/api/v1/pq-analysis/건화?threshold=99.9" | jq '{company, total_bids, threshold}'

echo ""
echo "4️⃣ Organizations..."
curl -s "$BASE_URL/api/v1/organizations" | jq '.[] | {name, total_records}'

echo ""
echo "5️⃣ Organization Data (경상남도, 처음 2개)..."
curl -s "$BASE_URL/api/v1/organizations/경상남도?limit=2" | jq '.[0:2] | .[] | {공고번호, 사업명, 낙찰여부}'

echo ""
echo "6️⃣ Uploaded CSV Files..."
curl -s "$BASE_URL/api/v1/uploaded-files" | jq '{total_files, files: .files | length}'

echo ""
echo "7️⃣ Excel Uploads..."
curl -s "$BASE_URL/api/v1/excel/uploads" | jq '{total}'

echo ""
echo "============================================"
echo "✅ 테스트 완료!"
echo "============================================"
