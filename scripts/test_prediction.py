"""
AI 예측 테스트 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.services.predictor import PredictorService
from app.models.bid import BidAnnouncement
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_prediction():
    """
    AI 예측 테스트
    """
    logger.info("=" * 60)
    logger.info("AI 예측 테스트")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Predictor Service 초기화
        logger.info("\n1. 예측 서비스 초기화")
        predictor = PredictorService(db, model_dir="./models")
        
        if not predictor.ensemble:
            logger.error("예측 모델이 로드되지 않았습니다.")
            logger.error("먼저 모델을 학습해주세요: python scripts/train_models.py")
            return
        
        logger.info("✅ 예측 서비스 초기화 완료")
        
        # 2. 테스트용 입찰공고 조회
        logger.info("\n2. 테스트 입찰공고 조회")
        announcement = db.query(BidAnnouncement).filter(
            BidAnnouncement.basis_prce.isnot(None),
            BidAnnouncement.basis_prce > 1000000
        ).first()
        
        if not announcement:
            logger.error("테스트할 입찰공고가 없습니다.")
            logger.error("먼저 데이터를 수집해주세요: python scripts/collect_data.py")
            return
        
        logger.info(f"공고번호: {announcement.bid_ntce_no}")
        logger.info(f"공고명: {announcement.bid_ntce_nm}")
        logger.info(f"기관명: {announcement.instt_nm}")
        logger.info(f"기초금액: {announcement.basis_prce:,}원")
        
        # 3. 예측 실행
        logger.info("\n3. AI 예측 실행")
        prediction = predictor.predict(
            announcement,
            use_historical=True,
            save_prediction=True
        )
        
        if not prediction:
            logger.error("예측 실패")
            return
        
        # 4. 결과 출력
        logger.info("\n" + "=" * 60)
        logger.info("예측 결과")
        logger.info("=" * 60)
        
        logger.info(f"\n📊 입력 정보:")
        logger.info(f"  - 기초금액: {prediction['basis_price']:,.0f}원")
        
        logger.info(f"\n🤖 DNBP 모델:")
        logger.info(f"  - 예측 사정률: {prediction['dnbp_predicted_rate']:.4f}%")
        logger.info(f"  - 신뢰도: {prediction['dnbp_confidence']:.4f}")
        logger.info(f"  - 상위 4개 사정률: {[f'{r:.4f}%' for r in prediction['dnbp_top4_rates']]}")
        
        if prediction.get('lstm_predicted_rate'):
            logger.info(f"\n📈 LSTM 모델:")
            logger.info(f"  - 예측 사정률: {prediction['lstm_predicted_rate']:.4f}%")
            logger.info(f"  - 신뢰도: {prediction['lstm_confidence']:.4f}")
        
        logger.info(f"\n🎯 앙상블 최종 예측:")
        logger.info(f"  - 예측 사정률: {prediction['final_predicted_rate']:.4f}%")
        logger.info(f"  - 예측 예정가격: {prediction['predicted_prdprc']:,.0f}원")
        logger.info(f"  - 추천 투찰금액: {prediction['recommended_bid_amt']:,.0f}원")
        logger.info(f"  - 추천 투찰률: {prediction['recommended_bid_rate']:.3f}%")
        
        logger.info(f"\n📉 예측 범위 (신뢰구간):")
        logger.info(f"  - 최소: {prediction['prediction_range_min']:.4f}%")
        logger.info(f"  - 최대: {prediction['prediction_range_max']:.4f}%")
        
        if prediction.get('ensemble_weights'):
            logger.info(f"\n⚖️  앙상블 가중치:")
            logger.info(f"  - DNBP: {prediction['ensemble_weights']['dnbp']:.2f}")
            logger.info(f"  - LSTM: {prediction['ensemble_weights']['lstm']:.2f}")
        
        if prediction.get('instt_historical_avg_rate'):
            logger.info(f"\n📊 발주기관 통계:")
            logger.info(f"  - 평균 사정률: {prediction['instt_historical_avg_rate']:.4f}%")
            logger.info(f"  - 표준편차: {prediction['instt_historical_std_rate']:.4f}%")
        
        if prediction.get('similar_cases_count'):
            logger.info(f"\n🔍 유사 케이스:")
            logger.info(f"  - 건수: {prediction['similar_cases_count']}건")
            logger.info(f"  - 평균 사정률: {prediction['similar_cases_avg_rate']:.4f}%")
        
        # 5. 예측 통계
        logger.info("\n4. 예측 통계 조회")
        stats = predictor.get_prediction_statistics()
        
        logger.info(f"\n📈 전체 예측 통계:")
        logger.info(f"  - 총 예측 수: {stats['total_predictions']}건")
        logger.info(f"  - 검증된 예측: {stats['validated_predictions']}건")
        logger.info(f"  - 검증 비율: {stats['validation_rate']:.2f}%")
        
        if stats['avg_error']:
            logger.info(f"  - 평균 오차: {stats['avg_error']:.4f}%")
            logger.info(f"  - 최대 오차: {stats['max_error']:.4f}%")
        
        if stats['avg_dnbp_confidence']:
            logger.info(f"  - 평균 신뢰도: {stats['avg_dnbp_confidence']:.4f}")
        
        logger.info("\n✅ 예측 테스트 완료!")
        
    except Exception as e:
        logger.error(f"❌ 예측 테스트 실패: {e}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    test_prediction()
