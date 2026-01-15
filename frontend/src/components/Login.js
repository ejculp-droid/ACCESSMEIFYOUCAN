import React, { useState } from 'react';
import authService from '../services/authService';

const Login = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await authService.register(email, password);
        alert('Registration successful! Please login.');
        setIsRegister(false);
      } else {
        await authService.login(email, password);
        onLoginSuccess();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.formCard}>
        <h2>{isRegister ? 'Register' : 'Login'}</h2>
        
        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={styles.input}
          />
          
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={styles.input}
          />
          
          {error && <div style={styles.error}>{error}</div>}
          
          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? 'Processing...' : (isRegister ? 'Register' : 'Login')}
          </button>
        </form>
        
        <button
          onClick={() => setIsRegister(!isRegister)}
          style={styles.toggleButton}
        >
          {isRegister ? 'Already have an account? Login' : 'Need an account? Register'}
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5'
  },
  formCard: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    width: '400px'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px'
  },
  input: {
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '16px'
  },
  button: {
    padding: '12px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  toggleButton: {
    marginTop: '15px',
    padding: '10px',
    backgroundColor: 'transparent',
    color: '#007bff',
    border: 'none',
    cursor: 'pointer',
    textDecoration: 'underline'
  },
  error: {
    color: 'red',
    fontSize: '14px'
  }
};

export default Login;
