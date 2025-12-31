import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { User, Search, MapPin, Shield, Activity, AlertTriangle } from 'lucide-react';
import apiService from '../services/api';

const Soldiers = () => {
  const navigate = useNavigate();
  const [soldiers, setSoldiers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock soldier data - in production, fetch from API
    const mockSoldiers = [
      {
        soldier_id: 'SGT_JOHNSON_001',
        name: 'Michael Johnson',
        rank: 'Sergeant',
        unit: '1st Battalion, 5th Marines',
        deployment_location: 'Forward Operating Base Delta',
        status: 'active',
        health_score: 87,
        alerts_count: 2,
        last_alert: '2 hours ago',
        deployment_start: '2024-06-15'
      },
      {
        soldier_id: 'CPL_MARTINEZ_002',
        name: 'Carlos Martinez',
        rank: 'Corporal',
        unit: '2nd Battalion, 7th Infantry',
        deployment_location: 'Camp Phoenix',
        status: 'active',
        health_score: 92,
        alerts_count: 0,
        last_alert: 'None',
        deployment_start: '2024-08-20'
      },
      {
        soldier_id: 'PFC_WILLIAMS_003',
        name: 'Sarah Williams',
        rank: 'Private First Class',
        unit: '3rd Battalion, 1st Marines',
        deployment_location: 'Base Medical',
        status: 'medical',
        health_score: 64,
        alerts_count: 5,
        last_alert: '30 mins ago',
        deployment_start: '2024-05-10'
      },
      {
        soldier_id: 'SFC_DAVIS_004',
        name: 'Robert Davis',
        rank: 'Sergeant First Class',
        unit: '1st Special Forces Group',
        deployment_location: 'Training Ground Charlie',
        status: 'active',
        health_score: 95,
        alerts_count: 1,
        last_alert: '1 day ago',
        deployment_start: '2024-03-01'
      },
      {
        soldier_id: 'SGT_BROWN_005',
        name: 'Jennifer Brown',
        rank: 'Sergeant',
        unit: '82nd Airborne Division',
        deployment_location: 'Patrol Route 7',
        status: 'active',
        health_score: 78,
        alerts_count: 3,
        last_alert: '4 hours ago',
        deployment_start: '2024-07-12'
      },
      {
        soldier_id: 'CPT_ANDERSON_006',
        name: 'James Anderson',
        rank: 'Captain',
        unit: '10th Mountain Division',
        deployment_location: 'Command Center Alpha',
        status: 'active',
        health_score: 89,
        alerts_count: 0,
        last_alert: 'None',
        deployment_start: '2024-04-05'
      }
    ];

    setSoldiers(mockSoldiers);
    setLoading(false);
  }, []);

  const filteredSoldiers = soldiers.filter(soldier =>
    soldier.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    soldier.soldier_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    soldier.rank.toLowerCase().includes(searchTerm.toLowerCase()) ||
    soldier.unit.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'var(--accent-green)';
      case 'medical': return 'var(--accent-amber)';
      case 'leave': return 'var(--accent-blue)';
      default: return 'var(--text-secondary)';
    }
  };

  const getHealthScoreColor = (score) => {
    if (score >= 80) return 'var(--accent-green)';
    if (score >= 60) return 'var(--accent-amber)';
    return 'var(--accent-red)';
  };

  if (loading) {
    return (
      <div className="main-content">
        <Navbar title="Soldiers" />
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  const activeCount = soldiers.filter(s => s.status === 'active').length;
  const medicalCount = soldiers.filter(s => s.status === 'medical').length;
  const avgHealthScore = Math.round(soldiers.reduce((acc, s) => acc + s.health_score, 0) / soldiers.length);

  return (
    <div className="main-content">
      <Navbar title="Soldiers" />

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Total Soldiers</span>
            <User size={20} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="stat-value">{soldiers.length}</div>
          <div className="stat-change">Under monitoring</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Active Duty</span>
            <Shield size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="stat-value">{activeCount}</div>
          <div className="stat-change">Deployed</div>
        </div>

        <div className="stat-card warning">
          <div className="stat-header">
            <span className="stat-label">Medical Status</span>
            <AlertTriangle size={20} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="stat-value">{medicalCount}</div>
          <div className="stat-change">Requires attention</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Avg Health Score</span>
            <Activity size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="stat-value">{avgHealthScore}%</div>
          <div className="stat-change">↑ 3% this month</div>
        </div>
      </div>

      {/* Search */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="search-box" style={{ maxWidth: '100%' }}>
          <Search className="search-icon" size={18} />
          <input
            type="text"
            className="search-input"
            placeholder="Search by name, ID, rank, or unit..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Soldiers Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', 
        gap: '20px' 
      }}>
        {filteredSoldiers.map((soldier) => (
          <div 
            key={soldier.soldier_id}
            className="card"
            style={{
              borderLeft: `4px solid ${getStatusColor(soldier.status)}`,
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onClick={() => navigate(`/soldier/${soldier.soldier_id}`)}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            {/* Header */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'flex-start',
              marginBottom: '16px' 
            }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    background: 'var(--gradient-success)',
                    borderRadius: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '20px',
                    fontWeight: '700',
                    color: '#fff'
                  }}>
                    {soldier.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <h4 style={{ margin: 0, fontSize: '18px', fontWeight: '600' }}>
                      {soldier.name}
                    </h4>
                    <p style={{ 
                      fontSize: '13px', 
                      color: 'var(--text-secondary)', 
                      margin: 0 
                    }}>
                      {soldier.rank}
                    </p>
                  </div>
                </div>
              </div>

              <span className={`badge badge-${
                soldier.status === 'active' ? 'success' :
                soldier.status === 'medical' ? 'warning' : 'info'
              }`}>
                {soldier.status}
              </span>
            </div>

            {/* Soldier Info */}
            <div style={{ 
              background: 'var(--secondary-bg)', 
              padding: '12px', 
              borderRadius: '6px',
              marginBottom: '12px'
            }}>
              <div style={{ marginBottom: '8px' }}>
                <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '2px' }}>
                  ID
                </p>
                <p style={{ 
                  fontSize: '13px', 
                  fontWeight: '600', 
                  fontFamily: 'monospace',
                  color: 'var(--accent-blue)',
                  margin: 0
                }}>
                  {soldier.soldier_id}
                </p>
              </div>

              <div>
                <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '2px' }}>
                  Unit
                </p>
                <p style={{ fontSize: '13px', margin: 0 }}>
                  {soldier.unit}
                </p>
              </div>
            </div>

            {/* Location */}
            <div style={{ marginBottom: '12px' }}>
              <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                <MapPin size={11} style={{ display: 'inline', marginRight: '4px' }} />
                Deployment Location
              </p>
              <p style={{ fontSize: '13px', margin: 0 }}>
                {soldier.deployment_location}
              </p>
            </div>

            {/* Health Score */}
            <div style={{
              background: 'var(--primary-bg)',
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '12px'
            }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px'
              }}>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>
                  HEALTH SCORE
                </span>
                <span style={{ 
                  fontSize: '18px', 
                  fontWeight: '700',
                  color: getHealthScoreColor(soldier.health_score)
                }}>
                  {soldier.health_score}%
                </span>
              </div>
              
              {/* Progress Bar */}
              <div style={{
                width: '100%',
                height: '6px',
                background: 'var(--secondary-bg)',
                borderRadius: '3px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${soldier.health_score}%`,
                  height: '100%',
                  background: getHealthScoreColor(soldier.health_score),
                  borderRadius: '3px',
                  transition: 'width 0.3s ease'
                }} />
              </div>
            </div>

            {/* Alerts */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              paddingTop: '12px',
              borderTop: '1px solid var(--border-color)',
              fontSize: '12px',
              color: 'var(--text-secondary)'
            }}>
              <div>
                <AlertTriangle size={12} style={{ display: 'inline', marginRight: '4px' }} />
                {soldier.alerts_count} active alert{soldier.alerts_count !== 1 ? 's' : ''}
              </div>
              <div>
                Last: {soldier.last_alert}
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredSoldiers.length === 0 && (
        <div className="card">
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <User size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
            <p>No soldiers found matching your search</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Soldiers;