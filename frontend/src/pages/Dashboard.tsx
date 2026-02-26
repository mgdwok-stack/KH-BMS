import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Assessment,
  CheckCircle,
  Speed,
} from '@mui/icons-material';
import { analyticsApi, predictionApi } from '@/services/api';
import TrendChart from '@/components/TrendChart';
import HistogramChart from '@/components/HistogramChart';

export default function Dashboard() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: analyticsApi.getDashboardSummary,
  });

  const { data: trends, isLoading: trendsLoading } = useQuery({
    queryKey: ['bidTrends', 90],
    queryFn: () => analyticsApi.getBidTrends(90),
  });

  const { data: histogram, isLoading: histogramLoading } = useQuery({
    queryKey: ['rateHistogram', 20, 90],
    queryFn: () => analyticsApi.getRateHistogram({ bins: 20, days: 90 }),
  });

  const { data: predictionStats } = useQuery({
    queryKey: ['predictionStats'],
    queryFn: predictionApi.getPredictionStats,
  });

  if (summaryLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const stats = [
    {
      title: '전체 입찰공고',
      value: summary?.total_statistics.total_announcements || 0,
      icon: <Assessment fontSize="large" />,
      color: '#1976d2',
    },
    {
      title: '낙찰결과',
      value: summary?.total_statistics.total_results || 0,
      icon: <CheckCircle fontSize="large" />,
      color: '#2e7d32',
    },
    {
      title: 'AI 예측',
      value: summary?.total_statistics.total_predictions || 0,
      icon: <TrendingUp fontSize="large" />,
      color: '#ed6c02',
    },
    {
      title: '평균 사정률',
      value: summary?.total_statistics.overall_avg_rate
        ? `${summary.total_statistics.overall_avg_rate.toFixed(2)}%`
        : 'N/A',
      icon: <Speed fontSize="large" />,
      color: '#9c27b0',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        대시보드
      </Typography>

      {/* 통계 카드 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper
              sx={{
                p: 3,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <Box>
                <Typography color="text.secondary" variant="body2" gutterBottom>
                  {stat.title}
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  {typeof stat.value === 'number'
                    ? stat.value.toLocaleString()
                    : stat.value}
                </Typography>
              </Box>
              <Box sx={{ color: stat.color }}>{stat.icon}</Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* AI 성능 지표 */}
      {predictionStats && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            AI 예측 성능
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Typography color="text.secondary" variant="body2">
                검증된 예측
              </Typography>
              <Typography variant="h6">
                {predictionStats.validated_predictions || 0}건
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography color="text.secondary" variant="body2">
                평균 예측 오차
              </Typography>
              <Typography variant="h6">
                {predictionStats.avg_prediction_error
                  ? `${predictionStats.avg_prediction_error.toFixed(3)}%`
                  : 'N/A'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography color="text.secondary" variant="body2">
                정확도 (오차 &lt; 0.1%)
              </Typography>
              <Typography variant="h6">
                {predictionStats.accuracy_rate
                  ? `${predictionStats.accuracy_rate.toFixed(1)}%`
                  : 'N/A'}
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* 차트 */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              사정률 분포 (최근 90일)
            </Typography>
            {histogramLoading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : histogram && histogram.histogram.length > 0 ? (
              <HistogramChart data={histogram} />
            ) : (
              <Alert severity="info">히스토그램 데이터가 없습니다</Alert>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              일별 입찰 트렌드 (최근 90일)
            </Typography>
            {trendsLoading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : trends && trends.daily_trends.length > 0 ? (
              <TrendChart data={trends.daily_trends} />
            ) : (
              <Alert severity="info">트렌드 데이터가 없습니다</Alert>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
