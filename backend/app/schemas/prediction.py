"""
AI 예측 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    """예측 요청 스키마"""
    bid_announcement_id: int = Field(description="입찰공고 ID")
    use_historical: bool = Field(default=True, description="과거 데이터 사용 여부 (LSTM 활성화)")
    save_prediction: bool = Field(default=True, description="예측 결과 DB 저장 여부")


class PredictionResponse(BaseModel):
    """예측 응답 스키마"""
    bid_ntce_no: str = Field(description="입찰공고번호")
    basis_prce: int = Field(description="기초금액")
    
    # 최종 예측 결과
    final_predicted_rate: float = Field(description="최종 예측 사정률 (%)")
    predicted_prdprc: int = Field(description="예측 예정가격 (원)")
    recommended_bid_amt: int = Field(description="추천 투찰금액 (원)")
    recommended_bid_rate: float = Field(description="추천 투찰비율 (%)")
    
    # DNBP 예측 결과
    dnbp_predicted_rate: Optional[float] = Field(None, description="DNBP 예측 사정률 (%)")
    dnbp_confidence: Optional[float] = Field(None, description="DNBP 신뢰도")
    dnbp_top4_rates: Optional[List[float]] = Field(None, description="DNBP Top-4 사정률")
    
    # LSTM 예측 결과
    lstm_predicted_rate: Optional[float] = Field(None, description="LSTM 예측 사정률 (%)")
    lstm_confidence: Optional[float] = Field(None, description="LSTM 신뢰도")
    
    # 예측 범위 (신뢰구간)
    prediction_range_min: float = Field(description="예측 하한 (%)")
    prediction_range_max: float = Field(description="예측 상한 (%)")
    
    # 통계 정보
    similar_cases_count: Optional[int] = Field(None, description="유사 케이스 수")
    institution_avg_rate: Optional[float] = Field(None, description="발주기관 평균 사정률 (%)")
    region_avg_rate: Optional[float] = Field(None, description="지역 평균 사정률 (%)")
    
    # 예측 메타데이터
    model_version: Optional[str] = Field(None, description="모델 버전")
    prediction_timestamp: Optional[datetime] = Field(None, description="예측 시간")


class PredictionListItem(BaseModel):
    """예측 목록 아이템 스키마"""
    id: int
    bid_ntce_no: str
    final_predicted_rate: float
    recommended_bid_amt: int
    actual_prdprc_rate: Optional[float] = None
    prediction_error: Optional[float] = None
    prediction_status: str
    predicted_at: datetime


class PredictionListResponse(BaseModel):
    """예측 목록 응답 스키마"""
    total: int = Field(description="전체 개수")
    page: int = Field(description="현재 페이지")
    page_size: int = Field(description="페이지 크기")
    items: List[PredictionListItem] = Field(description="예측 목록")


class PredictionStatsResponse(BaseModel):
    """예측 통계 응답 스키마"""
    total_predictions: int = Field(description="총 예측 수")
    validated_predictions: int = Field(description="검증된 예측 수")
    avg_prediction_error: Optional[float] = Field(None, description="평균 예측 오차 (%)")
    max_prediction_error: Optional[float] = Field(None, description="최대 예측 오차 (%)")
    avg_confidence: Optional[float] = Field(None, description="평균 신뢰도")
    accuracy_rate: Optional[float] = Field(None, description="정확도 (오차 < 0.1%)")
