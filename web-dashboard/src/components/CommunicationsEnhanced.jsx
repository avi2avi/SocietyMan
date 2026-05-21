import React, { useState, useEffect } from 'react';

/**
 * AnnouncementManager Component
 * Create, schedule, and manage announcements
 */
export const AnnouncementManager = ({ token, apiBase = 'http://localhost:8000' }) => {
  const [announcements, setAnnouncements] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    announcement_type: 'notice',
    priority: 'medium',
    scheduled_for: '',
    expires_at: '',
  });
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchAnnouncements();
  }, [filter]);

  const fetchAnnouncements = async () => {
    try {
      const params = filter !== 'all' ? `?announcement_type=${filter}` : '';
      const response = await fetch(`${apiBase}/api/communications/announcements${params}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setAnnouncements(data);
      }
    } catch (err) {
      console.error('Failed to fetch announcements');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiBase}/api/communications/announcements`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        setFormData({
          title: '',
          content: '',
          announcement_type: 'notice',
          priority: 'medium',
          scheduled_for: '',
          expires_at: '',
        });
        setShowForm(false);
        fetchAnnouncements();
      }
    } catch (err) {
      console.error('Failed to create announcement');
    }
  };

  const getTypeIcon = (type) => {
    const icons = {
      'notice': '📋',
      'meeting': '👥',
      'event': '🎉',
    };
    return icons[type] || '📌';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'high': '#ef4444',
      'medium': '#f59e0b',
      'low': '#10b981',
    };
    return colors[priority] || '#6b7280';
  };

  return (
    <div style={{ padding: '20px', background: '#fff', borderRadius: '8px' }}>
      <h2>Announcements</h2>

      <div style={{ marginBottom: '15px', display: 'flex', gap: '10px' }}>
        <button 
          onClick={() => setShowForm(!showForm)}
          style={{
            padding: '10px 20px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          + New Announcement
        </button>

        <select 
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ddd' }}
        >
          <option value="all">All Types</option>
          <option value="notice">Notices</option>
          <option value="meeting">Meetings</option>
          <option value="event">Events</option>
        </select>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px', padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
          <div style={{ marginBottom: '10px' }}>
            <label>Title: </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Content: </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              required
              rows={5}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
            <div>
              <label>Type: </label>
              <select 
                value={formData.announcement_type}
                onChange={(e) => setFormData({ ...formData, announcement_type: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              >
                <option value="notice">Notice</option>
                <option value="meeting">Meeting</option>
                <option value="event">Event</option>
              </select>
            </div>
            <div>
              <label>Priority: </label>
              <select 
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
            <div>
              <label>Schedule For (Optional): </label>
              <input
                type="datetime-local"
                value={formData.scheduled_for}
                onChange={(e) => setFormData({ ...formData, scheduled_for: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>
            <div>
              <label>Expires At (Optional): </label>
              <input
                type="datetime-local"
                value={formData.expires_at}
                onChange={(e) => setFormData({ ...formData, expires_at: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>
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

      <div style={{ display: 'grid', gap: '10px' }}>
        {announcements.map((ann) => (
          <div key={ann.id} style={{
            padding: '15px',
            background: '#f9fafb',
            borderRadius: '8px',
            borderLeft: `4px solid ${getPriorityColor(ann.priority)}`,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div style={{ flex: 1 }}>
                <h3 style={{ margin: '0 0 5px 0', fontSize: '16px' }}>
                  {getTypeIcon(ann.announcement_type)} {ann.title}
                </h3>
                <p style={{ margin: '5px 0', fontSize: '14px', color: '#666' }}>{ann.content}</p>
                <div style={{ display: 'flex', gap: '10px', marginTop: '10px', fontSize: '12px', color: '#999' }}>
                  <span>👁️ {ann.view_count} views</span>
                  <span>📅 {new Date(ann.created_at).toLocaleDateString()}</span>
                  <span>Priority: {ann.priority}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * ForumPost Component
 * Create and manage forum discussions with tags
 */
export const ForumPostManager = ({ token, apiBase = 'http://localhost:8000' }) => {
  const [posts, setPosts] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'general',
    tags: '',
  });
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    fetchPosts();
  }, [selectedCategory]);

  const fetchPosts = async () => {
    try {
      const params = selectedCategory !== 'all' ? `?category=${selectedCategory}` : '';
      const response = await fetch(`${apiBase}/api/communications/forum${params}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setPosts(data);
      }
    } catch (err) {
      console.error('Failed to fetch posts');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiBase}/api/communications/forum`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        setFormData({ title: '', content: '', category: 'general', tags: '' });
        setShowForm(false);
        fetchPosts();
      }
    } catch (err) {
      console.error('Failed to create post');
    }
  };

  const getCategoryEmoji = (cat) => {
    const emojis = {
      'general': '💬',
      'suggestions': '💡',
      'complaints': '⚠️',
      'security': '🔒',
    };
    return emojis[cat] || '📌';
  };

  return (
    <div style={{ padding: '20px', background: '#fff', borderRadius: '8px' }}>
      <h2>Community Forum</h2>

      <div style={{ marginBottom: '15px', display: 'flex', gap: '10px' }}>
        <button 
          onClick={() => setShowForm(!showForm)}
          style={{
            padding: '10px 20px',
            background: '#8b5cf6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          + New Discussion
        </button>

        <select 
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ddd' }}
        >
          <option value="all">All Categories</option>
          <option value="general">General</option>
          <option value="suggestions">Suggestions</option>
          <option value="complaints">Complaints</option>
          <option value="security">Security</option>
        </select>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px', padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
          <div style={{ marginBottom: '10px' }}>
            <label>Title: </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Content: </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              required
              rows={5}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
            <div>
              <label>Category: </label>
              <select 
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              >
                <option value="general">General</option>
                <option value="suggestions">Suggestions</option>
                <option value="complaints">Complaints</option>
                <option value="security">Security</option>
              </select>
            </div>
            <div>
              <label>Tags (comma-separated): </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                placeholder="tag1,tag2,tag3"
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button type="submit" style={{ padding: '8px 16px', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Post
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

      <div style={{ display: 'grid', gap: '12px' }}>
        {posts.map((post) => (
          <div key={post.id} style={{
            padding: '15px',
            background: '#f9fafb',
            borderRadius: '8px',
            borderTop: '3px solid #8b5cf6',
          }}>
            <h3 style={{ margin: '0 0 5px 0', fontSize: '16px' }}>
              {getCategoryEmoji(post.category)} {post.title}
            </h3>
            <p style={{ margin: '8px 0', fontSize: '14px', color: '#666' }}>{post.content}</p>
            <div style={{ display: 'flex', gap: '15px', marginTop: '10px', fontSize: '12px', color: '#999' }}>
              <span>👁️ {post.view_count} views</span>
              <span>💬 {post.reply_count} replies</span>
              <span>⭐ {post.engagement_score.toFixed(1)} engagement</span>
            </div>
            {post.tags && (
              <div style={{ marginTop: '10px', display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                {post.tags.split(',').map((tag, idx) => (
                  <span key={idx} style={{
                    padding: '2px 8px',
                    background: '#dbeafe',
                    color: '#1e40af',
                    borderRadius: '12px',
                    fontSize: '11px'
                  }}>
                    #{tag.trim()}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnnouncementManager;
