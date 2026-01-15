import React, { useState, useEffect } from 'react';
import serviceAPI from '../services/serviceAPI';

const SubscriptionManager = () => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const tiers = [
    {
      name: 'Free',
      price: 0,
      features: [
        '10 requests per month',
        'Business Consulting',
        'Technical Support',
        '2 requests per minute'
      ]
    },
    {
      name: 'Pro',
      price: 29.99,
      features: [
        '100 requests per month',
        'Business Consulting',
        'Technical Support',
        'Creative Services',
        '10 requests per minute'
      ]
    },
    {
      name: 'Enterprise',
      price: 299.99,
      features: [
        'Unlimited requests',
        'All Services',
        'Priority Support',
        'Legal Services',
        '50 requests per minute'
      ]
    }
  ];

  useEffect(() => {
    loadSubscription();
  }, []);

  const loadSubscription = async () => {
    try {
      const data = await serviceAPI.getSubscription();
      setSubscription(data.subscription);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (tierName) => {
    if (!window.confirm(`Upgrade to ${tierName} tier?`)) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      await serviceAPI.updateSubscription(tierName);
      await loadSubscription();
      alert('Subscription updated successfully!');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={styles.loading}>Loading...</div>;
  }

  return (
    <div style={styles.container}>
      <h1>Subscription Plans</h1>
      
      {subscription && (
        <div style={styles.currentPlan}>
          <h3>Current Plan: {subscription.membershipTier}</h3>
          <p>Requests this month: {subscription.requestsThisMonth} / {subscription.requestLimit === -1 ? 'Unlimited' : subscription.requestLimit}</p>
        </div>
      )}

      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.tiersGrid}>
        {tiers.map((tier) => (
          <div
            key={tier.name}
            style={{
              ...styles.tierCard,
              ...(subscription?.membershipTier === tier.name
                ? styles.currentTierCard
                : {})
            }}
          >
            <h2>{tier.name}</h2>
            <div style={styles.price}>
              ${tier.price}
              <span style={styles.priceInterval}>/month</span>
            </div>
            
            <ul style={styles.featureList}>
              {tier.features.map((feature, idx) => (
                <li key={idx} style={styles.feature}>✓ {feature}</li>
              ))}
            </ul>
            
            {subscription?.membershipTier === tier.name ? (
              <div style={styles.currentBadge}>Current Plan</div>
            ) : (
              <button
                onClick={() => handleUpgrade(tier.name)}
                style={styles.upgradeButton}
                disabled={loading}
              >
                {tier.price > (tiers.find(t => t.name === subscription?.membershipTier)?.price || 0)
                  ? 'Upgrade'
                  : 'Switch'}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto'
  },
  loading: {
    textAlign: 'center',
    padding: '50px',
    fontSize: '18px'
  },
  currentPlan: {
    backgroundColor: '#e7f3ff',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '30px',
    border: '2px solid #007bff'
  },
  error: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '20px'
  },
  tiersGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '20px'
  },
  tierCard: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    border: '2px solid #ddd',
    textAlign: 'center'
  },
  currentTierCard: {
    borderColor: '#28a745',
    boxShadow: '0 4px 15px rgba(40,167,69,0.3)'
  },
  price: {
    fontSize: '36px',
    fontWeight: 'bold',
    margin: '20px 0'
  },
  priceInterval: {
    fontSize: '16px',
    fontWeight: 'normal',
    color: '#666'
  },
  featureList: {
    listStyle: 'none',
    padding: 0,
    margin: '20px 0',
    textAlign: 'left'
  },
  feature: {
    padding: '8px 0',
    borderBottom: '1px solid #eee'
  },
  upgradeButton: {
    padding: '12px 24px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: 'bold',
    width: '100%'
  },
  currentBadge: {
    backgroundColor: '#28a745',
    color: 'white',
    padding: '12px',
    borderRadius: '4px',
    fontWeight: 'bold'
  }
};

export default SubscriptionManager;
