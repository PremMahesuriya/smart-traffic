import { useState, useEffect } from 'react';
import apiService from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function SystemStatus() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState({
    apiStatus: 'OFFLINE',
    dbStatus: 'DISCONNECTED',
    timestamp: 'N/A',
    service: 'N/A',
  });

  const checkStatus = async () => {
    try {
      setError(null);
      const health = await apiService.healthCheck();
      setStatus({
        apiStatus: 'ONLINE',
        dbStatus: 'CONNECTED',
        timestamp: health.timestamp || new Date().toISOString(),
        service: health.service || 'smart-traffic-backend-service',
      });
      setLoading(false);
    } catch (err) {
      setStatus({
        apiStatus: 'OFFLINE',
        dbStatus: 'DISCONNECTED',
        timestamp: new Date().toISOString(),
        service: 'N/A',
      });
      setError(err.message || 'API connection refused. Please check if the Node backend is running.');
      setLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 3000); // 3s polling
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontWeight: '700' }}>System Status</h2>

      {error && <ErrorMessage message={error} onRetry={checkStatus} />}

      <div className="card" style={{ maxWidth: '600px' }}>
        <h3 style={{ fontWeight: '600', marginBottom: '1.25rem' }}>Service Health Summary</h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
            <span style={{ fontWeight: '600', color: '#64748b' }}>Backend Server:</span>
            <span 
              style={{ 
                fontWeight: '700', 
                color: status.apiStatus === 'ONLINE' ? '#22c55e' : '#ef4444' 
              }}
            >
              {status.apiStatus}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
            <span style={{ fontWeight: '600', color: '#64748b' }}>MongoDB Database:</span>
            <span 
              style={{ 
                fontWeight: '700', 
                color: status.dbStatus === 'CONNECTED' ? '#22c55e' : '#ef4444' 
              }}
            >
              {status.dbStatus}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
            <span style={{ fontWeight: '600', color: '#64748b' }}>Service Name:</span>
            <span style={{ fontWeight: '600' }}>{status.service}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem' }}>
            <span style={{ fontWeight: '600', color: '#64748b' }}>Last Refresh:</span>
            <span style={{ fontSize: '0.9rem', color: '#475569' }}>
              {status.timestamp !== 'N/A' ? new Date(status.timestamp).toLocaleString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
