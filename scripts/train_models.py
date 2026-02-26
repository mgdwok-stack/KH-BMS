"""
AI 모델 학습 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.services.data_processor import DataProcessor
from app.ml.trainer import ModelTrainer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    DNBP와 LSTM 모델 학습
    """
    logger.info("=" * 60)
    logger.info("AI 모델 학습 시작")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. 데이터 준비
        logger.info("\n1. 학습 데이터 준비")
        processor = DataProcessor(db)
        df = processor.get_training_data()
        
        if df.empty:
            logger.error("학습 데이터가 없습니다. 먼저 데이터를 수집해주세요.")
            return
        
        logger.info(f"학습 데이터: {len(df)}건")
        logger.info(f"사정률 평균: {df['prdprc_rate'].mean():.2f}%")
        logger.info(f"사정률 범위: {df['prdprc_rate'].min():.2f}% ~ {df['prdprc_rate'].max():.2f}%")
        
        # 2. 모델 학습
        logger.info("\n2. 모델 학습 시작")
        trainer = ModelTrainer(model_save_dir="./models")
        
        results = trainer.train_all(
            df=df,
            price_range_percent=0.02,  # ±2%
            sequence_length=30,
            group_by='instt_nm',  # 발주기관별로 시퀀스 생성
            epochs_dnbp=50,  # DNBP 에포크 (테스트용: 50, 실제: 100+)
            epochs_lstm=50,  # LSTM 에포크 (테스트용: 50, 실제: 100+)
            batch_size=32
        )
        
        # 3. 결과 출력
        logger.info("\n" + "=" * 60)
        logger.info("학습 완료!")
        logger.info("=" * 60)
        
        logger.info(f"\n📊 학습 데이터: {results['training_samples']}건")
        logger.info(f"💾 모델 저장 위치: {results['model_save_dir']}")
        
        logger.info("\n🤖 DNBP 모델 성능:")
        for key, value in results['dnbp']['metrics'].items():
            logger.info(f"  - {key}: {value:.4f}")
        
        logger.info("\n📈 LSTM 모델 성능:")
        for key, value in results['lstm']['metrics'].items():
            logger.info(f"  - {key}: {value:.4f}")
        
        logger.info("\n✅ 모델 학습이 완료되었습니다!")
        logger.info("다음 명령으로 예측을 실행할 수 있습니다:")
        logger.info("  python scripts/test_prediction.py")
        
    except Exception as e:
        logger.error(f"❌ 학습 실패: {e}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    main()
