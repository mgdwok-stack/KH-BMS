/**
 * API 서비스 레이어
 */
import axios from 'axios';
import type {
  BidAnnouncement,
  BidResult,
  BidDetail,
  PredictionResponse,
  FilterOptions,
  DashboardSummary,
  TrendData,
  HistogramData,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    // 필요시 인증 토큰 추가
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// 입찰공고 API
export const bidApi = {
  // 입찰공고 목록 조회
  getBids: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    instt_nm?: string;
    rgn_nm?: string;
    induty_ty_nm?: string;
    min_basis_price?: number;
    max_basis_price?: number;
  }) => {
    const response = await apiClient.get<{
      total: number;
      page: number;
      page_size: number;
      items: BidAnnouncement[];
    }>('/bids/', { params });
    return response.data;
  },

  // 입찰공고 상세 조회
  getBidDetail: async (bidId: number, includePrediction: boolean = true) => {
    const response = await apiClient.get<BidDetail>(`/bids/${bidId}`, {
      params: { include_prediction: includePrediction },
    });
    return response.data;
  },

  // 필터 옵션 조회
  getFilterOptions: async () => {
    const response = await apiClient.get<FilterOptions>('/bids/search/filters');
    return response.data;
  },

  // 낙찰결과 목록 조회
  getBidResults: async (params?: {
    page?: number;
    page_size?: number;
    instt_nm?: string;
  }) => {
    const response = await apiClient.get<BidResult[]>('/bids/results/', { params });
    return response.data;
  },
};

// AI 예측 API
export const predictionApi = {
  // 사정률 예측
  predict: async (data: {
    bid_announcement_id: number;
    use_historical?: boolean;
    save_prediction?: boolean;
  }) => {
    const response = await apiClient.post<PredictionResponse>('/predictions/predict', data);
    return response.data;
  },

  // 예측 결과 조회
  getPrediction: async (predictionId: number) => {
    const response = await apiClient.get(`/predictions/${predictionId}`);
    return response.data;
  },

  // 예측 목록 조회
  getPredictions: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }) => {
    const response = await apiClient.get('/predictions/', { params });
    return response.data;
  },

  // 예측 통계 조회
  getPredictionStats: async () => {
    const response = await apiClient.get('/predictions/stats/summary');
    return response.data;
  },

  // 예측 정확도 업데이트
  updateAccuracy: async (predictionId: number, actualRate: number) => {
    const response = await apiClient.put(`/predictions/${predictionId}/accuracy`, null, {
      params: { actual_rate: actualRate },
    });
    return response.data;
  },

  // 정확도 리포트
  getAccuracyReport: async (days: number = 30) => {
    const response = await apiClient.get('/predictions/accuracy/report', {
      params: { days },
    });
    return response.data;
  },
};

// 분석 및 통계 API
export const analyticsApi = {
  // 대시보드 요약 정보
  getDashboardSummary: async () => {
    const response = await apiClient.get<DashboardSummary>('/analytics/summary');
    return response.data;
  },

  // 입찰 트렌드
  getBidTrends: async (days: number = 90) => {
    const response = await apiClient.get<TrendData>('/analytics/trends', {
      params: { days },
    });
    return response.data;
  },

  // 발주기관 분석
  getInstitutionAnalysis: async (institutionName: string, days: number = 365) => {
    const response = await apiClient.get(`/analytics/institution/${institutionName}`, {
      params: { days },
    });
    return response.data;
  },

  // 사정률 히스토그램
  getRateHistogram: async (params?: { bins?: number; days?: number }) => {
    const response = await apiClient.get<HistogramData>('/analytics/histogram', { params });
    return response.data;
  },
};

export default apiClient;
