"""
분석 및 통계 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..models.bid import BidAnnouncement
from ..models.result import BidResult
from ..models.prediction import Prediction

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/trends")
def get_bid_trends(
    days: int = Query(90, ge=7, le=365, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    입찰 트렌드 분석
    
    - **days**: 조회 기간 (기본값: 90일)
    
    Returns:
    - 일별 입찰 건수 및 평균 사정률
    - 지역별 통계
    - 업종별 통계
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # 일별 낙찰 통계
        daily_stats = db.query(
            func.date(BidResult.opengdt).label('date'),
            func.count(BidResult.id).label('count'),
            func.avg(BidResult.prdprc_rate).label('avg_rate'),
            func.stddev(BidResult.prdprc_rate).label('std_rate')
        ).filter(
            and_(
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).group_by(
            func.date(BidResult.opengdt)
        ).order_by(
            func.date(BidResult.opengdt)
        ).all()
        
        # 지역별 통계
        regional_stats = db.query(
            BidAnnouncement.rgn_nm.label('region'),
            func.count(BidAnnouncement.id).label('count'),
            func.avg(BidResult.prdprc_rate).label('avg_rate')
        ).join(
            BidResult,
            BidAnnouncement.bid_ntce_no == BidResult.bid_ntce_no
        ).filter(
            and_(
                BidAnnouncement.rgn_nm.isnot(None),
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).group_by(
            BidAnnouncement.rgn_nm
        ).all()
        
        # 업종별 통계 (상위 20개)
        industry_stats = db.query(
            BidAnnouncement.induty_ty_nm.label('industry'),
            func.count(BidAnnouncement.id).label('count'),
            func.avg(BidResult.prdprc_rate).label('avg_rate')
        ).join(
            BidResult,
            BidAnnouncement.bid_ntce_no == BidResult.bid_ntce_no
        ).filter(
            and_(
                BidAnnouncement.induty_ty_nm.isnot(None),
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).group_by(
            BidAnnouncement.induty_ty_nm
        ).order_by(
            func.count(BidAnnouncement.id).desc()
        ).limit(20).all()
        
        return {
            "period_days": days,
            "daily_trends": [
                {
                    "date": str(row.date),
                    "count": row.count,
                    "avg_rate": float(row.avg_rate) if row.avg_rate else None,
                    "std_rate": float(row.std_rate) if row.std_rate else None
                }
                for row in daily_stats
            ],
            "regional_stats": [
                {
                    "region": row.region,
                    "count": row.count,
                    "avg_rate": float(row.avg_rate) if row.avg_rate else None
                }
                for row in regional_stats
            ],
            "industry_stats": [
                {
                    "industry": row.industry,
                    "count": row.count,
                    "avg_rate": float(row.avg_rate) if row.avg_rate else None
                }
                for row in industry_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"트렌드 분석 실패: {e}")
        raise HTTPException(status_code=500, detail="트렌드 분석 실패")


@router.get("/institution/{institution_name}")
def get_institution_analysis(
    institution_name: str,
    days: int = Query(365, ge=30, le=1095, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    발주기관 분석
    
    - **institution_name**: 발주기관명
    - **days**: 조회 기간 (기본값: 365일)
    
    Returns:
    - 발주기관 입찰 통계
    - 평균 사정률 및 표준편차
    - 시계열 사정률 데이터
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # 발주기관 기본 통계
        basic_stats = db.query(
            func.count(BidResult.id).label('total_count'),
            func.avg(BidResult.prdprc_rate).label('avg_rate'),
            func.stddev(BidResult.prdprc_rate).label('std_rate'),
            func.min(BidResult.prdprc_rate).label('min_rate'),
            func.max(BidResult.prdprc_rate).label('max_rate'),
            func.avg(BidResult.presmpt_prce).label('avg_amount')
        ).filter(
            and_(
                BidResult.instt_nm.like(f"%{institution_name}%"),
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).first()
        
        if not basic_stats or basic_stats.total_count == 0:
            raise HTTPException(status_code=404, detail="해당 발주기관 데이터가 없습니다")
        
        # 월별 사정률 추이
        monthly_trends = db.query(
            func.date_trunc('month', BidResult.opengdt).label('month'),
            func.count(BidResult.id).label('count'),
            func.avg(BidResult.prdprc_rate).label('avg_rate')
        ).filter(
            and_(
                BidResult.instt_nm.like(f"%{institution_name}%"),
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).group_by(
            func.date_trunc('month', BidResult.opengdt)
        ).order_by(
            func.date_trunc('month', BidResult.opengdt)
        ).all()
        
        # 금액대별 분포
        price_ranges = [
            (0, 100000000, "1억 미만"),
            (100000000, 500000000, "1억~5억"),
            (500000000, 1000000000, "5억~10억"),
            (1000000000, 5000000000, "10억~50억"),
            (5000000000, None, "50억 이상")
        ]
        
        price_distribution = []
        for min_price, max_price, label in price_ranges:
            query_filters = [
                BidResult.instt_nm.like(f"%{institution_name}%"),
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None),
                BidResult.presmpt_prce >= min_price
            ]
            if max_price:
                query_filters.append(BidResult.presmpt_prce < max_price)
            
            stats = db.query(
                func.count(BidResult.id).label('count'),
                func.avg(BidResult.prdprc_rate).label('avg_rate')
            ).filter(and_(*query_filters)).first()
            
            if stats.count > 0:
                price_distribution.append({
                    "range": label,
                    "count": stats.count,
                    "avg_rate": float(stats.avg_rate) if stats.avg_rate else None
                })
        
        return {
            "institution_name": institution_name,
            "period_days": days,
            "statistics": {
                "total_count": basic_stats.total_count,
                "avg_rate": float(basic_stats.avg_rate) if basic_stats.avg_rate else None,
                "std_rate": float(basic_stats.std_rate) if basic_stats.std_rate else None,
                "min_rate": float(basic_stats.min_rate) if basic_stats.min_rate else None,
                "max_rate": float(basic_stats.max_rate) if basic_stats.max_rate else None,
                "avg_amount": int(basic_stats.avg_amount) if basic_stats.avg_amount else None
            },
            "monthly_trends": [
                {
                    "month": str(row.month)[:7],  # YYYY-MM
                    "count": row.count,
                    "avg_rate": float(row.avg_rate) if row.avg_rate else None
                }
                for row in monthly_trends
            ],
            "price_distribution": price_distribution
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"발주기관 분석 실패: {e}")
        raise HTTPException(status_code=500, detail="발주기관 분석 실패")


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    대시보드 요약 정보
    
    Returns:
    - 전체 입찰 통계
    - AI 예측 통계
    - 최근 트렌드
    """
    try:
        # 전체 입찰 통계
        total_announcements = db.query(func.count(BidAnnouncement.id)).scalar()
        total_results = db.query(func.count(BidResult.id)).scalar()
        total_predictions = db.query(func.count(Prediction.id)).scalar()
        
        # 최근 30일 통계
        last_30_days = datetime.now() - timedelta(days=30)
        
        recent_results = db.query(
            func.count(BidResult.id).label('count'),
            func.avg(BidResult.prdprc_rate).label('avg_rate')
        ).filter(
            and_(
                BidResult.opengdt >= last_30_days,
                BidResult.prdprc_rate.isnot(None)
            )
        ).first()
        
        # 평균 사정률 (전체)
        overall_avg_rate = db.query(
            func.avg(BidResult.prdprc_rate)
        ).filter(
            BidResult.prdprc_rate.isnot(None)
        ).scalar()
        
        # AI 예측 정확도
        validated_predictions = db.query(Prediction).filter(
            Prediction.prediction_status == 'validated'
        ).all()
        
        avg_error = None
        accuracy_rate = None
        if validated_predictions:
            errors = [p.prediction_error for p in validated_predictions if p.prediction_error is not None]
            if errors:
                import numpy as np
                avg_error = float(np.mean(errors))
                accuracy_rate = sum(1 for e in errors if e <= 0.1) / len(errors) * 100
        
        return {
            "total_statistics": {
                "total_announcements": total_announcements,
                "total_results": total_results,
                "total_predictions": total_predictions,
                "overall_avg_rate": float(overall_avg_rate) if overall_avg_rate else None
            },
            "recent_30_days": {
                "results_count": recent_results.count if recent_results else 0,
                "avg_rate": float(recent_results.avg_rate) if recent_results and recent_results.avg_rate else None
            },
            "ai_performance": {
                "validated_predictions": len(validated_predictions),
                "avg_prediction_error": avg_error,
                "accuracy_rate": accuracy_rate
            }
        }
        
    except Exception as e:
        logger.error(f"대시보드 요약 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="대시보드 요약 조회 실패")


@router.get("/histogram")
def get_rate_histogram(
    bins: int = Query(20, ge=10, le=100, description="히스토그램 구간 수"),
    days: int = Query(90, ge=7, le=365, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    사정률 분포 히스토그램 데이터
    
    - **bins**: 히스토그램 구간 수 (기본값: 20)
    - **days**: 조회 기간 (기본값: 90일)
    
    Returns:
    - 구간별 입찰 건수
    - 구간별 비율
    """
    try:
        import numpy as np
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 사정률 데이터 조회
        results = db.query(BidResult.prdprc_rate).filter(
            and_(
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None),
                BidResult.prdprc_rate >= 95.0,
                BidResult.prdprc_rate <= 105.0
            )
        ).all()
        
        if not results:
            return {"bins": [], "counts": [], "total": 0}
        
        rates = np.array([r[0] for r in results])
        
        # 히스토그램 생성
        counts, bin_edges = np.histogram(rates, bins=bins, range=(95.0, 105.0))
        
        histogram_data = []
        for i in range(len(counts)):
            histogram_data.append({
                "range_min": float(bin_edges[i]),
                "range_max": float(bin_edges[i + 1]),
                "count": int(counts[i]),
                "percentage": float(counts[i] / len(rates) * 100)
            })
        
        return {
            "period_days": days,
            "total_count": len(rates),
            "mean_rate": float(np.mean(rates)),
            "median_rate": float(np.median(rates)),
            "std_rate": float(np.std(rates)),
            "histogram": histogram_data
        }
        
    except Exception as e:
        logger.error(f"히스토그램 생성 실패: {e}")
        raise HTTPException(status_code=500, detail="히스토그램 생성 실패")
