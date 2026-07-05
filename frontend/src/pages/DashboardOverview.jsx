import { useState, useEffect } from 'react';
import apiService from '../services/api';
import StatCard from '../components/StatCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    totalVehicles: 0,
    activeSignal: 'RED',
    greenLane: 'None',
    avgDensity: 'Low',
    systemStatus: 'Healthy',
  });

  const fetchData = async () => {
    try {
      setError(null);
      const [analytics, signal, health] = await Promise.all([
        apiService.getTrafficAnalytics(),
        apiService.getCurrentSignal(),
        apiService.healthCheck(),
      ]);

      // Determine average density text based on average vehicles per lane
      let densityText = 'Low';
      const avg = analytics.averageVehiclesPerLane || 0;
      if (avg > 20) densityText = 'Very High';
      else if (avg > 10) densityText = 'High';
      else if (avg > 5) densityText = 'Medium';

      setData({
        totalVehicles: analytics.totalVehicles || 0,
        activeSignal: signal.signal || 'RED',
        greenLane: signal.activeLane || 'None',
        avgDensity: densityText,
        systemStatus: health.status === 'ok' ? 'Healthy' : 'Degraded',
      });
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to fetch dashboard data.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000); // Polling every 3s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  // Map signal colors
  const getSignalColor = (state) => {
    if (state === 'GREEN') return '#22c55e';
    if (state === 'YELLOW') return '#eab308';
    return '#ef4444';
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontWeight: '700' }}>Dashboard Overview</h2>
      <div className="grid-3">
        <StatCard title="Total Vehicles" value={data.totalVehicles} color="#0284c7" />
        <StatCard 
          title="Active Signal" 
          value={data.activeSignal} 
          color={getSignalColor(data.activeSignal)} 
        />
        <StatCard title="Current Green Lane" value={data.greenLane === 'None' ? 'None' : `Lane ${data.greenLane}`} color="#a855f7" />
        <StatCard title="Avg Traffic Density" value={data.avgDensity} color="#eab308" />
        <StatCard 
          title="System Status" 
          value={data.systemStatus} 
          color={data.systemStatus === 'Healthy' ? '#22c55e' : '#ef4444'} 
        />
      </div>
      
      <div className="card" style={{ marginTop: '2rem' }}>
        <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>Welcome to the Control Dashboard</h3>
        <p style={{ color: '#475569', lineHeight: '1.6' }}>
          This interface monitors traffic intersections in real-time. It maps persistent object tracks 
          using computer vision, calculates per-lane queue densities, and drives an adaptive 
          signal scheduler to minimize congestion. Select navigation options from the sidebar to inspect 
          live vehicle streams, signal transitions, and historical reports.
        </p>
      </div>
    </div>
  );
}
