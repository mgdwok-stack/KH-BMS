#!/bin/bash
echo "=========================================="
echo "📋 요구사항 검증 테스트"
echo "=========================================="
echo ""

# 1. PQ 대표사 목록 (낙찰 건수 포함)
echo "1️⃣ PQ 대표사 목록 (상위 5개, 낙찰 건수 확인)"
curl -s "http://localhost:8000/api/v1/pq-companies" | jq '.[0:5] | .[] | {company: .company_name, total: .total_participation, wins: .win_count, avg_rate: .avg_bid_rate}'
echo ""

# 2. PQ 분석 - 도화
echo "2️⃣ PQ 분석 - 도화 (낙찰 237건)"
curl -s "http://localhost:8000/api/v1/pq-analysis/도화?threshold=99.9" | jq '{company, total_bids, rank_1: .rank_stats["1"] | {count, wins: .above_threshold_count, win_prob: .above_threshold_probability}}'
echo ""

# 3. 발주처 목록
echo "3️⃣ 발주처 목록"
curl -s "http://localhost:8000/api/v1/organizations" | jq '.[] | {name, records: .total_records}'
echo ""

# 4. 발주처별 데이터 (경상남도)
echo "4️⃣ 발주처별 예가 분석 - 경상남도 (첫 2건)"
curl -s "http://localhost:8000/api/v1/organizations/경상남도?limit=2" | jq -r '.[] | "\(.업체명) - 예가: \(.예가)% - 낙찰: \(.낙찰여부)"'
echo ""

# 5. 업로드된 CSV 파일 수
echo "5️⃣ 업로드된 CSV 파일"
curl -s "http://localhost:8000/api/v1/uploaded-files" | jq '{total: .total_files}'
echo ""

echo "=========================================="
echo "✅ 검증 완료!"
echo "=========================================="
