import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { Radio, Battery, Wifi, AlertCircle, CheckCircle, User, MapPin } from 'lucide-react';

const Devices = () => {
  const [devices, setDevices] = useState([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    // Mock device data
    const mockDevices = [
      {
        id: 'DEV-001',
        name: 'Biometric Sensor Alpha',
        type: 'Wearable',
        soldier_id: 'SGT_JOHNSON_001',
        status: 'online',
        battery: 87,
        location: 'Forward Operating Base Delta',
        lastUpdate: new Date(Date.now() - 300000),
        metrics: { heartRate: 78, temperature: 98.6, oxygen: 98 }
      },
      {
        id: 'DEV-002',
        name: 'Heart Monitor Beta',
        type: 'Wearable',
        soldier_id: 'CPL_MARTINEZ_002',
        status: 'online',
        battery: 62,
        location: 'Camp Phoenix',
        lastUpdate: new Date(Date.now() - 120000),
        metrics: { heartRate: 72, temperature: 98.4, oxygen: 99 }
      },
      {
        id: 'DEV-003',
        name: 'Environmental Station 1',
        type: 'Environmental',
        soldier_id: null,
        status: 'warning',
        battery: 34,
        location: 'Burn Pit Zone A',
        lastUpdate: new Date(Date.now() - 60000),
        metrics: { pm25: 156, temperature: 104, humidity: 22 }
      },
      {
        id: 'DEV-004',
        name: 'Burn Pit Detector 1',
        type: 'Environmental',
        soldier_id: null,
        status: 'online',
        battery: 91,
        location: 'Burn Pit Zone B',
        lastUpdate: new Date(Date.now() - 45000),
        metrics: { pm25: 187, voc: 245, co: 12 }
      },
      {
        id: 'DEV-005',
        name: 'Biometric Sensor Gamma',
        type: 'Wearable',
        soldier_id: 'PFC_WILLIAMS_003',
        status: 'offline',
        battery: 8,
        location: 'Base Medical',
        lastUpdate: new Date(Date.now() - 7200000),
        metrics: { heartRate: null, temperature: null, oxygen: null }
      },
      {
        id: 'DEV-006',
        name: 'Heat Stress Monitor A',
        type: 'Wearable',
        soldier_id: 'SFC_DAVIS_004',
        status: 'online',
        battery: 74,
        location: 'Training Ground Charlie',
        lastUpdate: new Date(Date.now() - 90000),
        metrics: { coreTemp: 99.1, skinTemp: 95.2, sweating: 'moderate' }
      },
      {
        id: 'DEV-007',
        name: 'Environmental Station 2',
        type: 'Environmental',
        soldier_id: null,
        status: 'online',
        battery: 68,
        location: 'Main Camp',
        lastUpdate: new Date(Date.now() - 180000),
        metrics: { pm25: 42, temperature: 87, humidity: 31 }
      },
      {
        id: 'DEV-008',
        name: 'Respiratory Monitor Delta',
        type: 'Wearable',
        soldier_id: 'SGT_BROWN_005',
        status: 'warning',
        battery: 21,
        location: 'Patrol Route 7',
        lastUpdate: new Date(Date.now() - 240000),
        metrics: { respiratoryRate: 22, oxygen: 94, cough: 'detected' }
      }
    ];

    setDevices(mockDevices);
  }, []);

  const filteredDevices = devices.filter(device => {
    if (filter === 'all') return true;
    if (filter === 'online') return device.status === 'online';
    if (filter === 'warning') return device.status === 'warning' || device.battery < 30;
    if (filter === 'offline') return device.status === 'offline';
    return true;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'var(--accent-green)';
      case 'warning': return 'var(--accent-amber)';
      case 'offline': return 'var(--accent-red)';
      default: return 'var(--text-secondary)';
    }
  };

  const getBatteryColor = (battery) => {
    if (battery > 60) return 'var(--accent-green)';
    if (battery > 30) return 'var(--accent-amber)';
    return 'var(--accent-red)';
  };

  const onlineCount = devices.filter(d => d.status === 'online').length;
  const warningCount = devices.filter(d => d.status === 'warning' || d.battery < 30).length;
  const offlineCount = devices.filter(d => d.status === 'offline').length;

  return (
    <div className="main-content">
      <Navbar title="Devices & Sensors" />

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Total Devices</span>
            <Radio size={20} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="stat-value">{devices.length}</div>
          <div className="stat-change">Deployed devices</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Online</span>
            <CheckCircle size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="stat-value">{onlineCount}</div>
          <div className="stat-change">↑ Operational</div>
        </div>

        <div className="stat-card warning">
          <div className="stat-header">
            <span className="stat-label">Warning</span>
            <AlertCircle size={20} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="stat-value">{warningCount}</div>
          <div className="stat-change">Needs attention</div>
        </div>

        <div className="stat-card danger">
          <div className="stat-header">
            <span className="stat-label">Offline</span>
            <Wifi size={20} style={{ color: 'var(--accent-red)' }} />
          </div>
          <div className="stat-value">{offlineCount}</div>
          <div className="stat-change negative">Requires service</div>
        </div>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            className={filter === 'all' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setFilter('all')}
          >
            All Devices
          </button>
          <button
            className={filter === 'online' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setFilter('online')}
          >
            Online
          </button>
          <button
            className={filter === 'warning' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setFilter('warning')}
          >
            Warning
          </button>
          <button
            className={filter === 'offline' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setFilter('offline')}
          >
            Offline
          </button>
        </div>
      </div>

      {/* Device Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', 
        gap: '20px' 
      }}>
        {filteredDevices.map((device) => (
          <div 
            key={device.id}
            className="card"
            style={{
              borderLeft: `4px solid ${getStatusColor(device.status)}`,
              transition: 'all 0.3s ease'
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
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <Radio size={18} style={{ color: getStatusColor(device.status) }} />
                  <h4 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>
                    {device.name}
                  </h4>
                </div>
                <p style={{ 
                  fontSize: '12px', 
                  color: 'var(--text-secondary)', 
                  fontFamily: 'monospace',
                  margin: 0 
                }}>
                  {device.id}
                </p>
              </div>

              <span className={`badge badge-${
                device.status === 'online' ? 'success' :
                device.status === 'warning' ? 'warning' : 'danger'
              }`}>
                {device.status}
              </span>
            </div>

            {/* Device Info */}
            <div style={{ 
              background: 'var(--secondary-bg)', 
              padding: '12px', 
              borderRadius: '6px',
              marginBottom: '12px'
            }}>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr 1fr', 
                gap: '12px' 
              }}>
                <div>
                  <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '2px' }}>
                    Type
                  </p>
                  <p style={{ fontSize: '13px', fontWeight: '600', margin: 0 }}>
                    {device.type}
                  </p>
                </div>

                <div>
                  <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '2px' }}>
                    <Battery size={11} style={{ display: 'inline', marginRight: '2px' }} />
                    Battery
                  </p>
                  <p style={{ 
                    fontSize: '13px', 
                    fontWeight: '600', 
                    margin: 0,
                    color: getBatteryColor(device.battery)
                  }}>
                    {device.battery}%
                  </p>
                </div>
              </div>
            </div>

            {/* Soldier Assignment */}
            {device.soldier_id && (
              <div style={{ marginBottom: '12px' }}>
                <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  <User size={11} style={{ display: 'inline', marginRight: '4px' }} />
                  Assigned To
                </p>
                <p style={{ 
                  fontSize: '13px', 
                  fontWeight: '600', 
                  fontFamily: 'monospace',
                  color: 'var(--accent-blue)',
                  margin: 0
                }}>
                  {device.soldier_id}
                </p>
              </div>
            )}

            {/* Location */}
            <div style={{ marginBottom: '12px' }}>
              <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                <MapPin size={11} style={{ display: 'inline', marginRight: '4px' }} />
                Location
              </p>
              <p style={{ fontSize: '13px', margin: 0 }}>
                {device.location}
              </p>
            </div>

            {/* Metrics */}
            {device.metrics && Object.keys(device.metrics).length > 0 && (
              <div style={{
                background: 'var(--primary-bg)',
                padding: '12px',
                borderRadius: '6px',
                marginBottom: '12px'
              }}>
                <p style={{ 
                  fontSize: '11px', 
                  color: 'var(--text-secondary)', 
                  marginBottom: '8px',
                  fontWeight: '600'
                }}>
                  LIVE METRICS
                </p>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(80px, 1fr))', 
                  gap: '8px' 
                }}>
                  {Object.entries(device.metrics).map(([key, value]) => (
                    <div key={key}>
                      <p style={{ fontSize: '10px', color: 'var(--text-secondary)', marginBottom: '2px' }}>
                        {key}
                      </p>
                      <p style={{ 
                        fontSize: '13px', 
                        fontWeight: '600', 
                        color: value ? 'var(--accent-green)' : 'var(--text-secondary)',
                        margin: 0
                      }}>
                        {value || 'N/A'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Last Update */}
            <div style={{ 
              fontSize: '11px', 
              color: 'var(--text-secondary)',
              paddingTop: '8px',
              borderTop: '1px solid var(--border-color)'
            }}>
              Last update: {device.lastUpdate.toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>

      {filteredDevices.length === 0 && (
        <div className="card">
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <Radio size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
            <p>No devices found matching your filter</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Devices;