import { useState, useEffect } from 'react';
import apiService from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
const LANE_COLORS = {
  A: 'rgb(239, 68, 68)',   // Tailwind red-500
  B: 'rgb(34, 197, 94)',   // Tailwind green-500
  C: 'rgb(59, 130, 246)',  // Tailwind blue-500
  D: 'rgb(234, 179, 8)',   // Tailwind yellow-500
};

export default function LiveTraffic() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [traffic, setTraffic] = useState({});
  const [signal, setSignal] = useState({ activeLane: 'None', signal: 'RED' });

  const fetchData = async () => {
    try {
      setError(null);
      const [trafficData, signalData] = await Promise.all([
        apiService.getCurrentTraffic(),
        apiService.getCurrentSignal(),
      ]);
      setTraffic(trafficData);
      setSignal(signalData);
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to fetch live traffic.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000); // 3-second auto refresh
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  // Mapping lane letters to keys returned by the API (laneA, laneB, etc.)
  const laneKeys = {
    A: 'laneA',
    B: 'laneB',
    C: 'laneC',
    D: 'laneD',
  };

  // Helper to determine the signal status color of each lane
  const getLaneSignalColor = (laneLetter) => {
    if (signal.activeLane === laneLetter) {
      if (signal.signal === 'GREEN') return '#22c55e'; // Green
      if (signal.signal === 'YELLOW') return '#eab308'; // Yellow
    }
    return '#ef4444'; // Red for all other lanes
  };

  // Density colors mapping
  const getDensityColor = (density) => {
    if (density === 'Very High') return '#ef4444'; // Red
    if (density === 'High') return '#f97316'; // Orange
    if (density === 'Medium') return '#eab308'; // Yellow
    return '#22c55e'; // Green
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontWeight: '700' }}>Live Traffic Monitoring</h2>

      {/* Signal Status Bar */}
      <div className="card" style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <span style={{ color: '#64748b', fontSize: '0.9rem', fontWeight: '600' }}>ACTIVE SIGNAL DIRECTION</span>
          <h3 style={{ fontSize: '1.4rem', fontWeight: '700', marginTop: '0.25rem' }}>
            {signal.activeLane === 'None' ? 'No Active Green Lane' : `Lane ${signal.activeLane}`}
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ fontSize: '1.1rem', fontWeight: '600' }}>State:</span>
          <span
            className={`signal-badge ${signal.signal.toLowerCase()}`}
            style={{ margin: 0, textTransform: 'uppercase' }}
          >
            {signal.signal}
          </span>
        </div>
      </div>

      {/* 4 Lanes Grid */}
      <div className="grid-4">
        {['A', 'B', 'C', 'D'].map((letter) => {
          const key = laneKeys[letter];
          const data = traffic[key] || { count: 0, density: 'Low' };
          const borderL = LANE_COLORS[letter] ? `6px solid ${LANE_COLORS[letter]}` : undefined;

          return (
            <div key={letter} className="card stat-card" style={{ borderTop: borderL }}>
              <div className="lane-card-title">
                <span 
                  className="lane-status-circle" 
                  style={{ backgroundColor: getLaneSignalColor(letter) }}
                ></span>
                Lane {letter}
              </div>

              <div className="lane-grid-meta">
                <div className="meta-row">
                  <span className="meta-label">Vehicles:</span>
                  <span className="meta-value" style={{ fontSize: '1.35rem' }}>{data.count}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-label">Density:</span>
                  <span 
                    className="meta-value" 
                    style={{ color: getDensityColor(data.density) }}
                  >
                    {data.density}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
