"""
Celery Task Scheduler - 주기적인 데이터 수집 및 처리
"""
from celery import Celery
from celery.schedules import crontab
import logging
from datetime import datetime, timedelta
import asyncio

from ..config import settings
from ..database import SessionLocal
from ..services.data_collector import DataCollector
from ..services.data_processor import DataProcessor

logger = logging.getLogger(__name__)

# Celery 애플리케이션 생성
celery_app = Celery(
    'bid_bot_tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery 설정
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30분
    task_soft_time_limit=25 * 60,  # 25분
)

# Beat 스케줄 설정
celery_app.conf.beat_schedule = {
    # 매 시간마다 입찰공고 수집
    'collect-bid-announcements-hourly': {
        'task': 'app.tasks.scheduler.collect_bid_announcements_task',
        'schedule': crontab(minute=0),  # 매 시간 정각
    },
    # 매 6시간마다 낙찰결과 수집
    'collect-bid-results-every-6-hours': {
        'task': 'app.tasks.scheduler.collect_bid_results_task',
        'schedule': crontab(minute=30, hour='*/6'),  # 6시간마다 30분에
    },
    # 매일 자정에 데이터 정제
    'clean-data-daily': {
        'task': 'app.tasks.scheduler.clean_data_task',
        'schedule': crontab(hour=0, minute=0),  # 매일 00:00
    },
    # 매주 월요일 오전 1시에 데이터 검증
    'validate-data-weekly': {
        'task': 'app.tasks.scheduler.validate_data_task',
        'schedule': crontab(hour=1, minute=0, day_of_week=1),  # 매주 월요일 01:00
    },
}


@celery_app.task(name='app.tasks.scheduler.collect_bid_announcements_task')
def collect_bid_announcements_task():
    """
    입찰공고 수집 태스크
    매 시간마다 실행
    """
    logger.info("=== 입찰공고 수집 시작 ===")
    
    db = SessionLocal()
    try:
        collector = DataCollector(db)
        
        # 오늘부터 60일 후까지의 공고 수집
        start_date = datetime.now().strftime("%Y%m%d")
        end_date = (datetime.now() + timedelta(days=60)).strftime("%Y%m%d")
        
        total_collected = 0
        page = 1
        max_pages = 10  # 최대 10페이지까지 (1000건)
        
        while page <= max_pages:
            # 비동기 함수를 동기적으로 실행
            items = asyncio.run(
                collector.collect_bid_announcements(
                    start_date=start_date,
                    end_date=end_date,
                    page=page,
                    num_of_rows=100
                )
            )
            
            if not items:
                break
            
            # DB에 저장
            for item in items:
                try:
                    collector.save_bid_announcement(item)
                    total_collected += 1
                except Exception as e:
                    logger.error(f"입찰공고 저장 실패: {e}")
            
            logger.info(f"페이지 {page} 완료: {len(items)}건 수집")
            
            # 다음 페이지가 없으면 종료
            if len(items) < 100:
                break
            
            page += 1
        
        logger.info(f"=== 입찰공고 수집 완료: 총 {total_collected}건 ===")
        return {'status': 'success', 'total_collected': total_collected}
        
    except Exception as e:
        logger.error(f"입찰공고 수집 중 오류 발생: {e}")
        return {'status': 'error', 'message': str(e)}
        
    finally:
        db.close()


@celery_app.task(name='app.tasks.scheduler.collect_bid_results_task')
def collect_bid_results_task():
    """
    낙찰결과 수집 태스크
    매 6시간마다 실행
    """
    logger.info("=== 낙찰결과 수집 시작 ===")
    
    db = SessionLocal()
    try:
        collector = DataCollector(db)
        
        # 최근 30일간의 낙찰결과 수집
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        end_date = datetime.now().strftime("%Y%m%d")
        
        total_collected = 0
        page = 1
        max_pages = 20  # 최대 20페이지까지 (2000건)
        
        while page <= max_pages:
            items = asyncio.run(
                collector.collect_bid_results(
                    start_date=start_date,
                    end_date=end_date,
                    page=page,
                    num_of_rows=100
                )
            )
            
            if not items:
                break
            
            # DB에 저장
            for item in items:
                try:
                    collector.save_bid_result(item)
                    total_collected += 1
                except Exception as e:
                    logger.error(f"낙찰결과 저장 실패: {e}")
            
            logger.info(f"페이지 {page} 완료: {len(items)}건 수집")
            
            if len(items) < 100:
                break
            
            page += 1
        
        logger.info(f"=== 낙찰결과 수집 완료: 총 {total_collected}건 ===")
        return {'status': 'success', 'total_collected': total_collected}
        
    except Exception as e:
        logger.error(f"낙찰결과 수집 중 오류 발생: {e}")
        return {'status': 'error', 'message': str(e)}
        
    finally:
        db.close()


@celery_app.task(name='app.tasks.scheduler.clean_data_task')
def clean_data_task():
    """
    데이터 정제 태스크
    매일 자정에 실행
    """
    logger.info("=== 데이터 정제 시작 ===")
    
    db = SessionLocal()
    try:
        processor = DataProcessor(db)
        
        # 낙찰결과 데이터 정제
        cleaned_count = processor.clean_bid_results(min_basis_price=1000000)
        
        logger.info(f"=== 데이터 정제 완료: {cleaned_count}건 처리 ===")
        return {'status': 'success', 'cleaned_count': cleaned_count}
        
    except Exception as e:
        logger.error(f"데이터 정제 중 오류 발생: {e}")
        return {'status': 'error', 'message': str(e)}
        
    finally:
        db.close()


@celery_app.task(name='app.tasks.scheduler.validate_data_task')
def validate_data_task():
    """
    데이터 검증 태스크
    매주 월요일 오전 1시에 실행
    """
    logger.info("=== 데이터 검증 시작 ===")
    
    db = SessionLocal()
    try:
        from ..models.bid import BidAnnouncement
        from ..models.result import BidResult
        
        # 1. 총 데이터 건수 확인
        announcement_count = db.query(BidAnnouncement).count()
        result_count = db.query(BidResult).count()
        
        # 2. 최근 7일간 수집된 데이터
        recent_date = datetime.now() - timedelta(days=7)
        recent_announcements = db.query(BidAnnouncement).filter(
            BidAnnouncement.created_at >= recent_date
        ).count()
        recent_results = db.query(BidResult).filter(
            BidResult.created_at >= recent_date
        ).count()
        
        # 3. 사정률 통계
        from sqlalchemy import func
        avg_rate = db.query(func.avg(BidResult.prdprc_rate)).filter(
            BidResult.prdprc_rate.isnot(None)
        ).scalar()
        
        report = {
            'total_announcements': announcement_count,
            'total_results': result_count,
            'recent_announcements': recent_announcements,
            'recent_results': recent_results,
            'avg_prdprc_rate': float(avg_rate) if avg_rate else None,
            'validated_at': datetime.now().isoformat()
        }
        
        logger.info(f"=== 데이터 검증 완료 ===")
        logger.info(f"입찰공고: {announcement_count}건 (최근 7일: {recent_announcements}건)")
        logger.info(f"낙찰결과: {result_count}건 (최근 7일: {recent_results}건)")
        logger.info(f"평균 사정률: {avg_rate:.2f}%" if avg_rate else "평균 사정률: N/A")
        
        return {'status': 'success', 'report': report}
        
    except Exception as e:
        logger.error(f"데이터 검증 중 오류 발생: {e}")
        return {'status': 'error', 'message': str(e)}
        
    finally:
        db.close()


@celery_app.task(name='app.tasks.scheduler.collect_historical_data_task')
def collect_historical_data_task(start_date: str, end_date: str):
    """
    과거 데이터 일괄 수집 태스크 (수동 실행용)
    
    Args:
        start_date: 시작일 (YYYYMMDD)
        end_date: 종료일 (YYYYMMDD)
    """
    logger.info(f"=== 과거 데이터 수집 시작: {start_date} ~ {end_date} ===")
    
    db = SessionLocal()
    try:
        collector = DataCollector(db)
        
        total_announcements = 0
        total_results = 0
        
        # 입찰공고 수집
        page = 1
        while page <= 50:  # 최대 50페이지 (5000건)
            items = asyncio.run(
                collector.collect_bid_announcements(
                    start_date=start_date,
                    end_date=end_date,
                    page=page,
                    num_of_rows=100
                )
            )
            
            if not items:
                break
            
            for item in items:
                try:
                    collector.save_bid_announcement(item)
                    total_announcements += 1
                except Exception as e:
                    logger.error(f"입찰공고 저장 실패: {e}")
            
            logger.info(f"입찰공고 페이지 {page} 완료")
            
            if len(items) < 100:
                break
            
            page += 1
        
        # 낙찰결과 수집
        page = 1
        while page <= 50:
            items = asyncio.run(
                collector.collect_bid_results(
                    start_date=start_date,
                    end_date=end_date,
                    page=page,
                    num_of_rows=100
                )
            )
            
            if not items:
                break
            
            for item in items:
                try:
                    collector.save_bid_result(item)
                    total_results += 1
                except Exception as e:
                    logger.error(f"낙찰결과 저장 실패: {e}")
            
            logger.info(f"낙찰결과 페이지 {page} 완료")
            
            if len(items) < 100:
                break
            
            page += 1
        
        logger.info(f"=== 과거 데이터 수집 완료 ===")
        logger.info(f"입찰공고: {total_announcements}건, 낙찰결과: {total_results}건")
        
        return {
            'status': 'success',
            'total_announcements': total_announcements,
            'total_results': total_results
        }
        
    except Exception as e:
        logger.error(f"과거 데이터 수집 중 오류 발생: {e}")
        return {'status': 'error', 'message': str(e)}
        
    finally:
        db.close()


# 수동 실행용 유틸리티 함수
def trigger_immediate_collection():
    """
    즉시 데이터 수집 실행 (테스트 및 수동 실행용)
    """
    logger.info("수동 데이터 수집 트리거")
    
    # 입찰공고 수집
    result1 = collect_bid_announcements_task.delay()
    logger.info(f"입찰공고 수집 Task ID: {result1.id}")
    
    # 낙찰결과 수집
    result2 = collect_bid_results_task.delay()
    logger.info(f"낙찰결과 수집 Task ID: {result2.id}")
    
    return {
        'announcement_task_id': result1.id,
        'result_task_id': result2.id
    }
