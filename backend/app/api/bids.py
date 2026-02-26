"""
입찰 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import logging

from ..database import get_db
from ..models.bid import BidAnnouncement
from ..models.result import BidResult
from ..schemas.bid import (
    BidAnnouncementResponse,
    BidResultResponse,
    BidListResponse,
    BidDetailResponse
)
from ..services.predictor import PredictorService
from ..services.data_processor import DataProcessor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=BidListResponse)
def get_bid_announcements(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(50, ge=1, le=200, description="페이지 크기"),
    status: Optional[str] = Query(None, description="입찰상태 (announced, opened)"),
    instt_nm: Optional[str] = Query(None, description="공고기관명 (부분 검색)"),
    rgn_nm: Optional[str] = Query(None, description="지역명"),
    induty_ty_nm: Optional[str] = Query(None, description="업종명"),
    min_basis_price: Optional[int] = Query(None, description="최소 기초금액"),
    max_basis_price: Optional[int] = Query(None, description="최대 기초금액"),
    db: Session = Depends(get_db)
):
    """
    입찰공고 목록 조회
    
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지 크기 (기본값: 50, 최대: 200)
    - **status**: 입찰상태 필터
    - **instt_nm**: 공고기관명 필터 (부분 검색)
    - **rgn_nm**: 지역명 필터
    - **induty_ty_nm**: 업종명 필터
    - **min_basis_price**: 최소 기초금액
    - **max_basis_price**: 최대 기초금액
    """
    try:
        # 필터 조건 구성
        filters = []
        
        if status:
            filters.append(BidAnnouncement.bid_status == status)
        
        if instt_nm:
            filters.append(BidAnnouncement.instt_nm.like(f"%{instt_nm}%"))
        
        if rgn_nm:
            filters.append(BidAnnouncement.rgn_nm == rgn_nm)
        
        if induty_ty_nm:
            filters.append(BidAnnouncement.induty_ty_nm.like(f"%{induty_ty_nm}%"))
        
        if min_basis_price:
            filters.append(BidAnnouncement.basis_prce >= min_basis_price)
        
        if max_basis_price:
            filters.append(BidAnnouncement.basis_prce <= max_basis_price)
        
        # 총 개수 조회
        query = db.query(BidAnnouncement)
        if filters:
            query = query.filter(and_(*filters))
        
        total = query.count()
        
        # 페이지네이션
        offset = (page - 1) * page_size
        items = query.order_by(
            BidAnnouncement.created_at.desc()
        ).offset(offset).limit(page_size).all()
        
        return BidListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[BidAnnouncementResponse.from_orm(item) for item in items]
        )
        
    except Exception as e:
        logger.error(f"입찰공고 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="입찰공고 목록 조회 실패")


@router.get("/{bid_id}", response_model=BidDetailResponse)
def get_bid_detail(
    bid_id: int,
    include_prediction: bool = Query(True, description="AI 예측 포함 여부"),
    db: Session = Depends(get_db)
):
    """
    입찰공고 상세 조회 (AI 예측 포함)
    
    - **bid_id**: 입찰공고 ID
    - **include_prediction**: AI 예측 결과 포함 여부 (기본값: True)
    """
    try:
        # 입찰공고 조회
        announcement = db.query(BidAnnouncement).filter(
            BidAnnouncement.id == bid_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="입찰공고를 찾을 수 없습니다")
        
        # AI 예측 실행
        prediction = None
        if include_prediction and announcement.basis_prce:
            try:
                predictor = PredictorService(db)
                prediction = predictor.predict(
                    announcement,
                    use_historical=True,
                    save_prediction=True
                )
            except Exception as e:
                logger.warning(f"AI 예측 실패: {e}")
        
        # 유사 케이스 조회
        processor = DataProcessor(db)
        similar_cases_raw = processor._find_similar_cases(announcement, 365, 10)
        similar_cases = [BidResultResponse.from_orm(case) for case in similar_cases_raw]
        
        # 발주기관 통계
        historical_stats = None
        if announcement.instt_nm:
            stats = processor._get_institution_statistics(announcement.instt_nm, 365)
            if stats['instt_historical_count'] > 0:
                historical_stats = stats
        
        return BidDetailResponse(
            announcement=BidAnnouncementResponse.from_orm(announcement),
            prediction=prediction,
            similar_cases=similar_cases,
            historical_stats=historical_stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"입찰공고 상세 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="입찰공고 상세 조회 실패")


@router.get("/search/filters")
def get_filter_options(db: Session = Depends(get_db)):
    """
    필터 옵션 조회 (지역, 업종, 발주기관 목록)
    """
    try:
        from sqlalchemy import func, distinct
        
        # 지역 목록
        regions = db.query(
            BidAnnouncement.rgn_nm,
            func.count(BidAnnouncement.id).label('count')
        ).filter(
            BidAnnouncement.rgn_nm.isnot(None)
        ).group_by(BidAnnouncement.rgn_nm).all()
        
        # 업종 목록
        industries = db.query(
            BidAnnouncement.induty_ty_nm,
            func.count(BidAnnouncement.id).label('count')
        ).filter(
            BidAnnouncement.induty_ty_nm.isnot(None)
        ).group_by(BidAnnouncement.induty_ty_nm).limit(50).all()
        
        # 발주기관 목록 (상위 50개)
        institutions = db.query(
            BidAnnouncement.instt_nm,
            func.count(BidAnnouncement.id).label('count')
        ).filter(
            BidAnnouncement.instt_nm.isnot(None)
        ).group_by(BidAnnouncement.instt_nm).order_by(
            func.count(BidAnnouncement.id).desc()
        ).limit(50).all()
        
        return {
            "regions": [{"name": r[0], "count": r[1]} for r in regions],
            "industries": [{"name": i[0], "count": i[1]} for i in industries],
            "institutions": [{"name": inst[0], "count": inst[1]} for inst in institutions]
        }
        
    except Exception as e:
        logger.error(f"필터 옵션 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="필터 옵션 조회 실패")


@router.get("/results/", response_model=List[BidResultResponse])
def get_bid_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    instt_nm: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    낙찰결과 목록 조회
    """
    try:
        query = db.query(BidResult)
        
        if instt_nm:
            query = query.filter(BidResult.instt_nm.like(f"%{instt_nm}%"))
        
        offset = (page - 1) * page_size
        results = query.order_by(
            BidResult.opengdt.desc()
        ).offset(offset).limit(page_size).all()
        
        return [BidResultResponse.from_orm(r) for r in results]
        
    except Exception as e:
        logger.error(f"낙찰결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="낙찰결과 조회 실패")
