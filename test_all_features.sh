#!/bin/bash

echo "=========================================="
echo "🧪 전체 기능 테스트 시작"
echo "=========================================="
echo ""

# 1. Health check
echo "1️⃣ 서버 상태 확인..."
curl -s http://localhost:8000/health | jq '.'
echo ""

# 2. PQ 대표사 목록
echo "2️⃣ PQ 대표사 목록 (상위 3개)..."
curl -s "http://localhost:8000/api/v1/pq-companies" | jq '.[0:3] | .[] | {company: .company_name, participation: .total_participation, wins: .win_count}'
echo ""

# 3. PQ 분석 (건화)
echo "3️⃣ PQ 분석 - 건화 (PQ 1위 통계)..."
curl -s "http://localhost:8000/api/v1/pq-analysis/건화?threshold=99.9" | jq '{company, total_bids, rank_1: .rank_stats["1"]}'
echo ""

# 4. 발주처 목록
echo "4️⃣ 발주처 목록..."
curl -s "http://localhost:8000/api/v1/organizations" | jq '.[] | {name, records: .total_records, projects: .total_projects}'
echo ""

# 5. 발주처별 데이터 (경상남도)
echo "5️⃣ 발주처별 예가 분석 - 경상남도 (첫 2건)..."
curl -s "http://localhost:8000/api/v1/organizations/경상남도?limit=2" | jq '.[] | {공고번호, 사업명, 업체명, 예가, 낙찰여부}'
echo ""

# 6. 업로드된 CSV 파일 수
echo "6️⃣ 업로드된 CSV 파일..."
curl -s "http://localhost:8000/api/v1/uploaded-files" | jq '{total: .total_files, files: [.files[0:3][].filename]}'
echo ""

# 7. 로컬 DB 파일 확인
echo "7️⃣ 로컬 DB 파일 확인..."
echo "PQ 통계 DB: $(ls -lh data/bidbot_data.db | awk '{print $5}')"
echo "발주처 DB 개수: $(ls data/databases/*.db 2>/dev/null | wc -l)개"
echo ""

echo "=========================================="
echo "✅ 테스트 완료!"
echo "=========================================="
