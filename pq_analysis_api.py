#!/usr/bin/env python3
"""
PQ 통계 분석 전용 API 서버
"""
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
from collections import defaultdict
import glob
import pandas as pd
import shutil
from datetime import datetime

# FastAPI 앱 생성
app = FastAPI(
    title="PQ 통계 분석 API",
    version="1.0.0",
    description="대표사별 PQ순위 및 투찰 행동 분석 API"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (HTML 데모 페이지)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

PQ_DB_PATH = "data/bidbot_data.db"
ORG_DB_DIR = "data/databases"
UPLOAD_DIR = "data/upload_files"

# 업로드 디렉토리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)

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


@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 엔드포인트 - HTML 데모 페이지"""
    html_path = "static/index.html"
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return """
        <html>
            <head><title>PQ 분석 API</title></head>
            <body>
                <h1>🎯 PQ 통계 분석 API</h1>
                <p>API 문서: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """


@app.get("/health")
async def health_check():
    """헬스 체크"""
    db_exists = os.path.exists(PQ_DB_PATH)
    return {
        "status": "healthy",
        "app_name": "PQ Statistics Analysis API",
        "version": "1.0.0",
        "database_available": db_exists
    }


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


# ====================================================================================================
# 발주처 관련 API (조직 DB 조회)
# ====================================================================================================

class OrganizationInfo(BaseModel):
    """발주처 정보 모델"""
    name: str
    total_records: int
    total_projects: int

class BidRecord(BaseModel):
    """입찰 기록 모델"""
    announcement_no: str
    project_name: str
    base_amount: float
    estimated_price: float
    company_name: str
    is_winner: str


@app.get("/api/v1/organizations")
async def list_organizations():
    """발주처 목록 조회"""
    if not os.path.exists(ORG_DB_DIR):
        return []
    
    result = []
    db_files = glob.glob(os.path.join(ORG_DB_DIR, "*.db"))
    
    for db_file in db_files:
        org_name = os.path.splitext(os.path.basename(db_file))[0]
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 전체 레코드 수
            cursor.execute("SELECT COUNT(*) FROM bid_data")
            total_records = cursor.fetchone()[0]
            
            # 프로젝트 수
            cursor.execute("SELECT COUNT(DISTINCT pq_no) FROM bid_data")
            total_projects = cursor.fetchone()[0]
            
            conn.close()
            
            result.append({
                "name": org_name,
                "total_records": total_records,
                "total_projects": total_projects
            })
        except Exception as e:
            print(f"Error reading {db_file}: {e}")
            continue
    
    return result


@app.get("/api/v1/organizations/{org_name}")
async def get_organization_data(
    org_name: str,
    limit: int = Query(default=10, ge=1, le=100)
):
    """특정 발주처의 입찰 데이터 조회"""
    db_path = os.path.join(ORG_DB_DIR, f"{org_name}.db")
    
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail=f"발주처 '{org_name}'의 데이터베이스를 찾을 수 없습니다")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(f"""
        SELECT 
            pq_no as announcement_no,
            project_name,
            base_amount,
            estimated_price,
            company_name,
            is_winner
        FROM bid_data
        ORDER BY pq_no DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ====================================================================================================
# 엑셀/CSV 업로드 및 분석 API
# ====================================================================================================

class UploadResponse(BaseModel):
    """업로드 응답 모델"""
    success: bool
    message: str
    filename: Optional[str] = None
    records_count: Optional[int] = None


def process_csv_to_databases():
    """
    업로드된 CSV 파일들을 처리하여 발주처별 DB 생성
    """
    import subprocess
    
    # create_db_by_org.py 스크립트 실행
    try:
        result = subprocess.run(
            ["python3", "create_db_by_org.py"],
            cwd="/home/user/webapp",
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e)
        }


@app.post("/api/v1/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    CSV 파일 업로드 및 자동 DB 생성
    - 업로드된 CSV를 data/upload_files/에 저장
    - 자동으로 발주처별 DB 생성
    """
    try:
        # 파일 유효성 검사
        if not file.filename.endswith(('.csv', '.CSV')):
            raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다")
        
        # 파일 저장
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # CSV 읽기 및 기본 정보 추출
        try:
            df = pd.read_csv(file_path, encoding='cp949')
            records_count = len(df)
            
            # 발주처 정보 확인
            organizations = []
            if '발주처' in df.columns:
                organizations = df['발주처'].unique().tolist()
                org_info = f"발주처: {', '.join(map(str, organizations[:3]))}"
                if len(organizations) > 3:
                    org_info += f" 외 {len(organizations)-3}개"
            else:
                org_info = "발주처 정보 없음"
            
            # 자동으로 DB 생성 (백그라운드에서 실행)
            message = f"✅ 파일 업로드 성공! {records_count}건의 데이터가 업로드되었습니다. {org_info}\n"
            message += "🔄 발주처별 DB를 자동으로 생성합니다..."
            
            # DB 생성 프로세스 실행 (비동기)
            import threading
            def create_dbs():
                process_csv_to_databases()
            
            threading.Thread(target=create_dbs, daemon=True).start()
            
            return UploadResponse(
                success=True,
                message=message,
                filename=file.filename,
                records_count=records_count
            )
        except Exception as e:
            # 파일은 저장되었지만 분석 실패
            return UploadResponse(
                success=True,
                message=f"⚠️ 파일은 저장되었으나 분석 중 오류 발생: {str(e)}",
                filename=file.filename,
                records_count=0
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 실패: {str(e)}")


@app.get("/api/v1/uploaded-files")
async def list_uploaded_files():
    """업로드된 파일 목록 조회"""
    try:
        if not os.path.exists(UPLOAD_DIR):
            return {"files": [], "total": 0}
        
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith(('.csv', '.CSV', '.xlsx', '.xls')):
                file_path = os.path.join(UPLOAD_DIR, filename)
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # 최신 파일부터 정렬
        files.sort(key=lambda x: x['uploaded_at'], reverse=True)
        
        return {"files": files, "total": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 목록 조회 실패: {str(e)}")


@app.post("/api/v1/process-uploaded-files")
async def process_uploaded_files():
    """
    업로드된 CSV 파일들을 처리하여 DB 생성
    - 발주처별 DB 생성 (create_db_by_org.py 로직 사용)
    - PQ 통계 DB 생성 (build_pq_database.py 로직 사용)
    """
    try:
        if not os.path.exists(UPLOAD_DIR):
            raise HTTPException(status_code=404, detail="업로드 디렉토리가 없습니다")
        
        csv_files = glob.glob(os.path.join(UPLOAD_DIR, "*.csv")) + \
                    glob.glob(os.path.join(UPLOAD_DIR, "*.CSV"))
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="처리할 CSV 파일이 없습니다")
        
        # DB 생성 실행
        result = process_csv_to_databases()
        
        if result["success"]:
            # 생성된 DB 확인
            db_files = glob.glob("data/databases/*.db")
            
            return {
                "success": True,
                "message": f"✅ {len(csv_files)}개의 CSV 파일을 처리하여 {len(db_files)}개의 DB를 생성했습니다",
                "csv_files": [os.path.basename(f) for f in csv_files],
                "databases": [os.path.basename(f) for f in db_files],
                "output": result["output"]
            }
        else:
            return {
                "success": False,
                "message": "❌ DB 생성 실패",
                "error": result["error"],
                "output": result["output"]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 실패: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🎯 PQ 통계 분석 API 서버 시작...")
    print("=" * 80)
    print("📖 API 문서: http://localhost:8001/docs")
    print("🔗 서버 주소: http://localhost:8001")
    print("=" * 80)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
