import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { 
  User, MapPin, Shield, Activity, AlertTriangle, FileText, 
  Calendar, ArrowLeft, Heart, Thermometer, Wind, CheckCircle 
} from 'lucide-react';
import { Line } from 'react-chartjs-2';
import apiService from '../services/api';

const SoldierProfile = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [soldier, setSoldier] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingReport, setGeneratingReport] = useState(false);

  useEffect(() => {
    fetchSoldierData();
  }, [id]);

  const fetchSoldierData = async () => {
    try {
      const data = await apiService.getSoldierSummary(id);
      setSoldier(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching soldier data:', error);
      // Fallback to mock data
      setSoldier({
        soldier_id: id,
        name: 'Michael Johnson',
        rank: 'Sergeant',
        unit: '1st Battalion, 5th Marines',
        deployment_location: 'Forward Operating Base Delta',
        deployment_start: '2024-06-15',
        status: 'active',
        health_score: 87,
        vitals: {
          heart_rate: 78,
          temperature: 98.6,
          oxygen: 98,
          blood_pressure: '120/80'
        },
        recent_alerts: [
          {
            type: 'Heat Stress',
            severity: 'HIGH',
            timestamp: '2025-12-30T16:30:00Z',
            details: 'Core temperature elevated during patrol'
          },
          {
            type: 'Burn Pit Exposure',
            severity: 'MEDIUM',
            timestamp: '2025-12-29T14:15:00Z',
            details: 'Detected near waste disposal area'
          }
        ],
        health_history: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          scores: [92, 89, 91, 88, 85, 87]
        },
        exposure_count: 12,
        medical_visits: 3
      });
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      await apiService.generateVAReport(id);
      alert('VA Report generated successfully!');
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report');
    } finally {
      setGeneratingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="main-content">
        <Navbar title="Soldier Profile" />
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  const healthTrendData = {
    labels: soldier.health_history?.labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Health Score',
        data: soldier.health_history?.scores || [92, 89, 91, 88, 85, 87],
        borderColor: '#00ff88',
        backgroundColor: 'rgba(0, 255, 136, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        min: 0,
        max: 100,
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

  const getHealthScoreColor = (score) => {
    if (score >= 80) return 'var(--accent-green)';
    if (score >= 60) return 'var(--accent-amber)';
    return 'var(--accent-red)';
  };

  return (
    <div className="main-content">
      <Navbar title="Soldier Profile" />

      {/* Back Button */}
      <button 
        className="btn btn-secondary"
        onClick={() => navigate('/soldiers')}
        style={{ marginBottom: '20px' }}
      >
        <ArrowLeft size={16} />
        Back to Soldiers
      </button>

      {/* Profile Header */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'flex-start' }}>
          <div style={{
            width: '120px',
            height: '120px',
            background: 'var(--gradient-success)',
            borderRadius: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '48px',
            fontWeight: '700',
            color: '#fff',
            flexShrink: 0
          }}>
            {soldier.name?.split(' ').map(n => n[0]).join('') || 'MJ'}
          </div>

          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <h2 style={{ margin: '0 0 8px 0', fontSize: '32px' }}>{soldier.name}</h2>
                <p style={{ fontSize: '16px', color: 'var(--text-secondary)', margin: '0 0 12px 0' }}>
                  {soldier.rank} • {soldier.unit}
                </p>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  <span className={`badge badge-${soldier.status === 'active' ? 'success' : 'warning'}`}>
                    {soldier.status}
                  </span>
                  <span className="badge badge-info">
                    ID: {soldier.soldier_id}
                  </span>
                </div>
              </div>

              <button
                className="btn btn-primary"
                onClick={handleGenerateReport}
                disabled={generatingReport}
              >
                {generatingReport ? (
                  <><div className="spinner" style={{ width: '16px', height: '16px' }}></div> Generating...</>
                ) : (
                  <><FileText size={16} /> Generate VA Report</>
                )}
              </button>
            </div>

            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '16px',
              padding: '16px',
              background: 'var(--secondary-bg)',
              borderRadius: '8px'
            }}>
              <div>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  <MapPin size={12} style={{ display: 'inline', marginRight: '4px' }} />
                  Deployment Location
                </p>
                <p style={{ fontSize: '14px', fontWeight: '600', margin: 0 }}>
                  {soldier.deployment_location}
                </p>
              </div>

              <div>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  <Calendar size={12} style={{ display: 'inline', marginRight: '4px' }} />
                  Deployment Start
                </p>
                <p style={{ fontSize: '14px', fontWeight: '600', margin: 0 }}>
                  {new Date(soldier.deployment_start).toLocaleDateString()}
                </p>
              </div>

              <div>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  <Activity size={12} style={{ display: 'inline', marginRight: '4px' }} />
                  Health Score
                </p>
                <p style={{ 
                  fontSize: '20px', 
                  fontWeight: '700', 
                  color: getHealthScoreColor(soldier.health_score),
                  margin: 0
                }}>
                  {soldier.health_score}%
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Exposure Events</span>
            <Wind size={20} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="stat-value">{soldier.exposure_count || 0}</div>
          <div className="stat-change">Total recorded</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Medical Visits</span>
            <Heart size={20} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="stat-value">{soldier.medical_visits || 0}</div>
          <div className="stat-change">This deployment</div>
        </div>

        <div className="stat-card warning">
          <div className="stat-header">
            <span className="stat-label">Active Alerts</span>
            <AlertTriangle size={20} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="stat-value">{soldier.recent_alerts?.length || 0}</div>
          <div className="stat-change">Requiring attention</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Days Deployed</span>
            <Calendar size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="stat-value">
            {Math.floor((new Date() - new Date(soldier.deployment_start)) / (1000 * 60 * 60 * 24))}
          </div>
          <div className="stat-change">Current deployment</div>
        </div>
      </div>

      {/* Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        {/* Current Vitals */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Current Vitals</h3>
            <Activity size={20} style={{ color: 'var(--accent-green)' }} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{
              background: 'var(--secondary-bg)',
              padding: '16px',
              borderRadius: '8px',
              borderLeft: '4px solid var(--accent-red)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Heart size={16} style={{ color: 'var(--accent-red)' }} />
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>
                  HEART RATE
                </span>
              </div>
              <p style={{ fontSize: '24px', fontWeight: '700', margin: 0 }}>
                {soldier.vitals?.heart_rate || 78} <span style={{ fontSize: '14px', fontWeight: '400' }}>bpm</span>
              </p>
            </div>

            <div style={{
              background: 'var(--secondary-bg)',
              padding: '16px',
              borderRadius: '8px',
              borderLeft: '4px solid var(--accent-amber)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Thermometer size={16} style={{ color: 'var(--accent-amber)' }} />
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>
                  TEMPERATURE
                </span>
              </div>
              <p style={{ fontSize: '24px', fontWeight: '700', margin: 0 }}>
                {soldier.vitals?.temperature || 98.6} <span style={{ fontSize: '14px', fontWeight: '400' }}>°F</span>
              </p>
            </div>

            <div style={{
              background: 'var(--secondary-bg)',
              padding: '16px',
              borderRadius: '8px',
              borderLeft: '4px solid var(--accent-blue)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Wind size={16} style={{ color: 'var(--accent-blue)' }} />
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>
                  OXYGEN
                </span>
              </div>
              <p style={{ fontSize: '24px', fontWeight: '700', margin: 0 }}>
                {soldier.vitals?.oxygen || 98} <span style={{ fontSize: '14px', fontWeight: '400' }}>%</span>
              </p>
            </div>

            <div style={{
              background: 'var(--secondary-bg)',
              padding: '16px',
              borderRadius: '8px',
              borderLeft: '4px solid var(--accent-green)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Activity size={16} style={{ color: 'var(--accent-green)' }} />
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>
                  BLOOD PRESSURE
                </span>
              </div>
              <p style={{ fontSize: '24px', fontWeight: '700', margin: 0 }}>
                {soldier.vitals?.blood_pressure || '120/80'}
              </p>
            </div>
          </div>
        </div>

        {/* Health Trend */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Health Score Trend (6 months)</h3>
            <Activity size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div style={{ height: '240px' }}>
            <Line data={healthTrendData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Health Alerts</h3>
          <span className="badge badge-danger">{soldier.recent_alerts?.length || 0} Active</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {(soldier.recent_alerts || []).map((alert, index) => (
            <div
              key={index}
              style={{
                background: 'var(--secondary-bg)',
                border: `1px solid ${alert.severity === 'CRITICAL' ? 'var(--accent-red)' : 'var(--accent-amber)'}`,
                borderLeft: `4px solid ${alert.severity === 'CRITICAL' ? 'var(--accent-red)' : 'var(--accent-amber)'}`,
                borderRadius: '8px',
                padding: '16px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <AlertTriangle size={18} style={{ 
                      color: alert.severity === 'CRITICAL' ? 'var(--accent-red)' : 'var(--accent-amber)' 
                    }} />
                    <h4 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>
                      {alert.type}
                    </h4>
                    <span className={`badge badge-${alert.severity === 'CRITICAL' ? 'danger' : 'warning'}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <p style={{ fontSize: '14px', color: 'var(--text-secondary)', margin: '0 0 8px 0' }}>
                    {alert.details}
                  </p>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: 0 }}>
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ))}

          {(!soldier.recent_alerts || soldier.recent_alerts.length === 0) && (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <CheckCircle size={48} style={{ opacity: 0.3, marginBottom: '16px', color: 'var(--accent-green)' }} />
              <p>No active health alerts</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SoldierProfile;