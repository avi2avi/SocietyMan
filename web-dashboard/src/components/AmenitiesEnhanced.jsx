import React, { useState, useEffect } from 'react';

/**
 * AmenitiesBookingCalendar Component
 * Book community amenities with calendar view
 */
export const AmenitiesBookingCalendar = ({ token, apiBase = 'http://localhost:8000' }) => {
  const [amenities, setAmenities] = useState([]);
  const [selectedAmenity, setSelectedAmenity] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [formData, setFormData] = useState({
    start_datetime: '',
    end_datetime: '',
    purpose: '',
    notes: '',
  });
  const [availabilityCheck, setAvailabilityCheck] = useState(null);

  useEffect(() => {
    fetchAmenities();
  }, []);

  const fetchAmenities = async () => {
    try {
      const response = await fetch(`${apiBase}/api/amenities`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setAmenities(data);
      }
    } catch (err) {
      console.error('Failed to fetch amenities');
    }
  };

  const fetchBookings = async (amenityId) => {
    try {
      const response = await fetch(`${apiBase}/api/amenities/${amenityId}/bookings`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setBookings(data);
      }
    } catch (err) {
      console.error('Failed to fetch bookings');
    }
  };

  const checkAvailability = async () => {
    if (!formData.start_datetime || !formData.end_datetime) return;
    
    try {
      const response = await fetch(
        `${apiBase}/api/amenities/${selectedAmenity}/availability?start_datetime=${formData.start_datetime}&end_datetime=${formData.end_datetime}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      if (response.ok) {
        const data = await response.json();
        setAvailabilityCheck(data);
      }
    } catch (err) {
      console.error('Failed to check availability');
    }
  };

  const handleBooking = async (e) => {
    e.preventDefault();
    if (!availabilityCheck?.is_available) {
      alert('Amenity is not available for this time period');
      return;
    }

    try {
      const response = await fetch(`${apiBase}/api/amenities/${selectedAmenity}/bookings`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        alert('Booking created successfully!');
        setFormData({ start_datetime: '', end_datetime: '', purpose: '', notes: '' });
        fetchBookings(selectedAmenity);
      }
    } catch (err) {
      console.error('Failed to create booking');
    }
  };

  if (!selectedAmenity) {
    return (
      <div style={{ padding: '20px', background: '#fff', borderRadius: '8px' }}>
        <h2>Book Amenities</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '15px' }}>
          {amenities.map((amenity) => (
            <div 
              key={amenity.id}
              onClick={() => { setSelectedAmenity(amenity.id); fetchBookings(amenity.id); }}
              style={{
                padding: '15px',
                background: '#f9fafb',
                borderRadius: '8px',
                border: '2px solid #e5e7eb',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = '#3b82f6'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = '#e5e7eb'}
            >
              <h3 style={{ margin: '0 0 10px 0', fontSize: '16px' }}>🏛️ {amenity.name}</h3>
              <p style={{ margin: '5px 0', fontSize: '13px', color: '#666' }}>
                👥 Capacity: {amenity.capacity}
              </p>
              {amenity.location && (
                <p style={{ margin: '5px 0', fontSize: '13px', color: '#666' }}>
                  📍 {amenity.location}
                </p>
              )}
              {amenity.booking_price > 0 && (
                <p style={{ margin: '8px 0 0 0', fontSize: '14px', fontWeight: 'bold', color: '#10b981' }}>
                  ₹{amenity.booking_price} per booking
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  const amenity = amenities.find(a => a.id === selectedAmenity);

  return (
    <div style={{ padding: '20px', background: '#fff', borderRadius: '8px' }}>
      <button 
        onClick={() => setSelectedAmenity(null)}
        style={{ marginBottom: '15px', padding: '8px 16px', background: '#6b7280', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
      >
        ← Back to Amenities
      </button>

      <h2>Book: {amenity?.name}</h2>

      {amenity?.description && (
        <p style={{ margin: '10px 0', color: '#666' }}>{amenity.description}</p>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Booking Form */}
        <div style={{ padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
          <h3>Create Booking</h3>

          {availabilityCheck && (
            <div style={{
              padding: '10px',
              marginBottom: '15px',
              background: availabilityCheck.is_available ? '#d1fae5' : '#fee2e2',
              color: availabilityCheck.is_available ? '#065f46' : '#7f1d1d',
              borderRadius: '4px',
              fontSize: '14px',
            }}>
              {availabilityCheck.is_available ? '✓ Available' : '✗ Not Available'}
            </div>
          )}

          <form onSubmit={handleBooking}>
            <div style={{ marginBottom: '12px' }}>
              <label>Start Date & Time: </label>
              <input
                type="datetime-local"
                value={formData.start_datetime}
                onChange={(e) => setFormData({ ...formData, start_datetime: e.target.value })}
                onBlur={checkAvailability}
                required
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label>End Date & Time: </label>
              <input
                type="datetime-local"
                value={formData.end_datetime}
                onChange={(e) => setFormData({ ...formData, end_datetime: e.target.value })}
                onBlur={checkAvailability}
                required
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label>Purpose: </label>
              <input
                type="text"
                value={formData.purpose}
                onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
                placeholder="e.g., Birthday celebration"
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label>Notes: </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                placeholder="Any special requirements..."
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>

            <button 
              type="submit"
              disabled={!availabilityCheck?.is_available}
              style={{
                width: '100%',
                padding: '10px',
                background: availabilityCheck?.is_available ? '#3b82f6' : '#d1d5db',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: availabilityCheck?.is_available ? 'pointer' : 'not-allowed',
                fontWeight: '500',
              }}
            >
              Book Amenity
            </button>
          </form>
        </div>

        {/* Bookings List */}
        <div style={{ padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
          <h3>Upcoming Bookings</h3>
          
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {bookings.filter(b => b.status !== 'cancelled').length === 0 ? (
              <p style={{ color: '#999' }}>No bookings yet</p>
            ) : (
              bookings
                .filter(b => b.status !== 'cancelled')
                .map((booking) => (
                  <div key={booking.id} style={{
                    padding: '10px',
                    marginBottom: '10px',
                    background: 'white',
                    borderRadius: '4px',
                    borderLeft: booking.status === 'confirmed' ? '3px solid #10b981' : '3px solid #f59e0b',
                  }}>
                    <p style={{ margin: '3px 0', fontSize: '13px', fontWeight: 'bold' }}>
                      {new Date(booking.start_datetime).toLocaleDateString()}
                    </p>
                    <p style={{ margin: '3px 0', fontSize: '12px', color: '#666' }}>
                      {new Date(booking.start_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - 
                      {new Date(booking.end_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                    <p style={{ margin: '3px 0', fontSize: '11px', color: '#999' }}>
                      Status: <span style={{ 
                        fontWeight: 'bold', 
                        color: booking.status === 'confirmed' ? '#10b981' : '#f59e0b' 
                      }}>
                        {booking.status.toUpperCase()}
                      </span>
                    </p>
                    {booking.purpose && (
                      <p style={{ margin: '3px 0', fontSize: '11px' }}>Purpose: {booking.purpose}</p>
                    )}
                  </div>
                ))
            )}
          </div>
        </div>
      </div>

      {amenity?.rules && (
        <div style={{ marginTop: '20px', padding: '15px', background: '#eff6ff', borderRadius: '8px', borderLeft: '4px solid #0284c7' }}>
          <h4>📋 Rules & Guidelines</h4>
          <p style={{ margin: '10px 0', whiteSpace: 'pre-wrap', fontSize: '13px' }}>{amenity.rules}</p>
        </div>
      )}
    </div>
  );
};

/**
 * AmenityUsageStats Component
 * View amenity usage statistics and analytics
 */
export const AmenityUsageStats = ({ token, apiBase = 'http://localhost:8000' }) => {
  const [amenities, setAmenities] = useState([]);
  const [selectedAmenityId, setSelectedAmenityId] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAmenities();
  }, []);

  const fetchAmenities = async () => {
    try {
      const response = await fetch(`${apiBase}/api/amenities`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setAmenities(data);
      }
    } catch (err) {
      console.error('Failed to fetch amenities');
    }
  };

  const fetchStats = async (amenityId) => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBase}/api/amenities/${amenityId}/usage-stats`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  };

  const handleAmenitySelect = (amenityId) => {
    setSelectedAmenityId(amenityId);
    fetchStats(amenityId);
  };

  return (
    <div style={{ padding: '20px', background: '#fff', borderRadius: '8px' }}>
      <h2>Amenity Usage Statistics</h2>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {amenities.map((amenity) => (
          <button
            key={amenity.id}
            onClick={() => handleAmenitySelect(amenity.id)}
            style={{
              padding: '10px 15px',
              background: selectedAmenityId === amenity.id ? '#3b82f6' : '#e5e7eb',
              color: selectedAmenityId === amenity.id ? 'white' : '#333',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: selectedAmenityId === amenity.id ? 'bold' : 'normal',
            }}
          >
            {amenity.name}
          </button>
        ))}
      </div>

      {loading && <p>Loading statistics...</p>}

      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px' }}>
          <div style={{ padding: '15px', background: '#eff6ff', borderRadius: '8px', textAlign: 'center', borderLeft: '4px solid #3b82f6' }}>
            <p style={{ margin: '0', fontSize: '28px', fontWeight: 'bold', color: '#1e40af' }}>{stats.total_bookings}</p>
            <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#666' }}>Total Bookings</p>
          </div>

          <div style={{ padding: '15px', background: '#d1fae5', borderRadius: '8px', textAlign: 'center', borderLeft: '4px solid #10b981' }}>
            <p style={{ margin: '0', fontSize: '28px', fontWeight: 'bold', color: '#065f46' }}>{stats.completed}</p>
            <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#666' }}>Completed</p>
          </div>

          <div style={{ padding: '15px', background: '#fef3c7', borderRadius: '8px', textAlign: 'center', borderLeft: '4px solid #f59e0b' }}>
            <p style={{ margin: '0', fontSize: '28px', fontWeight: 'bold', color: '#92400e' }}>{stats.confirmed}</p>
            <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#666' }}>Confirmed</p>
          </div>

          <div style={{ padding: '15px', background: '#fee2e2', borderRadius: '8px', textAlign: 'center', borderLeft: '4px solid #ef4444' }}>
            <p style={{ margin: '0', fontSize: '28px', fontWeight: 'bold', color: '#7f1d1d' }}>{stats.cancelled}</p>
            <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#666' }}>Cancelled</p>
          </div>

          <div style={{ padding: '15px', background: '#f0fdf4', borderRadius: '8px', textAlign: 'center', borderLeft: '4px solid #22c55e' }}>
            <p style={{ margin: '0', fontSize: '28px', fontWeight: 'bold', color: '#15803d' }}>
              {stats.utilization_rate.toFixed(1)}%
            </p>
            <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#666' }}>Utilization</p>
          </div>

          <div style={{ padding: '15px', background: '#f3e8ff', borderRadius: '8px', textAlign: 'center', borderLeft: '4px solid #a855f7' }}>
            <p style={{ margin: '0', fontSize: '28px', fontWeight: 'bold', color: '#6b21a8' }}>{stats.pending}</p>
            <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#666' }}>Pending Approval</p>
          </div>
        </div>
      )}

      {!stats && !loading && selectedAmenityId && (
        <p style={{ color: '#999' }}>Select an amenity to view statistics</p>
      )}
    </div>
  );
};

export default AmenitiesBookingCalendar;
