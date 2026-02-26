"""
조달청 API 연동 테스트 스크립트
"""
import sys
import os
import asyncio

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.services.data_collector import DataCollector
from app.services.data_processor import DataProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_bid_announcements():
    """
    입찰공고 API 테스트
    """
    logger.info("=== 입찰공고 API 테스트 ===")
    
    db = SessionLocal()
    try:
        collector = DataCollector(db)
        
        # 최근 10일간 데이터 조회
        from datetime import datetime, timedelta
        start_date = datetime.now().strftime("%Y%m%d")
        end_date = (datetime.now() + timedelta(days=10)).strftime("%Y%m%d")
        
        logger.info(f"조회 기간: {start_date} ~ {end_date}")
        
        items = await collector.collect_bid_announcements(
            start_date=start_date,
            end_date=end_date,
            page=1,
            num_of_rows=10
        )
        
        logger.info(f"수집된 공고 수: {len(items)}건")
        
        if items:
            logger.info("첫 번째 공고 샘플:")
            first_item = items[0]
            logger.info(f"  - 공고번호: {first_item.get('bidNtceNo')}")
            logger.info(f"  - 공고명: {first_item.get('bidNtceNm')}")
            logger.info(f"  - 기관명: {first_item.get('insttNm')}")
            logger.info(f"  - 기초금액: {first_item.get('basisPrce')}")
            
            # DB 저장 테스트
            logger.info("\nDB 저장 테스트...")
            saved = collector.save_bid_announcement(first_item)
            if saved:
                logger.info(f"✅ 저장 성공: ID={saved.id}")
            else:
                logger.error("❌ 저장 실패")
        
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
    finally:
        db.close()


async def test_bid_results():
    """
    낙찰결과 API 테스트
    """
    logger.info("\n=== 낙찰결과 API 테스트 ===")
    
    db = SessionLocal()
    try:
        collector = DataCollector(db)
        
        # 최근 30일간 데이터 조회
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        end_date = datetime.now().strftime("%Y%m%d")
        
        logger.info(f"조회 기간: {start_date} ~ {end_date}")
        
        items = await collector.collect_bid_results(
            start_date=start_date,
            end_date=end_date,
            page=1,
            num_of_rows=10
        )
        
        logger.info(f"수집된 낙찰 수: {len(items)}건")
        
        if items:
            logger.info("첫 번째 낙찰 샘플:")
            first_item = items[0]
            logger.info(f"  - 공고번호: {first_item.get('bidNtceNo')}")
            logger.info(f"  - 기관명: {first_item.get('insttNm')}")
            logger.info(f"  - 기초금액: {first_item.get('basisPrce')}")
            logger.info(f"  - 예정가격: {first_item.get('prdprc')}")
            logger.info(f"  - 사정률: {first_item.get('prdprcRate')}")
            logger.info(f"  - 낙찰금액: {first_item.get('sucsfbidAmt')}")
            
            # DB 저장 테스트
            logger.info("\nDB 저장 테스트...")
            saved = collector.save_bid_result(first_item)
            if saved:
                logger.info(f"✅ 저장 성공: ID={saved.id}")
            else:
                logger.error("❌ 저장 실패")
        
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
    finally:
        db.close()


def test_data_processor():
    """
    데이터 전처리 테스트
    """
    logger.info("\n=== 데이터 전처리 테스트 ===")
    
    db = SessionLocal()
    try:
        processor = DataProcessor(db)
        
        # 학습 데이터 생성 테스트
        logger.info("학습 데이터 생성 중...")
        df = processor.get_training_data()
        
        if not df.empty:
            logger.info(f"✅ 학습 데이터 생성 완료: {len(df)}건")
            logger.info(f"컬럼: {list(df.columns)}")
            logger.info(f"\n데이터 샘플:\n{df.head()}")
            
            # 통계 정보
            logger.info(f"\n사정률 통계:")
            logger.info(f"  - 평균: {df['prdprc_rate'].mean():.2f}%")
            logger.info(f"  - 최소: {df['prdprc_rate'].min():.2f}%")
            logger.info(f"  - 최대: {df['prdprc_rate'].max():.2f}%")
            logger.info(f"  - 표준편차: {df['prdprc_rate'].std():.2f}%")
        else:
            logger.warning("⚠️  학습 데이터가 없습니다. 먼저 데이터를 수집해주세요.")
        
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
    finally:
        db.close()


async def main():
    """
    모든 테스트 실행
    """
    logger.info("=" * 60)
    logger.info("조달청 API 연동 및 데이터 파이프라인 테스트")
    logger.info("=" * 60)
    
    # 1. 입찰공고 API 테스트
    await test_bid_announcements()
    
    # 2. 낙찰결과 API 테스트
    await test_bid_results()
    
    # 3. 데이터 전처리 테스트
    test_data_processor()
    
    logger.info("\n" + "=" * 60)
    logger.info("테스트 완료!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
