import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Portal from './pages/Portal';
import DashboardOverview from './pages/DashboardOverview';
import LiveTraffic from './pages/LiveTraffic';
import SignalMonitor from './pages/SignalMonitor';
import TrafficAnalytics from './pages/TrafficAnalytics';
import SystemStatus from './pages/SystemStatus';

export default function App() {
  return (
    <Routes>
      {/* Front portal landing page (no sidebar / navbar layout) */}
      <Route path="/" element={<Portal />} />

      {/* Internal operator dashboard routes (includes sidebar / navbar layout) */}
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<DashboardOverview />} />
        <Route path="/traffic" element={<LiveTraffic />} />
        <Route path="/signals" element={<SignalMonitor />} />
        <Route path="/analytics" element={<TrafficAnalytics />} />
        <Route path="/status" element={<SystemStatus />} />
      </Route>
    </Routes>
  );
}
