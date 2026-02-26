"""
입찰 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class BidAnnouncementResponse(BaseModel):
    """입찰공고 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    bid_ntce_no: str
    bid_ntce_ord: Optional[int] = None
    bid_ntce_nm: Optional[str] = None
    instt_nm: Optional[str] = None
    dminstt_nm: Optional[str] = None
    rgn_nm: Optional[str] = None
    induty_ty_nm: Optional[str] = None
    cntrct_cnclsmt_mth_nm: Optional[str] = None
    bid_mthd_nm: Optional[str] = None
    presmpt_prce: Optional[int] = None
    basis_prce: Optional[int] = None
    asign_bdgt_amt: Optional[int] = None
    bid_begin_dt: Optional[datetime] = None
    bid_close_dt: Optional[datetime] = None
    openg_dt: Optional[datetime] = None
    bid_status: Optional[str] = None
    ntce_instt_cd: Optional[str] = None
    rbid_perm_yn: Optional[str] = None
    srch_value: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BidResultResponse(BaseModel):
    """낙찰결과 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    bid_ntce_no: str
    bid_ntce_ord: Optional[int] = None
    instt_nm: Optional[str] = None
    dminstt_nm: Optional[str] = None
    presmpt_prce: Optional[int] = None
    openg_dt: Optional[datetime] = None
    opengcorpinfo: Optional[str] = None
    bidprc: Optional[int] = None
    sucsfbid_amt: Optional[int] = None
    sucsfbid_rate: Optional[float] = None
    prdprc: Optional[int] = None
    prdprc_rate: Optional[float] = None
    sucsfbid_lwr_lmt_rt: Optional[float] = None
    d2b_mgt_dminstt_sns_mth_yr: Optional[str] = None
    d2b_mgt_dminstt_sns_mth_no: Optional[str] = None
    d2b_mgt_org_dgstfnc_no: Optional[str] = None
    d2b_mgt_ngttn_stmt_no: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BidListResponse(BaseModel):
    """입찰공고 목록 응답 스키마"""
    total: int = Field(description="전체 개수")
    page: int = Field(description="현재 페이지")
    page_size: int = Field(description="페이지 크기")
    items: List[BidAnnouncementResponse] = Field(description="입찰공고 목록")


class BidDetailResponse(BaseModel):
    """입찰공고 상세 응답 스키마 (AI 예측 포함)"""
    announcement: BidAnnouncementResponse
    prediction: Optional[Dict[str, Any]] = None
    similar_cases: List[BidResultResponse] = []
    historical_stats: Optional[Dict[str, Any]] = None
