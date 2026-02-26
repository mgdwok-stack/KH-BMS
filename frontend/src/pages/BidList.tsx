import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Typography,
  Box,
  TextField,
  Button,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Chip,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { bidApi } from '@/services/api';
import { format } from 'date-fns';

export default function BidList() {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(50);
  const [filters, setFilters] = useState({
    instt_nm: '',
    rgn_nm: '',
    induty_ty_nm: '',
    status: '',
  });

  const { data: filterOptions } = useQuery({
    queryKey: ['filterOptions'],
    queryFn: bidApi.getFilterOptions,
  });

  const { data, isLoading } = useQuery({
    queryKey: ['bids', page + 1, pageSize, filters],
    queryFn: () =>
      bidApi.getBids({
        page: page + 1,
        page_size: pageSize,
        ...filters,
      }),
  });

  const handleSearch = () => {
    setPage(0);
  };

  const handleRowClick = (bidId: number) => {
    navigate(`/bids/${bidId}`);
  };

  const formatCurrency = (amount: number | undefined) => {
    if (!amount) return '-';
    if (amount >= 100000000) {
      return `${(amount / 100000000).toFixed(1)}억원`;
    }
    if (amount >= 10000) {
      return `${(amount / 10000).toFixed(0)}만원`;
    }
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        입찰공고 목록
      </Typography>

      {/* 필터 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="공고기관명"
              value={filters.instt_nm}
              onChange={(e) => setFilters({ ...filters, instt_nm: e.target.value })}
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>지역</InputLabel>
              <Select
                value={filters.rgn_nm}
                label="지역"
                onChange={(e) => setFilters({ ...filters, rgn_nm: e.target.value })}
              >
                <MenuItem value="">전체</MenuItem>
                {filterOptions?.regions.slice(0, 20).map((region) => (
                  <MenuItem key={region.name} value={region.name}>
                    {region.name} ({region.count})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>입찰상태</InputLabel>
              <Select
                value={filters.status}
                label="입찰상태"
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              >
                <MenuItem value="">전체</MenuItem>
                <MenuItem value="announced">공고중</MenuItem>
                <MenuItem value="opened">개찰완료</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
            >
              검색
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* 테이블 */}
      <Paper>
        {isLoading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>입찰공고명</TableCell>
                    <TableCell>공고기관</TableCell>
                    <TableCell>지역</TableCell>
                    <TableCell align="right">기초금액</TableCell>
                    <TableCell>입찰마감</TableCell>
                    <TableCell>상태</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data?.items.map((bid) => (
                    <TableRow
                      key={bid.id}
                      hover
                      onClick={() => handleRowClick(bid.id)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {bid.bid_ntce_nm || bid.bid_ntce_no}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {bid.bid_ntce_no}
                        </Typography>
                      </TableCell>
                      <TableCell>{bid.instt_nm || '-'}</TableCell>
                      <TableCell>{bid.rgn_nm || '-'}</TableCell>
                      <TableCell align="right">
                        {formatCurrency(bid.basis_prce)}
                      </TableCell>
                      <TableCell>{formatDate(bid.bid_close_dt)}</TableCell>
                      <TableCell>
                        <Chip
                          label={bid.bid_status === 'opened' ? '개찰완료' : '공고중'}
                          color={bid.bid_status === 'opened' ? 'success' : 'primary'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={data?.total || 0}
              page={page}
              onPageChange={(_, newPage) => setPage(newPage)}
              rowsPerPage={pageSize}
              onRowsPerPageChange={(e) => {
                setPageSize(parseInt(e.target.value, 10));
                setPage(0);
              }}
              rowsPerPageOptions={[25, 50, 100]}
              labelRowsPerPage="페이지당 행 수:"
            />
          </>
        )}
      </Paper>
    </Box>
  );
}
