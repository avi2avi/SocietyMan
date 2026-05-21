import React, { useState, useEffect } from 'react';

/**
 * MaintenanceCategory Component
 * Allows viewing and creating maintenance categories
 */
export const MaintenanceCategoryManager = ({ token, apiBase = 'http://localhost:8000' }) => {
  const [categories, setCategories] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    icon: '🔧',
    color: '#3b82f6',
    sort_order: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch categories
  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBase}/api/maintenance/categories`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (err) {
      setError('Failed to fetch categories');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiBase}/api/maintenance/categories`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        setFormData({ name: '', description: '', icon: '🔧', color: '#3b82f6', sort_order: 0 });
        setShowForm(false);
        fetchCategories();
      }
    } catch (err) {
      setError('Failed to create category');
    }
  };

  return (
    <div style={{ padding: '20px', background: '#fff', borderRadius: '8px' }}>
      <h2>Maintenance Categories</h2>
      
      {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
      
      {!showForm ? (
        <button 
          onClick={() => setShowForm(true)}
          style={{
            padding: '10px 20px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginBottom: '20px',
          }}
        >
          + Add Category
        </button>
      ) : (
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px', padding: '15px', background: '#f5f5f5', borderRadius: '4px' }}>
          <div style={{ marginBottom: '10px' }}>
            <label>Name: </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Description: </label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Icon: </label>
            <input
              type="text"
              value={formData.icon}
              onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Color: </label>
            <input
              type="color"
              value={formData.color}
              onChange={(e) => setFormData({ ...formData, color: e.target.value })}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button type="submit" style={{ padding: '8px 16px', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Save
            </button>
            <button 
              type="button"
              onClick={() => setShowForm(false)}
              style={{ padding: '8px 16px', background: '#6b7280', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '15px' }}>
        {categories.map((cat) => (
          <div key={cat.id} style={{ 
            padding: '15px', 
            background: '#f9fafb', 
            borderRadius: '8px',
            borderLeft: `4px solid ${cat.color}`,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '5px' }}>{cat.icon}</div>
            <h3 style={{ margin: '5px 0', fontSize: '16px' }}>{cat.name}</h3>
            <p style={{ margin: '5px 0', fontSize: '12px', color: '#666' }}>{cat.description}</p>
          </div>
        ))}
      </div>

      {loading && <p>Loading...</p>}
    </div>
  );
};

/**
 * MaintenanceWorkLog Component
 * Display and add work logs for maintenance tickets
 */
export const MaintenanceWorkLog = ({ ticketId, token, apiBase = 'http://localhost:8000' }) => {
  const [workLogs, setWorkLogs] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    staff_user_id: '',
    description: '',
    hours_spent: '',
  });

  useEffect(() => {
    fetchWorkLogs();
  }, [ticketId]);

  const fetchWorkLogs = async () => {
    try {
      const response = await fetch(`${apiBase}/api/maintenance/${ticketId}/work-logs`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setWorkLogs(data);
      }
    } catch (err) {
      console.error('Failed to fetch work logs');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiBase}/api/maintenance/${ticketId}/work-logs`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        setFormData({ staff_user_id: '', description: '', hours_spent: '' });
        setShowForm(false);
        fetchWorkLogs();
      }
    } catch (err) {
      console.error('Failed to add work log');
    }
  };

  return (
    <div style={{ padding: '15px', background: '#fff', borderRadius: '8px' }}>
      <h3>Work Logs</h3>

      {!showForm ? (
        <button 
          onClick={() => setShowForm(true)}
          style={{
            padding: '8px 16px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginBottom: '15px',
          }}
        >
          + Add Work Log
        </button>
      ) : (
        <form onSubmit={handleSubmit} style={{ marginBottom: '15px', padding: '12px', background: '#f5f5f5', borderRadius: '4px' }}>
          <div style={{ marginBottom: '10px' }}>
            <label>Description: </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              required
              rows={3}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Hours Spent: </label>
            <input
              type="number"
              step="0.5"
              value={formData.hours_spent}
              onChange={(e) => setFormData({ ...formData, hours_spent: e.target.value })}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button type="submit" style={{ padding: '8px 16px', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Save
            </button>
            <button 
              type="button"
              onClick={() => setShowForm(false)}
              style={{ padding: '8px 16px', background: '#6b7280', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {workLogs.map((log) => (
          <div key={log.id} style={{
            padding: '12px',
            marginBottom: '10px',
            background: '#f9fafb',
            borderRadius: '4px',
            borderLeft: '3px solid #3b82f6'
          }}>
            <p style={{ margin: '5px 0', fontSize: '14px' }}>{log.description}</p>
            {log.hours_spent && <p style={{ margin: '5px 0', fontSize: '12px', color: '#666' }}>⏱️ {log.hours_spent} hours</p>}
            <p style={{ margin: '5px 0', fontSize: '11px', color: '#999' }}>
              {new Date(log.created_at).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * MaintenanceRating Component
 * Allow residents to rate maintenance work
 */
export const MaintenanceRating = ({ ticketId, token, apiBase = 'http://localhost:8000' }) => {
  const [rating, setRating] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    rating: 5,
    feedback: '',
  });

  useEffect(() => {
    fetchRating();
  }, [ticketId]);

  const fetchRating = async () => {
    try {
      const response = await fetch(`${apiBase}/api/maintenance/${ticketId}/rating`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setRating(data);
      }
    } catch (err) {
      console.error('Failed to fetch rating');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiBase}/api/maintenance/${ticketId}/rate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        fetchRating();
        setShowForm(false);
      }
    } catch (err) {
      console.error('Failed to submit rating');
    }
  };

  if (rating) {
    return (
      <div style={{ padding: '15px', background: '#d1fae5', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
        <h4>Your Rating</h4>
        <div>⭐ {rating.rating}/5.0</div>
        <p style={{ marginTop: '10px', color: '#666' }}>{rating.feedback}</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '15px', background: '#fff', borderRadius: '8px' }}>
      <h4>Rate this Maintenance</h4>

      {!showForm ? (
        <button 
          onClick={() => setShowForm(true)}
          style={{
            padding: '8px 16px',
            background: '#f59e0b',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Add Rating
        </button>
      ) : (
        <form onSubmit={handleSubmit} style={{ padding: '12px', background: '#fffbeb', borderRadius: '4px' }}>
          <div style={{ marginBottom: '10px' }}>
            <label>Rating: </label>
            <select 
              value={formData.rating}
              onChange={(e) => setFormData({ ...formData, rating: parseFloat(e.target.value) })}
              style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            >
              <option value={5}>⭐⭐⭐⭐⭐ Excellent</option>
              <option value={4}>⭐⭐⭐⭐ Good</option>
              <option value={3}>⭐⭐⭐ Average</option>
              <option value={2}>⭐⭐ Poor</option>
              <option value={1}>⭐ Very Poor</option>
            </select>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Feedback: </label>
            <textarea
              value={formData.feedback}
              onChange={(e) => setFormData({ ...formData, feedback: e.target.value })}
              placeholder="Tell us what you think..."
              rows={3}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button type="submit" style={{ padding: '8px 16px', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Submit
            </button>
            <button 
              type="button"
              onClick={() => setShowForm(false)}
              style={{ padding: '8px 16px', background: '#6b7280', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default MaintenanceCategoryManager;
