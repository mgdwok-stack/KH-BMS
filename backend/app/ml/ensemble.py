"""
Ensemble Predictor - DNBP와 LSTM 모델을 결합한 앙상블 예측기

두 모델의 예측값을 가중 평균하여 최종 사정률과 추천 투찰금액을 도출
"""
import numpy as np
from typing import Dict, Optional, Tuple
import logging

from .dnbp_model import DNBPModel
from .lstm_model import LSTMModel

logger = logging.getLogger(__name__)


class EnsemblePredictor:
    """
    DNBP + LSTM 앙상블 예측기
    """
    
    def __init__(
        self,
        dnbp_model: DNBPModel,
        lstm_model: Optional[LSTMModel] = None,
        dnbp_weight: float = 0.6,
        lstm_weight: float = 0.4,
        default_bid_rate: float = 87.745  # 일반적인 낙찰하한율
    ):
        """
        Args:
            dnbp_model: DNBP 모델 인스턴스
            lstm_model: LSTM 모델 인스턴스 (선택사항)
            dnbp_weight: DNBP 가중치 (기본: 0.6)
            lstm_weight: LSTM 가중치 (기본: 0.4)
            default_bid_rate: 기본 낙찰하한율 (%)
        """
        self.dnbp_model = dnbp_model
        self.lstm_model = lstm_model
        self.dnbp_weight = dnbp_weight
        self.lstm_weight = lstm_weight
        self.default_bid_rate = default_bid_rate
        
        # 가중치 합이 1이 되도록 정규화
        total_weight = dnbp_weight + lstm_weight
        self.dnbp_weight = dnbp_weight / total_weight
        self.lstm_weight = lstm_weight / total_weight
        
        logger.info(
            f"앙상블 예측기 초기화: DNBP={self.dnbp_weight:.2f}, "
            f"LSTM={self.lstm_weight:.2f}"
        )
    
    def predict(
        self,
        basis_price: float,
        historical_sequence: Optional[np.ndarray] = None,
        dynamic_weights: bool = True
    ) -> Dict:
        """
        앙상블 예측 실행
        
        Args:
            basis_price: 기초금액
            historical_sequence: 과거 사정률 시퀀스 (LSTM용, 선택사항)
            dynamic_weights: 동적 가중치 조정 여부
            
        Returns:
            예측 결과 딕셔너리
        """
        # 1. DNBP 예측
        dnbp_result = self.dnbp_model.predict_rate(basis_price)
        dnbp_rate = dnbp_result['predicted_rate']
        dnbp_confidence = dnbp_result['confidence']
        
        # 2. LSTM 예측 (시퀀스가 있는 경우)
        lstm_rate = None
        lstm_confidence = 0.0
        use_lstm = False
        
        if self.lstm_model is not None and historical_sequence is not None:
            try:
                lstm_result = self.lstm_model.predict_rate(
                    historical_sequence,
                    basis_price
                )
                lstm_rate = lstm_result['predicted_rate']
                lstm_confidence = lstm_result['confidence']
                use_lstm = True
            except Exception as e:
                logger.warning(f"LSTM 예측 실패, DNBP만 사용: {e}")
        
        # 3. 앙상블 가중치 결정
        if use_lstm and dynamic_weights:
            # 동적 가중치: 신뢰도에 비례하여 조정
            weights = self._calculate_dynamic_weights(
                dnbp_confidence,
                lstm_confidence,
                historical_sequence
            )
        else:
            # 고정 가중치 또는 DNBP만 사용
            weights = {
                'dnbp': 1.0 if not use_lstm else self.dnbp_weight,
                'lstm': 0.0 if not use_lstm else self.lstm_weight
            }
        
        # 4. 최종 사정률 계산 (가중 평균)
        if use_lstm:
            final_rate = (
                dnbp_rate * weights['dnbp'] +
                lstm_rate * weights['lstm']
            )
        else:
            final_rate = dnbp_rate
        
        # 5. 예정가격 계산
        predicted_prdprc = basis_price * (final_rate / 100)
        
        # 6. 추천 투찰금액 계산 (낙찰하한율 적용)
        recommended_bid_amt = predicted_prdprc * (self.default_bid_rate / 100)
        
        # 7. 예측 범위 계산 (신뢰구간)
        prediction_range = self._calculate_prediction_range(
            final_rate,
            dnbp_rate,
            lstm_rate if use_lstm else None,
            dnbp_confidence,
            lstm_confidence if use_lstm else 0.0
        )
        
        # 8. 결과 구성
        result = {
            # 최종 예측
            'final_predicted_rate': float(final_rate),
            'predicted_prdprc': float(predicted_prdprc),
            'recommended_bid_amt': float(recommended_bid_amt),
            'recommended_bid_rate': float(self.default_bid_rate),
            
            # DNBP 결과
            'dnbp_predicted_rate': float(dnbp_rate),
            'dnbp_confidence': float(dnbp_confidence),
            'dnbp_top4_rates': dnbp_result['top4_rates'],
            
            # LSTM 결과
            'lstm_predicted_rate': float(lstm_rate) if use_lstm else None,
            'lstm_confidence': float(lstm_confidence) if use_lstm else None,
            
            # 앙상블 정보
            'ensemble_weights': weights,
            'use_lstm': use_lstm,
            
            # 예측 범위
            'prediction_range_min': float(prediction_range['min']),
            'prediction_range_max': float(prediction_range['max']),
            
            # 입력 정보
            'basis_price': float(basis_price)
        }
        
        logger.info(
            f"앙상블 예측 완료: {final_rate:.4f}% "
            f"(DNBP: {dnbp_rate:.4f}%, LSTM: {lstm_rate:.4f}% if use_lstm else 'N/A')"
        )
        
        return result
    
    def _calculate_dynamic_weights(
        self,
        dnbp_confidence: float,
        lstm_confidence: float,
        historical_sequence: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        동적 가중치 계산
        
        - 신뢰도에 비례하여 가중치 조정
        - 과거 데이터가 많으면 LSTM 가중치 증가
        """
        # 기본 가중치
        dnbp_w = self.dnbp_weight
        lstm_w = self.lstm_weight
        
        # 신뢰도 차이에 따른 조정
        confidence_diff = dnbp_confidence - lstm_confidence
        adjustment = 0.1 * confidence_diff  # ±10% 최대 조정
        
        dnbp_w += adjustment
        lstm_w -= adjustment
        
        # 과거 데이터 풍부도에 따른 조정
        if historical_sequence is not None and len(historical_sequence) > 50:
            # 충분한 과거 데이터가 있으면 LSTM 가중치 증가
            lstm_w += 0.1
            dnbp_w -= 0.1
        
        # 정규화 (합이 1이 되도록)
        total = dnbp_w + lstm_w
        dnbp_w /= total
        lstm_w /= total
        
        # 최소/최대 제약
        dnbp_w = np.clip(dnbp_w, 0.3, 0.8)
        lstm_w = 1.0 - dnbp_w
        
        return {
            'dnbp': float(dnbp_w),
            'lstm': float(lstm_w)
        }
    
    def _calculate_prediction_range(
        self,
        final_rate: float,
        dnbp_rate: float,
        lstm_rate: Optional[float],
        dnbp_confidence: float,
        lstm_confidence: float
    ) -> Dict[str, float]:
        """
        예측 범위 (신뢰구간) 계산
        
        - 두 모델의 예측값 차이와 신뢰도를 고려
        - 신뢰도가 낮을수록 범위가 넓어짐
        """
        if lstm_rate is None:
            # DNBP만 사용하는 경우
            avg_confidence = dnbp_confidence
            spread = abs(final_rate * 0.01)  # ±1%
        else:
            # 앙상블 사용하는 경우
            avg_confidence = (dnbp_confidence + lstm_confidence) / 2
            
            # 두 모델 예측값의 차이
            diff = abs(dnbp_rate - lstm_rate)
            spread = max(diff / 2, final_rate * 0.005)  # 최소 ±0.5%
        
        # 신뢰도가 낮을수록 범위 확대
        confidence_factor = 1.0 / (0.5 + avg_confidence)
        adjusted_spread = spread * confidence_factor
        
        return {
            'min': final_rate - adjusted_spread,
            'max': final_rate + adjusted_spread
        }
    
    def set_weights(
        self,
        dnbp_weight: float,
        lstm_weight: float
    ):
        """
        앙상블 가중치 수동 설정
        """
        total = dnbp_weight + lstm_weight
        self.dnbp_weight = dnbp_weight / total
        self.lstm_weight = lstm_weight / total
        
        logger.info(
            f"앙상블 가중치 업데이트: DNBP={self.dnbp_weight:.2f}, "
            f"LSTM={self.lstm_weight:.2f}"
        )
    
    def predict_batch(
        self,
        basis_prices: np.ndarray,
        historical_sequences: Optional[np.ndarray] = None
    ) -> list:
        """
        배치 예측
        
        Args:
            basis_prices: 기초금액 배열
            historical_sequences: 과거 시퀀스 배열 (선택사항)
            
        Returns:
            예측 결과 리스트
        """
        results = []
        
        for i, basis_price in enumerate(basis_prices):
            sequence = None
            if historical_sequences is not None:
                sequence = historical_sequences[i]
            
            result = self.predict(basis_price, sequence)
            results.append(result)
        
        return results
    
    def evaluate_ensemble(
        self,
        test_data: list,
        actual_rates: np.ndarray
    ) -> Dict:
        """
        앙상블 성능 평가
        
        Args:
            test_data: [(basis_price, sequence), ...] 형태의 테스트 데이터
            actual_rates: 실제 사정률 배열
            
        Returns:
            평가 메트릭
        """
        predictions = []
        
        for basis_price, sequence in test_data:
            result = self.predict(basis_price, sequence)
            predictions.append(result['final_predicted_rate'])
        
        predictions = np.array(predictions)
        errors = predictions - actual_rates
        
        metrics = {
            'mae': float(np.mean(np.abs(errors))),
            'rmse': float(np.sqrt(np.mean(errors ** 2))),
            'mape': float(np.mean(np.abs(errors / actual_rates)) * 100),
            'max_error': float(np.max(np.abs(errors))),
            'std_error': float(np.std(errors))
        }
        
        logger.info(f"앙상블 평가 결과: {metrics}")
        
        return metrics
