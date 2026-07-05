import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiService from '../services/api';
import '../styles/portal.css';

export default function Portal() {
  const [isConnected, setIsConnected] = useState(null);

  // Retrieve base API URL or fallback to construct health endpoint link
  const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
  const healthUrl = `${apiBaseUrl}/health`;

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
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="portal-body">
      <div className="portal-container">
        
        <header className="portal-header">
          <div className="portal-badge">
            <span className="badge-dot"></span>
            System Hub Portal
          </div>
          <h1 className="portal-title">Smart Traffic Management</h1>
          <p className="portal-subtitle">
            An orchestrated Computer Vision and Adaptive Light Signal Controller optimized for real-time intersection throughput.
          </p>
        </header>

        {/* Portal Grid */}
        <div className="portal-grid">
          
          {/* Card 1: Dashboard UI */}
          <Link to="/dashboard" className="portal-card">
            <div className="portal-card-status online">
              <span className="status-circle" style={{ backgroundColor: '#22c55e' }}></span>
              ACTIVE SYSTEM
            </div>
            <div className="portal-card-icon-wrapper">📊</div>
            <h3 className="portal-card-title">Operator Dashboard</h3>
            <p className="portal-card-desc">
              Access the real-time visual dashboard showing counts, current lane status, light countdowns, and historical metrics charts.
            </p>
            <span className="portal-card-btn">Open Dashboard &rarr;</span>
          </Link>

          {/* Card 2: REST API Services */}
          <a href={healthUrl} className="portal-card" target="_blank" rel="noopener noreferrer">
            <div className={`portal-card-status ${isConnected ? 'online' : isConnected === false ? 'offline' : ''}`}>
              <span 
                className="status-circle" 
                style={{ 
                  backgroundColor: isConnected ? '#22c55e' : isConnected === false ? '#ef4444' : '#94a3b8' 
                }}
              ></span>
              {isConnected ? 'API ONLINE' : isConnected === false ? 'API OFFLINE' : 'CHECKING...'}
            </div>
            <div className="portal-card-icon-wrapper">⚡</div>
            <h3 className="portal-card-title">REST API Services</h3>
            <p className="portal-card-desc">
              Query backend API services and verify database synchronization, endpoint health responses, and system logs.
            </p>
            <span className="portal-card-btn">Check API Status &rarr;</span>
          </a>

          {/* Card 3: Documentation */}
          <a href="https://github.com/PremMahesuriya/smart-traffic#readme" className="portal-card" target="_blank" rel="noopener noreferrer">
            <div className="portal-card-status" style={{ backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
              <span className="status-circle" style={{ backgroundColor: '#38bdf8' }}></span>
              LOCAL MANUAL
            </div>
            <div className="portal-card-icon-wrapper">📖</div>
            <h3 className="portal-card-title">Project Documentation</h3>
            <p className="portal-card-desc">
              Browse local README documentation detailing algorithms, database schemas, directory layouts, and execution parameters.
            </p>
            <span className="portal-card-btn">View Code Docs &rarr;</span>
          </a>

        </div>

        {/* Pipeline Flow Overview */}
        <div className="portal-flow-section">
          <h2 className="portal-flow-title">Integrated Pipeline Flow</h2>
          <div className="portal-steps-container">
            
            <div className="portal-step-item">
              <div className="portal-step-number">1</div>
              <div className="portal-step-label">CV Tracking</div>
              <div className="portal-step-sub">YOLOv8 + ByteTrack</div>
            </div>

            <div className="portal-step-item">
              <div className="portal-step-number">2</div>
              <div className="portal-step-label">Lane Occupancy</div>
              <div className="portal-step-sub">Polygon Mapping</div>
            </div>

            <div className="portal-step-item">
              <div className="portal-step-number">3</div>
              <div className="portal-step-label">Adaptive Score</div>
              <div className="portal-step-sub">Priority Ageing</div>
            </div>

            <div className="portal-step-item">
              <div className="portal-step-number">4</div>
              <div className="portal-step-label">JSON REST Post</div>
              <div className="portal-step-sub">Express + MongoDB</div>
            </div>

          </div>
        </div>

        <footer className="portal-footer">
          <p>&copy; {new Date().getFullYear()} Smart Traffic Management System @premmahesuriya</p>
        </footer>

      </div>
    </div>
  );
}
