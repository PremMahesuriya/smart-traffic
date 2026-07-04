import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import LiveTraffic from './pages/LiveTraffic';
import SignalMonitor from './pages/SignalMonitor';
import TrafficAnalytics from './pages/TrafficAnalytics';
import SystemStatus from './pages/SystemStatus';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/traffic" element={<LiveTraffic />} />
        <Route path="/signals" element={<SignalMonitor />} />
        <Route path="/analytics" element={<TrafficAnalytics />} />
        <Route path="/status" element={<SystemStatus />} />
      </Routes>
    </Layout>
  );
}
