#!/usr/bin/env python3
"""
발주처별 데이터베이스 조회 API 서버
"""
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import glob
from pathlib import Path
from auto_update_dbs import DatabaseAutoUpdater

# FastAPI 앱 생성
app = FastAPI(
    title="Bid-Bot Clone - 발주처 DB API",
    version="2.0.0",
    description="발주처별 입찰 데이터 조회 및 관리 API"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_DIR = "data/databases"

class BidRecord(BaseModel):
    """입찰 기록 모델"""
    id: int
    pq_no: str
    announcement_date: str
    project_name: str
    organization: str
    bid_type: str
    base_amount: str
    estimated_price: str
    estimated_rate: float
    company_name: str
    pq_score: float
    bid_amount: str
    predicted_rate: float
    is_winner: str

class OrganizationInfo(BaseModel):
    """발주처 정보 모델"""
    name: str
    db_file: str
    total_records: int
    total_projects: int
    winner_count: int


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🏢 발주처별 입찰 데이터 API가 실행 중입니다!",
        "version": "2.1.0",
        "status": "healthy",
        "docs": "/docs",
        "features": [
            "발주처 목록 조회",
            "발주처별 입찰 데이터 조회",
            "발주처 DB 생성",
            "통계 조회",
            "🆕 자동 업데이트 (CSV 변경 감지)",
            "🆕 수동 업데이트 트리거"
        ],
        "endpoints": {
            "organizations": "/api/v1/organizations",
            "organization_data": "/api/v1/organizations/{org_name}",
            "create_db": "/api/v1/create-db/{org_name}",
            "search": "/api/v1/search",
            "check_updates": "/api/v1/check-updates",
            "update_all": "/api/v1/update-all-databases",
            "pq_stats": "/api/v1/pq-stats",
            "pq_analysis": "/api/v1/pq-analysis/{company_name}"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    db_count = len(list(Path(DB_DIR).glob("*.db"))) if os.path.exists(DB_DIR) else 0
    return {
        "status": "healthy",
        "app_name": "Bid-Bot Clone - Organization DB",
        "version": "2.0.0",
        "databases_count": db_count
    }


@app.get("/api/v1/organizations", response_model=List[OrganizationInfo])
async def list_organizations():
    """생성된 발주처 DB 목록 조회"""
    if not os.path.exists(DB_DIR):
        return []
    
    db_files = list(Path(DB_DIR).glob("*.db"))
    organizations = []
    
    for db_file in db_files:
        org_name = db_file.stem
        
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM bid_data")
            total_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT project_name) FROM bid_data")
            total_projects = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM bid_data WHERE is_winner = 'O'")
            winner_count = cursor.fetchone()[0]
            
            conn.close()
            
            organizations.append(OrganizationInfo(
                name=org_name,
                db_file=str(db_file),
                total_records=total_records,
                total_projects=total_projects,
                winner_count=winner_count
            ))
        except Exception as e:
            print(f"Error reading {db_file}: {e}")
            continue
    
    return organizations


@app.get("/api/v1/organizations/{org_name}", response_model=List[BidRecord])
async def get_organization_data(
    org_name: str,
    limit: Optional[int] = Query(100, ge=1, le=1000),
    offset: Optional[int] = Query(0, ge=0),
    winner_only: Optional[bool] = Query(False, description="낙찰업체만 조회")
):
    """특정 발주처의 입찰 데이터 조회"""
    db_path = os.path.join(DB_DIR, f"{org_name}.db")
    
    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=404,
            detail=f"'{org_name}' 발주처의 데이터베이스를 찾을 수 없습니다."
        )
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 쿼리 작성
        query = "SELECT * FROM bid_data"
        if winner_only:
            query += " WHERE is_winner = 'O'"
        query += " ORDER BY announcement_date DESC LIMIT ? OFFSET ?"
        
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        
        conn.close()
        
        # 딕셔너리로 변환
        records = []
        for row in rows:
            records.append(dict(row))
        
        return records
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"데이터 조회 중 오류 발생: {str(e)}"
        )


@app.get("/api/v1/organizations/{org_name}/stats")
async def get_organization_stats(org_name: str):
    """발주처 통계 조회"""
    db_path = os.path.join(DB_DIR, f"{org_name}.db")
    
    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=404,
            detail=f"'{org_name}' 발주처의 데이터베이스를 찾을 수 없습니다."
        )
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 기본 통계
        cursor.execute("SELECT COUNT(*) FROM bid_data")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT project_name) FROM bid_data")
        total_projects = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bid_data WHERE is_winner = 'O'")
        winner_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(estimated_rate) FROM bid_data")
        avg_estimated_rate = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(predicted_rate) FROM bid_data")
        avg_predicted_rate = cursor.fetchone()[0]
        
        # 낙찰업체 정보
        cursor.execute("""
            SELECT company_name, COUNT(*) as count 
            FROM bid_data 
            WHERE is_winner = 'O'
            GROUP BY company_name
            ORDER BY count DESC
        """)
        winners = cursor.fetchall()
        
        conn.close()
        
        return {
            "organization": org_name,
            "total_records": total_records,
            "total_projects": total_projects,
            "winner_count": winner_count,
            "avg_estimated_rate": round(avg_estimated_rate, 2) if avg_estimated_rate else 0,
            "avg_predicted_rate": round(avg_predicted_rate, 2) if avg_predicted_rate else 0,
            "winners": [{"company": w[0], "count": w[1]} for w in winners]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류 발생: {str(e)}"
        )


@app.post("/api/v1/create-db/{org_name}")
async def create_organization_db(org_name: str):
    """발주처 데이터베이스 생성"""
    import pandas as pd
    
    # CSV 파일 찾기
    csv_files = glob.glob("data/upload_files/*.CSV") + glob.glob("data/upload_files/*.csv")
    
    if not csv_files:
        raise HTTPException(
            status_code=404,
            detail="CSV 파일을 찾을 수 없습니다."
        )
    
    # 데이터 수집
    all_data = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='cp949')
            org_data = df[df['발주처'] == org_name]
            if len(org_data) > 0:
                all_data.append(org_data)
        except Exception as e:
            continue
    
    if not all_data:
        raise HTTPException(
            status_code=404,
            detail=f"'{org_name}' 발주처의 데이터를 찾을 수 없습니다."
        )
    
    # 데이터베이스 생성
    combined_df = pd.concat(all_data, ignore_index=True)
    
    os.makedirs(DB_DIR, exist_ok=True)
    db_path = os.path.join(DB_DIR, f"{org_name}.db")
    
    # 기존 파일 삭제
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bid_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pq_no TEXT,
            announcement_date TEXT,
            project_name TEXT,
            organization TEXT,
            bid_type TEXT,
            base_amount TEXT,
            estimated_price TEXT,
            estimated_rate REAL,
            company_name TEXT,
            pq_score REAL,
            bid_amount TEXT,
            predicted_rate REAL,
            is_winner TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 데이터 삽입
    for _, row in combined_df.iterrows():
        cursor.execute("""
            INSERT INTO bid_data (
                pq_no, announcement_date, project_name, organization, bid_type,
                base_amount, estimated_price, estimated_rate, company_name,
                pq_score, bid_amount, predicted_rate, is_winner
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['PQ공고 NO.'],
            row['공고일자'],
            row['사업명'],
            row['발주처'],
            row['입찰구분'],
            row['기초금액'],
            row['예정금액'],
            row['예가'],
            row['업체명'],
            row['PQ점수'],
            row['투찰금액'],
            row['추정예가'],
            row['낙찰여부']
        ))
    
    conn.commit()
    
    # 통계 조회
    cursor.execute("SELECT COUNT(*) FROM bid_data")
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "message": f"'{org_name}' 데이터베이스가 생성되었습니다.",
        "db_path": db_path,
        "total_records": total_count
    }


@app.get("/api/v1/search")
async def search_projects(
    keyword: str = Query(..., min_length=1, description="검색 키워드"),
    org_name: Optional[str] = Query(None, description="발주처 필터")
):
    """프로젝트 검색"""
    if not os.path.exists(DB_DIR):
        return []
    
    # 검색할 DB 파일 목록
    if org_name:
        db_files = [Path(DB_DIR) / f"{org_name}.db"]
    else:
        db_files = list(Path(DB_DIR).glob("*.db"))
    
    results = []
    
    for db_file in db_files:
        if not db_file.exists():
            continue
        
        try:
            conn = sqlite3.connect(str(db_file))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM bid_data 
                WHERE project_name LIKE ? OR company_name LIKE ?
                ORDER BY announcement_date DESC
                LIMIT 50
            """, (f"%{keyword}%", f"%{keyword}%"))
            
            rows = cursor.fetchall()
            
            for row in rows:
                results.append(dict(row))
            
            conn.close()
            
        except Exception as e:
            print(f"Error searching {db_file}: {e}")
            continue
    
    return results


@app.get("/api/v1/available-organizations")
async def list_available_organizations():
    """CSV에서 사용 가능한 발주처 목록"""
    import pandas as pd
    
    csv_files = glob.glob("data/upload_files/*.CSV") + glob.glob("data/upload_files/*.csv")
    
    if not csv_files:
        return {"organizations": []}
    
    all_orgs = set()
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='cp949')
            all_orgs.update(df['발주처'].unique())
        except:
            continue
    
    return {
        "organizations": sorted(list(all_orgs)),
        "count": len(all_orgs)
    }


@app.post("/api/v1/update-all-databases")
async def update_all_databases(
    background_tasks: BackgroundTasks,
    force: bool = Query(False, description="변경사항이 없어도 강제로 업데이트")
):
    """모든 발주처 DB 자동 업데이트"""
    
    def run_update():
        updater = DatabaseAutoUpdater()
        return updater.update_all_databases(force=force)
    
    # 백그라운드에서 실행
    background_tasks.add_task(run_update)
    
    return {
        "message": "데이터베이스 업데이트가 백그라운드에서 실행됩니다.",
        "force": force,
        "status": "started"
    }


@app.get("/api/v1/check-updates")
async def check_for_updates():
    """CSV 파일 변경사항 확인"""
    updater = DatabaseAutoUpdater()
    changes, current_state = updater.check_for_changes()
    
    csv_files = []
    for file_path, info in current_state.items():
        csv_files.append({
            "name": os.path.basename(file_path),
            "path": file_path,
            "size": info['size'],
            "modified": info['modified']
        })
    
    return {
        "has_changes": (
            len(changes['new_files']) > 0 or 
            len(changes['modified_files']) > 0 or 
            len(changes['deleted_files']) > 0
        ),
        "changes": {
            "new_files": [os.path.basename(f) for f in changes['new_files']],
            "modified_files": [os.path.basename(f) for f in changes['modified_files']],
            "deleted_files": [os.path.basename(f) for f in changes['deleted_files']]
        },
        "csv_files": csv_files,
        "total_csv_files": len(csv_files)
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 발주처별 데이터베이스 API 서버 시작...")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🔗 서버 주소: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================================================
# PQ 통계 분석 API 엔드포인트
# ============================================================================

PQ_DB_PATH = "data/bidbot_data.db"

class PQCompanyStats(BaseModel):
    """PQ 회사 통계 모델"""
    company_name: str
    total_bids: int
    participation_count: int
    avg_bid_rate: float
    
class PQRankAnalysis(BaseModel):
    """PQ 순위별 분석 모델"""
    rank: int
    bid_count: int
    avg_rate: float
    min_rate: float
    max_rate: float
    median_rate: float
    high_rate_count: int
    low_rate_count: int
    high_rate_percentage: float
    low_rate_percentage: float
    winner_count: int

class CompanyAnalysisResult(BaseModel):
    """회사 분석 결과 모델"""
    company_name: str
    total_bids: int
    reference_rate: float
    rank_analysis: List[PQRankAnalysis]
    insights: dict


@app.get("/api/v1/pq-stats")
async def get_pq_stats():
    """PQ 통계 데이터베이스 전체 현황"""
    if not os.path.exists(PQ_DB_PATH):
        raise HTTPException(status_code=404, detail="PQ 데이터베이스가 존재하지 않습니다")
    
    conn = sqlite3.connect(PQ_DB_PATH)
    cursor = conn.cursor()
    
    # 전체 통계
    cursor.execute("SELECT COUNT(*) FROM Company_PQ_Stats")
    total_records = cursor.fetchone()[0]
    
    # 대표사 목록
    cursor.execute("""
        SELECT 대표사, COUNT(*) as cnt
        FROM Company_PQ_Stats
        GROUP BY 대표사
        ORDER BY cnt DESC
    """)
    companies = [{"company": row[0], "participation_count": row[1]} for row in cursor.fetchall()]
    
    # PQ순위별 통계
    cursor.execute("""
        SELECT 
            PQ순위,
            COUNT(*) as 참여수,
            ROUND(AVG(투찰률), 2) as 평균투찰률,
            ROUND(MIN(투찰률), 2) as 최소투찰률,
            ROUND(MAX(투찰률), 2) as 최대투찰률
        FROM Company_PQ_Stats
        GROUP BY PQ순위
        ORDER BY PQ순위
    """)
    rank_stats = [
        {
            "rank": row[0],
            "count": row[1],
            "avg_rate": row[2],
            "min_rate": row[3],
            "max_rate": row[4]
        }
        for row in cursor.fetchall()
    ]
    
    conn.close()
    
    return {
        "total_records": total_records,
        "total_companies": len(companies),
        "companies": companies,
        "rank_statistics": rank_stats
    }


@app.get("/api/v1/pq-analysis/{company_name}", response_model=CompanyAnalysisResult)
async def analyze_company_pq(
    company_name: str,
    reference_rate: float = Query(99.9, description="기준 투찰률")
):
    """특정 대표사의 PQ순위별 투찰 행동 상세 분석"""
    
    if not os.path.exists(PQ_DB_PATH):
        raise HTTPException(status_code=404, detail="PQ 데이터베이스가 존재하지 않습니다")
    
    conn = sqlite3.connect(PQ_DB_PATH)
    cursor = conn.cursor()
    
    # 해당 회사 데이터 조회
    cursor.execute("""
        SELECT 공고번호, 업체명, PQ점수, PQ순위, 투찰률, 예가, 낙찰여부
        FROM Company_PQ_Stats
        WHERE 대표사 = ?
        ORDER BY PQ순위
    """, (company_name,))
    
    rows = cursor.fetchall()
    
    if not rows:
        conn.close()
        raise HTTPException(status_code=404, detail=f"'{company_name}' 데이터가 없습니다")
    
    # 순위별 그룹화
    from collections import defaultdict
    rank_groups = defaultdict(list)
    for row in rows:
        rank = row[3]
        bid_rate = row[4]
        is_winner = row[6]
        rank_groups[rank].append({
            "bid_rate": bid_rate,
            "is_winner": is_winner
        })
    
    # 순위별 분석
    rank_analysis_list = []
    for rank, bids in sorted(rank_groups.items()):
        rates = [b["bid_rate"] for b in bids]
        high_count = sum(1 for r in rates if r >= reference_rate)
        low_count = len(rates) - high_count
        winner_count = sum(1 for b in bids if b["is_winner"] == "O")
        
        rank_analysis_list.append(PQRankAnalysis(
            rank=rank,
            bid_count=len(bids),
            avg_rate=round(sum(rates) / len(rates), 2),
            min_rate=round(min(rates), 2),
            max_rate=round(max(rates), 2),
            median_rate=round(sorted(rates)[len(rates)//2], 2),
            high_rate_count=high_count,
            low_rate_count=low_count,
            high_rate_percentage=round(high_count / len(rates) * 100, 1),
            low_rate_percentage=round(low_count / len(rates) * 100, 1),
            winner_count=winner_count
        ))
    
    # 인사이트 생성
    insights = {}
    
    # 1순위 분석
    rank1_data = rank_groups.get(1, [])
    if rank1_data:
        rates_1 = [b["bid_rate"] for b in rank1_data]
        high_1 = sum(1 for r in rates_1 if r >= reference_rate)
        low_1 = len(rates_1) - high_1
        
        if high_1 > low_1:
            insights["rank_1_strategy"] = f"적극적 낙찰 전략 (안정적 고가 입찰, {high_1/len(rates_1)*100:.0f}%가 {reference_rate}% 이상)"
        else:
            insights["rank_1_strategy"] = f"공격적 낙찰 전략 (저가 입찰, {low_1/len(rates_1)*100:.0f}%가 {reference_rate}% 미만)"
    
    # 2순위 분석
    rank2_data = rank_groups.get(2, [])
    if rank2_data:
        avg_2 = sum(b["bid_rate"] for b in rank2_data) / len(rank2_data)
        if avg_2 < reference_rate:
            insights["rank_2_strategy"] = f"경쟁적 입찰 (평균 {avg_2:.2f}%, {reference_rate}% 미만)"
        else:
            insights["rank_2_strategy"] = f"안전한 입찰 (평균 {avg_2:.2f}%, {reference_rate}% 이상)"
    
    conn.close()
    
    return CompanyAnalysisResult(
        company_name=company_name,
        total_bids=len(rows),
        reference_rate=reference_rate,
        rank_analysis=rank_analysis_list,
        insights=insights
    )


@app.get("/api/v1/pq-companies")
async def list_pq_companies():
    """PQ 데이터베이스에 등록된 대표사 목록"""
    if not os.path.exists(PQ_DB_PATH):
        raise HTTPException(status_code=404, detail="PQ 데이터베이스가 존재하지 않습니다")
    
    conn = sqlite3.connect(PQ_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 대표사, COUNT(*) as cnt
        FROM Company_PQ_Stats
        GROUP BY 대표사
        ORDER BY cnt DESC
    """)
    
    companies = [{"company_name": row[0], "bid_count": row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return {
        "total_companies": len(companies),
        "companies": companies
    }

