"""
Predictor Service - AI 모델을 사용한 예측 서비스

DNBP, LSTM, Ensemble 모델을 통합하여 사정률 및 투찰금액 예측
"""
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
import numpy as np

from ..models.bid import BidAnnouncement
from ..models.result import BidResult
from ..models.prediction import Prediction
from .dnbp_model import DNBPModel
from .lstm_model import LSTMModel
from .ensemble import EnsemblePredictor
from .trainer import ModelTrainer
from .data_processor import DataProcessor

logger = logging.getLogger(__name__)


class PredictorService:
    """
    AI 예측 서비스
    """
    
    def __init__(
        self,
        db: Session,
        model_dir: str = "./models"
    ):
        """
        Args:
            db: 데이터베이스 세션
            model_dir: 모델 저장 디렉토리
        """
        self.db = db
        self.model_dir = model_dir
        
        # 모델 로드
        trainer = ModelTrainer(model_save_dir=model_dir)
        self.dnbp_model, self.lstm_model = trainer.load_trained_models()
        
        # 앙상블 예측기
        if self.dnbp_model:
            self.ensemble = EnsemblePredictor(
                dnbp_model=self.dnbp_model,
                lstm_model=self.lstm_model
            )
        else:
            self.ensemble = None
            logger.warning("DNBP 모델이 없어 예측 서비스를 사용할 수 없습니다.")
        
        # 데이터 프로세서
        self.processor = DataProcessor(db)
    
    def predict(
        self,
        bid_announcement: BidAnnouncement,
        use_historical: bool = True,
        save_prediction: bool = True
    ) -> Optional[Dict]:
        """
        입찰공고에 대한 사정률 및 투찰금액 예측
        
        Args:
            bid_announcement: 입찰공고 객체
            use_historical: 과거 데이터 사용 여부 (LSTM)
            save_prediction: 예측 결과 DB 저장 여부
            
        Returns:
            예측 결과 딕셔너리 또는 None
        """
        if not self.ensemble:
            logger.error("예측 모델이 로드되지 않았습니다.")
            return None
        
        try:
            # 1. 특징 추출
            features = self.processor.extract_features_for_prediction(
                bid_announcement
            )
            
            basis_price = bid_announcement.basis_prce
            
            if not basis_price or basis_price <= 0:
                logger.error("유효하지 않은 기초금액")
                return None
            
            # 2. 과거 시퀀스 준비 (LSTM용)
            historical_sequence = None
            if use_historical and self.lstm_model:
                historical_sequence = self._get_historical_sequence(
                    bid_announcement
                )
            
            # 3. 앙상블 예측
            prediction = self.ensemble.predict(
                basis_price,
                historical_sequence,
                dynamic_weights=True
            )
            
            # 4. 특징 정보 추가
            prediction.update({
                'features': features,
                'instt_historical_avg_rate': features.get('instt_historical_avg_rate'),
                'instt_historical_std_rate': features.get('instt_historical_std_rate'),
                'similar_cases_count': features.get('similar_cases_count'),
                'similar_cases_avg_rate': features.get('similar_cases_avg_rate')
            })
            
            # 5. DB 저장
            if save_prediction:
                self._save_prediction(bid_announcement, prediction)
            
            logger.info(
                f"예측 완료: 공고번호={bid_announcement.bid_ntce_no}, "
                f"사정률={prediction['final_predicted_rate']:.4f}%"
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"예측 중 오류 발생: {e}", exc_info=True)
            return None
    
    def _get_historical_sequence(
        self,
        bid_announcement: BidAnnouncement,
        lookback_days: int = 365
    ) -> Optional[np.ndarray]:
        """
        과거 사정률 시퀀스 조회
        
        우선순위:
        1. 같은 발주기관
        2. 같은 지역
        3. 전체
        """
        from datetime import datetime, timedelta
        from sqlalchemy import and_
        
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        # 1차: 같은 발주기관
        if bid_announcement.instt_nm:
            results = self.db.query(BidResult).filter(
                and_(
                    BidResult.instt_nm == bid_announcement.instt_nm,
                    BidResult.opengdt >= start_date,
                    BidResult.prdprc_rate.isnot(None)
                )
            ).order_by(BidResult.opengdt).limit(100).all()
            
            if len(results) >= 30:
                rates = np.array([r.prdprc_rate for r in results])
                return rates[-30:]  # 최근 30개
        
        # 2차: 같은 지역
        if bid_announcement.rgn_nm:
            results = self.db.query(BidResult).filter(
                and_(
                    BidResult.rgn_nm == bid_announcement.rgn_nm,
                    BidResult.opengdt >= start_date,
                    BidResult.prdprc_rate.isnot(None)
                )
            ).order_by(BidResult.opengdt).limit(100).all()
            
            if len(results) >= 30:
                rates = np.array([r.prdprc_rate for r in results])
                return rates[-30:]
        
        # 3차: 전체
        results = self.db.query(BidResult).filter(
            and_(
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).order_by(BidResult.opengdt).limit(100).all()
        
        if len(results) >= 30:
            rates = np.array([r.prdprc_rate for r in results])
            return rates[-30:]
        
        logger.warning("충분한 과거 데이터가 없어 LSTM을 사용하지 않습니다.")
        return None
    
    def _save_prediction(
        self,
        bid_announcement: BidAnnouncement,
        prediction: Dict
    ):
        """
        예측 결과 DB 저장
        """
        try:
            prediction_record = Prediction(
                bid_announcement_id=bid_announcement.id,
                bid_ntce_no=bid_announcement.bid_ntce_no,
                basis_prce=bid_announcement.basis_prce,
                presmpt_prce=bid_announcement.presmpt_prce,
                
                # DNBP 결과
                dnbp_predicted_rate=prediction.get('dnbp_predicted_rate'),
                dnbp_top4_rates=prediction.get('dnbp_top4_rates'),
                dnbp_confidence=prediction.get('dnbp_confidence'),
                
                # LSTM 결과
                lstm_predicted_rate=prediction.get('lstm_predicted_rate'),
                lstm_confidence=prediction.get('lstm_confidence'),
                
                # 앙상블 결과
                final_predicted_rate=prediction.get('final_predicted_rate'),
                predicted_prdprc=prediction.get('predicted_prdprc'),
                recommended_bid_amt=prediction.get('recommended_bid_amt'),
                recommended_bid_rate=prediction.get('recommended_bid_rate'),
                
                # 예측 범위
                prediction_range_min=prediction.get('prediction_range_min'),
                prediction_range_max=prediction.get('prediction_range_max'),
                
                # 메타데이터
                ensemble_weights=prediction.get('ensemble_weights'),
                features=prediction.get('features'),
                
                # 유사 케이스
                similar_cases_count=prediction.get('similar_cases_count'),
                similar_cases_avg_rate=prediction.get('similar_cases_avg_rate'),
                
                # 발주기관 통계
                instt_historical_avg_rate=prediction.get('instt_historical_avg_rate'),
                instt_historical_std_rate=prediction.get('instt_historical_std_rate'),
                
                prediction_status='predicted'
            )
            
            self.db.add(prediction_record)
            self.db.commit()
            self.db.refresh(prediction_record)
            
            logger.info(f"예측 결과 저장: ID={prediction_record.id}")
            
        except Exception as e:
            logger.error(f"예측 결과 저장 실패: {e}")
            self.db.rollback()
    
    def update_prediction_accuracy(
        self,
        prediction_id: int,
        actual_rate: float
    ):
        """
        예측 정확도 업데이트 (개찰 후)
        
        Args:
            prediction_id: 예측 ID
            actual_rate: 실제 사정률
        """
        try:
            prediction = self.db.query(Prediction).filter(
                Prediction.id == prediction_id
            ).first()
            
            if not prediction:
                logger.error(f"예측을 찾을 수 없음: ID={prediction_id}")
                return
            
            # 예측 오차 계산
            error = abs(prediction.final_predicted_rate - actual_rate)
            
            prediction.actual_prdprc_rate = actual_rate
            prediction.prediction_error = error
            prediction.prediction_status = 'validated'
            
            self.db.commit()
            
            logger.info(
                f"예측 정확도 업데이트: ID={prediction_id}, "
                f"오차={error:.4f}%"
            )
            
        except Exception as e:
            logger.error(f"예측 정확도 업데이트 실패: {e}")
            self.db.rollback()
    
    def get_prediction_statistics(self) -> Dict:
        """
        예측 통계 조회
        
        Returns:
            통계 딕셔너리
        """
        from sqlalchemy import func
        
        # 전체 예측 수
        total_predictions = self.db.query(Prediction).count()
        
        # 검증된 예측 수
        validated_predictions = self.db.query(Prediction).filter(
            Prediction.prediction_status == 'validated'
        ).count()
        
        # 평균 오차
        avg_error = self.db.query(
            func.avg(Prediction.prediction_error)
        ).filter(
            Prediction.prediction_error.isnot(None)
        ).scalar()
        
        # 최대 오차
        max_error = self.db.query(
            func.max(Prediction.prediction_error)
        ).filter(
            Prediction.prediction_error.isnot(None)
        ).scalar()
        
        # 평균 신뢰도
        avg_dnbp_confidence = self.db.query(
            func.avg(Prediction.dnbp_confidence)
        ).filter(
            Prediction.dnbp_confidence.isnot(None)
        ).scalar()
        
        stats = {
            'total_predictions': total_predictions,
            'validated_predictions': validated_predictions,
            'validation_rate': (validated_predictions / total_predictions * 100) if total_predictions > 0 else 0,
            'avg_error': float(avg_error) if avg_error else None,
            'max_error': float(max_error) if max_error else None,
            'avg_dnbp_confidence': float(avg_dnbp_confidence) if avg_dnbp_confidence else None
        }
        
        return stats
