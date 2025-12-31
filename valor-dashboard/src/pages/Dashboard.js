import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { Users, AlertTriangle, Activity, TrendingUp, Heart, Thermometer } from 'lucide-react';
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
  Legend
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
  Legend
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
      const [alertsData, metricsData] = await Promise.all([
        apiService.getHealthAlerts(),
        apiService.getConfluentMetrics()
      ]);

      setAlerts(alertsData.alerts || []);
      setMetrics(metricsData);

      // Calculate stats
      const activeAlerts = (alertsData.alerts || []).filter(a => a.status !== 'resolved');
      const criticalAlerts = activeAlerts.filter(a => a.severity === 'CRITICAL');

      setStats({
        totalSoldiers: alertsData.total_soldiers || 0,
        activeAlerts: activeAlerts.length,
        criticalAlerts: criticalAlerts.length,
        healthScore: alertsData.overall_health_score || 0
      });

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const alertTrendData = {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    datasets: [
      {
        label: 'Critical',
        data: [2, 3, 5, 4, 6, stats.criticalAlerts],
        borderColor: '#ff3860',
        backgroundColor: 'rgba(255, 56, 96, 0.1)',
        tension: 0.4
      },
      {
        label: 'Warning',
        data: [5, 7, 6, 8, 7, stats.activeAlerts - stats.criticalAlerts],
        borderColor: '#ffa726',
        backgroundColor: 'rgba(255, 167, 38, 0.1)',
        tension: 0.4
      }
    ]
  };

  const alertDistributionData = {
    labels: ['Burn Pit Exposure', 'Heat Stress', 'Cardiac Irregularity', 'Respiratory', 'Other'],
    datasets: [
      {
        data: [12, 8, 5, 7, 3],
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
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
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

  return (
    <div className="main-content">
      <Navbar title="Dashboard" />

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Total Soldiers</span>
            <div className="stat-icon">
              <Users size={20} />
            </div>
          </div>
          <div className="stat-value">{stats.totalSoldiers}</div>
          <div className="stat-change">↑ 3% from last week</div>
        </div>

        <div className="stat-card warning">
          <div className="stat-header">
            <span className="stat-label">Active Alerts</span>
            <div className="stat-icon" style={{ background: 'rgba(255, 167, 38, 0.1)', color: 'var(--accent-amber)' }}>
              <AlertTriangle size={20} />
            </div>
          </div>
          <div className="stat-value">{stats.activeAlerts}</div>
          <div className="stat-change">↑ {stats.activeAlerts} pending</div>
        </div>

        <div className="stat-card danger">
          <div className="stat-header">
            <span className="stat-label">Critical Alerts</span>
            <div className="stat-icon" style={{ background: 'rgba(255, 56, 96, 0.1)', color: 'var(--accent-red)' }}>
              <Heart size={20} />
            </div>
          </div>
          <div className="stat-value">{stats.criticalAlerts}</div>
          <div className="stat-change negative">Requires immediate attention</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Health Score</span>
            <div className="stat-icon" style={{ background: 'rgba(0, 212, 255, 0.1)', color: 'var(--accent-blue)' }}>
              <Activity size={20} />
            </div>
          </div>
          <div className="stat-value">{stats.healthScore}%</div>
          <div className="stat-change">↑ 2.3% improvement</div>
        </div>
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', marginBottom: '24px' }}>
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Alert Trends (24h)</h3>
            <TrendingUp size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div style={{ height: '300px' }}>
            <Line data={alertTrendData} options={chartOptions} />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Alert Distribution</h3>
          </div>
          <div style={{ height: '300px' }}>
            <Doughnut data={alertDistributionData} options={{
              ...chartOptions,
              plugins: {
                legend: {
                  position: 'bottom',
                  labels: {
                    color: '#8898aa',
                    font: {
                      size: 11,
                      family: 'Rajdhani'
                    }
                  }
                }
              }
            }} />
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Critical Alerts</h3>
          <span className="badge badge-danger">Live</span>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Soldier ID</th>
                <th>Alert Type</th>
                <th>Severity</th>
                <th>Location</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {alerts.slice(0, 5).map((alert, index) => (
                <tr key={index}>
                  <td style={{ fontWeight: '600' }}>{alert.soldier_id}</td>
                  <td>{alert.event_type}</td>
                  <td>
                    <span className={`badge badge-${
                      alert.severity === 'CRITICAL' ? 'danger' : 
                      alert.severity === 'HIGH' ? 'warning' : 'info'
                    }`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td>{alert.location}</td>
                  <td style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </td>
                  <td>
                    <span className={`badge ${
                      alert.status === 'resolved' ? 'badge-success' : 'badge-warning'
                    }`}>
                      {alert.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Confluent Metrics Summary */}
      {metrics && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Data Pipeline Status</h3>
            <span className="badge badge-success">Operational</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
            <div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Cluster Health</p>
              <p style={{ fontSize: '20px', fontWeight: '700', color: 'var(--accent-green)' }}>
                {metrics.cluster_health || 'HEALTHY'}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Total Topics</p>
              <p style={{ fontSize: '20px', fontWeight: '700' }}>
                {metrics.topics?.length || 0}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Consumer Groups</p>
              <p style={{ fontSize: '20px', fontWeight: '700' }}>
                {metrics.consumer_groups?.length || 0}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Messages/sec</p>
              <p style={{ fontSize: '20px', fontWeight: '700', color: 'var(--accent-blue)' }}>
                {metrics.throughput || '1.2K'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;