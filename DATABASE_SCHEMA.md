# Database Schema Documentation

## Overview
This document describes the database schema for the Bid-Bot Clone AI bidding analysis solution. The database is designed to store procurement data from Korea's Public Procurement Service API and AI prediction results.

## Entity Relationship Diagram

```
┌─────────────────────────────┐
│   bid_announcements         │
│  (입찰공고 정보)              │
├─────────────────────────────┤
│ PK: id                      │
│ UK: bid_ntce_no             │
│     bid_ntce_nm             │
│     instt_nm                │
│     basis_prce              │
│     presmpt_prce            │
│     bid_clsedt              │
│     rgn_nm                  │
│     induty_ty_nm            │
│     bid_status              │
│     ...                     │
└──────────┬──────────────────┘
           │ 1
           │
           │ N
┌──────────┴──────────────────┐
│   bid_results               │
│  (낙찰결과 정보)              │
├─────────────────────────────┤
│ PK: id                      │
│ FK: bid_announcement_id     │
│     bid_ntce_no             │
│     prdprc (예정가격)        │
│     basis_prce              │
│     sucsfbid_amt (낙찰금액)  │
│     prdprc_rate (사정률)    │
│     sucsfbid_rate (투찰률)  │
│     instt_nm                │
│     opengdt                 │
│     ...                     │
└─────────────────────────────┘

┌──────────┬──────────────────┐
│   predictions               │
│  (AI 예측 결과)              │
├─────────────────────────────┤
│ PK: id                      │
│ FK: bid_announcement_id     │
│     bid_ntce_no             │
│     dnbp_predicted_rate     │
│     lstm_predicted_rate     │
│     final_predicted_rate    │
│     predicted_prdprc        │
│     recommended_bid_amt     │
│     actual_prdprc_rate      │
│     prediction_error        │
│     ...                     │
└─────────────────────────────┘

┌─────────────────────────────┐
│   user_preferences          │
│  (사용자 설정)                │
├─────────────────────────────┤
│ PK: id                      │
│ UK: user_id, username       │
│     preferred_regions       │
│     preferred_industries    │
│     licenses                │
│     min_basis_price         │
│     max_basis_price         │
│     ...                     │
└─────────────────────────────┘
```

## Tables

### 1. bid_announcements (입찰공고 정보)
Stores bid announcement data from the Procurement Service API.

**Purpose**: Store basic bid announcement information

**Key Columns**:
- `bid_ntce_no`: Unique bid notice number (입찰공고번호)
- `basis_prce`: Base price (기초금액) - Critical for AI prediction
- `presmpt_prce`: Estimated price (추정가격)
- `bid_methd_nm`: Bidding method (입찰방식명)
- `instt_nm`: Announcing institution (공고기관명)
- `rgn_nm`: Region name (지역명)
- `induty_ty_nm`: Industry type (업종유형명)
- `bid_status`: Bid status (announced/opened/cancelled)

**Indexes**:
- `bid_ntce_no` (unique)
- `instt_nm`, `bid_clsedt` (composite)
- `rgn_nm`, `induty_ty_nm` (composite)
- `bid_status`, `created_at` (composite)

### 2. bid_results (낙찰결과 정보)
Stores successful bid results - the core dataset for AI model training.

**Purpose**: Store actual bid results for ML model training

**Key Columns**:
- `bid_announcement_id`: Foreign key to bid_announcements
- `prdprc`: Predetermined price (예정가격) - Target for DNBP prediction
- `basis_prce`: Base price (기초금액)
- `sucsfbid_amt`: Successful bid amount (낙찰금액)
- `prdprc_rate`: Predetermined price rate (사정률) - **Primary prediction target**
- `sucsfbid_rate`: Successful bid rate (투찰률)
- `drawn_reserve_prices`: Drawn reserve price numbers (1-15)
- `opengdt`: Opening date (개찰일시)

**Key Metrics Formulas**:
```
사정률 (prdprc_rate) = (예정가격 / 기초금액) × 100
투찰률 (sucsfbid_rate) = (낙찰금액 / 예정가격) × 100
```

**Indexes**:
- `bid_ntce_no`
- `instt_nm`, `opengdt` (composite)
- `rgn_nm`, `induty_ty_nm`, `opengdt` (composite)
- `prdprc_rate`, `sucsfbid_rate`, `opengdt` (composite)

### 3. predictions (AI 예측 결과)
Stores AI model predictions for bid rates.

**Purpose**: Store and track AI prediction results

**Key Columns**:
- `bid_announcement_id`: Foreign key to bid_announcements
- `dnbp_predicted_rate`: DNBP model prediction
- `dnbp_top4_rates`: Top 4 predicted rates from DNBP
- `lstm_predicted_rate`: LSTM model prediction
- `final_predicted_rate`: Ensemble final prediction
- `predicted_prdprc`: Predicted predetermined price
- `recommended_bid_amt`: Recommended bid amount
- `actual_prdprc_rate`: Actual rate (updated after opening)
- `prediction_error`: Absolute prediction error

**Prediction Flow**:
```
Input: basis_prce (기초금액)
  ↓
DNBP Model → Top 4 rates → Average → dnbp_predicted_rate
  ↓
LSTM Model → Pattern analysis → lstm_predicted_rate
  ↓
Ensemble (weighted average) → final_predicted_rate
  ↓
Calculate: predicted_prdprc = basis_prce × (final_predicted_rate / 100)
  ↓
Calculate: recommended_bid_amt = predicted_prdprc × 0.87745
```

### 4. user_preferences (사용자 설정)
Stores user-specific filter preferences and settings.

**Purpose**: Personalize bid filtering and notifications

**Key Columns**:
- `user_id`: Unique user identifier
- `preferred_regions`: Preferred regions (JSON array)
- `preferred_industries`: Preferred industries (JSON array)
- `licenses`: User licenses (JSON array)
- `min_basis_price`, `max_basis_price`: Price range filters
- `notification_enabled`: Enable/disable notifications
- `ai_prediction_enabled`: Enable/disable AI predictions

## Data Flow

### 1. Data Collection Flow
```
Procurement API
  ↓
data_collector.py (Celery task)
  ↓
bid_announcements table
  ↓ (after opening)
bid_results table
```

### 2. AI Prediction Flow
```
User requests prediction
  ↓
Load bid_announcement data
  ↓
Query historical bid_results (similar cases)
  ↓
DNBP Model inference
  ↓
LSTM Model inference
  ↓
Ensemble combination
  ↓
Save to predictions table
  ↓
Return to user
```

### 3. Model Training Flow
```
Query bid_results (historical data)
  ↓
Data preprocessing
  ↓
Feature engineering
  ↓
Train DNBP model
  ↓
Train LSTM model
  ↓
Validate on test set
  ↓
Save trained models
```

## Query Patterns

### Most Common Queries

1. **Get recent bid announcements with filters**
```sql
SELECT * FROM bid_announcements
WHERE bid_status = 'announced'
  AND rgn_nm = '서울특별시'
  AND induty_ty_nm LIKE '%건설%'
  AND basis_prce BETWEEN 100000000 AND 1000000000
ORDER BY bid_clsedt ASC
LIMIT 50;
```

2. **Get historical bid results for training**
```sql
SELECT * FROM bid_results
WHERE instt_nm = '국토교통부'
  AND opengdt >= '2023-01-01'
ORDER BY opengdt DESC;
```

3. **Get prediction accuracy metrics**
```sql
SELECT 
  AVG(prediction_error) as avg_error,
  STDDEV(prediction_error) as std_error,
  COUNT(*) as total_predictions
FROM predictions
WHERE prediction_status = 'validated'
  AND predicted_at >= NOW() - INTERVAL '30 days';
```

## Performance Considerations

### Indexes
- All foreign keys are indexed
- Composite indexes on frequently queried column combinations
- Date columns are indexed for time-based queries

### Partitioning (Future)
- Consider partitioning `bid_results` by `opengdt` (monthly/quarterly)
- Consider partitioning `predictions` by `predicted_at`

### Data Retention
- Keep `bid_announcements` for 2 years
- Keep `bid_results` indefinitely (training data)
- Archive `predictions` older than 1 year

## Security

### Data Privacy
- User information in `user_preferences` should be encrypted
- API keys stored in environment variables, not in database

### Access Control
- Implement row-level security for user-specific data
- Separate read-only and read-write database users

## Backup Strategy

1. **Full Backup**: Daily at 2 AM
2. **Incremental Backup**: Every 6 hours
3. **Retention**: 30 days for full backups, 7 days for incremental

## Migration Strategy

Using Alembic for database migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Future Enhancements

1. Add `bid_participants` table to track all bidders
2. Add `model_performance` table to track model metrics over time
3. Add `audit_log` table for tracking data changes
4. Implement time-series database (TimescaleDB) for better performance
