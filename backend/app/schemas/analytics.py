"""
분석/통계 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class TrendDataPoint(BaseModel):
    """트렌드 데이터 포인트"""
    date: datetime = Field(..., description="날짜")
    avg_rate: float = Field(..., description="평균 사정률")
    count: int = Field(..., description="건수")


class TrendResponse(BaseModel):
    """트렌드 응답"""
    period: str = Field(..., description="기간 (예: 2024-01)")
    data: List[TrendDataPoint] = Field(..., description="트렌드 데이터")


class InstitutionStatsItem(BaseModel):
    """발주기관 통계 항목"""
    instt_nm: str = Field(..., description="기관명")
    total_count: int = Field(..., description="총 건수")
    avg_rate: float = Field(..., description="평균 사정률")
    std_rate: float = Field(..., description="표준편차")
    min_rate: float = Field(..., description="최소 사정률")
    max_rate: float = Field(..., description="최대 사정률")


class RegionStatsItem(BaseModel):
    """지역별 통계 항목"""
    rgn_nm: str = Field(..., description="지역명")
    total_count: int = Field(..., description="총 건수")
    avg_rate: float = Field(..., description="평균 사정률")
    avg_basis_price: int = Field(..., description="평균 기초금액")


class IndustryStatsItem(BaseModel):
    """업종별 통계 항목"""
    induty_ty_nm: str = Field(..., description="업종명")
    total_count: int = Field(..., description="총 건수")
    avg_rate: float = Field(..., description="평균 사정률")


class AnalyticsResponse(BaseModel):
    """종합 분석 응답"""
    summary: Dict[str, any] = Field(..., description="요약 통계")
    top_institutions: List[InstitutionStatsItem] = Field(..., description="상위 발주기관")
    top_regions: List[RegionStatsItem] = Field(..., description="상위 지역")
    top_industries: List[IndustryStatsItem] = Field(..., description="상위 업종")
    recent_trends: List[TrendDataPoint] = Field(..., description="최근 트렌드")


class RateDistributionResponse(BaseModel):
    """사정률 분포 응답"""
    bins: List[str] = Field(..., description="구간 (예: 95-96)")
    counts: List[int] = Field(..., description="건수")
    percentages: List[float] = Field(..., description="비율 (%)")
