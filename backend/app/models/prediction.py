"""
AI 예측 결과 모델 (Prediction Model)
DNBP/LSTM 모델이 생성한 예측 사정률 및 추천 투찰금액 저장
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Float, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Prediction(Base):
    """
    AI 예측 결과 테이블
    """
    __tablename__ = "predictions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key to BidAnnouncement
    bid_announcement_id = Column(
        Integer,
        ForeignKey("bid_announcements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="입찰공고 ID"
    )
    
    # 공고 식별 정보
    bid_ntce_no = Column(String(50), nullable=False, index=True, comment="입찰공고번호")
    
    # 입력 데이터
    basis_prce = Column(BigInteger, nullable=False, comment="기초금액 (원)")
    presmpt_prce = Column(BigInteger, comment="추정가격 (원)")
    
    # DNBP 모델 예측 결과
    dnbp_predicted_rate = Column(
        Float,
        comment="DNBP 모델 예측 사정률 (%)"
    )
    dnbp_top4_rates = Column(
        JSON,
        comment="DNBP 상위 4개 예측 사정률 배열 (예: [99.52, 99.48, 99.56, 99.44])"
    )
    dnbp_confidence = Column(
        Float,
        comment="DNBP 예측 신뢰도 (0~1)"
    )
    
    # LSTM 모델 예측 결과
    lstm_predicted_rate = Column(
        Float,
        comment="LSTM 모델 예측 사정률 (%)"
    )
    lstm_confidence = Column(
        Float,
        comment="LSTM 예측 신뢰도 (0~1)"
    )
    
    # 앙상블 최종 예측 결과
    final_predicted_rate = Column(
        Float,
        nullable=False,
        index=True,
        comment="앙상블 최종 예측 사정률 (%)"
    )
    
    # 추천 투찰 금액 (예정가격 예측값)
    predicted_prdprc = Column(
        BigInteger,
        nullable=False,
        comment="예측 예정가격 (원)"
    )
    
    # 추천 낙찰하한가 (일반적으로 예정가격의 87.745%)
    recommended_bid_amt = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="추천 투찰금액 (원)"
    )
    
    # 낙찰하한율
    recommended_bid_rate = Column(
        Float,
        default=87.745,
        comment="추천 투찰률 (%)"
    )
    
    # 예측 범위 (신뢰구간)
    prediction_range_min = Column(
        Float,
        comment="예측 사정률 최소값 (%)"
    )
    prediction_range_max = Column(
        Float,
        comment="예측 사정률 최대값 (%)"
    )
    
    # 모델 버전 및 메타데이터
    dnbp_model_version = Column(String(50), comment="DNBP 모델 버전")
    lstm_model_version = Column(String(50), comment="LSTM 모델 버전")
    ensemble_weights = Column(
        JSON,
        comment="앙상블 가중치 (예: {'dnbp': 0.6, 'lstm': 0.4})"
    )
    
    # 특징 데이터 (학습 시 사용된 특징)
    features = Column(
        JSON,
        comment="예측에 사용된 특징 데이터"
    )
    
    # 유사 케이스 분석
    similar_cases_count = Column(
        Integer,
        default=0,
        comment="유사 입찰 건수"
    )
    similar_cases_avg_rate = Column(
        Float,
        comment="유사 입찰 평균 사정률 (%)"
    )
    
    # 발주기관 과거 패턴
    instt_historical_avg_rate = Column(
        Float,
        comment="해당 발주기관 과거 평균 사정률 (%)"
    )
    instt_historical_std_rate = Column(
        Float,
        comment="해당 발주기관 과거 사정률 표준편차"
    )
    
    # 예측 정확도 (개찰 후 실제값과 비교)
    actual_prdprc_rate = Column(
        Float,
        comment="실제 사정률 (개찰 후 업데이트)"
    )
    prediction_error = Column(
        Float,
        comment="예측 오차 (|예측값 - 실제값|)"
    )
    
    # 예측 상태
    prediction_status = Column(
        String(20),
        default="predicted",
        index=True,
        comment="예측상태 (predicted: 예측완료, validated: 검증완료)"
    )
    
    # 사용자 정보 (향후 확장)
    user_id = Column(Integer, comment="사용자 ID (향후 구현)")
    
    # 비고
    notes = Column(Text, comment="예측 관련 메모")
    
    # 메타데이터
    predicted_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        comment="예측일시"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일시"
    )
    
    # Relationship
    bid_announcement = relationship("BidAnnouncement", backref="predictions")
    
    # Indexes
    __table_args__ = (
        Index('idx_prediction_accuracy', 'prediction_error', 'predicted_at'),
        Index('idx_status_date', 'prediction_status', 'predicted_at'),
    )

    def __repr__(self):
        return f"<Prediction(id={self.id}, bid_ntce_no={self.bid_ntce_no}, final_rate={self.final_predicted_rate})>"
    
    @property
    def accuracy_percentage(self) -> float:
        """
        예측 정확도 계산 (%)
        """
        if self.actual_prdprc_rate and self.final_predicted_rate:
            error = abs(self.actual_prdprc_rate - self.final_predicted_rate)
            return round(100 - (error / self.actual_prdprc_rate * 100), 2)
        return 0.0
