"""
사용자 설정 모델 (User Preference Model)
사용자별 지역, 업종, 면허 필터링 설정
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Index
from sqlalchemy.sql import func
from ..database import Base


class UserPreference(Base):
    """
    사용자 설정 테이블
    """
    __tablename__ = "user_preferences"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 사용자 식별 (향후 인증 시스템 연동)
    user_id = Column(Integer, unique=True, nullable=False, index=True, comment="사용자 ID")
    username = Column(String(100), unique=True, nullable=False, comment="사용자명")
    email = Column(String(200), unique=True, comment="이메일")
    
    # 필터 설정 - 지역
    preferred_regions = Column(
        JSON,
        comment="선호 지역 리스트 (예: ['서울특별시', '경기도'])"
    )
    
    # 필터 설정 - 업종
    preferred_industries = Column(
        JSON,
        comment="선호 업종 리스트 (예: ['건설', '정보통신'])"
    )
    
    # 필터 설정 - 면허
    licenses = Column(
        JSON,
        comment="보유 면허 리스트 (예: ['건설업 면허', '전기공사업 면허'])"
    )
    
    # 필터 설정 - 금액 범위
    min_basis_price = Column(
        Integer,
        comment="최소 기초금액 (원)"
    )
    max_basis_price = Column(
        Integer,
        comment="최대 기초금액 (원)"
    )
    
    # 입찰 방식 선호
    preferred_bid_methods = Column(
        JSON,
        comment="선호 입찰방식 리스트 (예: ['일반경쟁입찰', '제한경쟁입찰'])"
    )
    
    # 알림 설정
    notification_enabled = Column(
        Boolean,
        default=True,
        comment="알림 활성화 여부"
    )
    notification_email = Column(
        Boolean,
        default=True,
        comment="이메일 알림"
    )
    notification_push = Column(
        Boolean,
        default=False,
        comment="푸시 알림"
    )
    
    # 알림 조건
    notify_days_before_deadline = Column(
        Integer,
        default=3,
        comment="마감 N일 전 알림"
    )
    
    # 대시보드 설정
    dashboard_layout = Column(
        JSON,
        comment="대시보드 레이아웃 설정"
    )
    
    # 즐겨찾기 발주기관
    favorite_institutions = Column(
        JSON,
        comment="즐겨찾기 발주기관 리스트"
    )
    
    # AI 예측 설정
    ai_prediction_enabled = Column(
        Boolean,
        default=True,
        comment="AI 예측 기능 활성화"
    )
    preferred_model = Column(
        String(20),
        default="ensemble",
        comment="선호 모델 (dnbp, lstm, ensemble)"
    )
    
    # 활성화 상태
    is_active = Column(
        Boolean,
        default=True,
        index=True,
        comment="계정 활성화 여부"
    )
    
    # 비고
    notes = Column(Text, comment="메모")
    
    # 메타데이터
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="생성일시"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일시"
    )
    last_login_at = Column(
        DateTime(timezone=True),
        comment="마지막 로그인 일시"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_user_active', 'user_id', 'is_active'),
    )

    def __repr__(self):
        return f"<UserPreference(id={self.id}, username={self.username})>"
