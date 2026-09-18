import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Sidebar.css';

const NAV = [
  { to: '/app', label: 'Overview', end: true },
  { to: '/app/screen', label: 'New screening' },
  { to: '/app/history', label: 'Case history' },
  { to: '/app/analytics', label: 'Analytics', adminOnly: true },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">FIS</div>
        <div>
          <div className="brand-name">Fake Identity Screening</div>
          <div className="brand-sub">SIH 2026 · Prototype</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV.filter((item) => !item.adminOnly || user?.role === 'admin').map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => 'sidebar-link' + (isActive ? ' active' : '')}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="user-avatar">{user?.name?.[0]?.toUpperCase() || '?'}</div>
          <div>
            <div className="user-name">{user?.name}</div>
            <div className="user-role">{user?.role === 'admin' ? 'Administrator' : 'Screening officer'}</div>
          </div>
        </div>
        <button className="sidebar-logout" onClick={handleLogout}>
          Sign out
        </button>
      </div>
    </aside>
  );
}
