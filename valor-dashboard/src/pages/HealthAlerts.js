import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { AlertTriangle, CheckCircle, Clock, MapPin, Search, Filter } from 'lucide-react';
import apiService from '../services/api';

const HealthAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [resolving, setResolving] = useState(null);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const data = await apiService.getHealthAlerts();
      setAlerts(data.alerts || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setLoading(false);
    }
  };

  const handleResolveAlert = async (alertId) => {
    setResolving(alertId);
    try {
      await apiService.resolveAlert(alertId, 'Resolved by operator');
      await fetchAlerts();
    } catch (error) {
      console.error('Error resolving alert:', error);
    } finally {
      setResolving(null);
    }
  };

  const filteredAlerts = alerts
    .filter(alert => {
      if (filter === 'all') return true;
      if (filter === 'active') return alert.status !== 'resolved';
      if (filter === 'critical') return alert.severity === 'CRITICAL';
      return alert.severity === filter.toUpperCase();
    })
    .filter(alert => 
      alert.soldier_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.event_type.toLowerCase().includes(searchTerm.toLowerCase())
    );

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'var(--accent-red)';
      case 'HIGH': return 'var(--accent-amber)';
      case 'MEDIUM': return 'var(--accent-blue)';
      default: return 'var(--accent-green)';
    }
  };

  if (loading) {
    return (
      <div className="main-content">
        <Navbar title="Health Alerts" />
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  const criticalCount = alerts.filter(a => a.severity === 'CRITICAL' && a.status !== 'resolved').length;
  const activeCount = alerts.filter(a => a.status !== 'resolved').length;

  return (
    <div className="main-content">
      <Navbar title="Health Alerts" />

      {/* Alert Summary */}
      <div className="stats-grid">
        <div className="stat-card danger">
          <div className="stat-header">
            <span className="stat-label">Critical Alerts</span>
            <AlertTriangle size={20} style={{ color: 'var(--accent-red)' }} />
          </div>
          <div className="stat-value">{criticalCount}</div>
          <div className="stat-change negative">Requires immediate action</div>
        </div>

        <div className="stat-card warning">
          <div className="stat-header">
            <span className="stat-label">Active Alerts</span>
            <Clock size={20} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="stat-value">{activeCount}</div>
          <div className="stat-change">Pending resolution</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Resolved Today</span>
            <CheckCircle size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="stat-value">{alerts.filter(a => a.status === 'resolved').length}</div>
          <div className="stat-change">↑ 15% from yesterday</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Response Time</span>
            <Clock size={20} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="stat-value">4.2m</div>
          <div className="stat-change">Average response time</div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div className="search-box" style={{ flex: '1', minWidth: '300px' }}>
            <Search className="search-icon" size={18} />
            <input
              type="text"
              className="search-input"
              placeholder="Search by soldier ID or alert type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <Filter size={20} style={{ color: 'var(--text-secondary)' }} />
            <button
              className={filter === 'all' ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setFilter('all')}
              style={{ padding: '8px 16px' }}
            >
              All
            </button>
            <button
              className={filter === 'active' ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setFilter('active')}
              style={{ padding: '8px 16px' }}
            >
              Active
            </button>
            <button
              className={filter === 'critical' ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setFilter('critical')}
              style={{ padding: '8px 16px' }}
            >
              Critical
            </button>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Health Alerts ({filteredAlerts.length})</h3>
          <span className="badge badge-danger">Live Updates</span>
        </div>

        {filteredAlerts.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <AlertTriangle size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
            <p>No alerts found matching your criteria</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {filteredAlerts.map((alert, index) => (
              <div
                key={index}
                style={{
                  background: 'var(--secondary-bg)',
                  border: `1px solid ${getSeverityColor(alert.severity)}`,
                  borderLeft: `4px solid ${getSeverityColor(alert.severity)}`,
                  borderRadius: '8px',
                  padding: '20px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateX(4px)';
                  e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateX(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                      <AlertTriangle size={20} style={{ color: getSeverityColor(alert.severity) }} />
                      <h4 style={{ margin: 0, fontSize: '18px', fontWeight: '600' }}>
                        {alert.event_type}
                      </h4>
                      <span className={`badge badge-${
                        alert.severity === 'CRITICAL' ? 'danger' :
                        alert.severity === 'HIGH' ? 'warning' : 'info'
                      }`}>
                        {alert.severity}
                      </span>
                      {alert.status === 'resolved' && (
                        <span className="badge badge-success">Resolved</span>
                      )}
                    </div>

                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                      gap: '16px',
                      marginBottom: '12px'
                    }}>
                      <div>
                        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                          Soldier ID
                        </p>
                        <p style={{ fontSize: '15px', fontWeight: '600' }}>{alert.soldier_id}</p>
                      </div>

                      <div>
                        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                          <MapPin size={12} style={{ display: 'inline', marginRight: '4px' }} />
                          Location
                        </p>
                        <p style={{ fontSize: '15px' }}>{alert.location}</p>
                      </div>

                      <div>
                        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                          <Clock size={12} style={{ display: 'inline', marginRight: '4px' }} />
                          Timestamp
                        </p>
                        <p style={{ fontSize: '15px' }}>
                          {new Date(alert.timestamp).toLocaleString()}
                        </p>
                      </div>

                      <div>
                        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                          Event ID
                        </p>
                        <p style={{ fontSize: '13px', fontFamily: 'monospace', color: 'var(--accent-blue)' }}>
                          {alert.event_id}
                        </p>
                      </div>
                    </div>

                    {alert.details && (
                      <div style={{
                        background: 'var(--primary-bg)',
                        padding: '12px',
                        borderRadius: '6px',
                        marginTop: '12px'
                      }}>
                        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
                          <strong>Details:</strong> {JSON.stringify(alert.details)}
                        </p>
                      </div>
                    )}
                  </div>

                  {alert.status !== 'resolved' && (
                    <button
                      className="btn btn-primary"
                      onClick={() => handleResolveAlert(alert.event_id)}
                      disabled={resolving === alert.event_id}
                      style={{ marginLeft: '16px' }}
                    >
                      {resolving === alert.event_id ? (
                        <><div className="spinner" style={{ width: '16px', height: '16px' }}></div> Resolving...</>
                      ) : (
                        <><CheckCircle size={16} /> Resolve</>
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HealthAlerts;