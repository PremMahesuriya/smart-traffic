import { NavLink } from 'react-router-dom';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="logo-container">
        <h1 className="logo">Smart Traffic</h1>
      </div>
      <nav className="nav-links">
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} end>
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
