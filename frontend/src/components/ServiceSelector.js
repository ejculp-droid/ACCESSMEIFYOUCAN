import React, { useState, useEffect } from 'react';
import serviceAPI from '../services/serviceAPI';

const ServiceSelector = () => {
  const [services, setServices] = useState([]);
  const [membershipTier, setMembershipTier] = useState('Free');
  const [selectedService, setSelectedService] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadServices();
  }, []);

  const loadServices = async () => {
    try {
      const data = await serviceAPI.getServices();
      setServices(data.services);
      setMembershipTier(data.membershipTier);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleServiceRequest = async () => {
    if (!selectedService || !prompt) {
      setError('Please select a service and enter a prompt');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await serviceAPI.requestService(
        selectedService.categoryId,
        { prompt }
      );

      // If request is accepted, process with agent
      if (response.status === 'accepted') {
        const agentResult = await serviceAPI.processWithAgent(
          response.agentType,
          { prompt }
        );
        setResult(agentResult);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const categoryIcons = {
    consulting: '💼',
    legal: '⚖️',
    technical: '🔧',
    creative: '🎨'
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>AI Professional Services</h1>
        <div style={styles.tierBadge}>
          {membershipTier} Tier
        </div>
      </div>

      <div style={styles.servicesGrid}>
        {services.map((service) => (
          <div
            key={service.categoryId}
            style={{
              ...styles.serviceCard,
              ...(selectedService?.categoryId === service.categoryId
                ? styles.serviceCardSelected
                : {}),
              ...(service.available ? {} : styles.serviceCardDisabled)
            }}
            onClick={() => service.available && setSelectedService(service)}
          >
            <div style={styles.serviceIcon}>
              {categoryIcons[service.categoryId] || '📋'}
            </div>
            <h3>{service.name}</h3>
            <p>{service.description}</p>
            {!service.available && (
              <div style={styles.upgradeTag}>Upgrade Required</div>
            )}
          </div>
        ))}
      </div>

      {selectedService && (
        <div style={styles.promptSection}>
          <h3>Request {selectedService.name}</h3>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your request..."
            style={styles.textarea}
            rows="6"
          />
          <button
            onClick={handleServiceRequest}
            disabled={loading}
            style={styles.submitButton}
          >
            {loading ? 'Processing...' : 'Submit Request'}
          </button>
        </div>
      )}

      {error && <div style={styles.error}>{error}</div>}

      {result && (
        <div style={styles.resultSection}>
          <h3>Result</h3>
          <div style={styles.resultCard}>
            <p><strong>Response:</strong> {result.result?.response}</p>
            <p><strong>Confidence:</strong> {(result.result?.confidence * 100).toFixed(0)}%</p>
            <p><strong>Tokens Used:</strong> {result.result?.tokens_used}</p>
            <p><strong>Request ID:</strong> {result.requestId}</p>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px'
  },
  tierBadge: {
    backgroundColor: '#28a745',
    color: 'white',
    padding: '8px 16px',
    borderRadius: '20px',
    fontWeight: 'bold'
  },
  servicesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '30px'
  },
  serviceCard: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
    cursor: 'pointer',
    transition: 'all 0.3s',
    textAlign: 'center',
    border: '2px solid transparent'
  },
  serviceCardSelected: {
    borderColor: '#007bff',
    boxShadow: '0 4px 10px rgba(0,123,255,0.3)'
  },
  serviceCardDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed'
  },
  serviceIcon: {
    fontSize: '48px',
    marginBottom: '10px'
  },
  upgradeTag: {
    marginTop: '10px',
    backgroundColor: '#ffc107',
    color: '#000',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 'bold'
  },
  promptSection: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
    marginBottom: '20px'
  },
  textarea: {
    width: '100%',
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '16px',
    marginBottom: '15px',
    fontFamily: 'inherit'
  },
  submitButton: {
    padding: '12px 24px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  error: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '20px'
  },
  resultSection: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
  },
  resultCard: {
    backgroundColor: '#f8f9fa',
    padding: '15px',
    borderRadius: '4px',
    borderLeft: '4px solid #28a745'
  }
};

export default ServiceSelector;
