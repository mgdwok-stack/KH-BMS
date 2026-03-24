"""
Database models for Bid-Bot Clone
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class BidAnnouncement(Base):
    """입찰공고 정보"""
    __tablename__ = 'bid_announcements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bid_ntce_no = Column(String(50), unique=True, nullable=False, comment='입찰공고번호')
    bid_ntce_nm = Column(String(500), comment='입찰공고명')
    ntce_instt_nm = Column(String(200), comment='공고기관명')
    dminstt_nm = Column(String(100), comment='수요기관명/지역')
    industry_ty_nm = Column(String(100), comment='업종명')
    ntce_dt = Column(String(20), comment='공고일시')
    bid_clse_dt = Column(String(20), comment='입찰마감일시')
    opng_dt = Column(String(20), comment='개찰일시')
    basis_prc = Column(Float, comment='기초금액')
    bid_status = Column(String(20), default='진행중', comment='입찰상태')
    raw_data = Column(JSON, comment='원본 API 데이터')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    results = relationship("BidResult", back_populates="announcement")
    predictions = relationship("Prediction", back_populates="announcement")
    
    # Indexes
    __table_args__ = (
        Index('idx_bid_ntce_no', 'bid_ntce_no'),
        Index('idx_ntce_dt', 'ntce_dt'),
        Index('idx_bid_status', 'bid_status'),
        Index('idx_dminstt_nm', 'dminstt_nm'),
        Index('idx_industry_ty_nm', 'industry_ty_nm'),
    )

class BidResult(Base):
    """낙찰결과 정보"""
    __tablename__ = 'bid_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bid_ntce_no = Column(String(50), ForeignKey('bid_announcements.bid_ntce_no'), unique=True, nullable=False)
    opng_dt = Column(String(20), comment='개찰일시')
    prdprc_rate = Column(Float, comment='예가율(사정률)')
    prdprc = Column(Float, comment='예정가격')
    sucbid_prc = Column(Float, comment='낙찰금액')
    sucbid_rate = Column(Float, comment='낙찰율')
    bidprc_plnprc = Column(Float, comment='투찰금액')
    raw_data = Column(JSON, comment='원본 API 데이터')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    announcement = relationship("BidAnnouncement", back_populates="results")
    
    # Indexes
    __table_args__ = (
        Index('idx_result_bid_ntce_no', 'bid_ntce_no'),
        Index('idx_opng_dt', 'opng_dt'),
        Index('idx_prdprc_rate', 'prdprc_rate'),
    )

class Prediction(Base):
    """AI 예측 결과"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bid_ntce_no = Column(String(50), ForeignKey('bid_announcements.bid_ntce_no'), nullable=False)
    
    # DNBP Model Results
    dnbp_predicted_rate = Column(Float, comment='DNBP 예측 사정률')
    dnbp_confidence = Column(Float, comment='DNBP 신뢰도')
    
    # LSTM Model Results
    lstm_predicted_rate = Column(Float, comment='LSTM 예측 사정률')
    lstm_confidence = Column(Float, comment='LSTM 신뢰도')
    
    # Ensemble Results
    final_predicted_rate = Column(Float, comment='최종 예측 사정률')
    predicted_prdprc = Column(Float, comment='예측 예정가격')
    recommended_bid_amt = Column(Float, comment='권장 투찰금액')
    prediction_range_min = Column(Float, comment='예측 하한')
    prediction_range_max = Column(Float, comment='예측 상한')
    confidence_score = Column(Float, comment='종합 신뢰도')
    
    # Accuracy Tracking
    actual_prdprc_rate = Column(Float, comment='실제 사정률')
    prediction_error = Column(Float, comment='예측 오차')
    
    # Status
    status = Column(String(20), default='pending', comment='예측상태: pending/validated')
    predicted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    announcement = relationship("BidAnnouncement", back_populates="predictions")
    
    # Indexes
    __table_args__ = (
        Index('idx_pred_bid_ntce_no', 'bid_ntce_no'),
        Index('idx_predicted_at', 'predicted_at'),
        Index('idx_status', 'status'),
    )

class UserPreference(Base):
    """사용자 설정"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False)
    favorite_regions = Column(JSON, comment='관심 지역')
    favorite_industries = Column(JSON, comment='관심 업종')
    price_range_min = Column(Float, comment='관심 금액 최소')
    price_range_max = Column(Float, comment='관심 금액 최대')
    notification_enabled = Column(Integer, default=1, comment='알림 활성화')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
