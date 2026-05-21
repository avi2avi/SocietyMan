import React, { useEffect, useState } from "react";
import axios from "axios";

// === FAMILY MEMBERS ===
export function FamilyMembersSection({ apiBase, token, user }) {
  const [members, setMembers] = useState([]);
  const [units, setUnits] = useState([]);
  const [selectedUnitId, setSelectedUnitId] = useState(null);
  const [form, setForm] = useState({ unit_id: "", name: "", relationship: "spouse", phone: "", email: "", age: "", occupation: "" });

  useEffect(() => {
    if (token) fetchMembers();
  }, [token, selectedUnitId]);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchMembers = async () => {
    try {
      const params = selectedUnitId ? `?unit_id=${selectedUnitId}` : "";
      const res = await axios.get(`${apiBase}/community/families${params}`, { headers });
      setMembers(res.data);
    } catch (e) { setMembers([]); }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${apiBase}/community/families`, { ...form, unit_id: Number(form.unit_id) }, { headers });
      setForm({ unit_id: "", name: "", relationship: "spouse", phone: "", email: "", age: "", occupation: "" });
      fetchMembers();
    } catch (err) { alert(err.response?.data?.detail || "Failed to add"); }
  };

  const handleRemove = async (id) => {
    try {
      await axios.delete(`${apiBase}/community/families/${id}`, { headers });
      fetchMembers();
    } catch (err) { alert("Failed to remove"); }
  };

  return (
    <article className="panel card-panel">
      <div className="section-heading-row light">
        <div>
          <p className="eyebrow">Family</p>
          <h3>Family members</h3>
        </div>
      </div>
      <form onSubmit={handleAdd} className="inline-form">
        <input type="number" placeholder="Unit ID" value={form.unit_id} onChange={(e) => setForm({ ...form, unit_id: e.target.value })} required />
        <input type="text" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <select value={form.relationship} onChange={(e) => setForm({ ...form, relationship: e.target.value })}>
          <option value="spouse">Spouse</option><option value="child">Child</option><option value="parent">Parent</option><option value="sibling">Sibling</option><option value="other">Other</option>
        </select>
        <input type="text" placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <button className="primary-button" type="submit">Add Member</button>
      </form>
      {members.length > 0 ? (
        <div className="table-card">
          {members.map((m) => (
            <div key={m.id} className="table-row">
              <span><strong>{m.name}</strong> ({m.relationship})</span>
              <span>{m.phone || "—"}</span>
              <span>Unit {m.unit_id}</span>
              <button className="secondary-button" onClick={() => handleRemove(m.id)}>Remove</button>
            </div>
          ))}
        </div>
      ) : <p>No family members found.</p>}
    </article>
  );
}

// === SOCIETY DIRECTORY ===
export function SocietyDirectorySection({ apiBase, token, user }) {
  const [directory, setDirectory] = useState([]);
  useEffect(() => {
    if (token) {
      axios.get(`${apiBase}/community/directory`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setDirectory(r.data))
        .catch(() => setDirectory([]));
    }
  }, [token]);

  return (
    <article className="panel card-panel">
      <h3>Society Directory</h3>
      <p>Complete resident directory by unit</p>
      <div className="table-card">
        {directory.map((entry) => (
          <div key={entry.unit_id} className="table-row">
            <span><strong>{entry.building} - {entry.unit_number}</strong></span>
            <span>{entry.residents.map((r) => r.name).join(", ") || "Vacant"}</span>
          </div>
        ))}
      </div>
    </article>
  );
}

// === COMMUNITY DASHBOARD ===
export function CommunityDashboardSection({ apiBase, token, user }) {
  const [stats, setStats] = useState(null);
  useEffect(() => {
    if (token) {
      axios.get(`${apiBase}/community/dashboard`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setStats(r.data))
        .catch(() => setStats(null));
    }
  }, [token]);

  return (
    <article className="panel card-panel">
      <h3>Community Dashboard</h3>
      {stats ? (
        <div className="operations-metric-grid">
          {Object.entries(stats).map(([key, val]) => (
            <div className="mini-metric" key={key}>
              <span>{key.replace(/_/g, " ")}</span>
              <strong>{val}</strong>
            </div>
          ))}
        </div>
      ) : <p>Loading community stats...</p>}
    </article>
  );
}

// === NOTICE BOARD ===
export function NoticeBoardSection({ apiBase, token, user }) {
  const [notices, setNotices] = useState([]);
  const [form, setForm] = useState({ title: "", content: "", category: "general", priority: "normal" });

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) fetchNotices();
  }, [token]);

  const fetchNotices = async () => {
    try {
      const res = await axios.get(`${apiBase}/community/notices`, { headers });
      setNotices(res.data);
    } catch (e) { setNotices([]); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${apiBase}/community/notices`, form, { headers });
      setForm({ title: "", content: "", category: "general", priority: "normal" });
      fetchNotices();
    } catch (err) { alert(err.response?.data?.detail || "Failed"); }
  };

  const priorityBadge = (p) => {
    const colors = { low: "#6b7280", normal: "#3b82f6", high: "#f59e0b", urgent: "#ef4444" };
    return <span style={{ background: colors[p] || "#6b7280", color: "#fff", padding: "2px 8px", borderRadius: "12px", fontSize: "0.75rem" }}>{p}</span>;
  };

  return (
    <article className="panel card-panel">
      <div className="section-heading-row light">
        <div>
          <p className="eyebrow">Notices</p>
          <h3>Notice Board</h3>
        </div>
      </div>
      <form onSubmit={handleSubmit} className="inline-form">
        <input type="text" placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
        <textarea placeholder="Content" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} required />
        <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
          <option value="general">General</option><option value="maintenance">Maintenance</option><option value="event">Event</option><option value="emergency">Emergency</option><option value="legal">Legal</option>
        </select>
        <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
          <option value="normal">Normal</option><option value="high">High</option><option value="urgent">Urgent</option><option value="low">Low</option>
        </select>
        <button className="primary-button" type="submit">Post Notice</button>
      </form>
      <div className="feed-section">
        {notices.map((n) => (
          <div key={n.id} className="feed-card" style={{ borderLeft: `4px solid ${n.priority === "urgent" ? "#ef4444" : n.priority === "high" ? "#f59e0b" : "#3b82f6"}` }}>
            <div className="feed-header">
              <h4>{n.title}</h4>
              {priorityBadge(n.priority)}
            </div>
            <p>{n.content}</p>
            <div className="feed-footer">
              <span className="timestamp">{new Date(n.created_at).toLocaleDateString()}</span>
              <span className="timestamp">{n.category}</span>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

// === COMMUNITY FEED (Conversations like Adda) ===
export function CommunityFeedSection({ apiBase, token, user }) {
  const [posts, setPosts] = useState([]);
  const [newPost, setNewPost] = useState("");
  const [showComments, setShowComments] = useState({});

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) fetchPosts();
  }, [token]);

  const fetchPosts = async () => {
    try {
      const res = await axios.get(`${apiBase}/community/posts`, { headers });
      setPosts(res.data);
    } catch (e) { setPosts([]); }
  };

  const handlePost = async (e) => {
    e.preventDefault();
    if (!newPost.trim()) return;
    try {
      await axios.post(`${apiBase}/community/posts`, { content: newPost }, { headers });
      setNewPost("");
      fetchPosts();
    } catch (err) { alert(err.response?.data?.detail || "Failed"); }
  };

  const handleLike = async (postId) => {
    try {
      await axios.post(`${apiBase}/community/posts/${postId}/like`, {}, { headers });
      fetchPosts();
    } catch (e) {}
  };

  const toggleComments = (postId) => {
    setShowComments((prev) => ({ ...prev, [postId]: !prev[postId] }));
  };

  return (
    <article className="panel card-panel">
      <div className="section-heading-row light">
        <div>
          <p className="eyebrow">Community</p>
          <h3>Community Conversations</h3>
        </div>
      </div>
      <form onSubmit={handlePost} className="inline-form">
        <input type="text" placeholder="Start a conversation..." value={newPost} onChange={(e) => setNewPost(e.target.value)} className="quick-post-input" />
        <button className="primary-button" type="submit">Post</button>
      </form>
      <div className="feed-section">
        {posts.map((post) => (
          <div key={post.id} className="feed-card">
            <div className="feed-header">
              <div className="avatar">{post.author_name?.charAt(0) || "U"}</div>
              <div className="feed-info">
                <h4>{post.author_name || "Unknown"}</h4>
                <p className="role">{post.author_role}</p>
              </div>
              <span className="timestamp">{new Date(post.created_at).toLocaleDateString()}</span>
            </div>
            <div className="feed-content">{post.content}</div>
            <div className="feed-footer">
              <button className="comment-btn" onClick={() => handleLike(post.id)}>👍 {post.like_count}</button>
              <button className="comment-btn" onClick={() => toggleComments(post.id)}>💬 {post.comment_count} Comments</button>
              {post.comment_count > 0 && showComments[post.id] && <CommentSection apiBase={apiBase} token={token} postId={post.id} />}
            </div>
          </div>
        ))}
        {posts.length === 0 && <p>No posts yet. Start a conversation!</p>}
      </div>
    </article>
  );
}

function CommentSection({ apiBase, token, postId }) {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");

  useEffect(() => {
    if (token) fetchComments();
  }, [token, postId]);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchComments = async () => {
    try {
      const res = await axios.get(`${apiBase}/community/posts/${postId}/comments`, { headers });
      setComments(res.data);
    } catch (e) { setComments([]); }
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    try {
      await axios.post(`${apiBase}/community/posts/${postId}/comments`, { post_id: postId, content: newComment }, { headers });
      setNewComment("");
      fetchComments();
    } catch (err) { alert("Failed"); }
  };

  return (
    <div className="comments-section">
      {comments.map((c) => (
        <div key={c.id} className="comment-item">
          <strong>{c.author_name}</strong>: {c.content}
        </div>
      ))}
      <form onSubmit={handleComment} className="inline-form">
        <input type="text" placeholder="Write a comment..." value={newComment} onChange={(e) => setNewComment(e.target.value)} />
        <button className="secondary-button" type="submit">Reply</button>
      </form>
    </div>
  );
}

// === EMERGENCY CONTACTS ===
export function EmergencyContactsSection({ apiBase, token, user }) {
  const [contacts, setContacts] = useState([]);
  const [filter, setFilter] = useState("");

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) {
      const params = filter ? `?contact_type=${filter}` : "";
      axios.get(`${apiBase}/community/emergency-contacts${params}`, { headers })
        .then(r => setContacts(r.data))
        .catch(() => setContacts([]));
    }
  }, [token, filter]);

  const typeIcons = { police: "🚔", fire: "🚒", ambulance: "🚑", hospital: "🏥", plumber: "🔧", electrician: "⚡", gas: "🔥" };

  return (
    <article className="panel card-panel">
      <div className="section-heading-row light">
        <div>
          <p className="eyebrow">Emergency</p>
          <h3>Emergency Contacts</h3>
        </div>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="">All</option>
          <option value="police">Police</option><option value="fire">Fire</option><option value="ambulance">Ambulance</option>
          <option value="hospital">Hospital</option><option value="plumber">Plumber</option><option value="electrician">Electrician</option><option value="gas">Gas</option>
        </select>
      </div>
      <div className="operations-metric-grid">
        {contacts.map((c) => (
          <div key={c.id} className="mini-metric" style={{ background: "#fef2f2", border: "1px solid #fecaca" }}>
            <span>{typeIcons[c.contact_type] || "📞"} {c.contact_type.toUpperCase()}</span>
            <strong>{c.name}</strong>
            <span>{c.phone}</span>
          </div>
        ))}
      </div>
    </article>
  );
}

// === EVENTS ===
export function EventsListSection({ apiBase, token, user }) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (token) {
      axios.get(`${apiBase}/community/events`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setEvents(r.data))
        .catch(() => setEvents([]));
    }
  }, [token]);

  return (
    <article className="panel card-panel">
      <h3>Society Events</h3>
      <div className="feed-section">
        {events.map((ev) => (
          <div key={ev.id} className="feed-card">
            <h4>{ev.title}</h4>
            <p>{ev.description}</p>
            <div className="feed-footer">
              <span>📅 {new Date(ev.starts_at).toLocaleDateString()}</span>
              <span>📍 {ev.location || "TBD"}</span>
              <span className="status-pill">{ev.status}</span>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

// === POLLS ===
export function PollsListSection({ apiBase, token, user }) {
  const [polls, setPolls] = useState([]);

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) fetchPolls();
  }, [token]);

  const fetchPolls = async () => {
    try {
      const res = await axios.get(`${apiBase}/community/polls`, { headers });
      setPolls(res.data);
    } catch (e) { setPolls([]); }
  };

  const handleVote = async (pollId, optionId) => {
    try {
      await axios.post(`${apiBase}/community/polls/${pollId}/vote`, { option_id: optionId }, { headers });
      fetchPolls();
    } catch (err) { alert(err.response?.data?.detail || "Vote failed"); }
  };

  return (
    <article className="panel card-panel">
      <h3>Polls & Voting</h3>
      <div className="poll-section">
        {polls.map((poll) => (
          <div key={poll.id} className="poll-card">
            <h4>{poll.title}</h4>
            <p>{poll.description}</p>
            <div className="poll-options">
              {poll.options.map((opt) => (
                <button key={opt.id} className="poll-option-btn" onClick={() => handleVote(poll.id, opt.id)}>
                  <span>{opt.option_text}</span>
                  <span className="option-votes">{opt.vote_count} votes</span>
                </button>
              ))}
            </div>
            <div className="poll-stats">Total votes: {poll.options.reduce((s, o) => s + o.vote_count, 0)}</div>
          </div>
        ))}
      </div>
    </article>
  );
}

// === MEETINGS ===
export function MeetingsListSection({ apiBase, token, user }) {
  const [meetings, setMeetings] = useState([]);

  useEffect(() => {
    if (token) {
      axios.get(`${apiBase}/community/meetings`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setMeetings(r.data))
        .catch(() => setMeetings([]));
    }
  }, [token]);

  return (
    <article className="panel card-panel">
      <h3>Meetings & AGM</h3>
      <div className="feed-section">
        {meetings.map((m) => (
          <div key={m.id} className="feed-card">
            <h4>{m.title} {m.meeting_type === "agm" && <span className="status-pill">AGM</span>}</h4>
            <p>{m.description}</p>
            <div className="feed-footer">
              <span>📅 {new Date(m.meeting_date).toLocaleDateString()}</span>
              <span>📍 {m.location || "TBD"}</span>
              <span className={`status-pill ${m.status}`}>{m.status}</span>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

// === EXPENSES ===
export function ExpensesListSection({ apiBase, token, user }) {
  const [expenses, setExpenses] = useState([]);

  useEffect(() => {
    if (token) {
      axios.get(`${apiBase}/community/expenses`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setExpenses(r.data))
        .catch(() => setExpenses([]));
    }
  }, [token]);

  return (
    <article className="panel card-panel">
      <h3>Expense Tracking</h3>
      <div className="table-card">
        {expenses.map((e) => (
          <div key={e.id} className="table-row">
            <span><strong>{e.title}</strong></span>
            <span>₹{e.amount}</span>
            <span>{new Date(e.expense_date).toLocaleDateString()}</span>
            <span className={`status-pill ${e.status}`}>{e.status}</span>
          </div>
        ))}
      </div>
    </article>
  );
}

// === EXPENSE CATEGORIES ===
export function ExpenseCategoriesSection({ apiBase, token, user }) {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    if (token) {
      axios.get(`${apiBase}/community/expense-categories`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setCategories(r.data))
        .catch(() => setCategories([]));
    }
  }, [token]);

  return (
    <article className="panel card-panel">
      <h3>Expense Categories</h3>
      <div className="table-card">
        {categories.map((c) => (
          <div key={c.id} className="table-row">
            <span><strong>{c.name}</strong></span>
            <span>Budget: ₹{c.budget_amount}</span>
            <span>{c.description || "—"}</span>
          </div>
        ))}
      </div>
    </article>
  );
}

// === UTILITIES ===
export function UtilitiesListSection({ apiBase, token, user }) {
  const [utilities, setUtilities] = useState([]);

  useEffect(() => {
    if (token) {
      axios.get(`${apiBase}/community/utilities`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setUtilities(r.data))
        .catch(() => setUtilities([]));
    }
  }, [token]);

  return (
    <article className="panel card-panel">
      <h3>Utility Readings</h3>
      <div className="table-card">
        {utilities.map((u) => (
          <div key={u.id} className="table-row">
            <span><strong>{u.utility_type.toUpperCase()}</strong></span>
            <span>{u.reading_value} {u.unit_of_measure}</span>
            <span>₹{u.total_cost}</span>
            <span>{new Date(u.reading_date).toLocaleDateString()}</span>
          </div>
        ))}
      </div>
    </article>
  );
}

// === PARCELS ===
export function ParcelsListSection({ apiBase, token, user }) {
  const [parcels, setParcels] = useState([]);

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) fetchParcels();
  }, [token]);

  const fetchParcels = async () => {
    try {
      const res = await axios.get(`${apiBase}/community/parcels`, { headers });
      setParcels(res.data);
    } catch (e) { setParcels([]); }
  };

  const handleCollect = async (id) => {
    try {
      await axios.post(`${apiBase}/community/parcels/${id}/collect`, {}, { headers });
      fetchParcels();
    } catch (err) { alert("Failed"); }
  };

  return (
    <article className="panel card-panel">
      <h3>Parcel & Delivery Management</h3>
      <div className="table-card">
        {parcels.map((p) => (
          <div key={p.id} className="table-row">
            <span><strong>{p.courier_name}</strong></span>
            <span>{p.description || "—"}</span>
            <span className={`status-pill ${p.status}`}>{p.status}</span>
            {p.status === "pending" && <button className="secondary-button" onClick={() => handleCollect(p.id)}>Collect</button>}
          </div>
        ))}
      </div>
    </article>
  );
}

// === PATROLS ===
export function PatrolsListSection({ apiBase, token, user }) {
  const [patrols, setPatrols] = useState([]);

  useEffect(() => {
    if (token) {
      axios.get(`${apiBase}/community/patrols`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setPatrols(r.data))
        .catch(() => setPatrols([]));
    }
  }, [token]);

  return (
    <article className="panel card-panel">
      <h3>Security Patrols</h3>
      <div className="table-card">
        {patrols.map((p) => (
          <div key={p.id} className="table-row">
            <span><strong>{p.patrol_type} patrol</strong></span>
            <span>{new Date(p.start_time).toLocaleString()}</span>
            <span className={`status-pill ${p.status}`}>{p.status}</span>
          </div>
        ))}
      </div>
    </article>
  );
}

// === DOMESTIC HELP (Enhanced with CRUD) ===
export function DomesticHelpSection({ apiBase, token, user }) {
  const [helpers, setHelpers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", phone: "", help_type: "maid", working_days: "", working_hours: "", id_proof_type: "", id_proof_number: "" });

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) fetchHelpers();
  }, [token]);

  const fetchHelpers = async () => {
    try {
      const res = await axios.get(`${apiBase}/community/domestic-help`, { headers });
      setHelpers(res.data);
    } catch (e) { setHelpers([]); }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${apiBase}/community/domestic-help`, { ...form, society_id: user.society_id }, { headers });
      setForm({ name: "", phone: "", help_type: "maid", working_days: "", working_hours: "", id_proof_type: "", id_proof_number: "" });
      setShowForm(false);
      fetchHelpers();
    } catch (err) { alert(err.response?.data?.detail || "Failed to add"); }
  };

  const handleToggle = async (id) => {
    try {
      await axios.patch(`${apiBase}/community/domestic-help/${id}/toggle`, {}, { headers });
      fetchHelpers();
    } catch (e) { alert("Failed to toggle"); }
  };

  const typeColors = { maid: "#3b82f6", cook: "#f59e0b", driver: "#10b981", gardener: "#22c55e", nanny: "#ec4899", other: "#6b7280" };

  return (
    <article className="panel card-panel">
      <div className="section-heading-row light">
        <div>
          <p className="eyebrow">Domestic Help</p>
          <h3>Domestic Help Management</h3>
        </div>
        <button className="secondary-button" type="button" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "Add Helper"}
        </button>
      </div>
      {showForm && (
        <form onSubmit={handleAdd} className="inline-form" style={{ marginBottom: "1rem" }}>
          <input type="text" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <input type="text" placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          <select value={form.help_type} onChange={(e) => setForm({ ...form, help_type: e.target.value })}>
            <option value="maid">Maid</option><option value="cook">Cook</option><option value="driver">Driver</option>
            <option value="gardener">Gardener</option><option value="nanny">Nanny</option><option value="other">Other</option>
          </select>
          <input type="text" placeholder="Working days (Mon,Tue,...)" value={form.working_days} onChange={(e) => setForm({ ...form, working_days: e.target.value })} />
          <input type="text" placeholder="Hours (e.g. 9:00-11:00)" value={form.working_hours} onChange={(e) => setForm({ ...form, working_hours: e.target.value })} />
          <button className="primary-button" type="submit">Add Helper</button>
        </form>
      )}
      {helpers.length > 0 ? (
        <div className="table-card">
          {helpers.map((h) => (
            <div key={h.id} className="table-row">
              <span><strong>{h.name}</strong></span>
              <span style={{ color: typeColors[h.help_type] || "#6b7280", fontWeight: 600 }}>{h.help_type}</span>
              <span>{h.phone || "—"}</span>
              <span>{h.working_hours || "—"}</span>
              <span className={`status-pill`} style={{ background: h.is_active ? "#dcfce7" : "#fef2f2", color: h.is_active ? "#16a34a" : "#dc2626" }}>
                {h.is_active ? "Active" : "Inactive"}
              </span>
              <button className="secondary-button" onClick={() => handleToggle(h.id)}>
                {h.is_active ? "Deactivate" : "Activate"}
              </button>
            </div>
          ))}
        </div>
      ) : <p>No domestic help registered. Add your first helper.</p>}
    </article>
  );
}

// === COMPLAINT MANAGEMENT ===
export function ComplaintsSection({ apiBase, token, user }) {
  const [complaints, setComplaints] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ category_id: "", title: "", description: "", priority: "normal" });

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) {
      fetchComplaints();
      fetchCategories();
    }
  }, [token]);

  const fetchComplaints = async () => {
    try {
      const res = await axios.get(`${apiBase}/community/complaints`, { headers });
      setComplaints(res.data);
    } catch (e) { setComplaints([]); }
  };

  const fetchCategories = async () => {
    try {
      const res = await axios.get(`${apiBase}/community/complaint-categories`, { headers });
      setCategories(res.data);
    } catch (e) { setCategories([]); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${apiBase}/community/complaints`, {
        ...form,
        category_id: Number(form.category_id) || null,
        society_id: user.society_id,
      }, { headers });
      setForm({ category_id: "", title: "", description: "", priority: "normal" });
      setShowForm(false);
      fetchComplaints();
    } catch (err) { alert(err.response?.data?.detail || "Failed to submit"); }
  };

  const handleStatusUpdate = async (id, status) => {
    try {
      await axios.patch(`${apiBase}/community/complaints/${id}`, { status }, { headers });
      fetchComplaints();
    } catch (e) { alert("Failed to update"); }
  };

  const statusColors = { open: "#ef4444", in_progress: "#f59e0b", resolved: "#22c55e", closed: "#6b7280" };
  const priorityColors = { low: "#6b7280", normal: "#3b82f6", high: "#f59e0b", urgent: "#ef4444" };

  return (
    <article className="panel card-panel">
      <div className="section-heading-row light">
        <div>
          <p className="eyebrow">Helpdesk</p>
          <h3>Complaint Management</h3>
          <p>Track and manage society complaints and service requests</p>
        </div>
        <button className="secondary-button" type="button" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "New Complaint"}
        </button>
      </div>
      {showForm && (
        <form onSubmit={handleSubmit} className="inline-form" style={{ marginBottom: "1rem" }}>
          {categories.length > 0 && (
            <select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
              <option value="">Select category</option>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          )}
          <input type="text" placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          <textarea placeholder="Describe your complaint..." value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required />
          <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
            <option value="normal">Normal</option><option value="high">High</option><option value="urgent">Urgent</option><option value="low">Low</option>
          </select>
          <button className="primary-button" type="submit">Submit Complaint</button>
        </form>
      )}
      {complaints.length > 0 ? (
        <div className="table-card">
          <div className="table-row table-header">
            <span>Title</span><span>Category</span><span>Status</span><span>Priority</span><span>Actions</span>
          </div>
          {complaints.map((c) => (
            <div key={c.id} className="table-row">
              <span><strong>{c.title}</strong><br /><small>{c.description?.substring(0, 60)}</small></span>
              <span>{c.category_name || "—"}</span>
              <span className="status-pill" style={{ background: statusColors[c.status] + "20", color: statusColors[c.status], fontWeight: 600 }}>
                {c.status?.replace(/_/g, " ")}
              </span>
              <span style={{ color: priorityColors[c.priority], fontWeight: 600 }}>{c.priority}</span>
              <span className="actions-column">
                {c.status !== "resolved" && c.status !== "closed" && (
                  <>
                    <button className="secondary-button" onClick={() => handleStatusUpdate(c.id, "in_progress")}>In Progress</button>
                    <button className="secondary-button" onClick={() => handleStatusUpdate(c.id, "resolved")}>Resolve</button>
                  </>
                )}
              </span>
            </div>
          ))}
        </div>
      ) : <p>No complaints found.</p>}
    </article>
  );
}

// === VEHICLE ENTRY LOGS ===
export function VehicleLogsSection({ apiBase, token, user }) {
  const [logs, setLogs] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ vehicle_number: "", driver_name: "", driver_phone: "", purpose: "" });

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) fetchLogs();
  }, [token]);

  const fetchLogs = async () => {
    try {
      const res = await axios.get(`${apiBase}/community/vehicle-logs`, { headers });
      setLogs(res.data);
    } catch (e) { setLogs([]); }
  };

  const handleEntry = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${apiBase}/community/vehicle-logs`, { ...form, society_id: user.society_id }, { headers });
      setForm({ vehicle_number: "", driver_name: "", driver_phone: "", purpose: "" });
      setShowForm(false);
      fetchLogs();
    } catch (err) { alert(err.response?.data?.detail || "Failed"); }
  };

  const handleExit = async (id) => {
    try {
      await axios.post(`${apiBase}/community/vehicle-logs/${id}/exit`, {}, { headers });
      fetchLogs();
    } catch (e) { alert("Failed"); }
  };

  return (
    <article className="panel card-panel">
      <div className="section-heading-row light">
        <div>
          <p className="eyebrow">Gate</p>
          <h3>Vehicle Entry Logs</h3>
        </div>
        <button className="secondary-button" type="button" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "Log Entry"}
        </button>
      </div>
      {showForm && (
        <form onSubmit={handleEntry} className="inline-form" style={{ marginBottom: "1rem" }}>
          <input type="text" placeholder="Vehicle Number" value={form.vehicle_number} onChange={(e) => setForm({ ...form, vehicle_number: e.target.value })} required />
          <input type="text" placeholder="Driver Name" value={form.driver_name} onChange={(e) => setForm({ ...form, driver_name: e.target.value })} required />
          <input type="text" placeholder="Driver Phone" value={form.driver_phone} onChange={(e) => setForm({ ...form, driver_phone: e.target.value })} />
          <input type="text" placeholder="Purpose" value={form.purpose} onChange={(e) => setForm({ ...form, purpose: e.target.value })} />
          <button className="primary-button" type="submit">Log Entry</button>
        </form>
      )}
      {logs.length > 0 ? (
        <div className="table-card">
          <div className="table-row table-header">
            <span>Vehicle</span><span>Driver</span><span>Entry</span><span>Status</span><span>Actions</span>
          </div>
          {logs.map((l) => (
            <div key={l.id} className="table-row">
              <span><strong>{l.vehicle_number}</strong></span>
              <span>{l.driver_name}</span>
              <span>{new Date(l.entry_at).toLocaleString()}</span>
              <span className={`status-pill`} style={{ background: l.status === "active" ? "#dcfce7" : "#f3f4f6", color: l.status === "active" ? "#16a34a" : "#6b7280" }}>
                {l.status}
              </span>
              <span>
                {l.status === "active" && <button className="secondary-button" onClick={() => handleExit(l.id)}>Mark Exit</button>}
              </span>
            </div>
          ))}
        </div>
      ) : <p>No vehicle logs found.</p>}
    </article>
  );
}

// === VISITOR MANAGEMENT ===
export function VisitorManagementSection({ apiBase, token, user }) {
  const [visitors, setVisitors] = useState([]);
  const [residents, setResidents] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ resident_user_id: "", visitor_name: "", visitor_phone: "", visitor_type: "guest", purpose: "" });

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) {
      fetchVisitors();
      fetchResidents();
    }
  }, [token]);

  const fetchVisitors = async () => {
    try {
      const societyId = user?.society_id;
      if (!societyId) return;
      const res = await axios.get(`${apiBase}/users/society/${societyId}/users`, { headers });
      setVisitors([]);
      // Visitors via another route would need a GET /visitors endpoint
      // For now, show visitor entries via the entry log
    } catch (e) { setVisitors([]); }
  };

  const fetchResidents = async () => {
    try {
      const societyId = user?.society_id;
      if (!societyId) return;
      const res = await axios.get(`${apiBase}/users/society/${societyId}/users`, { headers });
      setResidents(res.data.filter((u) => u.role === "resident" || u.role === "society_admin"));
    } catch (e) { setResidents([]); }
  };

  const handleEntry = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${apiBase}/visitors/entry`, {
        ...form,
        resident_user_id: Number(form.resident_user_id),
        visitor_type: form.visitor_type,
      }, { headers });
      setForm({ resident_user_id: "", visitor_name: "", visitor_phone: "", visitor_type: "guest", purpose: "" });
      setShowForm(false);
      setMessage("Visitor entry logged. Notification sent.");
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to log visitor");
    }
  };

  const [message, setMessage] = useState("");

  return (
    <article className="panel card-panel">
      <div className="section-heading-row light">
        <div>
          <p className="eyebrow">Gate</p>
          <h3>Visitor Management</h3>
        </div>
        <button className="secondary-button" type="button" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "Log Visitor"}
        </button>
      </div>
      {message && <div className="toast-alert">{message}</div>}
      {showForm && (
        <form onSubmit={handleEntry} className="inline-form" style={{ marginBottom: "1rem" }}>
          <select value={form.visitor_type} onChange={(e) => setForm({ ...form, visitor_type: e.target.value })}>
            <option value="guest">Guest</option><option value="delivery">Delivery</option>
          </select>
          {residents.length > 0 ? (
            <select value={form.resident_user_id} onChange={(e) => setForm({ ...form, resident_user_id: e.target.value })} required>
              <option value="">Visiting resident</option>
              {residents.map((r) => <option key={r.id} value={r.id}>{r.full_name} - {r.phone}</option>)}
            </select>
          ) : (
            <input type="number" placeholder="Resident User ID" value={form.resident_user_id} onChange={(e) => setForm({ ...form, resident_user_id: e.target.value })} required />
          )}
          <input type="text" placeholder="Visitor Name" value={form.visitor_name} onChange={(e) => setForm({ ...form, visitor_name: e.target.value })} required />
          <input type="text" placeholder="Visitor Phone" value={form.visitor_phone} onChange={(e) => setForm({ ...form, visitor_phone: e.target.value })} required />
          <input type="text" placeholder="Purpose (optional)" value={form.purpose} onChange={(e) => setForm({ ...form, purpose: e.target.value })} />
          <button className="primary-button" type="submit">Log Entry</button>
        </form>
      )}
      <p className="note-text">Use the visitor entry form to log guest or delivery visits at the gate. Notifications are sent to residents.</p>
    </article>
  );
}
