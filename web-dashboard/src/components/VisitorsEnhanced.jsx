import React, { useState, useEffect } from 'react';

/**
 * VisitorPreRegistration Component
 * Pre-register visitors for approval
 */
export const VisitorPreRegistration = ({ token, apiBase = 'http://localhost:8000' }) => {
  const [visitorLogId, setVisitorLogId] = useState('');
  const [formData, setFormData] = useState({
    approval_status: 'pending',
    vehicle_number: '',
    vehicle_type: 'car',
    parking_slot: '',
  });
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiBase}/api/visitors/enhanced/pre-register`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          visitor_log_id: parseInt(visitorLogId),
          ...formData,
        }),
      });
      if (response.ok) {
        setSuccess(true);
        setVisitorLogId('');
        setFormData({ approval_status: 'pending', vehicle_number: '', vehicle_type: 'car', parking_slot: '' });
        setTimeout(() => setSuccess(false), 3000);
      }
    } catch (err) {
      console.error('Failed to pre-register visitor');
    }
  };

  return (
    <div style={{ padding: '20px', background: '#fff', borderRadius: '8px', maxWidth: '500px' }}>
      <h2>Pre-Register Visitor</h2>

      {success && (
        <div style={{
          padding: '12px',
          background: '#d1fae5',
          borderRadius: '4px',
          color: '#065f46',
          marginBottom: '15px',
        }}>
          ✓ Visitor pre-registered successfully!
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '12px' }}>
          <label>Visitor Log ID: </label>
          <input
            type="number"
            value={visitorLogId}
            onChange={(e) => setVisitorLogId(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            placeholder="Enter visitor log ID"
          />
        </div>

        <div style={{ marginBottom: '12px' }}>
          <label>Vehicle Type: </label>
          <select 
            value={formData.vehicle_type}
            onChange={(e) => setFormData({ ...formData, vehicle_type: e.target.value })}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
          >
            <option value="car">Car</option>
            <option value="bike">Bike</option>
            <option value="auto">Auto</option>
            <option value="taxi">Taxi</option>
            <option value="truck">Truck</option>
          </select>
        </div>

        <div style={{ marginBottom: '12px' }}>
          <label>Vehicle Number: </label>
          <input
            type="text"
            value={formData.vehicle_number}
            onChange={(e) => setFormData({ ...formData, vehicle_number: e.target.value })}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            placeholder="e.g., MH02AB1234"
          />
        </div>

        <div style={{ marginBottom: '12px' }}>
          <label>Parking Slot (Optional): </label>
          <input
            type="text"
            value={formData.parking_slot}
            onChange={(e) => setFormData({ ...formData, parking_slot: e.target.value })}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            placeholder="e.g., A-101"
          />
        </div>

        <button 
          type="submit"
          style={{
            width: '100%',
            padding: '10px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: '500',
          }}
        >
          Pre-Register Visitor
        </button>
      </form>
    </div>
  );
};

/**
 * VisitorApprovalDashboard Component
 * Manage pending visitor approvals
 */
export const VisitorApprovalDashboard = ({ token, apiBase = 'http://localhost:8000' }) => {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedApproval, setSelectedApproval] = useState(null);
  const [actionData, setActionData] = useState({
    approval_status: 'approved',
    vehicle_number: '',
    vehicle_type: 'car',
    parking_slot: '',
    rejection_reason: '',
  });

  useEffect(() => {
    fetchPendingApprovals();
  }, []);

  const fetchPendingApprovals = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBase}/api/visitors/enhanced/pending-approvals`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setApprovals(data);
      }
    } catch (err) {
      console.error('Failed to fetch approvals');
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (approvalId) => {
    try {
      const response = await fetch(`${apiBase}/api/visitors/enhanced/approvals/${approvalId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(actionData),
      });
      if (response.ok) {
        setSelectedApproval(null);
        fetchPendingApprovals();
      }
    } catch (err) {
      console.error('Failed to process approval');
    }
  };

  if (selectedApproval) {
    const approval = approvals.find(a => a.id === selectedApproval);
    return (
      <div style={{ padding: '20px', background: '#fff', borderRadius: '8px' }}>
        <button 
          onClick={() => setSelectedApproval(null)}
          style={{ marginBottom: '15px', padding: '8px 16px', background: '#6b7280', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          ← Back
        </button>

        <h3>Approve/Reject Visitor</h3>

        <div style={{ marginBottom: '15px', padding: '12px', background: '#f5f5f5', borderRadius: '4px' }}>
          <p><strong>Visitor ID:</strong> {approval.visitor_log_id}</p>
          <p><strong>Resident:</strong> Resident #{approval.resident_user_id}</p>
        </div>

        <form onSubmit={(e) => { e.preventDefault(); handleApproval(approval.id); }}>
          <div style={{ marginBottom: '12px' }}>
            <label>Decision: </label>
            <select 
              value={actionData.approval_status}
              onChange={(e) => setActionData({ ...actionData, approval_status: e.target.value })}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            >
              <option value="approved">✓ Approve</option>
              <option value="rejected">✗ Reject</option>
            </select>
          </div>

          {actionData.approval_status === 'approved' ? (
            <>
              <div style={{ marginBottom: '12px' }}>
                <label>Vehicle Type: </label>
                <select 
                  value={actionData.vehicle_type}
                  onChange={(e) => setActionData({ ...actionData, vehicle_type: e.target.value })}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                >
                  <option value="car">Car</option>
                  <option value="bike">Bike</option>
                  <option value="auto">Auto</option>
                </select>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label>Vehicle Number: </label>
                <input
                  type="text"
                  value={actionData.vehicle_number}
                  onChange={(e) => setActionData({ ...actionData, vehicle_number: e.target.value })}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label>Parking Slot: </label>
                <input
                  type="text"
                  value={actionData.parking_slot}
                  onChange={(e) => setActionData({ ...actionData, parking_slot: e.target.value })}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
            </>
          ) : (
            <div style={{ marginBottom: '12px' }}>
              <label>Rejection Reason: </label>
              <textarea
                value={actionData.rejection_reason}
                onChange={(e) => setActionData({ ...actionData, rejection_reason: e.target.value })}
                rows={3}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>
          )}

          <button 
            type="submit"
            style={{
              width: '100%',
              padding: '10px',
              background: actionData.approval_status === 'approved' ? '#10b981' : '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: '500',
            }}
          >
            {actionData.approval_status === 'approved' ? 'Approve' : 'Reject'} Visitor
          </button>
        </form>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', background: '#fff', borderRadius: '8px' }}>
      <h2>Visitor Approvals ({approvals.length})</h2>

      {loading ? (
        <p>Loading...</p>
      ) : approvals.length === 0 ? (
        <p style={{ color: '#999' }}>No pending approvals</p>
      ) : (
        <div style={{ display: 'grid', gap: '10px' }}>
          {approvals.map((approval) => (
            <div key={approval.id} style={{
              padding: '15px',
              background: '#fef3c7',
              borderRadius: '8px',
              borderLeft: '4px solid #f59e0b',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <div>
                <h4 style={{ margin: '0 0 5px 0' }}>Visitor #{approval.visitor_log_id}</h4>
                <p style={{ margin: '3px 0', fontSize: '14px' }}>Resident: User #{approval.resident_user_id}</p>
                <p style={{ margin: '3px 0', fontSize: '12px', color: '#666' }}>
                  Status: <span style={{ fontWeight: 'bold', color: '#f59e0b' }}>PENDING</span>
                </p>
              </div>
              <button 
                onClick={() => setSelectedApproval(approval.id)}
                style={{
                  padding: '10px 20px',
                  background: '#f59e0b',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Review
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * VisitorHistory Component
 * View visitor history with approval details
 */
export const VisitorHistory = ({ token, apiBase = 'http://localhost:8000' }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBase}/api/visitors/enhanced/history`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (err) {
      console.error('Failed to fetch visitor history');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      'approved': '#d1fae5',
      'rejected': '#fee2e2',
      'pending': '#fef3c7',
    };
    const textColors = {
      'approved': '#065f46',
      'rejected': '#7f1d1d',
      'pending': '#92400e',
    };
    return { background: colors[status], color: textColors[status] };
  };

  return (
    <div style={{ padding: '20px', background: '#fff', borderRadius: '8px' }}>
      <h2>Visitor History</h2>

      {loading ? (
        <p>Loading...</p>
      ) : history.length === 0 ? (
        <p style={{ color: '#999' }}>No visitor history</p>
      ) : (
        <div style={{ display: 'grid', gap: '10px', maxHeight: '500px', overflowY: 'auto' }}>
          {history.map((visitor, idx) => (
            <div key={idx} style={{
              padding: '12px',
              background: '#f9fafb',
              borderRadius: '4px',
              borderLeft: '3px solid #3b82f6',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <h4 style={{ margin: '0 0 5px 0' }}>👤 {visitor.name}</h4>
                  <p style={{ margin: '3px 0', fontSize: '13px', color: '#666' }}>📱 {visitor.phone}</p>
                  <p style={{ margin: '3px 0', fontSize: '13px', color: '#666' }}>🎯 {visitor.purpose}</p>
                  {visitor.approval && (
                    <>
                      <p style={{ margin: '5px 0', fontSize: '12px' }}>
                        {visitor.approval.vehicle && `🚗 ${visitor.approval.vehicle}`}
                      </p>
                      {visitor.approval.parking_slot && (
                        <p style={{ margin: '3px 0', fontSize: '12px' }}>🅿️ Slot: {visitor.approval.parking_slot}</p>
                      )}
                      {visitor.approval.pass_number && (
                        <p style={{ margin: '3px 0', fontSize: '12px', fontFamily: 'monospace' }}>
                          Pass: {visitor.approval.pass_number}
                        </p>
                      )}
                    </>
                  )}
                </div>
                {visitor.approval && (
                  <div style={{
                    padding: '6px 12px',
                    ...getStatusBadge(visitor.approval.status),
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                  }}>
                    {visitor.approval.status.toUpperCase()}
                  </div>
                )}
              </div>
              <p style={{ margin: '8px 0 0 0', fontSize: '11px', color: '#999' }}>
                📅 {new Date(visitor.entry_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default VisitorPreRegistration;
