"""
통합 Bid-Bot 서버
- 원래 Bid-Bot 기능 (입찰 공고, AI 예측)
- PQ 분석 기능
- CSV 업로드 및 처리
- 조직별 통계
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import logging
import sqlite3
import shutil
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# Import original app components
from app.config import settings
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting up Unified Bid-Bot API...")
    
    # Initialize original database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Ensure directories exist
    os.makedirs("data/databases", exist_ok=True)
    os.makedirs("data/upload_files", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    yield
    
    logger.info("Shutting down Unified Bid-Bot API...")


# Create unified app
app = FastAPI(
    title="Unified Bid-Bot API",
    version="2.0.0",
    description="통합 입찰 분석 시스템 - 원래 Bid-Bot + PQ 분석 + CSV 업로드",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve frontend public files
if os.path.exists("frontend/public"):
    app.mount("/app", StaticFiles(directory="frontend/public"), name="frontend")


# ============= Pydantic Models =============
class OrganizationInfo(BaseModel):
    name: str
    total_records: int
    total_projects: int


class BidRecord(BaseModel):
    announcement_no: str
    project_name: str
    organization: str
    base_amount: int
    estimated_price: int
    estimated_rate: float
    company_name: str
    pq_score: int
    bid_amount: int
    predicted_rate: float
    is_winner: str


class PQStats(BaseModel):
    total_records: int
    total_companies: int
    rank_range: dict
    avg_winning_rate: float


class UploadedFileInfo(BaseModel):
    filename: str
    size: int
    uploaded_at: datetime


# ============= Root Endpoints =============
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Unified Bid-Bot API",
        "version": "2.0.0",
        "features": [
            "원래 Bid-Bot 기능 (입찰 공고, AI 예측)",
            "PQ 분석 기능",
            "CSV 업로드 및 자동 처리",
            "조직별 통계"
        ],
        "endpoints": {
            "original_bidbot": "/api/v1/bids, /api/v1/predictions, /api/v1/analytics",
            "pq_analysis": "/api/v1/pq-stats, /api/v1/pq-companies, /api/v1/pq-analysis/{company}",
            "organizations": "/api/v1/organizations, /api/v1/organizations/{org_name}",
            "csv_upload": "/api/v1/upload-csv, /api/v1/uploaded-files"
        },
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check"""
    org_dbs = len(list(Path("data/databases").glob("*.db"))) if Path("data/databases").exists() else 0
    pq_db_exists = Path("data/bidbot_data.db").exists()
    
    return {
        "status": "healthy",
        "app_name": "Unified Bid-Bot",
        "version": "2.0.0",
        "databases": {
            "original_bidbot": Path("backend/data/bidbot.db").exists(),
            "pq_stats": pq_db_exists,
            "organization_dbs": org_dbs
        }
    }


# ============= Original Bid-Bot Routes =============
# Import and include original routers
try:
    from app.api import bids_router, predictions_router, analytics_router
    from app.routes.excel_routes import router as excel_router
    
    app.include_router(bids_router, prefix="/api/v1/bids", tags=["입찰공고"])
    app.include_router(predictions_router, prefix="/api/v1/predictions", tags=["AI 예측"])
    app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["분석 및 통계"])
    app.include_router(excel_router, prefix="/api/v1/excel", tags=["엑셀 업로드"])
    logger.info("Original Bid-Bot routes loaded successfully")
except Exception as e:
    logger.warning(f"Could not load some original routes: {e}")


# ============= Organization Statistics =============
ORG_DB_DIR = "data/databases"

@app.get("/api/v1/organizations", response_model=List[OrganizationInfo])
async def list_organizations():
    """조직별 데이터베이스 목록"""
    results = []
    db_dir = Path(ORG_DB_DIR)
    
    if not db_dir.exists():
        return []
    
    for db_file in db_dir.glob("*.db"):
        org_name = db_file.stem
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # Count total records
            cursor.execute("SELECT COUNT(*) FROM bid_data")
            total_records = cursor.fetchone()[0]
            
            # Count unique projects
            cursor.execute("SELECT COUNT(DISTINCT pq_no) FROM bid_data")
            total_projects = cursor.fetchone()[0]
            
            conn.close()
            
            results.append({
                "name": org_name,
                "total_records": total_records,
                "total_projects": total_projects
            })
        except Exception as e:
            logger.error(f"Error reading {org_name}: {e}")
    
    return results


@app.get("/api/v1/organizations/{org_name}")
async def get_organization_data(org_name: str, limit: int = 50):
    """특정 조직의 입찰 데이터"""
    db_path = Path(ORG_DB_DIR) / f"{org_name}.db"
    
    if not db_path.exists():
        raise HTTPException(status_code=404, detail=f"조직 '{org_name}'의 데이터베이스를 찾을 수 없습니다")
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(f"""
        SELECT 
            pq_no as "공고번호",
            project_name as "사업명",
            company_name as "업체명",
            base_amount as "기초금액",
            estimated_rate as "예가",
            is_winner as "낙찰여부",
            announcement_date as "공고일자"
        FROM bid_data
        LIMIT {min(limit, 100)}
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ============= PQ Analysis =============
PQ_DB_PATH = "data/bidbot_data.db"

@app.get("/api/v1/pq-stats")
async def get_pq_stats():
    """PQ 통계 전체 조회"""
    if not Path(PQ_DB_PATH).exists():
        raise HTTPException(status_code=404, detail="PQ 통계 데이터베이스가 없습니다")
    
    conn = sqlite3.connect(PQ_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            `PQ순위` as pq_rank,
            COUNT(*) as total_bids,
            AVG(CASE WHEN `낙찰여부` = 'O' THEN `투찰률` ELSE NULL END) as avg_winning_rate,
            MIN(`투찰률`) as min_rate,
            MAX(`투찰률`) as max_rate
        FROM Company_PQ_Stats
        GROUP BY `PQ순위`
        ORDER BY `PQ순위`
    """)
    
    stats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {
        "total_records": sum(s["total_bids"] for s in stats),
        "rank_statistics": stats
    }


@app.get("/api/v1/pq-companies")
async def get_pq_companies():
    """PQ 대표사 목록 (win_count 포함)"""
    if not Path(PQ_DB_PATH).exists():
        raise HTTPException(status_code=404, detail="PQ 통계 데이터베이스가 없습니다")
    
    conn = sqlite3.connect(PQ_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            `대표사` as company_name,
            COUNT(*) as total_participation,
            COUNT(CASE WHEN `낙찰여부` = 'O' THEN 1 END) as win_count,
            AVG(`투찰률`) as avg_bid_rate
        FROM Company_PQ_Stats
        GROUP BY `대표사`
        ORDER BY total_participation DESC
    """)
    
    companies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return companies


@app.get("/api/v1/pq-analysis/{company_name}")
async def analyze_company_pq(company_name: str, threshold: float = 99.9):
    """특정 대표사의 PQ 순위별 분석 (확률 계산 포함)"""
    if not Path(PQ_DB_PATH).exists():
        raise HTTPException(status_code=404, detail="PQ 통계 데이터베이스가 없습니다")
    
    conn = sqlite3.connect(PQ_DB_PATH)
    cursor = conn.cursor()
    
    # Get total bids count for this company
    cursor.execute("""
        SELECT COUNT(*) FROM Company_PQ_Stats WHERE `대표사` = ?
    """, (company_name,))
    total_bids = cursor.fetchone()[0]
    
    if total_bids == 0:
        conn.close()
        raise HTTPException(status_code=404, detail=f"'{company_name}' 대표사의 데이터가 없습니다")
    
    # Get detailed analysis by rank with probability calculations
    cursor.execute("""
        SELECT `PQ순위`, `투찰률` FROM Company_PQ_Stats WHERE `대표사` = ?
    """, (company_name,))
    all_rows = cursor.fetchall()
    conn.close()
    
    # Group by rank and calculate statistics
    from collections import defaultdict
    import statistics
    
    rank_data = defaultdict(list)
    for pq_rank, bid_rate in all_rows:
        if bid_rate is not None:
            rank_data[pq_rank].append(bid_rate)
    
    rank_stats = {}
    for rank in sorted(rank_data.keys()):
        rates = rank_data[rank]
        above_threshold = sum(1 for r in rates if r >= threshold)
        below_threshold = sum(1 for r in rates if r < threshold)
        
        rank_stats[rank] = {
            "count": len(rates),
            "mean": round(statistics.mean(rates), 2) if rates else 0,
            "median": round(statistics.median(rates), 2) if rates else 0,
            "std": round(statistics.stdev(rates), 2) if len(rates) > 1 else 0,
            "min": round(min(rates), 2) if rates else 0,
            "max": round(max(rates), 2) if rates else 0,
            "above_threshold_count": above_threshold,
            "below_threshold_count": below_threshold,
            "above_threshold_probability": round((above_threshold / len(rates) * 100), 2) if rates else 0,
            "below_threshold_probability": round((below_threshold / len(rates) * 100), 2) if rates else 0
        }
    
    return {
        "company": company_name,
        "total_bids": total_bids,
        "threshold": threshold,
        "rank_stats": rank_stats
    }


# ============= CSV Upload =============
UPLOAD_DIR = Path("data/upload_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/api/v1/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """CSV 파일 업로드 및 자동 DB 생성"""
    if not file.filename.endswith('.CSV') and not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다")
    
    file_path = UPLOAD_DIR / file.filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = file_path.stat().st_size
    
    # Auto-generate databases
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "create_db_by_org.py"],
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            timeout=30
        )
        logger.info(f"DB generation output: {result.stdout}")
        if result.returncode != 0:
            logger.error(f"DB generation error: {result.stderr}")
    except Exception as e:
        logger.error(f"Failed to auto-generate DBs: {e}")
    
    return {
        "filename": file.filename,
        "size": file_size,
        "message": "파일이 업로드되고 데이터베이스가 생성되었습니다",
        "uploaded_at": datetime.now().isoformat()
    }


@app.get("/api/v1/uploaded-files")
async def list_uploaded_files():
    """업로드된 CSV 파일 목록"""
    files = []
    
    # Check both uppercase and lowercase extensions
    for pattern in ["*.CSV", "*.csv"]:
        for file_path in UPLOAD_DIR.glob(pattern):
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    # Remove duplicates (case-insensitive)
    seen = set()
    unique_files = []
    for f in files:
        key = f['filename'].lower()
        if key not in seen:
            seen.add(key)
            unique_files.append(f)
    
    return {
        "files": unique_files,
        "total_files": len(unique_files)
    }


if __name__ == "__main__":
    import uvicorn
    
    print("="*80)
    print("🚀 통합 Bid-Bot API 서버 시작")
    print("="*80)
    print(f"📖 API 문서: http://localhost:8000/docs")
    print(f"🔗 서버 주소: http://localhost:8000")
    print("="*80)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
