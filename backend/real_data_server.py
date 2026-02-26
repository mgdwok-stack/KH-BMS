#!/usr/bin/env python3
"""
Bid-Bot Clone - Real Data Demo Server
Serves actual bid data from SQLite database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.database import BidAnnouncement, BidResult, Prediction

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(
    title="Bid-Bot Clone API (Real Data)",
    version="1.0.0",
    description="실제 입찰 데이터 분석 시스템"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response Models
class BidAnnouncementResponse(BaseModel):
    id: int
    bid_ntce_no: str
    bid_ntce_nm: str
    ntce_instt_nm: str
    dminstt_nm: str
    industry_ty_nm: str
    basis_prc: float
    ntce_dt: str
    bid_status: str
    
class BidResultResponse(BaseModel):
    bid_ntce_no: str
    prdprc_rate: float
    prdprc: float
    sucbid_prc: float
    sucbid_rate: float
    opng_dt: str

class StatsSummaryResponse(BaseModel):
    total_announcements: int
    total_results: int
    avg_prdprc_rate: float
    avg_basis_prc: float
    success_rate: float

class RegionalStatsResponse(BaseModel):
    region: str
    count: int
    avg_prdprc_rate: float
    avg_basis_prc: float

class IndustryStatsResponse(BaseModel):
    industry: str
    count: int
    avg_prdprc_rate: float
    avg_basis_prc: float

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    db = SessionLocal()
    try:
        total_announcements = db.query(BidAnnouncement).count()
        total_results = db.query(BidResult).count()
        
        return {
            "message": "🎯 Bid-Bot Clone API가 실제 데이터와 함께 실행 중입니다!",
            "version": "1.0.0",
            "status": "healthy",
            "docs": "/docs",
            "database": {
                "total_announcements": total_announcements,
                "total_results": total_results,
                "success_rate": f"{total_results/total_announcements*100:.1f}%" if total_announcements > 0 else "0%"
            },
            "features": [
                "실제 입찰 공고 데이터 조회",
                "실제 낙찰 결과 분석",
                "지역/업종/기관별 통계"
            ]
        }
    finally:
        db.close()

@app.get("/api/v1/bids/", response_model=Dict[str, Any])
async def list_bids(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    region: Optional[str] = None,
    industry: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """List bid announcements with filters"""
    db = SessionLocal()
    try:
        query = db.query(BidAnnouncement)
        
        # Apply filters
        if region:
            query = query.filter(BidAnnouncement.dminstt_nm == region)
        if industry:
            query = query.filter(BidAnnouncement.industry_ty_nm == industry)
        if min_price:
            query = query.filter(BidAnnouncement.basis_prc >= min_price)
        if max_price:
            query = query.filter(BidAnnouncement.basis_prc <= max_price)
        
        # Count total
        total = query.count()
        
        # Paginate
        announcements = query.order_by(desc(BidAnnouncement.ntce_dt)).offset((page - 1) * page_size).limit(page_size).all()
        
        items = []
        for ann in announcements:
            items.append({
                "id": ann.id,
                "bid_ntce_no": ann.bid_ntce_no,
                "bid_ntce_nm": ann.bid_ntce_nm,
                "ntce_instt_nm": ann.ntce_instt_nm,
                "dminstt_nm": ann.dminstt_nm,
                "industry_ty_nm": ann.industry_ty_nm,
                "basis_prc": ann.basis_prc,
                "basis_prc_display": f"{ann.basis_prc/1_000_000_000:.2f}B KRW" if ann.basis_prc >= 1_000_000_000 else f"{ann.basis_prc/1_000_000:.0f}M KRW",
                "ntce_dt": ann.ntce_dt,
                "bid_status": ann.bid_status
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }
    finally:
        db.close()

@app.get("/api/v1/bids/{bid_ntce_no}")
async def get_bid_detail(bid_ntce_no: str):
    """Get bid announcement detail with result"""
    db = SessionLocal()
    try:
        announcement = db.query(BidAnnouncement).filter(
            BidAnnouncement.bid_ntce_no == bid_ntce_no
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="Bid not found")
        
        # Get result if exists
        result = db.query(BidResult).filter(
            BidResult.bid_ntce_no == bid_ntce_no
        ).first()
        
        response = {
            "announcement": {
                "id": announcement.id,
                "bid_ntce_no": announcement.bid_ntce_no,
                "bid_ntce_nm": announcement.bid_ntce_nm,
                "ntce_instt_nm": announcement.ntce_instt_nm,
                "dminstt_nm": announcement.dminstt_nm,
                "industry_ty_nm": announcement.industry_ty_nm,
                "basis_prc": announcement.basis_prc,
                "basis_prc_display": f"{announcement.basis_prc/1_000_000_000:.2f}B KRW" if announcement.basis_prc >= 1_000_000_000 else f"{announcement.basis_prc/1_000_000:.0f}M KRW",
                "ntce_dt": announcement.ntce_dt,
                "bid_clse_dt": announcement.bid_clse_dt,
                "opng_dt": announcement.opng_dt,
                "bid_status": announcement.bid_status
            }
        }
        
        if result:
            response["result"] = {
                "prdprc_rate": result.prdprc_rate,
                "prdprc": result.prdprc,
                "prdprc_display": f"{result.prdprc/1_000_000_000:.2f}B KRW" if result.prdprc >= 1_000_000_000 else f"{result.prdprc/1_000_000:.0f}M KRW",
                "sucbid_prc": result.sucbid_prc,
                "sucbid_prc_display": f"{result.sucbid_prc/1_000_000_000:.2f}B KRW" if result.sucbid_prc >= 1_000_000_000 else f"{result.sucbid_prc/1_000_000:.0f}M KRW",
                "sucbid_rate": result.sucbid_rate,
                "opng_dt": result.opng_dt
            }
        
        return response
        
    finally:
        db.close()

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    """Get overall analytics summary"""
    db = SessionLocal()
    try:
        total_announcements = db.query(BidAnnouncement).count()
        total_results = db.query(BidResult).count()
        
        avg_prdprc_rate = db.query(func.avg(BidResult.prdprc_rate)).scalar() or 0
        avg_basis_prc = db.query(func.avg(BidAnnouncement.basis_prc)).scalar() or 0
        min_prdprc_rate = db.query(func.min(BidResult.prdprc_rate)).scalar() or 0
        max_prdprc_rate = db.query(func.max(BidResult.prdprc_rate)).scalar() or 0
        
        return {
            "total_stats": {
                "total_announcements": total_announcements,
                "total_results": total_results,
                "success_rate": round(total_results/total_announcements*100, 2) if total_announcements > 0 else 0,
                "avg_basis_prc": round(avg_basis_prc, 0),
                "avg_basis_prc_display": f"{avg_basis_prc/1_000_000_000:.2f}B KRW"
            },
            "prediction_rate_stats": {
                "avg_prdprc_rate": round(avg_prdprc_rate, 2),
                "min_prdprc_rate": round(min_prdprc_rate, 2),
                "max_prdprc_rate": round(max_prdprc_rate, 2),
                "range": round(max_prdprc_rate - min_prdprc_rate, 2)
            }
        }
    finally:
        db.close()

@app.get("/api/v1/analytics/regional")
async def get_regional_stats():
    """Get regional statistics"""
    db = SessionLocal()
    try:
        # Announcements by region
        ann_stats = db.query(
            BidAnnouncement.dminstt_nm,
            func.count(BidAnnouncement.id).label('count'),
            func.avg(BidAnnouncement.basis_prc).label('avg_price')
        ).group_by(BidAnnouncement.dminstt_nm).all()
        
        # Results by region (with join)
        result_stats = db.query(
            BidAnnouncement.dminstt_nm,
            func.avg(BidResult.prdprc_rate).label('avg_rate')
        ).join(
            BidResult, BidAnnouncement.bid_ntce_no == BidResult.bid_ntce_no
        ).group_by(BidAnnouncement.dminstt_nm).all()
        
        # Merge
        result_map = {r[0]: r[1] for r in result_stats}
        
        stats = []
        for region, count, avg_price in ann_stats:
            stats.append({
                "region": region,
                "count": count,
                "avg_basis_prc": round(avg_price, 0),
                "avg_basis_prc_display": f"{avg_price/1_000_000_000:.2f}B KRW" if avg_price >= 1_000_000_000 else f"{avg_price/1_000_000:.0f}M KRW",
                "avg_prdprc_rate": round(result_map.get(region, 0), 2)
            })
        
        # Sort by count
        stats.sort(key=lambda x: x['count'], reverse=True)
        
        return {"regions": stats}
        
    finally:
        db.close()

@app.get("/api/v1/analytics/industry")
async def get_industry_stats():
    """Get industry statistics"""
    db = SessionLocal()
    try:
        # Announcements by industry
        ann_stats = db.query(
            BidAnnouncement.industry_ty_nm,
            func.count(BidAnnouncement.id).label('count'),
            func.avg(BidAnnouncement.basis_prc).label('avg_price')
        ).group_by(BidAnnouncement.industry_ty_nm).all()
        
        # Results by industry (with join)
        result_stats = db.query(
            BidAnnouncement.industry_ty_nm,
            func.avg(BidResult.prdprc_rate).label('avg_rate')
        ).join(
            BidResult, BidAnnouncement.bid_ntce_no == BidResult.bid_ntce_no
        ).group_by(BidAnnouncement.industry_ty_nm).all()
        
        # Merge
        result_map = {r[0]: r[1] for r in result_stats}
        
        stats = []
        for industry, count, avg_price in ann_stats:
            stats.append({
                "industry": industry,
                "count": count,
                "avg_basis_prc": round(avg_price, 0),
                "avg_basis_prc_display": f"{avg_price/1_000_000_000:.2f}B KRW" if avg_price >= 1_000_000_000 else f"{avg_price/1_000_000:.0f}M KRW",
                "avg_prdprc_rate": round(result_map.get(industry, 0), 2)
            })
        
        # Sort by count
        stats.sort(key=lambda x: x['count'], reverse=True)
        
        return {"industries": stats}
        
    finally:
        db.close()

@app.get("/api/v1/analytics/institution")
async def get_institution_stats():
    """Get institution statistics"""
    db = SessionLocal()
    try:
        # Announcements by institution
        ann_stats = db.query(
            BidAnnouncement.ntce_instt_nm,
            func.count(BidAnnouncement.id).label('count'),
            func.avg(BidAnnouncement.basis_prc).label('avg_price')
        ).group_by(BidAnnouncement.ntce_instt_nm).all()
        
        # Results by institution (with join)
        result_stats = db.query(
            BidAnnouncement.ntce_instt_nm,
            func.avg(BidResult.prdprc_rate).label('avg_rate')
        ).join(
            BidResult, BidAnnouncement.bid_ntce_no == BidResult.bid_ntce_no
        ).group_by(BidAnnouncement.ntce_instt_nm).all()
        
        # Merge
        result_map = {r[0]: r[1] for r in result_stats}
        
        stats = []
        for institution, count, avg_price in ann_stats:
            stats.append({
                "institution": institution,
                "count": count,
                "avg_basis_prc": round(avg_price, 0),
                "avg_basis_prc_display": f"{avg_price/1_000_000_000:.2f}B KRW" if avg_price >= 1_000_000_000 else f"{avg_price/1_000_000:.0f}M KRW",
                "avg_prdprc_rate": round(result_map.get(institution, 0), 2)
            })
        
        # Sort by count
        stats.sort(key=lambda x: x['count'], reverse=True)
        
        return {"institutions": stats}
        
    finally:
        db.close()

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "message": "Real data server is running"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Bid-Bot Clone Real Data Server...")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print(f"🌐 Access at: http://0.0.0.0:8000")
    print(f"📖 API Docs: http://0.0.0.0:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
