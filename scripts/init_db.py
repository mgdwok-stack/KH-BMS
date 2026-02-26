"""
데이터베이스 초기화 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import Base, engine, init_db
from app.models import BidAnnouncement, BidResult, Prediction, UserPreference
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    데이터베이스 테이블 생성
    """
    logger.info("=== 데이터베이스 초기화 시작 ===")
    
    try:
        # 모든 테이블 생성
        logger.info("데이터베이스 테이블 생성 중...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ 데이터베이스 초기화 완료!")
        logger.info("생성된 테이블:")
        logger.info("  - bid_announcements (입찰공고)")
        logger.info("  - bid_results (낙찰결과)")
        logger.info("  - predictions (AI 예측)")
        logger.info("  - user_preferences (사용자 설정)")
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
