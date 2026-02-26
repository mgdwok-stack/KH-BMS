"""
낙찰결과 정보 모델 (Bid Result Model)
조달청 API의 getDataSetOpnStdScsbidInfo 데이터 저장
AI 모델 학습의 핵심 데이터셋
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Float, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class BidResult(Base):
    """
    낙찰결과 정보 테이블
    """
    __tablename__ = "bid_results"

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
    
    # 공고 식별 정보 (중복 저장하여 조회 성능 향상)
    bid_ntce_no = Column(String(50), nullable=False, index=True, comment="입찰공고번호")
    bid_ntce_ord = Column(String(10), comment="입찰공고차수")
    
    # 낙찰자 정보
    bsnm_bddpr_nm = Column(String(200), comment="낙찰자(사업자명)")
    bddpr_corp_no = Column(String(50), comment="낙찰자 법인번호")
    
    # 금액 정보 (AI 예측의 핵심 데이터)
    prdprc = Column(BigInteger, nullable=False, index=True, comment="예정가격 (원)")
    basis_prce = Column(BigInteger, nullable=False, comment="기초금액 (원)")
    presmpt_prce = Column(BigInteger, comment="추정가격 (원)")
    
    # 낙찰 금액
    sucsfbid_amt = Column(BigInteger, nullable=False, index=True, comment="낙찰금액 (원)")
    
    # 사정률 (AI 모델의 예측 타겟)
    # 사정률 = 예정가격 / 기초금액 * 100
    prdprc_rate = Column(
        Float,
        nullable=False,
        index=True,
        comment="예정가격 사정률 (예: 99.52)"
    )
    
    # 투찰률 (낙찰하한율)
    # 투찰률 = 낙찰금액 / 예정가격 * 100
    sucsfbid_rate = Column(
        Float,
        nullable=False,
        index=True,
        comment="투찰률/낙찰하한율 (예: 87.745)"
    )
    
    # 실제 낙찰하한가
    # 낙찰하한가 = 예정가격 * (낙찰하한율 / 100)
    sucsfbid_lwltrate = Column(Float, comment="낙찰하한율 (%)")
    
    # 투찰자 정보
    bidder_count = Column(Integer, default=0, comment="총 투찰자 수")
    
    # 복수예비가격 관련 (DNBP 모델 학습용)
    # 실제 추첨된 4개의 예비가격 번호 (1~15번 중)
    drawn_reserve_prices = Column(String(50), comment="추첨된 예비가격 번호 (예: 3,7,11,14)")
    
    # 개찰 일시
    opengdt = Column(DateTime, nullable=False, index=True, comment="개찰일시")
    
    # 지역 및 업종 (분석용 중복 저장)
    rgn_nm = Column(String(100), index=True, comment="지역명")
    induty_ty_nm = Column(String(200), index=True, comment="업종유형명")
    
    # 발주기관 (패턴 분석용)
    instt_nm = Column(String(200), index=True, comment="공고기관명")
    dminstt_nm = Column(String(200), comment="수요기관명")
    
    # 입찰 방식
    bid_methd_nm = Column(String(100), comment="입찰방식명")
    
    # 비고
    remarks = Column(Text, comment="비고사항")
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일시"
    )
    
    # Relationship
    bid_announcement = relationship("BidAnnouncement", backref="results")
    
    # Indexes for AI model training queries
    __table_args__ = (
        Index('idx_instt_opengdt', 'instt_nm', 'opengdt'),
        Index('idx_rgn_induty_date', 'rgn_nm', 'induty_ty_nm', 'opengdt'),
        Index('idx_rate_analysis', 'prdprc_rate', 'sucsfbid_rate', 'opengdt'),
        Index('idx_price_range', 'basis_prce', 'prdprc', 'sucsfbid_amt'),
    )

    def __repr__(self):
        return f"<BidResult(id={self.id}, bid_ntce_no={self.bid_ntce_no}, prdprc_rate={self.prdprc_rate})>"
    
    @property
    def calculated_prdprc_rate(self) -> float:
        """
        예정가격 사정률 계산
        """
        if self.basis_prce and self.prdprc:
            return round((self.prdprc / self.basis_prce) * 100, 4)
        return 0.0
    
    @property
    def calculated_sucsfbid_rate(self) -> float:
        """
        투찰률 계산
        """
        if self.prdprc and self.sucsfbid_amt:
            return round((self.sucsfbid_amt / self.prdprc) * 100, 4)
        return 0.0
