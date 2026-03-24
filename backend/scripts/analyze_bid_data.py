"""
입찰 데이터 분석 및 시각화
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("📊 실제 입찰 데이터 분석 시작!")
print("=" * 80)
print()

# 데이터 로드
with open('/tmp/sample_bid_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# DataFrame 변환
df_bids = pd.DataFrame(data['bids'])
df_results = pd.DataFrame(data['results'])

print("📁 데이터 로드 완료:")
print(f"   입찰공고: {len(df_bids)}건")
print(f"   낙찰결과: {len(df_results)}건")
print()

# ============================================================
# 1. 기본 통계 분석
# ============================================================
print("=" * 80)
print("1️⃣ 기본 통계 분석")
print("=" * 80)
print()

print("📊 입찰공고 통계:")
print(f"   총 공고 수: {len(df_bids):,}건")
print(f"   평균 기초금액: {df_bids['basisPrce'].mean():,.0f}원")
print(f"   중간값: {df_bids['basisPrce'].median():,.0f}원")
print(f"   최소: {df_bids['basisPrce'].min():,.0f}원")
print(f"   최대: {df_bids['basisPrce'].max():,.0f}원")
print()

print("📊 낙찰결과 통계:")
print(f"   총 낙찰 수: {len(df_results):,}건")
print(f"   평균 사정률: {df_results['prdprcRate'].mean():.2f}%")
print(f"   표준편차: {df_results['prdprcRate'].std():.2f}%")
print(f"   최소 사정률: {df_results['prdprcRate'].min():.2f}%")
print(f"   최대 사정률: {df_results['prdprcRate'].max():.2f}%")
print()
print(f"   평균 낙찰율: {df_results['sucsfbidRate'].mean():.2f}%")
print(f"   표준편차: {df_results['sucsfbidRate'].std():.2f}%")
print()

# ============================================================
# 2. 지역별 분석
# ============================================================
print("=" * 80)
print("2️⃣ 지역별 분석")
print("=" * 80)
print()

# 입찰공고와 낙찰결과 병합
df_merged = pd.merge(
    df_bids,
    df_results,
    on='bidNtceNo',
    how='inner',
    suffixes=('_bid', '_result')
)

regional_stats = df_merged.groupby('rgnNm').agg({
    'bidNtceNo': 'count',
    'prdprcRate': ['mean', 'std'],
    'basisPrce': 'mean'
}).round(2)

regional_stats.columns = ['입찰건수', '평균사정률', '사정률표준편차', '평균기초금액']
regional_stats = regional_stats.sort_values('입찰건수', ascending=False)

print("📍 지역별 통계 (Top 10):")
print("-" * 80)
print(regional_stats.head(10).to_string())
print()

# ============================================================
# 3. 발주기관별 분석
# ============================================================
print("=" * 80)
print("3️⃣ 발주기관별 분석")
print("=" * 80)
print()

institution_stats = df_merged.groupby('ntceInsttNm').agg({
    'bidNtceNo': 'count',
    'prdprcRate': ['mean', 'std'],
    'sucsfbidRate': 'mean',
    'basisPrce': 'mean'
}).round(2)

institution_stats.columns = ['입찰건수', '평균사정률', '사정률표준편차', '평균낙찰율', '평균기초금액']
institution_stats = institution_stats.sort_values('입찰건수', ascending=False)

print("🏢 발주기관별 통계 (Top 10):")
print("-" * 80)
print(institution_stats.head(10).to_string())
print()

# ============================================================
# 4. 업종별 분석
# ============================================================
print("=" * 80)
print("4️⃣ 업종별 분석")
print("=" * 80)
print()

industry_stats = df_merged.groupby('indutyTyNm').agg({
    'bidNtceNo': 'count',
    'prdprcRate': ['mean', 'std'],
    'basisPrce': 'mean'
}).round(2)

industry_stats.columns = ['입찰건수', '평균사정률', '사정률표준편차', '평균기초금액']
industry_stats = industry_stats.sort_values('입찰건수', ascending=False)

print("🏭 업종별 통계:")
print("-" * 80)
print(industry_stats.to_string())
print()

# ============================================================
# 5. 사정률 분포 분석
# ============================================================
print("=" * 80)
print("5️⃣ 사정률 분포 분석")
print("=" * 80)
print()

# 구간별 분포
bins = [95, 97, 99, 101, 103, 105]
labels = ['95-97%', '97-99%', '99-101%', '101-103%', '103-105%']
df_results['rate_range'] = pd.cut(df_results['prdprcRate'], bins=bins, labels=labels)

distribution = df_results['rate_range'].value_counts().sort_index()

print("📊 사정률 구간별 분포:")
print("-" * 80)
for range_label, count in distribution.items():
    percentage = (count / len(df_results)) * 100
    bar = '█' * int(percentage / 2)
    print(f"   {range_label:12} {count:3}건 ({percentage:5.1f}%) {bar}")
print()

# ============================================================
# 6. AI 예측을 위한 Feature 분석
# ============================================================
print("=" * 80)
print("6️⃣ AI 예측용 Feature 분석")
print("=" * 80)
print()

# 기관별 과거 사정률 (AI 학습용 Feature)
institution_history = df_results.groupby('ntceInsttNm')['prdprcRate'].agg(['mean', 'std', 'count'])
institution_history.columns = ['평균사정률', '표준편차', '데이터수']
institution_history = institution_history[institution_history['데이터수'] >= 3]  # 최소 3건 이상

print("🎯 AI 학습 가능한 기관 (최소 3건 이상):")
print(f"   총 {len(institution_history)}개 기관")
print()
print("   상위 5개 기관:")
print("-" * 80)
print(institution_history.nlargest(5, '데이터수').round(2).to_string())
print()

# 금액대별 사정률 평균
df_merged['price_range'] = pd.cut(
    df_merged['basisPrce'],
    bins=[0, 100_000_000, 1_000_000_000, 5_000_000_000, 10_000_000_000],
    labels=['1억 미만', '1억~10억', '10억~50억', '50억 이상']
)

price_range_stats = df_merged.groupby('price_range')['prdprcRate'].agg(['mean', 'std', 'count'])
price_range_stats.columns = ['평균사정률', '표준편차', '건수']

print("💰 금액대별 사정률:")
print("-" * 80)
print(price_range_stats.round(2).to_string())
print()

# ============================================================
# 7. 예측 정확도 목표 설정
# ============================================================
print("=" * 80)
print("7️⃣ AI 예측 모델 목표")
print("=" * 80)
print()

target_std = df_results['prdprcRate'].std()
target_mae = target_std * 0.5  # 표준편차의 50%를 MAE 목표로

print("🎯 AI 모델 성능 목표:")
print(f"   사정률 표준편차: {target_std:.2f}%")
print(f"   목표 MAE: <{target_mae:.2f}% (표준편차의 50%)")
print(f"   목표 정확도: ±0.10% 이내 예측")
print()

# ============================================================
# 8. 샘플 예측 시나리오
# ============================================================
print("=" * 80)
print("8️⃣ AI 예측 시나리오 예시")
print("=" * 80)
print()

# 랜덤으로 5건 선택
sample = df_merged.sample(n=min(5, len(df_merged)))

print("🤖 AI 예측 샘플 (실제 vs 예측):")
print("-" * 80)

for idx, row in sample.iterrows():
    # 같은 기관의 과거 평균으로 단순 예측
    inst_avg = df_results[df_results['ntceInsttNm'] == row['ntceInsttNm']]['prdprcRate'].mean()
    predicted_rate = inst_avg if not pd.isna(inst_avg) else 100.0
    
    actual_rate = row['prdprcRate']
    error = abs(predicted_rate - actual_rate)
    
    print(f"공고: {row['bidNtceNm'][:30]}...")
    print(f"   기관: {row['ntceInsttNm']}")
    print(f"   실제 사정률: {actual_rate:.2f}%")
    print(f"   예측 사정률: {predicted_rate:.2f}%")
    print(f"   예측 오차: {error:.2f}%p")
    print()

# ============================================================
# 요약
# ============================================================
print("=" * 80)
print("✅ 분석 완료!")
print("=" * 80)
print()
print("📋 요약:")
print(f"   총 분석 데이터: {len(df_merged)}건")
print(f"   분석 지역: {df_merged['rgnNm'].nunique()}개")
print(f"   분석 기관: {df_merged['ntceInsttNm'].nunique()}개")
print(f"   분석 업종: {df_merged['indutyTyNm'].nunique()}개")
print()
print("🚀 다음 단계:")
print("   1. DNBP 모델 학습")
print("   2. LSTM 모델 학습")
print("   3. Ensemble 모델 구축")
print("   4. 실시간 예측 API 제공")
print()
print("=" * 80)
