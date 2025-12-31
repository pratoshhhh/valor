import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  FileText, 
  Activity, 
  Radio,
  User,
  LogOut
} from 'lucide-react';

const Sidebar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('valorAuth');
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/alerts', icon: AlertTriangle, label: 'Health Alerts' },
    { path: '/reports', icon: FileText, label: 'VA Reports' },
    { path: '/metrics', icon: Activity, label: 'Confluent Metrics' },
    { path: '/devices', icon: Radio, label: 'Devices' },
    { path: '/soldiers', icon: User, label: 'Soldiers' }
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1 className="logo">VALOR</h1>
        <p style={{ 
          fontSize: '12px', 
          color: 'var(--text-secondary)', 
          marginTop: '8px',
          letterSpacing: '1px'
        }}>
          HEALTH MONITORING SYSTEM
        </p>
      </div>

      <ul className="nav-menu">
        {navItems.map((item) => (
          <li key={item.path} className="nav-item">
            <NavLink 
              to={item.path} 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <item.icon className="nav-icon" />
              <span>{item.label}</span>
            </NavLink>
          </li>
        ))}
      </ul>

      <div style={{ 
        position: 'absolute', 
        bottom: '20px', 
        left: '12px', 
        right: '12px' 
      }}>
        <button 
          onClick={handleLogout}
          className="nav-link"
          style={{ 
            width: '100%', 
            border: 'none', 
            background: 'transparent',
            cursor: 'pointer',
            color: 'var(--accent-red)'
          }}
        >
          <LogOut className="nav-icon" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;