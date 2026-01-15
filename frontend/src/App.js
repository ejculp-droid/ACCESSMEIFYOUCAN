import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import ServiceSelector from './components/ServiceSelector';
import SubscriptionManager from './components/SubscriptionManager';
import authService from './services/authService';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('services');

  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setCurrentView('services');
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div style={styles.app}>
      <nav style={styles.nav}>
        <div style={styles.navBrand}>
          <h2>ACCESSMEIFYOUCAN</h2>
        </div>
        <div style={styles.navLinks}>
          <button
            onClick={() => setCurrentView('services')}
            style={{
              ...styles.navButton,
              ...(currentView === 'services' ? styles.navButtonActive : {})
            }}
          >
            Services
          </button>
          <button
            onClick={() => setCurrentView('subscription')}
            style={{
              ...styles.navButton,
              ...(currentView === 'subscription' ? styles.navButtonActive : {})
            }}
          >
            Subscription
          </button>
          <button onClick={handleLogout} style={styles.logoutButton}>
            Logout
          </button>
        </div>
      </nav>

      <main style={styles.main}>
        {currentView === 'services' && <ServiceSelector />}
        {currentView === 'subscription' && <SubscriptionManager />}
      </main>

      <footer style={styles.footer}>
        <p>© 2026 ACCESSMEIFYOUCAN - Multi-tenant AI Professional Services Platform</p>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    display: 'flex',
    flexDirection: 'column'
  },
  nav: {
    backgroundColor: '#2c3e50',
    color: 'white',
    padding: '15px 30px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
  },
  navBrand: {
    fontSize: '18px',
    fontWeight: 'bold'
  },
  navLinks: {
    display: 'flex',
    gap: '15px'
  },
  navButton: {
    backgroundColor: 'transparent',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    cursor: 'pointer',
    fontSize: '16px',
    borderRadius: '4px',
    transition: 'background-color 0.3s'
  },
  navButtonActive: {
    backgroundColor: '#34495e'
  },
  logoutButton: {
    backgroundColor: '#e74c3c',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    cursor: 'pointer',
    fontSize: '16px',
    borderRadius: '4px',
    fontWeight: 'bold'
  },
  main: {
    flex: 1,
    padding: '20px'
  },
  footer: {
    backgroundColor: '#2c3e50',
    color: 'white',
    textAlign: 'center',
    padding: '20px',
    marginTop: 'auto'
  }
};

export default App;
