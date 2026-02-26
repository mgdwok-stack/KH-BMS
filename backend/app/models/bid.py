"""
입찰공고 정보 모델 (Bid Announcement Model)
조달청 API의 getDataSetOpnStdBidPblancInfo 데이터 저장
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Float, Text, Index
from sqlalchemy.sql import func
from ..database import Base


class BidAnnouncement(Base):
    """
    입찰공고 정보 테이블
    """
    __tablename__ = "bid_announcements"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 공고 식별 정보
    bid_ntce_no = Column(String(50), unique=True, nullable=False, index=True, comment="입찰공고번호")
    bid_ntce_ord = Column(String(10), comment="입찰공고차수")
    
    # 입찰 기본 정보
    bid_ntce_nm = Column(String(500), nullable=False, comment="입찰공고명")
    instt_cd = Column(String(50), comment="기관코드")
    instt_nm = Column(String(200), index=True, comment="공고기관명")
    dminstt_cd = Column(String(50), comment="수요기관코드")
    dminstt_nm = Column(String(200), comment="수요기관명")
    
    # 입찰 방식
    bid_methd_nm = Column(String(100), index=True, comment="입찰방식명")
    cntrct_cnclsn_methd_nm = Column(String(100), comment="계약체결방법명")
    
    # 금액 정보 (원화, 단위: 원)
    presmpt_prce = Column(BigInteger, comment="추정가격")
    basis_prce = Column(BigInteger, index=True, comment="기초금액")
    
    # 예가 범위 (사정률 계산에 중요)
    prdprc_rate = Column(Float, comment="예정가격 범위 비율 (예: 0.02 = ±2%)")
    
    # 입찰 일정
    bid_qlfct_rgst_dt = Column(DateTime, comment="입찰참가자격등록 마감일시")
    bid_begdt = Column(DateTime, comment="입찰서제출 시작일시")
    bid_clsedt = Column(DateTime, index=True, comment="입찰서제출 마감일시")
    opengdt = Column(DateTime, comment="개찰일시")
    
    # 지역 정보
    rgn_cd = Column(String(50), comment="지역코드")
    rgn_nm = Column(String(100), index=True, comment="지역명")
    
    # 업종 정보
    induty_ty_cd = Column(String(50), comment="업종유형코드")
    induty_ty_nm = Column(String(200), index=True, comment="업종유형명")
    
    # 제한 정보
    lcns_nm = Column(String(500), comment="면허명")
    
    # 상세 정보
    bid_notice_dtl_url = Column(Text, comment="입찰공고 상세 URL")
    
    # 입찰자 수 정보 (개찰 후 업데이트)
    bidder_count = Column(Integer, default=0, comment="투찰자 수")
    
    # 상태 정보
    bid_status = Column(
        String(20),
        default="announced",
        index=True,
        comment="입찰상태 (announced: 공고중, opened: 개찰완료, cancelled: 취소)"
    )
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일시"
    )
    
    # Indexes for query optimization
    __table_args__ = (
        Index('idx_instt_bid_date', 'instt_nm', 'bid_clsedt'),
        Index('idx_rgn_induty', 'rgn_nm', 'induty_ty_nm'),
        Index('idx_status_date', 'bid_status', 'created_at'),
    )

    def __repr__(self):
        return f"<BidAnnouncement(id={self.id}, bid_ntce_no={self.bid_ntce_no}, bid_ntce_nm={self.bid_ntce_nm})>"
