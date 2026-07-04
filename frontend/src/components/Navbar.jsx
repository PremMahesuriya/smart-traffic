import { useState, useEffect } from 'react';
import apiService from '../services/api';

export default function Navbar() {
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await apiService.healthCheck();
        setIsConnected(true);
      } catch (err) {
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000); // Poll health status every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="navbar">
      <h2 className="navbar-title">Control Center</h2>
      <div className={`connection-badge ${isConnected ? 'connected' : 'disconnected'}`}>
        <span className="lane-status-circle" style={{ backgroundColor: isConnected ? '#22c55e' : '#ef4444' }}></span>
        {isConnected ? 'API CONNECTED' : 'API OFFLINE'}
      </div>
    </header>
  );
}
