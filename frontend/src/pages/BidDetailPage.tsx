import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Divider,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Assessment,
  TrendingUp,
  AccountBalance,
  LocationOn,
  Business,
} from '@mui/icons-material';
import { bidApi } from '@/services/api';
import { format } from 'date-fns';

export default function BidDetailPage() {
  const { bidId } = useParams<{ bidId: string }>();

  const { data, isLoading, error } = useQuery({
    queryKey: ['bidDetail', bidId],
    queryFn: () => bidApi.getBidDetail(Number(bidId), true),
    enabled: !!bidId,
  });

  const formatCurrency = (amount: number | undefined) => {
    if (!amount) return '-';
    return `${amount.toLocaleString()}원`;
  };

  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return '-';
    try {
      return format(new Date(dateStr), 'yyyy-MM-dd HH:mm');
    } catch {
      return dateStr;
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !data) {
    return <Alert severity="error">입찰공고를 불러올 수 없습니다.</Alert>;
  }

  const { announcement, prediction, similar_cases, historical_stats } = data;

  return (
    <Box>
      {/* 헤더 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          {announcement.bid_ntce_nm || '입찰공고 상세'}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          입찰공고번호: {announcement.bid_ntce_no}
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Chip
            label={announcement.bid_status === 'opened' ? '개찰완료' : '공고중'}
            color={announcement.bid_status === 'opened' ? 'success' : 'primary'}
          />
        </Box>
      </Paper>

      <Grid container spacing={3}>
        {/* 입찰 정보 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              <AccountBalance sx={{ mr: 1, verticalAlign: 'middle' }} />
              입찰 기본정보
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  공고기관
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {announcement.instt_nm || '-'}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  수요기관
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {announcement.dminstt_nm || '-'}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  지역
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  <LocationOn fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                  {announcement.rgn_nm || '-'}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  업종
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  <Business fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                  {announcement.induty_ty_nm || '-'}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  계약방법
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {announcement.cntrct_cnclsmt_mth_nm || '-'}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  입찰방법
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {announcement.bid_mthd_nm || '-'}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* 금액 정보 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
              금액 정보
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  추정가격
                </Typography>
                <Typography variant="h6" fontWeight="bold" color="primary">
                  {formatCurrency(announcement.presmpt_prce)}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  기초금액
                </Typography>
                <Typography variant="h6" fontWeight="bold">
                  {formatCurrency(announcement.basis_prce)}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  배정예산
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {formatCurrency(announcement.asign_bdgt_amt)}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* AI 예측 결과 */}
        {prediction && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3, bgcolor: '#f5f5f5' }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
                AI 예측 결과
              </Typography>
              <Divider sx={{ mb: 3 }} />
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        최종 예측 사정률
                      </Typography>
                      <Typography variant="h4" fontWeight="bold" color="primary">
                        {prediction.final_predicted_rate.toFixed(2)}%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        예측 예정가격
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        {formatCurrency(prediction.predicted_prdprc)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        추천 투찰금액
                      </Typography>
                      <Typography variant="h6" fontWeight="bold" color="secondary">
                        {formatCurrency(prediction.recommended_bid_amt)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        추천 투찰비율
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        {prediction.recommended_bid_rate.toFixed(2)}%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* 모델별 예측 */}
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    DNBP 예측
                  </Typography>
                  <Typography variant="h6">
                    {prediction.dnbp_predicted_rate
                      ? `${prediction.dnbp_predicted_rate.toFixed(2)}%`
                      : 'N/A'}
                    {prediction.dnbp_confidence && (
                      <Typography
                        component="span"
                        variant="body2"
                        color="text.secondary"
                        sx={{ ml: 1 }}
                      >
                        (신뢰도: {(prediction.dnbp_confidence * 100).toFixed(1)}%)
                      </Typography>
                    )}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    LSTM 예측
                  </Typography>
                  <Typography variant="h6">
                    {prediction.lstm_predicted_rate
                      ? `${prediction.lstm_predicted_rate.toFixed(2)}%`
                      : 'N/A'}
                    {prediction.lstm_confidence && (
                      <Typography
                        component="span"
                        variant="body2"
                        color="text.secondary"
                        sx={{ ml: 1 }}
                      >
                        (신뢰도: {(prediction.lstm_confidence * 100).toFixed(1)}%)
                      </Typography>
                    )}
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    예측 범위: {prediction.prediction_range_min.toFixed(2)}% ~{' '}
                    {prediction.prediction_range_max.toFixed(2)}%
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        )}

        {/* 유사 케이스 */}
        {similar_cases && similar_cases.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                유사 낙찰 사례 ({similar_cases.length}건)
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>공고번호</TableCell>
                      <TableCell>공고기관</TableCell>
                      <TableCell align="right">추정가격</TableCell>
                      <TableCell align="right">예정가격</TableCell>
                      <TableCell align="right">사정률</TableCell>
                      <TableCell>개찰일</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {similar_cases.slice(0, 10).map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.bid_ntce_no}</TableCell>
                        <TableCell>{item.instt_nm}</TableCell>
                        <TableCell align="right">
                          {formatCurrency(item.presmpt_prce)}
                        </TableCell>
                        <TableCell align="right">{formatCurrency(item.prdprc)}</TableCell>
                        <TableCell align="right">
                          {item.prdprc_rate ? `${item.prdprc_rate.toFixed(2)}%` : '-'}
                        </TableCell>
                        <TableCell>{formatDate(item.openg_dt)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        )}

        {/* 발주기관 통계 */}
        {historical_stats && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                발주기관 통계
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="text.secondary">
                    기관 평균 사정률
                  </Typography>
                  <Typography variant="h6">
                    {historical_stats.instt_historical_avg_rate?.toFixed(2)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    ({historical_stats.instt_historical_count}건)
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="text.secondary">
                    지역 평균 사정률
                  </Typography>
                  <Typography variant="h6">
                    {historical_stats.rgn_historical_avg_rate?.toFixed(2)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    ({historical_stats.rgn_historical_count}건)
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="text.secondary">
                    업종 평균 사정률
                  </Typography>
                  <Typography variant="h6">
                    {historical_stats.induty_historical_avg_rate?.toFixed(2)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    ({historical_stats.induty_historical_count}건)
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
