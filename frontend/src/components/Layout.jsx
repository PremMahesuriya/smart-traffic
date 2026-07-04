import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Home', icon: '🏠' },
  { to: '/camera', label: 'Live Camera', icon: '📹' },
  { to: '/signals', label: 'Traffic Signal', icon: '🚦' },
  { to: '/emergency', label: 'Emergency Alerts', icon: '🚑' },
  { to: '/analytics', label: 'Analytics', icon: '📈' },
  { to: '/accidents', label: 'Accident Reports', icon: '⚠' },
  { to: '/admin', label: 'Admin Panel', icon: '👤' },
];

export default function Layout({ children }) {
  return (
    <div className="app">
      <aside className="sidebar">
        <h1 className="logo">Smart Traffic</h1>
        <nav>
          {links.map(({ to, label, icon }) => (
            <NavLink key={to} to={to} className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
              <span>{icon}</span> {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
