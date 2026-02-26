import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { analyticsApi } from '@/services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Analytics() {
  const [tabValue, setTabValue] = useState(0);
  const [institutionName, setInstitutionName] = useState('');
  const [searchInstitution, setSearchInstitution] = useState('');

  const { data: trends } = useQuery({
    queryKey: ['bidTrends', 90],
    queryFn: () => analyticsApi.getBidTrends(90),
  });

  const { data: histogram } = useQuery({
    queryKey: ['rateHistogram', 20, 90],
    queryFn: () => analyticsApi.getRateHistogram({ bins: 20, days: 90 }),
  });

  const {
    data: institutionData,
    isLoading: institutionLoading,
    error: institutionError,
  } = useQuery({
    queryKey: ['institutionAnalysis', searchInstitution],
    queryFn: () => analyticsApi.getInstitutionAnalysis(searchInstitution, 365),
    enabled: !!searchInstitution,
  });

  const handleInstitutionSearch = () => {
    setSearchInstitution(institutionName);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        분석 및 통계
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="지역별 통계" />
          <Tab label="업종별 통계" />
          <Tab label="발주기관 분석" />
        </Tabs>
      </Box>

      {/* 지역별 통계 */}
      <TabPanel value={tabValue} index={0}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            지역별 평균 사정률 (최근 90일)
          </Typography>
          {trends?.regional_stats && trends.regional_stats.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={trends.regional_stats.slice(0, 15)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="region"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  tick={{ fontSize: 12 }}
                />
                <YAxis label={{ value: '평균 사정률 (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value: any) => `${Number(value).toFixed(2)}%`} />
                <Legend />
                <Bar dataKey="avg_rate" fill="#1976d2" name="평균 사정률">
                  {trends.regional_stats.slice(0, 15).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <Alert severity="info">지역별 통계 데이터가 없습니다</Alert>
          )}
        </Paper>
      </TabPanel>

      {/* 업종별 통계 */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                업종별 평균 사정률 (Top 10)
              </Typography>
              {trends?.industry_stats && trends.industry_stats.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={trends.industry_stats.slice(0, 10)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="industry"
                      angle={-45}
                      textAnchor="end"
                      height={120}
                      tick={{ fontSize: 10 }}
                    />
                    <YAxis />
                    <Tooltip formatter={(value: any) => `${Number(value).toFixed(2)}%`} />
                    <Bar dataKey="avg_rate" fill="#00C49F" name="평균 사정률" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Alert severity="info">업종별 통계 데이터가 없습니다</Alert>
              )}
            </Paper>
          </Grid>
          <Grid item xs={12} lg={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                업종별 입찰 건수 (Top 10)
              </Typography>
              {trends?.industry_stats && trends.industry_stats.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={trends.industry_stats.slice(0, 10)}
                      dataKey="count"
                      nameKey="industry"
                      cx="50%"
                      cy="50%"
                      outerRadius={120}
                      label={(entry) => `${entry.industry}: ${entry.count}`}
                    >
                      {trends.industry_stats.slice(0, 10).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Alert severity="info">업종별 통계 데이터가 없습니다</Alert>
              )}
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* 발주기관 분석 */}
      <TabPanel value={tabValue} index={2}>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            발주기관 검색
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <TextField
              fullWidth
              label="발주기관명"
              value={institutionName}
              onChange={(e) => setInstitutionName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleInstitutionSearch()}
              placeholder="예: 국방부, 서울시"
            />
            <Button variant="contained" onClick={handleInstitutionSearch} sx={{ minWidth: 100 }}>
              검색
            </Button>
          </Box>
        </Paper>

        {institutionLoading && (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        )}

        {institutionError && <Alert severity="error">발주기관 데이터를 불러올 수 없습니다</Alert>}

        {institutionData && (
          <>
            {/* 기본 통계 */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                {institutionData.institution_name} - 기본 통계
              </Typography>
              <Grid container spacing={3} sx={{ mt: 1 }}>
                <Grid item xs={12} md={2}>
                  <Typography variant="body2" color="text.secondary">
                    총 건수
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {institutionData.statistics.total_count}건
                  </Typography>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Typography variant="body2" color="text.secondary">
                    평균 사정률
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="primary">
                    {institutionData.statistics.avg_rate?.toFixed(2)}%
                  </Typography>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Typography variant="body2" color="text.secondary">
                    표준편차
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {institutionData.statistics.std_rate?.toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Typography variant="body2" color="text.secondary">
                    최소 사정률
                  </Typography>
                  <Typography variant="h6">
                    {institutionData.statistics.min_rate?.toFixed(2)}%
                  </Typography>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Typography variant="body2" color="text.secondary">
                    최대 사정률
                  </Typography>
                  <Typography variant="h6">
                    {institutionData.statistics.max_rate?.toFixed(2)}%
                  </Typography>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Typography variant="body2" color="text.secondary">
                    평균 금액
                  </Typography>
                  <Typography variant="h6">
                    {institutionData.statistics.avg_amount
                      ? `${(institutionData.statistics.avg_amount / 100000000).toFixed(1)}억`
                      : '-'}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>

            {/* 월별 추이 */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                월별 사정률 추이
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={institutionData.monthly_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value: any) => `${Number(value).toFixed(2)}%`} />
                  <Legend />
                  <Bar dataKey="avg_rate" fill="#1976d2" name="평균 사정률" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>

            {/* 금액대별 분포 */}
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                금액대별 분포
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={institutionData.price_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis yAxisId="left" label={{ value: '건수', angle: -90, position: 'insideLeft' }} />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    label={{ value: '평균 사정률 (%)', angle: 90, position: 'insideRight' }}
                  />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="count" fill="#8884d8" name="건수" />
                  <Bar yAxisId="right" dataKey="avg_rate" fill="#82ca9d" name="평균 사정률" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </>
        )}
      </TabPanel>
    </Box>
  );
}
