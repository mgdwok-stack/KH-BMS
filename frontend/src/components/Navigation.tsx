import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AssessmentIcon from '@mui/icons-material/Assessment';

export default function Navigation() {
  return (
    <AppBar position="static">
      <Toolbar>
        <AssessmentIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Bid-Bot Clone - AI 입찰 분석
        </Typography>
        <Box>
          <Button color="inherit" component={RouterLink} to="/">
            대시보드
          </Button>
          <Button color="inherit" component={RouterLink} to="/bids">
            입찰공고
          </Button>
          <Button color="inherit" component={RouterLink} to="/analytics">
            분석
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
