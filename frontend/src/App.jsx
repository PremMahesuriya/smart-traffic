import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import LiveCamera from './pages/LiveCamera';
import TrafficSignal from './pages/TrafficSignal';
import EmergencyAlerts from './pages/EmergencyAlerts';
import Analytics from './pages/Analytics';
import AccidentReports from './pages/AccidentReports';
import AdminPanel from './pages/AdminPanel';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/camera" element={<LiveCamera />} />
        <Route path="/signals" element={<TrafficSignal />} />
        <Route path="/emergency" element={<EmergencyAlerts />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/accidents" element={<AccidentReports />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Layout>
  );
}
