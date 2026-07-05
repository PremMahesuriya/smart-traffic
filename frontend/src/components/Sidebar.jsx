import { NavLink, Link } from 'react-router-dom';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="logo-container">
        <Link to="/" style={{ textDecoration: 'none' }}>
          <h1 className="logo">Smart Traffic</h1>
        </Link>
      </div>
      <nav className="nav-links">
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} end>
          Portal Home
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          Dashboard
        </NavLink>
        <NavLink to="/traffic" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          Live Traffic
        </NavLink>
        <NavLink to="/signals" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          Signal Monitor
        </NavLink>
        <NavLink to="/analytics" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          Traffic Analytics
        </NavLink>
        <NavLink to="/status" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          System Status
        </NavLink>
      </nav>
    </aside>
  );
}
