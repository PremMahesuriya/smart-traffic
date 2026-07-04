import { useEffect, useState } from 'react';
import { fetchSignals } from '../services/api';

export default function TrafficSignal() {
  const [signals, setSignals] = useState([]);

  useEffect(() => {
    fetchSignals().then(setSignals).catch(console.error);
    const interval = setInterval(() => {
      fetchSignals().then(setSignals).catch(console.error);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>Traffic Signals</h2>
      <div className="grid">
        {signals.map((sig) => (
          <div key={sig._id} className="signal-card">
            <h3>Lane {sig.lane}</h3>
            <p className={`light ${sig.state}`}>{sig.state?.toUpperCase()}</p>
            <p>Green: {sig.greenDurationSec}s</p>
            <p>Vehicles: {sig.vehicleCount}</p>
            <p>Density: {sig.density ?? '—'}</p>
          </div>
        ))}
      </div>
      {signals.length === 0 && <p className="empty">No signal data yet.</p>}
    </div>
  );
}
