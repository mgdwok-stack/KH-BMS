/**
 * TypeScript 타입 정의
 */

export interface BidAnnouncement {
  id: number;
  bid_ntce_no: string;
  bid_ntce_ord?: number;
  bid_ntce_nm?: string;
  instt_nm?: string;
  dminstt_nm?: string;
  rgn_nm?: string;
  induty_ty_nm?: string;
  cntrct_cnclsmt_mth_nm?: string;
  bid_mthd_nm?: string;
  presmpt_prce?: number;
  basis_prce?: number;
  asign_bdgt_amt?: number;
  bid_begin_dt?: string;
  bid_close_dt?: string;
  openg_dt?: string;
  bid_status?: string;
  ntce_instt_cd?: string;
  rbid_perm_yn?: string;
  srch_value?: string;
  created_at: string;
  updated_at: string;
}

export interface BidResult {
  id: number;
  bid_ntce_no: string;
  bid_ntce_ord?: number;
  instt_nm?: string;
  dminstt_nm?: string;
  presmpt_prce?: number;
  openg_dt?: string;
  opengcorpinfo?: string;
  bidprc?: number;
  sucsfbid_amt?: number;
  sucsfbid_rate?: number;
  prdprc?: number;
  prdprc_rate?: number;
  sucsfbid_lwr_lmt_rt?: number;
  created_at: string;
  updated_at: string;
}

export interface PredictionResponse {
  bid_ntce_no: string;
  basis_prce: number;
  final_predicted_rate: number;
  predicted_prdprc: number;
  recommended_bid_amt: number;
  recommended_bid_rate: number;
  dnbp_predicted_rate?: number;
  dnbp_confidence?: number;
  dnbp_top4_rates?: number[];
  lstm_predicted_rate?: number;
  lstm_confidence?: number;
  prediction_range_min: number;
  prediction_range_max: number;
  similar_cases_count?: number;
  institution_avg_rate?: number;
  region_avg_rate?: number;
  model_version?: string;
  prediction_timestamp?: string;
}

export interface BidDetail {
  announcement: BidAnnouncement;
  prediction?: PredictionResponse;
  similar_cases: BidResult[];
  historical_stats?: {
    instt_historical_count: number;
    instt_historical_avg_rate: number;
    instt_historical_std_rate: number;
    rgn_historical_count: number;
    rgn_historical_avg_rate: number;
    induty_historical_count: number;
    induty_historical_avg_rate: number;
  };
}

export interface FilterOptions {
  regions: Array<{ name: string; count: number }>;
  industries: Array<{ name: string; count: number }>;
  institutions: Array<{ name: string; count: number }>;
}

export interface DashboardSummary {
  total_statistics: {
    total_announcements: number;
    total_results: number;
    total_predictions: number;
    overall_avg_rate: number;
  };
  recent_30_days: {
    results_count: number;
    avg_rate: number;
  };
  ai_performance: {
    validated_predictions: number;
    avg_prediction_error: number;
    accuracy_rate: number;
  };
}

export interface TrendData {
  period_days: number;
  daily_trends: Array<{
    date: string;
    count: number;
    avg_rate: number;
    std_rate: number;
  }>;
  regional_stats: Array<{
    region: string;
    count: number;
    avg_rate: number;
  }>;
  industry_stats: Array<{
    industry: string;
    count: number;
    avg_rate: number;
  }>;
}

export interface HistogramData {
  period_days: number;
  total_count: number;
  mean_rate: number;
  median_rate: number;
  std_rate: number;
  histogram: Array<{
    range_min: number;
    range_max: number;
    count: number;
    percentage: number;
  }>;
}
