import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User } from 'lucide-react';

const Login = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    
    // Simple authentication - replace with real auth
    if (credentials.username === 'admin' && credentials.password === 'valor2024') {
      localStorage.setItem('valorAuth', 'true');
      navigate('/dashboard');
    } else {
      setError('Invalid credentials. Use admin/valor2024');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--primary-bg)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background Effect */}
      <div style={{
        position: 'absolute',
        top: '-50%',
        right: '-20%',
        width: '800px',
        height: '800px',
        background: 'radial-gradient(circle, rgba(0,255,136,0.1) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(60px)'
      }} />

      <div style={{
        background: 'var(--card-bg)',
        padding: '48px',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-lg)',
        width: '100%',
        maxWidth: '440px',
        position: 'relative',
        zIndex: 1
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: 'var(--gradient-success)',
            borderRadius: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px',
            boxShadow: '0 8px 24px rgba(0,255,136,0.3)'
          }}>
            <Shield size={40} color="#fff" />
          </div>
          
          <h1 style={{
            fontSize: '32px',
            fontWeight: '900',
            background: 'var(--gradient-success)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '2px',
            marginBottom: '8px'
          }}>
            VALOR
          </h1>
          
          <p style={{
            color: 'var(--text-secondary)',
            fontSize: '14px',
            letterSpacing: '1px'
          }}>
            HEALTH MONITORING SYSTEM
          </p>
        </div>

        <form onSubmit={handleLogin}>
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
              Username
            </label>
            <div style={{ position: 'relative' }}>
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
                value={credentials.username}
                onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px 16px 12px 44px',
                  background: 'var(--secondary-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                  fontSize: '14px'
                }}
                placeholder="Enter username"
                required
              />
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: 'var(--text-secondary)',
              fontSize: '13px',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock 
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
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px 16px 12px 44px',
                  background: 'var(--secondary-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                  fontSize: '14px'
                }}
                placeholder="Enter password"
                required
              />
            </div>
          </div>

          {error && (
            <div className="alert alert-danger" style={{ marginBottom: '20px' }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{
              width: '100%',
              padding: '14px',
              fontSize: '15px',
              fontWeight: '700'
            }}
          >
            LOGIN
          </button>
        </form>

        <div style={{
          marginTop: '24px',
          padding: '16px',
          background: 'rgba(0,255,136,0.05)',
          borderRadius: '8px',
          border: '1px solid rgba(0,255,136,0.2)'
        }}>
          <p style={{
            fontSize: '12px',
            color: 'var(--text-secondary)',
            textAlign: 'center',
            margin: '0'
          }}>
            Demo Credentials: <strong style={{ color: 'var(--accent-green)' }}>admin</strong> / <strong style={{ color: 'var(--accent-green)' }}>valor2024</strong>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;