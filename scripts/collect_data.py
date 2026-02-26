"""
수동 데이터 수집 스크립트
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.services.data_collector import DataCollector
from app.services.data_processor import DataProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def collect_recent_data(days_back: int = 30, days_forward: int = 60):
    """
    최근 데이터 수집
    
    Args:
        days_back: 과거 며칠 (낙찰결과용)
        days_forward: 미래 며칠 (입찰공고용)
    """
    logger.info("=== 최근 데이터 수집 시작 ===")
    
    db = SessionLocal()
    try:
        collector = DataCollector(db)
        
        # 1. 입찰공고 수집 (오늘부터 미래)
        logger.info(f"\n1. 입찰공고 수집 (오늘 ~ {days_forward}일 후)")
        start_date = datetime.now().strftime("%Y%m%d")
        end_date = (datetime.now() + timedelta(days=days_forward)).strftime("%Y%m%d")
        
        total_announcements = 0
        for page in range(1, 11):  # 최대 10페이지
            items = await collector.collect_bid_announcements(
                start_date=start_date,
                end_date=end_date,
                page=page,
                num_of_rows=100
            )
            
            if not items:
                break
            
            for item in items:
                try:
                    collector.save_bid_announcement(item)
                    total_announcements += 1
                except Exception as e:
                    logger.error(f"저장 실패: {e}")
            
            logger.info(f"  페이지 {page}: {len(items)}건 수집")
            
            if len(items) < 100:
                break
        
        logger.info(f"✅ 입찰공고 수집 완료: {total_announcements}건")
        
        # 2. 낙찰결과 수집 (과거부터 오늘)
        logger.info(f"\n2. 낙찰결과 수집 ({days_back}일 전 ~ 오늘)")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
        end_date = datetime.now().strftime("%Y%m%d")
        
        total_results = 0
        for page in range(1, 21):  # 최대 20페이지
            items = await collector.collect_bid_results(
                start_date=start_date,
                end_date=end_date,
                page=page,
                num_of_rows=100
            )
            
            if not items:
                break
            
            for item in items:
                try:
                    collector.save_bid_result(item)
                    total_results += 1
                except Exception as e:
                    logger.error(f"저장 실패: {e}")
            
            logger.info(f"  페이지 {page}: {len(items)}건 수집")
            
            if len(items) < 100:
                break
        
        logger.info(f"✅ 낙찰결과 수집 완료: {total_results}건")
        
        # 3. 데이터 정제
        logger.info("\n3. 데이터 정제")
        processor = DataProcessor(db)
        cleaned = processor.clean_bid_results()
        logger.info(f"✅ 데이터 정제 완료: {cleaned}건 처리")
        
        logger.info("\n=== 수집 완료 ===")
        logger.info(f"입찰공고: {total_announcements}건")
        logger.info(f"낙찰결과: {total_results}건")
        
    except Exception as e:
        logger.error(f"❌ 수집 실패: {e}")
    finally:
        db.close()


async def collect_historical_data(start_year: int, end_year: int):
    """
    과거 데이터 대량 수집
    
    Args:
        start_year: 시작 연도
        end_year: 종료 연도
    """
    logger.info(f"=== 과거 데이터 수집: {start_year} ~ {end_year} ===")
    
    db = SessionLocal()
    try:
        collector = DataCollector(db)
        
        for year in range(start_year, end_year + 1):
            logger.info(f"\n{year}년 데이터 수집 중...")
            
            start_date = f"{year}0101"
            end_date = f"{year}1231"
            
            # 낙찰결과만 수집 (과거 데이터는 결과가 중요)
            total_results = 0
            for page in range(1, 51):  # 최대 50페이지
                items = await collector.collect_bid_results(
                    start_date=start_date,
                    end_date=end_date,
                    page=page,
                    num_of_rows=100
                )
                
                if not items:
                    break
                
                for item in items:
                    try:
                        collector.save_bid_result(item)
                        total_results += 1
                    except Exception as e:
                        logger.error(f"저장 실패: {e}")
                
                logger.info(f"  페이지 {page}: {len(items)}건")
                
                if len(items) < 100:
                    break
                
                # API 부하 방지
                await asyncio.sleep(1)
            
            logger.info(f"✅ {year}년 완료: {total_results}건")
        
        logger.info("\n=== 과거 데이터 수집 완료 ===")
        
    except Exception as e:
        logger.error(f"❌ 수집 실패: {e}")
    finally:
        db.close()


async def main():
    """
    메인 실행 함수
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='조달청 데이터 수집')
    parser.add_argument(
        '--mode',
        choices=['recent', 'historical'],
        default='recent',
        help='수집 모드 (recent: 최근 데이터, historical: 과거 데이터)'
    )
    parser.add_argument(
        '--days-back',
        type=int,
        default=30,
        help='과거 며칠 (낙찰결과용, 기본값: 30)'
    )
    parser.add_argument(
        '--days-forward',
        type=int,
        default=60,
        help='미래 며칠 (입찰공고용, 기본값: 60)'
    )
    parser.add_argument(
        '--start-year',
        type=int,
        help='시작 연도 (historical 모드용)'
    )
    parser.add_argument(
        '--end-year',
        type=int,
        help='종료 연도 (historical 모드용)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'recent':
        await collect_recent_data(args.days_back, args.days_forward)
    elif args.mode == 'historical':
        if not args.start_year or not args.end_year:
            logger.error("historical 모드는 --start-year와 --end-year가 필요합니다.")
            sys.exit(1)
        await collect_historical_data(args.start_year, args.end_year)


if __name__ == "__main__":
    asyncio.run(main())
