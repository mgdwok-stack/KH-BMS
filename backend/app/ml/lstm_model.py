"""
LSTM Model - Long Short-Term Memory for Time Series Prediction

시계열 입찰 데이터를 학습하여 발주기관별/지역별 사정률 패턴을 예측하는 모델

핵심 로직:
1. 과거 N일간의 입찰 결과 시퀀스를 입력으로 사용
2. LSTM 네트워크로 시계열 패턴 학습
3. 다음 입찰의 예정가격 사정률 예측
4. 발주기관, 지역, 업종 등의 컨텍스트 정보 활용
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class LSTMModel:
    """
    LSTM 기반 사정률 예측 모델
    """
    
    def __init__(
        self,
        sequence_length: int = 30,
        feature_dim: int = 1,
        lstm_units: List[int] = [128, 64],
        dense_units: int = 32,
        dropout_rate: float = 0.2,
        model_path: Optional[str] = None
    ):
        """
        Args:
            sequence_length: 시퀀스 길이 (과거 N개 데이터)
            feature_dim: 특징 차원 (1: 사정률만, N: 다중 특징)
            lstm_units: LSTM 레이어별 유닛 수
            dense_units: Dense 레이어 유닛 수
            dropout_rate: Dropout 비율
            model_path: 저장된 모델 경로
        """
        self.sequence_length = sequence_length
        self.feature_dim = feature_dim
        self.lstm_units = lstm_units
        self.dense_units = dense_units
        self.dropout_rate = dropout_rate
        self.model = None
        
        if model_path:
            self.load_model(model_path)
        else:
            self.model = self._build_model()
    
    def _build_model(self) -> keras.Model:
        """
        LSTM 신경망 모델 구축
        
        구조:
        - Input: (sequence_length, feature_dim)
        - LSTM Layer 1: 128 units (return_sequences=True)
        - Dropout: 0.2
        - LSTM Layer 2: 64 units
        - Dropout: 0.2
        - Dense Layer: 32 units (ReLU)
        - Output: 1 unit (Linear - 사정률 예측)
        """
        model = models.Sequential([
            # Input Layer
            layers.Input(
                shape=(self.sequence_length, self.feature_dim),
                name='input_layer'
            ),
            
            # LSTM Layer 1 (return sequences for next LSTM layer)
            layers.LSTM(
                self.lstm_units[0],
                return_sequences=True,
                kernel_initializer='glorot_uniform',
                name='lstm_1'
            ),
            layers.Dropout(self.dropout_rate),
            
            # LSTM Layer 2
            layers.LSTM(
                self.lstm_units[1] if len(self.lstm_units) > 1 else 64,
                return_sequences=False,
                kernel_initializer='glorot_uniform',
                name='lstm_2'
            ),
            layers.Dropout(self.dropout_rate),
            
            # Dense Layer
            layers.Dense(
                self.dense_units,
                activation='relu',
                kernel_initializer='he_normal',
                name='dense_1'
            ),
            
            # Output Layer (사정률 회귀)
            layers.Dense(
                1,
                activation='linear',
                name='output_layer'
            )
        ])
        
        # 모델 컴파일
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',  # Mean Squared Error
            metrics=['mae', 'mape']  # Mean Absolute Error, Mean Absolute Percentage Error
        )
        
        logger.info(f"LSTM 모델 구축 완료: {model.count_params():,} parameters")
        
        return model
    
    def prepare_sequences(
        self,
        data: np.ndarray,
        lookback: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        시계열 데이터를 LSTM 입력 시퀀스로 변환
        
        Args:
            data: 시계열 데이터 (1D array: 사정률 시퀀스)
            lookback: 시퀀스 길이 (None이면 self.sequence_length 사용)
            
        Returns:
            (X, y) - X: 입력 시퀀스, y: 타겟 값
        """
        if lookback is None:
            lookback = self.sequence_length
        
        X, y = [], []
        
        for i in range(len(data) - lookback):
            X.append(data[i:i+lookback])
            y.append(data[i+lookback])
        
        X = np.array(X)
        y = np.array(y)
        
        # 특징 차원 추가 (shape: (N, seq_len) -> (N, seq_len, 1))
        if len(X.shape) == 2:
            X = np.expand_dims(X, axis=-1)
        
        return X, y
    
    def predict_rate(
        self,
        sequence: np.ndarray,
        basis_price: Optional[float] = None
    ) -> Dict:
        """
        사정률 예측
        
        Args:
            sequence: 과거 사정률 시퀀스 (shape: (sequence_length,) or (sequence_length, feature_dim))
            basis_price: 기초금액 (예정가격 계산용, 선택사항)
            
        Returns:
            예측 결과 딕셔너리
        """
        # 입력 형태 조정
        if len(sequence.shape) == 1:
            # (seq_len,) -> (1, seq_len, 1)
            input_seq = sequence.reshape(1, -1, 1)
        elif len(sequence.shape) == 2:
            # (seq_len, feature_dim) -> (1, seq_len, feature_dim)
            input_seq = np.expand_dims(sequence, axis=0)
        else:
            input_seq = sequence
        
        # 예측
        predicted_rate = self.model.predict(input_seq, verbose=0)[0][0]
        
        result = {
            'predicted_rate': float(predicted_rate),
            'confidence': self._calculate_confidence(sequence, predicted_rate),
            'sequence_mean': float(np.mean(sequence)),
            'sequence_std': float(np.std(sequence))
        }
        
        # 기초금액이 주어진 경우 예정가격 계산
        if basis_price:
            result['predicted_price'] = float(basis_price * (predicted_rate / 100))
            result['basis_price'] = float(basis_price)
        
        logger.info(f"LSTM 예측: {predicted_rate:.4f}%")
        
        return result
    
    def _calculate_confidence(
        self,
        sequence: np.ndarray,
        prediction: float
    ) -> float:
        """
        예측 신뢰도 계산
        
        시퀀스의 변동성을 기반으로 신뢰도 추정:
        - 변동성이 작을수록 신뢰도 높음
        - 예측값이 시퀀스 범위 내에 있으면 신뢰도 높음
        """
        seq_mean = np.mean(sequence)
        seq_std = np.std(sequence)
        seq_min = np.min(sequence)
        seq_max = np.max(sequence)
        
        # 변동성 기반 신뢰도 (낮은 표준편차 = 높은 신뢰도)
        volatility_confidence = 1 / (1 + seq_std)
        
        # 범위 기반 신뢰도 (예측값이 범위 내 = 높은 신뢰도)
        if seq_min <= prediction <= seq_max:
            range_confidence = 1.0
        else:
            # 범위 밖일 경우 거리에 비례하여 신뢰도 감소
            distance = min(abs(prediction - seq_min), abs(prediction - seq_max))
            range_confidence = 1 / (1 + distance / seq_std) if seq_std > 0 else 0.5
        
        # 종합 신뢰도 (0~1)
        confidence = (volatility_confidence + range_confidence) / 2
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 100,
        batch_size: int = 32,
        callbacks: Optional[List] = None
    ) -> keras.callbacks.History:
        """
        모델 학습
        
        Args:
            X_train: 학습 입력 시퀀스 (shape: (N, seq_len, feature_dim))
            y_train: 학습 타겟 사정률 (shape: (N,))
            X_val: 검증 입력 시퀀스
            y_val: 검증 타겟 사정률
            epochs: 에포크 수
            batch_size: 배치 크기
            callbacks: Keras 콜백 리스트
            
        Returns:
            학습 이력
        """
        # 기본 콜백 설정
        if callbacks is None:
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=15,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=7,
                    min_lr=1e-6
                )
            ]
        
        # 검증 데이터 설정
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        # 모델 학습
        logger.info(f"LSTM 모델 학습 시작: {len(X_train)}건")
        
        history = self.model.fit(
            X_train,
            y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("LSTM 모델 학습 완료")
        
        return history
    
    def predict_batch(
        self,
        sequences: np.ndarray
    ) -> np.ndarray:
        """
        배치 예측
        
        Args:
            sequences: 입력 시퀀스 배치 (shape: (N, seq_len, feature_dim))
            
        Returns:
            예측 사정률 배열 (shape: (N,))
        """
        predictions = self.model.predict(sequences, verbose=0)
        return predictions.flatten()
    
    def save_model(self, path: str):
        """
        모델 저장
        """
        self.model.save(path)
        logger.info(f"LSTM 모델 저장: {path}")
    
    def load_model(self, path: str):
        """
        모델 로드
        """
        self.model = keras.models.load_model(path)
        logger.info(f"LSTM 모델 로드: {path}")
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict:
        """
        모델 평가
        
        Args:
            X_test: 테스트 입력 시퀀스
            y_test: 테스트 타겟 사정률
            
        Returns:
            평가 메트릭 딕셔너리
        """
        results = self.model.evaluate(X_test, y_test, verbose=0)
        
        # 추가 메트릭 계산
        predictions = self.predict_batch(X_test)
        rmse = np.sqrt(np.mean((y_test - predictions) ** 2))
        
        metrics = {
            'loss': results[0],  # MSE
            'mae': results[1],   # Mean Absolute Error
            'mape': results[2],  # Mean Absolute Percentage Error
            'rmse': float(rmse)  # Root Mean Squared Error
        }
        
        logger.info(f"LSTM 평가 결과: {metrics}")
        
        return metrics
    
    def get_model_summary(self) -> str:
        """
        모델 구조 요약
        """
        summary_list = []
        self.model.summary(print_fn=lambda x: summary_list.append(x))
        return '\n'.join(summary_list)
