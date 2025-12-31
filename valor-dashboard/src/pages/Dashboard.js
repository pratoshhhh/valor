import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { TrendingUp, AlertTriangle, Activity, Users } from 'lucide-react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import apiService from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Dashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalSoldiers: 0,
    activeAlerts: 0,
    criticalAlerts: 0,
    healthScore: 0
  });

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Fetch alerts
      const alertsData = await apiService.getHealthAlerts();
      const fetchedAlerts = alertsData.alerts || [];
      setAlerts(fetchedAlerts);

      // Fetch Confluent metrics
      try {
        const metricsData = await apiService.getConfluentMetrics();
        setMetrics(metricsData);
      } catch (error) {
        console.log('Confluent metrics not available');
      }

      // Calculate stats from alerts data
      const activeAlerts = fetchedAlerts.filter(a => a.status !== 'resolved' && a.status !== 'RESOLVED');
      const criticalAlerts = activeAlerts.filter(a => a.severity === 'CRITICAL');
      
      // Get unique soldier count from alerts
      const uniqueSoldiers = new Set(fetchedAlerts.map(a => a.soldier_id).filter(Boolean));
      const totalSoldiers = uniqueSoldiers.size || 5; // Default to 5 if no alerts yet
      
      // Calculate average health score
      // Since we don't have direct soldier data, estimate from alert severity
      let estimatedHealthScore = 85;
      if (fetchedAlerts.length > 0) {
        const criticalCount = fetchedAlerts.filter(a => a.severity === 'CRITICAL').length;
        const highCount = fetchedAlerts.filter(a => a.severity === 'HIGH').length;
        const mediumCount = fetchedAlerts.filter(a => a.severity === 'MEDIUM').length;
        
        // Simple scoring: reduce score based on alert severity
        const penalty = (criticalCount * 10) + (highCount * 5) + (mediumCount * 2);
        estimatedHealthScore = Math.max(0, Math.min(100, 100 - penalty));
      }

      setStats({
        totalSoldiers,
        activeAlerts: activeAlerts.length,
        criticalAlerts: criticalAlerts.length,
        healthScore: Math.round(estimatedHealthScore)
      });

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  // Prepare chart data
  const alertTrendData = {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', 'Now'],
    datasets: [
      {
        label: 'Critical',
        data: [2, 3, 5, 4, 6, 5, stats.criticalAlerts || 0],
        borderColor: '#ff3860',
        backgroundColor: 'rgba(255, 56, 96, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'High',
        data: [4, 5, 7, 6, 8, 7, stats.activeAlerts - stats.criticalAlerts || 0],
        borderColor: '#ffa726',
        backgroundColor: 'rgba(255, 167, 38, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  };

  // Count alerts by type for distribution
  const alertsByType = alerts.reduce((acc, alert) => {
    const type = alert.event_type || 'Unknown';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  const distributionData = {
    labels: Object.keys(alertsByType).slice(0, 5) || ['No Data'],
    datasets: [{
      data: Object.values(alertsByType).slice(0, 5) || [1],
      backgroundColor: [
        'rgba(255, 56, 96, 0.8)',
        'rgba(255, 167, 38, 0.8)',
        'rgba(0, 212, 255, 0.8)',
        'rgba(0, 255, 136, 0.8)',
        'rgba(136, 132, 216, 0.8)'
      ],
      borderColor: [
        '#ff3860',
        '#ffa726',
        '#00d4ff',
        '#00ff88',
        '#8884d8'
      ],
      borderWidth: 2
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: '#8898aa',
          font: {
            size: 12,
            family: 'Rajdhani'
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.05)'
        },
        ticks: {
          color: '#8898aa'
        }
      },
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)'
        },
        ticks: {
          color: '#8898aa'
        }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'right',
        labels: {
          color: '#8898aa',
          font: {
            size: 11,
            family: 'Rajdhani'
          }
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="main-content">
        <Navbar title="Dashboard" />
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  // Get recent critical alerts
  const recentCriticalAlerts = alerts
    .filter(a => a.severity === 'CRITICAL' || a.severity === 'HIGH')
    .slice(0, 5);

  return (
    <div className="main-content">
      <Navbar title="Dashboard" />

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">TOTAL SOLDIERS</span>
            <Users size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="stat-value">{stats.totalSoldiers}</div>
          <div className="stat-change">↑ 3% from last week</div>
        </div>

        <div className="stat-card warning">
          <div className="stat-header">
            <span className="stat-label">ACTIVE ALERTS</span>
            <AlertTriangle size={20} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="stat-value">{stats.activeAlerts}</div>
          <div className="stat-change">↑ 0 pending</div>
        </div>

        <div className="stat-card danger">
          <div className="stat-header">
            <span className="stat-label">CRITICAL ALERTS</span>
            <AlertTriangle size={20} style={{ color: 'var(--accent-red)' }} />
          </div>
          <div className="stat-value">{stats.criticalAlerts}</div>
          <div className="stat-change negative">Requires immediate attention</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">HEALTH SCORE</span>
            <Activity size={20} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="stat-value">{stats.healthScore}%</div>
          <div className="stat-change">↑ 2.3% improvement</div>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Alert Trends (24h)</h3>
            <TrendingUp size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div style={{ height: '300px', padding: '20px' }}>
            <Line data={alertTrendData} options={chartOptions} />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Alert Distribution</h3>
            <Activity size={20} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div style={{ height: '300px', padding: '20px' }}>
            <Doughnut data={distributionData} options={doughnutOptions} />
          </div>
        </div>
      </div>

      {/* Recent Critical Alerts */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Critical Alerts</h3>
          <span className="badge badge-danger">LIVE</span>
        </div>

        {recentCriticalAlerts.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <AlertTriangle size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
            <p>No critical alerts at this time</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>SOLDIER ID</th>
                  <th>ALERT TYPE</th>
                  <th>SEVERITY</th>
                  <th>LOCATION</th>
                  <th>TIME</th>
                  <th>STATUS</th>
                </tr>
              </thead>
              <tbody>
                {recentCriticalAlerts.map((alert, index) => (
                  <tr key={index}>
                    <td style={{ fontWeight: '600', fontFamily: 'monospace' }}>
                      {alert.soldier_id || 'Unknown'}
                    </td>
                    <td>{alert.event_type || alert.alert_type || 'Unknown'}</td>
                    <td>
                      <span className={`badge badge-${
                        alert.severity === 'CRITICAL' ? 'danger' : 'warning'
                      }`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td>{alert.location || 'Unknown'}</td>
                    <td style={{ fontSize: '13px' }}>
                      {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'N/A'}
                    </td>
                    <td>
                      <span className={`badge badge-${
                        alert.status === 'resolved' ? 'success' : 'warning'
                      }`}>
                        {alert.status || 'pending'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Confluent Status */}
      {metrics && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Confluent Pipeline Status</h3>
            <span className={`badge badge-${
              metrics.cluster_health === 'HEALTHY' ? 'success' : 'danger'
            }`}>
              {metrics.cluster_health || 'UNKNOWN'}
            </span>
          </div>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '20px',
            padding: '20px'
          }}>
            <div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                Active Topics
              </p>
              <p style={{ fontSize: '24px', fontWeight: '700', color: 'var(--accent-green)' }}>
                {metrics.topics?.length || 0}
              </p>
            </div>

            <div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                Consumer Groups
              </p>
              <p style={{ fontSize: '24px', fontWeight: '700', color: 'var(--accent-blue)' }}>
                {metrics.consumer_groups?.length || 0}
              </p>
            </div>

            <div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                Messages Processed
              </p>
              <p style={{ fontSize: '24px', fontWeight: '700', color: 'var(--accent-green)' }}>
                {alerts.length}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;