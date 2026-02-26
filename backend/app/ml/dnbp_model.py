"""
DNBP Model - Deep learning Network to predict Budget Price

복수예비가격 산출 로직을 딥러닝으로 모방하여 예정가격 사정률을 예측하는 모델

핵심 로직:
1. 기초금액 기준으로 15개의 가상 예비가격 생성 (±2% 또는 ±3% 범위)
2. 15개 중 최적화된 6개 노드(a, g, h, i, j, k)만 입력으로 사용
3. 딥러닝 신경망으로 15개 중 상위 4개 추첨 확률 예측
4. 예측된 상위 4개의 평균값으로 예정가격 사정률 도출
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class DNBPModel:
    """
    DNBP (Deep learning Network to predict Budget Price) 모델
    """
    
    # 최적화된 6개 입력 노드 인덱스 (0-based)
    # a=0, g=6, h=7, i=8, j=9, k=10
    OPTIMIZED_INDICES = [0, 6, 7, 8, 9, 10]
    
    def __init__(
        self,
        price_range_percent: float = 0.02,  # ±2% (일반적)
        num_reserve_prices: int = 15,
        input_dim: int = 6,
        model_path: Optional[str] = None
    ):
        """
        Args:
            price_range_percent: 예가범위 비율 (0.02 = ±2%, 0.03 = ±3%)
            num_reserve_prices: 예비가격 개수 (기본 15개)
            input_dim: 입력 차원 (최적화된 노드 개수, 기본 6개)
            model_path: 저장된 모델 경로 (로드 시 사용)
        """
        self.price_range_percent = price_range_percent
        self.num_reserve_prices = num_reserve_prices
        self.input_dim = input_dim
        self.model = None
        
        if model_path:
            self.load_model(model_path)
        else:
            self.model = self._build_model()
    
    def _build_model(self) -> keras.Model:
        """
        DNBP 신경망 모델 구축
        
        구조:
        - Input: 6개 노드 (최적화된 예비가격 구간)
        - Hidden Layer 1: 64 nodes (ReLU)
        - Hidden Layer 2: 32 nodes (ReLU)
        - Hidden Layer 3: 16 nodes (ReLU)
        - Output: 15 nodes (Softmax - 15개 예비가격 확률 분포)
        """
        model = models.Sequential([
            # Input Layer
            layers.Input(shape=(self.input_dim,), name='input_layer'),
            
            # Hidden Layer 1
            layers.Dense(
                64,
                activation='relu',
                kernel_initializer='he_normal',
                name='hidden_1'
            ),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Hidden Layer 2
            layers.Dense(
                32,
                activation='relu',
                kernel_initializer='he_normal',
                name='hidden_2'
            ),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Hidden Layer 3
            layers.Dense(
                16,
                activation='relu',
                kernel_initializer='he_normal',
                name='hidden_3'
            ),
            layers.Dropout(0.1),
            
            # Output Layer (15개 예비가격에 대한 확률 분포)
            layers.Dense(
                self.num_reserve_prices,
                activation='softmax',
                name='output_layer'
            )
        ])
        
        # 모델 컴파일
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )
        
        logger.info(f"DNBP 모델 구축 완료: {model.count_params():,} parameters")
        
        return model
    
    def generate_reserve_prices(
        self,
        basis_price: float
    ) -> np.ndarray:
        """
        기초금액 기준으로 15개의 가상 예비가격 생성
        
        Args:
            basis_price: 기초금액
            
        Returns:
            15개 예비가격 배열
        """
        # 예가범위 계산
        min_price = basis_price * (1 - self.price_range_percent)
        max_price = basis_price * (1 + self.price_range_percent)
        
        # 15개 균등 분할
        reserve_prices = np.linspace(min_price, max_price, self.num_reserve_prices)
        
        return reserve_prices
    
    def extract_optimized_features(
        self,
        reserve_prices: np.ndarray,
        basis_price: float
    ) -> np.ndarray:
        """
        15개 예비가격 중 최적화된 6개 노드 추출
        
        Args:
            reserve_prices: 15개 예비가격 배열
            basis_price: 기초금액
            
        Returns:
            6개 특징 배열 (정규화된 값)
        """
        # 6개 인덱스의 예비가격 선택
        selected_prices = reserve_prices[self.OPTIMIZED_INDICES]
        
        # 정규화 (기초금액 대비 비율)
        features = selected_prices / basis_price
        
        return features
    
    def prepare_input(
        self,
        basis_price: float
    ) -> np.ndarray:
        """
        예측을 위한 입력 데이터 준비
        
        Args:
            basis_price: 기초금액
            
        Returns:
            모델 입력 텐서 (shape: (1, 6))
        """
        # 1. 15개 예비가격 생성
        reserve_prices = self.generate_reserve_prices(basis_price)
        
        # 2. 6개 특징 추출
        features = self.extract_optimized_features(reserve_prices, basis_price)
        
        # 3. 배치 차원 추가
        input_tensor = np.expand_dims(features, axis=0)
        
        return input_tensor
    
    def predict_top4_indices(
        self,
        basis_price: float
    ) -> Tuple[List[int], np.ndarray]:
        """
        상위 4개 예비가격 인덱스 예측
        
        Args:
            basis_price: 기초금액
            
        Returns:
            (상위 4개 인덱스 리스트, 전체 확률 분포)
        """
        # 입력 준비
        input_tensor = self.prepare_input(basis_price)
        
        # 예측 (15개 확률 분포)
        probabilities = self.model.predict(input_tensor, verbose=0)[0]
        
        # 상위 4개 인덱스 추출
        top4_indices = np.argsort(probabilities)[-4:][::-1].tolist()
        
        logger.debug(f"상위 4개 인덱스: {top4_indices}")
        logger.debug(f"확률: {probabilities[top4_indices]}")
        
        return top4_indices, probabilities
    
    def predict_rate(
        self,
        basis_price: float
    ) -> Dict:
        """
        예정가격 사정률 예측
        
        Args:
            basis_price: 기초금액
            
        Returns:
            예측 결과 딕셔너리
            {
                'predicted_rate': 예측 사정률,
                'top4_indices': 상위 4개 인덱스,
                'top4_rates': 상위 4개 사정률,
                'confidence': 예측 신뢰도,
                'predicted_price': 예측 예정가격
            }
        """
        # 1. 15개 예비가격 생성
        reserve_prices = self.generate_reserve_prices(basis_price)
        
        # 2. 상위 4개 인덱스 예측
        top4_indices, probabilities = self.predict_top4_indices(basis_price)
        
        # 3. 상위 4개의 예비가격
        top4_prices = reserve_prices[top4_indices]
        
        # 4. 상위 4개의 평균 = 예정가격
        predicted_price = np.mean(top4_prices)
        
        # 5. 예정가격 사정률 계산
        predicted_rate = (predicted_price / basis_price) * 100
        
        # 6. 상위 4개의 사정률
        top4_rates = [(price / basis_price) * 100 for price in top4_prices]
        
        # 7. 신뢰도 (상위 4개의 확률 합)
        confidence = np.sum(probabilities[top4_indices])
        
        result = {
            'predicted_rate': float(predicted_rate),
            'top4_indices': top4_indices,
            'top4_rates': top4_rates,
            'confidence': float(confidence),
            'predicted_price': float(predicted_price),
            'basis_price': float(basis_price)
        }
        
        logger.info(f"DNBP 예측: {predicted_rate:.4f}% (신뢰도: {confidence:.4f})")
        
        return result
    
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
            X_train: 학습 입력 데이터 (shape: (N, 6))
            y_train: 학습 타겟 데이터 (shape: (N, 15), one-hot encoded)
            X_val: 검증 입력 데이터
            y_val: 검증 타겟 데이터
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
                    patience=10,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-6
                )
            ]
        
        # 검증 데이터 설정
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        # 모델 학습
        logger.info(f"DNBP 모델 학습 시작: {len(X_train)}건")
        
        history = self.model.fit(
            X_train,
            y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("DNBP 모델 학습 완료")
        
        return history
    
    def save_model(self, path: str):
        """
        모델 저장
        """
        self.model.save(path)
        logger.info(f"DNBP 모델 저장: {path}")
    
    def load_model(self, path: str):
        """
        모델 로드
        """
        self.model = keras.models.load_model(path)
        logger.info(f"DNBP 모델 로드: {path}")
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict:
        """
        모델 평가
        
        Args:
            X_test: 테스트 입력 데이터
            y_test: 테스트 타겟 데이터 (one-hot encoded)
            
        Returns:
            평가 메트릭 딕셔너리
        """
        results = self.model.evaluate(X_test, y_test, verbose=0)
        
        metrics = {
            'loss': results[0],
            'accuracy': results[1],
            'top_k_accuracy': results[2]
        }
        
        logger.info(f"DNBP 평가 결과: {metrics}")
        
        return metrics
    
    def get_model_summary(self) -> str:
        """
        모델 구조 요약
        """
        summary_list = []
        self.model.summary(print_fn=lambda x: summary_list.append(x))
        return '\n'.join(summary_list)
