import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, User } from 'lucide-react';

const Navbar = ({ title }) => {
  const navigate = useNavigate();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      // Navigate to soldiers page with search parameter
      navigate(`/soldiers?search=${encodeURIComponent(searchTerm)}`);
    }
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

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
        <form onSubmit={handleSearch} className="search-box">
          <Search className="search-icon" size={18} />
          <input 
            type="text" 
            className="search-input" 
            placeholder="Search soldiers, alerts..." 
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </form>

        <button className="btn-icon" title="Notifications">
          <Bell size={20} />
        </button>

        <button 
          className="btn-icon" 
          title="Profile"
          onClick={() => navigate('/soldiers')}
        >
          <User size={20} />
        </button>
      </div>
    </div>
  );
};

export default Navbar;