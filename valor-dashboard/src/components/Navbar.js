import React, { useState, useEffect } from 'react';
import { Search, Bell, User } from 'lucide-react';

const Navbar = ({ title }) => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="top-navbar">
      <div>
        <h2 className="page-title">{title}</h2>
        <p style={{ 
          fontSize: '13px', 
          color: 'var(--text-secondary)', 
          marginTop: '4px' 
        }}>
          {currentTime.toLocaleString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          })}
        </p>
      </div>

      <div className="top-actions">
        <div className="search-box">
          <Search className="search-icon" size={18} />
          <input 
            type="text" 
            className="search-input" 
            placeholder="Search soldiers, alerts..." 
          />
        </div>

        <button className="btn-icon">
          <Bell size={20} />
        </button>

        <button className="btn-icon">
          <User size={20} />
        </button>
      </div>
    </div>
  );
};

export default Navbar;