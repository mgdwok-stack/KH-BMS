"""
AI 예측 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ..database import get_db
from ..models.bid import BidAnnouncement
from ..models.prediction import Prediction
from ..schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionListResponse,
    PredictionStatsResponse
)
from ..services.predictor import PredictorService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict_bid_rate(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """
    입찰공고에 대한 사정률 및 투찰금액 예측
    
    - **bid_announcement_id**: 입찰공고 ID
    - **use_historical**: 과거 데이터 사용 여부 (LSTM 모델 활성화)
    - **save_prediction**: 예측 결과 DB 저장 여부
    
    Returns:
    - 최종 예측 사정률
    - 예측 예정가격
    - 추천 투찰금액
    - DNBP/LSTM 개별 예측 결과
    - 예측 범위 (신뢰구간)
    - 통계 정보
    """
    try:
        # 입찰공고 조회
        announcement = db.query(BidAnnouncement).filter(
            BidAnnouncement.id == request.bid_announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="입찰공고를 찾을 수 없습니다")
        
        if not announcement.basis_prce or announcement.basis_prce <= 0:
            raise HTTPException(status_code=400, detail="유효하지 않은 기초금액입니다")
        
        # AI 예측 실행
        predictor = PredictorService(db)
        prediction = predictor.predict(
            announcement,
            use_historical=request.use_historical,
            save_prediction=request.save_prediction
        )
        
        if not prediction:
            raise HTTPException(status_code=500, detail="AI 예측 실행 실패")
        
        return PredictionResponse(**prediction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"예측 실행 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"예측 실행 중 오류 발생: {str(e)}")


@router.get("/{prediction_id}")
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    """
    예측 결과 조회
    
    - **prediction_id**: 예측 ID
    """
    try:
        prediction = db.query(Prediction).filter(
            Prediction.id == prediction_id
        ).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="예측 결과를 찾을 수 없습니다")
        
        return {
            "id": prediction.id,
            "bid_ntce_no": prediction.bid_ntce_no,
            "basis_prce": prediction.basis_prce,
            "final_predicted_rate": prediction.final_predicted_rate,
            "predicted_prdprc": prediction.predicted_prdprc,
            "recommended_bid_amt": prediction.recommended_bid_amt,
            "recommended_bid_rate": prediction.recommended_bid_rate,
            "dnbp_predicted_rate": prediction.dnbp_predicted_rate,
            "dnbp_confidence": prediction.dnbp_confidence,
            "lstm_predicted_rate": prediction.lstm_predicted_rate,
            "lstm_confidence": prediction.lstm_confidence,
            "prediction_range_min": prediction.prediction_range_min,
            "prediction_range_max": prediction.prediction_range_max,
            "actual_prdprc_rate": prediction.actual_prdprc_rate,
            "prediction_error": prediction.prediction_error,
            "prediction_status": prediction.prediction_status,
            "predicted_at": prediction.predicted_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"예측 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="예측 조회 실패")


@router.get("/", response_model=PredictionListResponse)
def get_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, description="예측상태 (predicted, validated)"),
    db: Session = Depends(get_db)
):
    """
    예측 목록 조회
    
    - **page**: 페이지 번호
    - **page_size**: 페이지 크기
    - **status**: 예측 상태 필터
    """
    try:
        query = db.query(Prediction)
        
        if status:
            query = query.filter(Prediction.prediction_status == status)
        
        total = query.count()
        
        offset = (page - 1) * page_size
        predictions = query.order_by(
            Prediction.predicted_at.desc()
        ).offset(offset).limit(page_size).all()
        
        items = []
        for pred in predictions:
            items.append({
                "id": pred.id,
                "bid_ntce_no": pred.bid_ntce_no,
                "final_predicted_rate": pred.final_predicted_rate,
                "recommended_bid_amt": pred.recommended_bid_amt,
                "actual_prdprc_rate": pred.actual_prdprc_rate,
                "prediction_error": pred.prediction_error,
                "prediction_status": pred.prediction_status,
                "predicted_at": pred.predicted_at
            })
        
        return PredictionListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )
        
    except Exception as e:
        logger.error(f"예측 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="예측 목록 조회 실패")


@router.get("/stats/summary", response_model=PredictionStatsResponse)
def get_prediction_stats(db: Session = Depends(get_db)):
    """
    예측 통계 조회
    
    Returns:
    - 총 예측 수
    - 검증된 예측 수
    - 평균 오차
    - 최대 오차
    - 평균 신뢰도
    """
    try:
        predictor = PredictorService(db)
        stats = predictor.get_prediction_statistics()
        
        return PredictionStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"예측 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="예측 통계 조회 실패")


@router.put("/{prediction_id}/accuracy")
def update_prediction_accuracy(
    prediction_id: int,
    actual_rate: float = Query(..., description="실제 사정률"),
    db: Session = Depends(get_db)
):
    """
    예측 정확도 업데이트 (개찰 후)
    
    - **prediction_id**: 예측 ID
    - **actual_rate**: 실제 사정률
    """
    try:
        predictor = PredictorService(db)
        predictor.update_prediction_accuracy(prediction_id, actual_rate)
        
        return {
            "message": "예측 정확도 업데이트 완료",
            "prediction_id": prediction_id,
            "actual_rate": actual_rate
        }
        
    except Exception as e:
        logger.error(f"예측 정확도 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail="예측 정확도 업데이트 실패")


@router.get("/accuracy/report")
def get_accuracy_report(
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    예측 정확도 리포트
    
    - **days**: 조회 기간 (기본값: 30일)
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, and_
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 기간 내 검증된 예측
        validated = db.query(Prediction).filter(
            and_(
                Prediction.prediction_status == 'validated',
                Prediction.predicted_at >= start_date
            )
        ).all()
        
        if not validated:
            return {
                "period_days": days,
                "validated_count": 0,
                "message": "검증된 예측이 없습니다"
            }
        
        errors = [p.prediction_error for p in validated if p.prediction_error is not None]
        
        import numpy as np
        
        report = {
            "period_days": days,
            "validated_count": len(validated),
            "avg_error": float(np.mean(errors)),
            "median_error": float(np.median(errors)),
            "std_error": float(np.std(errors)),
            "min_error": float(np.min(errors)),
            "max_error": float(np.max(errors)),
            "accuracy_within_01pct": sum(1 for e in errors if e <= 0.1) / len(errors) * 100,
            "accuracy_within_02pct": sum(1 for e in errors if e <= 0.2) / len(errors) * 100,
            "accuracy_within_05pct": sum(1 for e in errors if e <= 0.5) / len(errors) * 100
        }
        
        return report
        
    except Exception as e:
        logger.error(f"정확도 리포트 생성 실패: {e}")
        raise HTTPException(status_code=500, detail="정확도 리포트 생성 실패")
