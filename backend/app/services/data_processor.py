"""
데이터 전처리 및 정제 서비스
"""
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models.bid import BidAnnouncement
from ..models.result import BidResult

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    수집된 데이터의 전처리, 정제, 특징 엔지니어링
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def clean_bid_results(self, min_basis_price: int = 1000000) -> int:
        """
        낙찰결과 데이터 정제
        
        - 결측치 제거
        - 이상치 탐지 및 처리
        - 잘못된 사정률 데이터 제거
        
        Args:
            min_basis_price: 최소 기초금액 (기본값: 100만원)
            
        Returns:
            정제된 레코드 수
        """
        try:
            # 1. 필수 필드가 NULL인 데이터 조회
            invalid_records = self.db.query(BidResult).filter(
                (BidResult.prdprc.is_(None)) |
                (BidResult.basis_prce.is_(None)) |
                (BidResult.sucsfbid_amt.is_(None))
            ).all()
            
            logger.info(f"필수 필드 누락 데이터: {len(invalid_records)}건")
            
            # 2. 기초금액이 너무 작은 데이터
            small_price_records = self.db.query(BidResult).filter(
                BidResult.basis_prce < min_basis_price
            ).all()
            
            logger.info(f"기초금액 너무 작음: {len(small_price_records)}건")
            
            # 3. 사정률이 정상 범위를 벗어난 데이터 (일반적으로 95% ~ 105%)
            abnormal_rate_records = self.db.query(BidResult).filter(
                (BidResult.prdprc_rate < 95.0) |
                (BidResult.prdprc_rate > 105.0)
            ).all()
            
            logger.info(f"사정률 이상: {len(abnormal_rate_records)}건")
            
            # 4. 사정률 재계산 및 검증
            recalculated_count = 0
            for result in self.db.query(BidResult).filter(
                BidResult.prdprc.isnot(None),
                BidResult.basis_prce.isnot(None),
                BidResult.basis_prce > 0
            ).all():
                calculated_rate = (result.prdprc / result.basis_prce) * 100
                
                # 기존 사정률과 차이가 크면 재계산값으로 업데이트
                if result.prdprc_rate is None or abs(result.prdprc_rate - calculated_rate) > 0.5:
                    result.prdprc_rate = round(calculated_rate, 4)
                    recalculated_count += 1
                
                # 투찰률 재계산
                if result.prdprc > 0:
                    calculated_bid_rate = (result.sucsfbid_amt / result.prdprc) * 100
                    if result.sucsfbid_rate is None or abs(result.sucsfbid_rate - calculated_bid_rate) > 0.5:
                        result.sucsfbid_rate = round(calculated_bid_rate, 4)
            
            self.db.commit()
            logger.info(f"사정률 재계산: {recalculated_count}건")
            
            # 5. 중복 데이터 제거 (같은 bid_ntce_no가 여러 개인 경우)
            duplicates = self.db.query(
                BidResult.bid_ntce_no,
                func.count(BidResult.id).label('count')
            ).group_by(BidResult.bid_ntce_no).having(func.count(BidResult.id) > 1).all()
            
            removed_duplicates = 0
            for dup in duplicates:
                # 가장 최신 데이터만 남기고 나머지 삭제
                records = self.db.query(BidResult).filter(
                    BidResult.bid_ntce_no == dup.bid_ntce_no
                ).order_by(BidResult.created_at.desc()).all()
                
                for record in records[1:]:  # 첫 번째(최신)를 제외하고 삭제
                    self.db.delete(record)
                    removed_duplicates += 1
            
            self.db.commit()
            logger.info(f"중복 데이터 제거: {removed_duplicates}건")
            
            return recalculated_count + removed_duplicates
            
        except Exception as e:
            logger.error(f"데이터 정제 중 오류: {e}")
            self.db.rollback()
            return 0
    
    def extract_features_for_prediction(
        self,
        bid_announcement: BidAnnouncement,
        lookback_days: int = 365
    ) -> Dict:
        """
        AI 예측을 위한 특징 추출
        
        Args:
            bid_announcement: 예측할 입찰공고
            lookback_days: 과거 데이터 조회 기간 (일)
            
        Returns:
            특징 딕셔너리
        """
        features = {
            'basis_prce': bid_announcement.basis_prce,
            'presmpt_prce': bid_announcement.presmpt_prce,
            'instt_nm': bid_announcement.instt_nm,
            'rgn_nm': bid_announcement.rgn_nm,
            'induty_ty_nm': bid_announcement.induty_ty_nm,
            'bid_methd_nm': bid_announcement.bid_methd_nm
        }
        
        # 1. 발주기관 과거 통계
        instt_stats = self._get_institution_statistics(
            bid_announcement.instt_nm,
            lookback_days
        )
        features.update(instt_stats)
        
        # 2. 지역 과거 통계
        region_stats = self._get_region_statistics(
            bid_announcement.rgn_nm,
            lookback_days
        )
        features.update(region_stats)
        
        # 3. 업종 과거 통계
        industry_stats = self._get_industry_statistics(
            bid_announcement.induty_ty_nm,
            lookback_days
        )
        features.update(industry_stats)
        
        # 4. 기초금액 구간별 통계
        price_range_stats = self._get_price_range_statistics(
            bid_announcement.basis_prce,
            lookback_days
        )
        features.update(price_range_stats)
        
        # 5. 유사 케이스 찾기
        similar_cases = self._find_similar_cases(bid_announcement, lookback_days)
        features['similar_cases_count'] = len(similar_cases)
        
        if similar_cases:
            features['similar_cases_avg_rate'] = np.mean([c.prdprc_rate for c in similar_cases])
            features['similar_cases_std_rate'] = np.std([c.prdprc_rate for c in similar_cases])
        else:
            features['similar_cases_avg_rate'] = None
            features['similar_cases_std_rate'] = None
        
        return features
    
    def _get_institution_statistics(
        self,
        instt_nm: str,
        lookback_days: int
    ) -> Dict:
        """
        발주기관별 과거 통계
        """
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        results = self.db.query(BidResult).filter(
            and_(
                BidResult.instt_nm == instt_nm,
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).all()
        
        if not results:
            return {
                'instt_historical_avg_rate': None,
                'instt_historical_std_rate': None,
                'instt_historical_min_rate': None,
                'instt_historical_max_rate': None,
                'instt_historical_count': 0
            }
        
        rates = [r.prdprc_rate for r in results]
        
        return {
            'instt_historical_avg_rate': float(np.mean(rates)),
            'instt_historical_std_rate': float(np.std(rates)),
            'instt_historical_min_rate': float(np.min(rates)),
            'instt_historical_max_rate': float(np.max(rates)),
            'instt_historical_count': len(results)
        }
    
    def _get_region_statistics(
        self,
        rgn_nm: str,
        lookback_days: int
    ) -> Dict:
        """
        지역별 과거 통계
        """
        if not rgn_nm:
            return {
                'rgn_historical_avg_rate': None,
                'rgn_historical_count': 0
            }
        
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        results = self.db.query(BidResult).filter(
            and_(
                BidResult.rgn_nm == rgn_nm,
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).all()
        
        if not results:
            return {
                'rgn_historical_avg_rate': None,
                'rgn_historical_count': 0
            }
        
        rates = [r.prdprc_rate for r in results]
        
        return {
            'rgn_historical_avg_rate': float(np.mean(rates)),
            'rgn_historical_count': len(results)
        }
    
    def _get_industry_statistics(
        self,
        induty_ty_nm: str,
        lookback_days: int
    ) -> Dict:
        """
        업종별 과거 통계
        """
        if not induty_ty_nm:
            return {
                'induty_historical_avg_rate': None,
                'induty_historical_count': 0
            }
        
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        results = self.db.query(BidResult).filter(
            and_(
                BidResult.induty_ty_nm == induty_ty_nm,
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).all()
        
        if not results:
            return {
                'induty_historical_avg_rate': None,
                'induty_historical_count': 0
            }
        
        rates = [r.prdprc_rate for r in results]
        
        return {
            'induty_historical_avg_rate': float(np.mean(rates)),
            'induty_historical_count': len(results)
        }
    
    def _get_price_range_statistics(
        self,
        basis_prce: int,
        lookback_days: int
    ) -> Dict:
        """
        기초금액 구간별 통계
        """
        if not basis_prce:
            return {
                'price_range_avg_rate': None,
                'price_range_count': 0
            }
        
        # 기초금액 ±20% 범위
        min_price = basis_prce * 0.8
        max_price = basis_prce * 1.2
        
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        results = self.db.query(BidResult).filter(
            and_(
                BidResult.basis_prce >= min_price,
                BidResult.basis_prce <= max_price,
                BidResult.opengdt >= start_date,
                BidResult.prdprc_rate.isnot(None)
            )
        ).all()
        
        if not results:
            return {
                'price_range_avg_rate': None,
                'price_range_count': 0
            }
        
        rates = [r.prdprc_rate for r in results]
        
        return {
            'price_range_avg_rate': float(np.mean(rates)),
            'price_range_count': len(results)
        }
    
    def _find_similar_cases(
        self,
        bid_announcement: BidAnnouncement,
        lookback_days: int,
        max_cases: int = 100
    ) -> List[BidResult]:
        """
        유사한 입찰 케이스 찾기
        
        - 같은 발주기관
        - 같은 지역
        - 같은 업종
        - 유사한 기초금액 (±30%)
        """
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        # 기초금액 범위
        if bid_announcement.basis_prce:
            min_price = bid_announcement.basis_prce * 0.7
            max_price = bid_announcement.basis_prce * 1.3
        else:
            min_price = 0
            max_price = float('inf')
        
        # 쿼리 조건 생성
        filters = [
            BidResult.opengdt >= start_date,
            BidResult.prdprc_rate.isnot(None)
        ]
        
        if bid_announcement.instt_nm:
            filters.append(BidResult.instt_nm == bid_announcement.instt_nm)
        
        if bid_announcement.rgn_nm:
            filters.append(BidResult.rgn_nm == bid_announcement.rgn_nm)
        
        if bid_announcement.induty_ty_nm:
            filters.append(BidResult.induty_ty_nm == bid_announcement.induty_ty_nm)
        
        if bid_announcement.basis_prce:
            filters.append(BidResult.basis_prce >= min_price)
            filters.append(BidResult.basis_prce <= max_price)
        
        similar_cases = self.db.query(BidResult).filter(
            and_(*filters)
        ).order_by(BidResult.opengdt.desc()).limit(max_cases).all()
        
        return similar_cases
    
    def get_training_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_basis_price: int = 1000000
    ) -> pd.DataFrame:
        """
        AI 모델 학습용 데이터셋 생성
        
        Args:
            start_date: 데이터 시작일
            end_date: 데이터 종료일
            min_basis_price: 최소 기초금액
            
        Returns:
            pandas DataFrame
        """
        # 기본값: 최근 2년 데이터
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=730)
        
        # 쿼리 실행
        results = self.db.query(BidResult).filter(
            and_(
                BidResult.opengdt >= start_date,
                BidResult.opengdt <= end_date,
                BidResult.basis_prce >= min_basis_price,
                BidResult.prdprc_rate.isnot(None),
                BidResult.prdprc.isnot(None)
            )
        ).order_by(BidResult.opengdt).all()
        
        # DataFrame 변환
        data = []
        for result in results:
            data.append({
                'id': result.id,
                'bid_ntce_no': result.bid_ntce_no,
                'basis_prce': result.basis_prce,
                'presmpt_prce': result.presmpt_prce,
                'prdprc': result.prdprc,
                'prdprc_rate': result.prdprc_rate,
                'sucsfbid_amt': result.sucsfbid_amt,
                'sucsfbid_rate': result.sucsfbid_rate,
                'instt_nm': result.instt_nm,
                'rgn_nm': result.rgn_nm,
                'induty_ty_nm': result.induty_ty_nm,
                'bid_methd_nm': result.bid_methd_nm,
                'opengdt': result.opengdt,
                'bidder_count': result.bidder_count
            })
        
        df = pd.DataFrame(data)
        
        logger.info(f"학습 데이터셋 생성: {len(df)}건")
        
        return df
    
    def get_time_series_data(
        self,
        instt_nm: Optional[str] = None,
        rgn_nm: Optional[str] = None,
        lookback_days: int = 365,
        sequence_length: int = 30
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        LSTM 학습용 시계열 데이터 생성
        
        Args:
            instt_nm: 발주기관명 (특정 기관만 조회)
            rgn_nm: 지역명 (특정 지역만 조회)
            lookback_days: 조회 기간
            sequence_length: 시퀀스 길이
            
        Returns:
            (X, y) 튜플 - X: 입력 시퀀스, y: 타겟 사정률
        """
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        filters = [
            BidResult.opengdt >= start_date,
            BidResult.prdprc_rate.isnot(None)
        ]
        
        if instt_nm:
            filters.append(BidResult.instt_nm == instt_nm)
        if rgn_nm:
            filters.append(BidResult.rgn_nm == rgn_nm)
        
        results = self.db.query(BidResult).filter(
            and_(*filters)
        ).order_by(BidResult.opengdt).all()
        
        if len(results) < sequence_length + 1:
            logger.warning(f"시계열 데이터 부족: {len(results)}건")
            return np.array([]), np.array([])
        
        # 사정률만 추출
        rates = np.array([r.prdprc_rate for r in results])
        
        # 시퀀스 생성
        X, y = [], []
        for i in range(len(rates) - sequence_length):
            X.append(rates[i:i+sequence_length])
            y.append(rates[i+sequence_length])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"시계열 데이터 생성: X shape={X.shape}, y shape={y.shape}")
        
        return X, y
