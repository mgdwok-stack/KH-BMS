"""
Model Trainer - DNBP와 LSTM 모델 학습 파이프라인

학습 데이터 준비, 모델 학습, 평가, 저장을 관리
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging
import os

from .dnbp_model import DNBPModel
from .lstm_model import LSTMModel
from ..services.data_processor import DataProcessor

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    AI 모델 학습 파이프라인
    """
    
    def __init__(
        self,
        model_save_dir: str = "./models",
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42
    ):
        """
        Args:
            model_save_dir: 모델 저장 디렉토리
            test_size: 테스트 데이터 비율
            val_size: 검증 데이터 비율
            random_state: 랜덤 시드
        """
        self.model_save_dir = model_save_dir
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        
        # 디렉토리 생성
        os.makedirs(model_save_dir, exist_ok=True)
    
    def prepare_dnbp_training_data(
        self,
        df: pd.DataFrame,
        price_range_percent: float = 0.02
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        DNBP 모델 학습 데이터 준비
        
        Args:
            df: 학습 데이터 DataFrame (basis_prce, prdprc_rate 필수)
            price_range_percent: 예가범위 비율
            
        Returns:
            (X_train, X_test, y_train, y_test)
        """
        logger.info("DNBP 학습 데이터 준비 시작")
        
        X_list = []
        y_list = []
        
        dnbp = DNBPModel(price_range_percent=price_range_percent)
        
        for _, row in df.iterrows():
            basis_price = row['basis_prce']
            actual_rate = row['prdprc_rate']
            
            # 1. 15개 예비가격 생성
            reserve_prices = dnbp.generate_reserve_prices(basis_price)
            
            # 2. 6개 특징 추출
            features = dnbp.extract_optimized_features(reserve_prices, basis_price)
            
            # 3. 실제 예정가격으로부터 가장 가까운 예비가격 인덱스 찾기
            actual_price = basis_price * (actual_rate / 100)
            closest_idx = np.argmin(np.abs(reserve_prices - actual_price))
            
            X_list.append(features)
            y_list.append(closest_idx)
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        # One-hot encoding for classification
        y_onehot = np.zeros((len(y), 15))
        y_onehot[np.arange(len(y)), y] = 1
        
        # Train/Test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_onehot,
            test_size=self.test_size,
            random_state=self.random_state
        )
        
        logger.info(
            f"DNBP 데이터 준비 완료: "
            f"Train={len(X_train)}, Test={len(X_test)}"
        )
        
        return X_train, X_test, y_train, y_test
    
    def prepare_lstm_training_data(
        self,
        df: pd.DataFrame,
        sequence_length: int = 30,
        group_by: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        LSTM 모델 학습 데이터 준비
        
        Args:
            df: 학습 데이터 DataFrame (prdprc_rate, opengdt 필수)
            sequence_length: 시퀀스 길이
            group_by: 그룹화 기준 컬럼 (예: 'instt_nm', 'rgn_nm')
            
        Returns:
            (X_train, X_test, y_train, y_test)
        """
        logger.info("LSTM 학습 데이터 준비 시작")
        
        # 날짜 정렬
        df = df.sort_values('opengdt')
        
        X_list = []
        y_list = []
        
        lstm = LSTMModel(sequence_length=sequence_length)
        
        if group_by and group_by in df.columns:
            # 그룹별로 시퀀스 생성
            for group_name, group_df in df.groupby(group_by):
                if len(group_df) < sequence_length + 1:
                    continue  # 데이터 부족
                
                rates = group_df['prdprc_rate'].values
                X, y = lstm.prepare_sequences(rates, lookback=sequence_length)
                
                X_list.append(X)
                y_list.append(y)
        else:
            # 전체 데이터로 시퀀스 생성
            rates = df['prdprc_rate'].values
            X, y = lstm.prepare_sequences(rates, lookback=sequence_length)
            X_list.append(X)
            y_list.append(y)
        
        # 결합
        X = np.vstack(X_list) if len(X_list) > 1 else X_list[0]
        y = np.concatenate(y_list) if len(y_list) > 1 else y_list[0]
        
        # Train/Test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            shuffle=False  # 시계열 데이터는 순서 유지
        )
        
        logger.info(
            f"LSTM 데이터 준비 완료: "
            f"Train={len(X_train)}, Test={len(X_test)}"
        )
        
        return X_train, X_test, y_train, y_test
    
    def train_dnbp(
        self,
        df: pd.DataFrame,
        price_range_percent: float = 0.02,
        epochs: int = 100,
        batch_size: int = 32,
        save_model: bool = True
    ) -> Tuple[DNBPModel, Dict]:
        """
        DNBP 모델 학습
        
        Args:
            df: 학습 데이터 DataFrame
            price_range_percent: 예가범위 비율
            epochs: 에포크 수
            batch_size: 배치 크기
            save_model: 모델 저장 여부
            
        Returns:
            (trained_model, metrics)
        """
        logger.info("=" * 60)
        logger.info("DNBP 모델 학습 시작")
        logger.info("=" * 60)
        
        # 1. 데이터 준비
        X_train, X_test, y_train, y_test = self.prepare_dnbp_training_data(
            df, price_range_percent
        )
        
        # 2. Train/Val split
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train,
            test_size=self.val_size,
            random_state=self.random_state
        )
        
        # 3. 모델 생성 및 학습
        model = DNBPModel(price_range_percent=price_range_percent)
        
        history = model.train(
            X_train, y_train,
            X_val, y_val,
            epochs=epochs,
            batch_size=batch_size
        )
        
        # 4. 평가
        test_metrics = model.evaluate(X_test, y_test)
        
        # 5. 모델 저장
        if save_model:
            model_path = os.path.join(self.model_save_dir, "dnbp_model.h5")
            model.save_model(model_path)
        
        logger.info("DNBP 모델 학습 완료")
        
        return model, test_metrics
    
    def train_lstm(
        self,
        df: pd.DataFrame,
        sequence_length: int = 30,
        group_by: Optional[str] = None,
        epochs: int = 100,
        batch_size: int = 32,
        save_model: bool = True
    ) -> Tuple[LSTMModel, Dict]:
        """
        LSTM 모델 학습
        
        Args:
            df: 학습 데이터 DataFrame
            sequence_length: 시퀀스 길이
            group_by: 그룹화 기준
            epochs: 에포크 수
            batch_size: 배치 크기
            save_model: 모델 저장 여부
            
        Returns:
            (trained_model, metrics)
        """
        logger.info("=" * 60)
        logger.info("LSTM 모델 학습 시작")
        logger.info("=" * 60)
        
        # 1. 데이터 준비
        X_train, X_test, y_train, y_test = self.prepare_lstm_training_data(
            df, sequence_length, group_by
        )
        
        # 2. Train/Val split
        split_idx = int(len(X_train) * (1 - self.val_size))
        X_val = X_train[split_idx:]
        y_val = y_train[split_idx:]
        X_train = X_train[:split_idx]
        y_train = y_train[:split_idx]
        
        # 3. 모델 생성 및 학습
        model = LSTMModel(sequence_length=sequence_length)
        
        history = model.train(
            X_train, y_train,
            X_val, y_val,
            epochs=epochs,
            batch_size=batch_size
        )
        
        # 4. 평가
        test_metrics = model.evaluate(X_test, y_test)
        
        # 5. 모델 저장
        if save_model:
            model_path = os.path.join(self.model_save_dir, "lstm_model.h5")
            model.save_model(model_path)
        
        logger.info("LSTM 모델 학습 완료")
        
        return model, test_metrics
    
    def train_all(
        self,
        df: pd.DataFrame,
        price_range_percent: float = 0.02,
        sequence_length: int = 30,
        group_by: Optional[str] = None,
        epochs_dnbp: int = 100,
        epochs_lstm: int = 100,
        batch_size: int = 32
    ) -> Dict:
        """
        DNBP와 LSTM 모두 학습
        
        Args:
            df: 학습 데이터 DataFrame
            price_range_percent: 예가범위 비율
            sequence_length: LSTM 시퀀스 길이
            group_by: LSTM 그룹화 기준
            epochs_dnbp: DNBP 에포크 수
            epochs_lstm: LSTM 에포크 수
            batch_size: 배치 크기
            
        Returns:
            학습 결과 딕셔너리
        """
        logger.info("=" * 60)
        logger.info("전체 모델 학습 시작 (DNBP + LSTM)")
        logger.info("=" * 60)
        
        # 1. DNBP 학습
        dnbp_model, dnbp_metrics = self.train_dnbp(
            df,
            price_range_percent=price_range_percent,
            epochs=epochs_dnbp,
            batch_size=batch_size,
            save_model=True
        )
        
        # 2. LSTM 학습
        lstm_model, lstm_metrics = self.train_lstm(
            df,
            sequence_length=sequence_length,
            group_by=group_by,
            epochs=epochs_lstm,
            batch_size=batch_size,
            save_model=True
        )
        
        results = {
            'dnbp': {
                'model': dnbp_model,
                'metrics': dnbp_metrics
            },
            'lstm': {
                'model': lstm_model,
                'metrics': lstm_metrics
            },
            'training_samples': len(df),
            'model_save_dir': self.model_save_dir
        }
        
        logger.info("=" * 60)
        logger.info("전체 모델 학습 완료")
        logger.info(f"DNBP 성능: {dnbp_metrics}")
        logger.info(f"LSTM 성능: {lstm_metrics}")
        logger.info("=" * 60)
        
        return results
    
    def load_trained_models(
        self,
        dnbp_path: Optional[str] = None,
        lstm_path: Optional[str] = None
    ) -> Tuple[Optional[DNBPModel], Optional[LSTMModel]]:
        """
        저장된 모델 로드
        
        Args:
            dnbp_path: DNBP 모델 경로
            lstm_path: LSTM 모델 경로
            
        Returns:
            (dnbp_model, lstm_model)
        """
        dnbp_model = None
        lstm_model = None
        
        # DNBP 모델 로드
        if dnbp_path is None:
            dnbp_path = os.path.join(self.model_save_dir, "dnbp_model.h5")
        
        if os.path.exists(dnbp_path):
            dnbp_model = DNBPModel(model_path=dnbp_path)
            logger.info(f"DNBP 모델 로드 완료: {dnbp_path}")
        else:
            logger.warning(f"DNBP 모델을 찾을 수 없음: {dnbp_path}")
        
        # LSTM 모델 로드
        if lstm_path is None:
            lstm_path = os.path.join(self.model_save_dir, "lstm_model.h5")
        
        if os.path.exists(lstm_path):
            lstm_model = LSTMModel(model_path=lstm_path)
            logger.info(f"LSTM 모델 로드 완료: {lstm_path}")
        else:
            logger.warning(f"LSTM 모델을 찾을 수 없음: {lstm_path}")
        
        return dnbp_model, lstm_model
