import { Routes, Route } from 'react-router-dom';
import { Container, Box } from '@mui/material';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import BidList from './pages/BidList';
import BidDetailPage from './pages/BidDetailPage';
import Analytics from './pages/Analytics';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navigation />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bids" element={<BidList />} />
          <Route path="/bids/:bidId" element={<BidDetailPage />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App;
