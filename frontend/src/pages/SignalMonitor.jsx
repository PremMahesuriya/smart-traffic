import { useState, useEffect } from 'react';
import apiService from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function SignalMonitor() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [current, setCurrent] = useState({ activeLane: 'None', signal: 'RED', remainingTime: 0 });
  const [history, setHistory] = useState([]);

  const fetchData = async () => {
    try {
      setError(null);
      const [currentSignal, signalHistory] = await Promise.all([
        apiService.getCurrentSignal(),
        apiService.getSignalHistory(),
      ]);
      setCurrent(currentSignal);
      setHistory(signalHistory);
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to fetch signals.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000); // 2s refresh interval
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontWeight: '700' }}>Signal Monitor</h2>

      {/* Current Signal status panel */}
      <div className="grid-3" style={{ marginBottom: '2rem' }}>
        <div className="card stat-card" style={{ borderLeft: '4px solid #3b82f6' }}>
          <span className="stat-title">Active Green Lane</span>
          <span className="stat-value">
            {current.activeLane === 'None' ? 'None' : `Lane ${current.activeLane}`}
          </span>
        </div>

        <div className="card stat-card" style={{ borderLeft: '4px solid #10b981' }}>
          <span className="stat-title">Current Signal Color</span>
          <span
            className={`signal-badge ${current.signal.toLowerCase()}`}
            style={{ width: 'fit-content', padding: '0.25rem 0.75rem', fontSize: '1.2rem', margin: '0.25rem 0 0 0' }}
          >
            {current.signal}
          </span>
        </div>

        <div className="card stat-card" style={{ borderLeft: '4px solid #f59e0b' }}>
          <span className="stat-title">Remaining Green Time</span>
          <span className="stat-value">
            {current.remainingTime}s
          </span>
        </div>
      </div>

      {/* Signal transition history table */}
      <div className="card">
        <h3 style={{ fontWeight: '600', marginBottom: '1rem' }}>Signal Log Transitions</h3>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Video Timeline (s)</th>
                <th>Target Lane</th>
                <th>Signal State</th>
                <th>Target Duration (s)</th>
                <th>Capture Frame</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan="5" className="empty">No historical signal transitions recorded in DB.</td>
                </tr>
              ) : (
                history.map((log) => (
                  <tr key={log._id}>
                    <td>{log.timestamp.toFixed(2)}s</td>
                    <td style={{ fontWeight: '700' }}>Lane {log.activeLane}</td>
                    <td>
                      <span
                        style={{
                          fontWeight: '700',
                          color: log.signalState === 'GREEN' ? '#22c55e' : (log.signalState === 'YELLOW' ? '#eab308' : '#ef4444')
                        }}
                      >
                        {log.signalState}
                      </span>
                    </td>
                    <td>{log.greenTime}s</td>
                    <td>{Math.round(log.timestamp * 30)}</td> {/* Derived frame number */}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
