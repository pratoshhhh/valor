import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { FileText, Download, Loader, User, Calendar, CheckCircle, AlertTriangle } from 'lucide-react';
import apiService from '../services/api';

const VAReports = () => {
  const [selectedSoldier, setSelectedSoldier] = useState('');
  const [generating, setGenerating] = useState(false);
  const [reportUrl, setReportUrl] = useState(null);
  const [error, setError] = useState(null);
  const [recentReports, setRecentReports] = useState([
    { soldier_id: 'SGT_JOHNSON_001', date: '2025-12-29', status: 'completed', url: '#' },
    { soldier_id: 'CPL_MARTINEZ_002', date: '2025-12-28', status: 'completed', url: '#' },
    { soldier_id: 'PFC_WILLIAMS_003', date: '2025-12-27', status: 'completed', url: '#' }
  ]);

  const handleGenerateReport = async () => {
    if (!selectedSoldier) {
      setError('Please enter a Soldier ID');
      return;
    }

    setGenerating(true);
    setError(null);
    setReportUrl(null);

    try {
      const response = await apiService.generateVAReport(selectedSoldier);
      
      if (response.report_url) {
        setReportUrl(response.report_url);
        setRecentReports([
          {
            soldier_id: selectedSoldier,
            date: new Date().toISOString().split('T')[0],
            status: 'completed',
            url: response.report_url
          },
          ...recentReports.slice(0, 9)
        ]);
      }
    } catch (err) {
      setError('Failed to generate report. Please try again.');
      console.error('Report generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="main-content">
      <Navbar title="VA Reports" />

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Total Reports</span>
            <FileText size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="stat-value">127</div>
          <div className="stat-change">↑ 12 this month</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Pending</span>
            <Loader size={20} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="stat-value">3</div>
          <div className="stat-change">In progress</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Completed</span>
            <CheckCircle size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="stat-value">124</div>
          <div className="stat-change">97.6% success rate</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Avg. Generation Time</span>
            <Calendar size={20} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="stat-value">2.4m</div>
          <div className="stat-change">↓ 15% faster</div>
        </div>
      </div>

      {/* Generate Report Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <h3 className="card-title">Generate New VA Report</h3>
          <FileText size={20} style={{ color: 'var(--accent-green)' }} />
        </div>

        <div style={{ 
          background: 'var(--secondary-bg)', 
          padding: '24px', 
          borderRadius: '8px',
          border: '1px solid var(--border-color)'
        }}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: 'var(--text-secondary)',
              fontSize: '13px',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Soldier ID
            </label>
            <div style={{ position: 'relative', maxWidth: '500px' }}>
              <User 
                size={18} 
                style={{
                  position: 'absolute',
                  left: '14px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-secondary)'
                }}
              />
              <input
                type="text"
                value={selectedSoldier}
                onChange={(e) => setSelectedSoldier(e.target.value)}
                placeholder="e.g., SGT_JOHNSON_001"
                style={{
                  width: '100%',
                  padding: '12px 16px 12px 44px',
                  background: 'var(--primary-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                  fontSize: '14px'
                }}
              />
            </div>
          </div>

          {error && (
            <div className="alert alert-danger" style={{ marginBottom: '20px' }}>
              <AlertTriangle size={18} />
              <span>{error}</span>
            </div>
          )}

          {reportUrl && (
            <div className="alert alert-success" style={{ marginBottom: '20px' }}>
              <CheckCircle size={18} />
              <div>
                <p style={{ margin: '0 0 8px 0', fontWeight: '600' }}>Report Generated Successfully!</p>
                <a 
                  href={reportUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ color: 'var(--accent-green)', textDecoration: 'underline' }}
                >
                  {reportUrl}
                </a>
              </div>
            </div>
          )}

          <button
            className="btn btn-primary"
            onClick={handleGenerateReport}
            disabled={generating}
            style={{ minWidth: '200px' }}
          >
            {generating ? (
              <>
                <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
                Generating Report...
              </>
            ) : (
              <>
                <FileText size={16} />
                Generate VA Report
              </>
            )}
          </button>

          <div style={{
            marginTop: '20px',
            padding: '16px',
            background: 'rgba(0, 212, 255, 0.05)',
            borderRadius: '8px',
            border: '1px solid rgba(0, 212, 255, 0.2)'
          }}>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
              <strong>Note:</strong> Report generation typically takes 30-90 seconds. 
              The system analyzes all health events, exposure data, and medical assessments 
              for the specified soldier to generate a comprehensive VA disability claim report.
            </p>
          </div>
        </div>
      </div>

      {/* Recent Reports */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Reports</h3>
          <span className="badge badge-info">{recentReports.length} Total</span>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Soldier ID</th>
                <th>Generation Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {recentReports.map((report, index) => (
                <tr key={index}>
                  <td style={{ fontWeight: '600', fontFamily: 'monospace' }}>
                    {report.soldier_id}
                  </td>
                  <td>
                    <Calendar size={14} style={{ 
                      display: 'inline', 
                      marginRight: '6px',
                      color: 'var(--text-secondary)' 
                    }} />
                    {new Date(report.date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </td>
                  <td>
                    <span className="badge badge-success">
                      <CheckCircle size={12} style={{ marginRight: '4px' }} />
                      {report.status}
                    </span>
                  </td>
                  <td>
                    <button 
                      className="btn btn-secondary"
                      style={{ padding: '6px 12px', fontSize: '13px' }}
                      onClick={() => window.open(report.url, '_blank')}
                    >
                      <Download size={14} />
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Report Info */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">About VA Reports</h3>
        </div>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px'
        }}>
          <div>
            <h4 style={{ 
              fontSize: '15px', 
              color: 'var(--accent-green)', 
              marginBottom: '8px',
              fontWeight: '600'
            }}>
              AI-Powered Analysis
            </h4>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              Reports are generated using Google's Gemini AI to analyze health data, 
              exposure events, and medical assessments.
            </p>
          </div>

          <div>
            <h4 style={{ 
              fontSize: '15px', 
              color: 'var(--accent-green)', 
              marginBottom: '8px',
              fontWeight: '600'
            }}>
              Comprehensive Coverage
            </h4>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              Includes burn pit exposure, heat stress incidents, cardiac events, 
              respiratory issues, and environmental hazards.
            </p>
          </div>

          <div>
            <h4 style={{ 
              fontSize: '15px', 
              color: 'var(--accent-green)', 
              marginBottom: '8px',
              fontWeight: '600'
            }}>
              VA-Ready Format
            </h4>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              Reports are formatted for direct submission to the VA, 
              including all required documentation and medical evidence.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VAReports;