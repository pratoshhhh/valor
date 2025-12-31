import React, { useState, useEffect } from 'react';
import { getHealthAlerts, resolveAlert } from '../services/api';
import '../styles/HealthAlerts.css';

function HealthAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');

  useEffect(() => {
    fetchAlerts();
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const data = await getHealthAlerts();
      setAlerts(data.alerts || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setLoading(false);
    }
  };

  const handleResolve = async (alertId) => {
    try {
      await resolveAlert(alertId, 'Resolved by user');
      fetchAlerts(); // Refresh the list
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  // Helper function to safely get event type
  const getEventType = (alert) => {
    return alert.event_type || alert.alert_type || 'Unknown Event';
  };

  // Helper function to get message
  const getMessage = (alert) => {
    if (alert.message) return alert.message;
    if (alert.details?.description) return alert.details.description;
    return `Alert for ${alert.soldier_id}`;
  };

  const filteredAlerts = alerts.filter(alert => {
    // Get event type safely
    const eventType = getEventType(alert);
    const message = getMessage(alert);
    const soldierId = alert.soldier_id || '';
    const severity = alert.severity || '';
    const status = alert.status || (alert.resolved === false ? 'pending' : 'resolved');
    
    // Search filter - safely check all fields
    const matchesSearch = searchTerm === '' || 
      soldierId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      eventType.toLowerCase().includes(searchTerm.toLowerCase()) ||
      message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      severity.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Status filter
    const matchesStatus = filterStatus === 'all' || status === filterStatus;
    
    // Severity filter
    const matchesSeverity = filterSeverity === 'all' || severity === filterSeverity;
    
    return matchesSearch && matchesStatus && matchesSeverity;
  });

  // Get severity badge class
  const getSeverityClass = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'severity-critical';
      case 'HIGH':
        return 'severity-high';
      case 'MEDIUM':
        return 'severity-medium';
      case 'LOW':
        return 'severity-low';
      default:
        return 'severity-medium';
    }
  };

  // Get status badge class
  const getStatusClass = (alert) => {
    const status = alert.status || (alert.resolved === false ? 'pending' : 'resolved');
    return status === 'pending' ? 'status-pending' : 'status-resolved';
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (e) {
      return timestamp;
    }
  };

  if (loading) {
    return (
      <div className="health-alerts">
        <div className="loading">Loading alerts...</div>
      </div>
    );
  }

  return (
    <div className="health-alerts">
      <div className="alerts-header">
        <h1>Health Alerts</h1>
        <div className="alerts-stats">
          <div className="stat-item">
            <span className="stat-label">Total Alerts:</span>
            <span className="stat-value">{alerts.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Pending:</span>
            <span className="stat-value">
              {alerts.filter(a => (a.status || (a.resolved === false ? 'pending' : 'resolved')) === 'pending').length}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Critical:</span>
            <span className="stat-value severity-critical">
              {alerts.filter(a => a.severity === 'CRITICAL').length}
            </span>
          </div>
        </div>
      </div>

      <div className="alerts-filters">
        <input
          type="text"
          placeholder="Search by soldier ID, event type, or message..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="resolved">Resolved</option>
        </select>

        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Severity</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      <div className="alerts-list">
        {filteredAlerts.length === 0 ? (
          <div className="no-alerts">
            {searchTerm || filterStatus !== 'all' || filterSeverity !== 'all'
              ? 'No alerts match your filters'
              : 'No alerts found'}
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const status = alert.status || (alert.resolved === false ? 'pending' : 'resolved');
            const eventType = getEventType(alert);
            const message = getMessage(alert);
            
            return (
              <div key={alert.id || alert.event_id} className="alert-card">
                <div className="alert-header">
                  <div className="alert-title">
                    <span className={`severity-badge ${getSeverityClass(alert.severity)}`}>
                      {alert.severity || 'MEDIUM'}
                    </span>
                    <h3>{eventType}</h3>
                    <span className={`status-badge ${getStatusClass(alert)}`}>
                      {status}
                    </span>
                  </div>
                  {status === 'pending' && (
                    <button
                      onClick={() => handleResolve(alert.id || alert.event_id)}
                      className="resolve-btn"
                    >
                      Resolve
                    </button>
                  )}
                </div>

                <div className="alert-body">
                  <div className="alert-info">
                    <div className="info-row">
                      <span className="info-label">Soldier ID:</span>
                      <span className="info-value">{alert.soldier_id || 'N/A'}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Event ID:</span>
                      <span className="info-value">{alert.event_id || alert.id || 'N/A'}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Timestamp:</span>
                      <span className="info-value">{formatTimestamp(alert.timestamp || alert.created_at)}</span>
                    </div>
                    {alert.location && (
                      <div className="info-row">
                        <span className="info-label">Location:</span>
                        <span className="info-value">{alert.location}</span>
                      </div>
                    )}
                  </div>

                  <div className="alert-message">
                    <p>{message}</p>
                  </div>

                  {alert.details && typeof alert.details === 'object' && (
                    <div className="alert-details">
                      <h4>Details:</h4>
                      <ul>
                        {Object.entries(alert.details).map(([key, value]) => {
                          if (key === 'description') return null; // Already shown in message
                          return (
                            <li key={key}>
                              <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>{' '}
                              {value !== null && value !== undefined ? String(value) : 'N/A'}
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  )}

                  {/* Show environmental data if available */}
                  {(alert.noise_level_db || alert.air_quality_index) && (
                    <div className="environmental-data">
                      <h4>Environmental Data:</h4>
                      <ul>
                        {alert.noise_level_db && (
                          <li><strong>Noise Level:</strong> {alert.noise_level_db.toFixed(1)} dB</li>
                        )}
                        {alert.air_quality_index && (
                          <li><strong>Air Quality Index:</strong> {alert.air_quality_index}</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default HealthAlerts;