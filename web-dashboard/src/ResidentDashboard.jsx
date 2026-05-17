import React, { useEffect, useState } from "react";
import axios from "axios";
import "./resident-dashboard.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function ResidentDashboard({ token, user }) {
  const [activeTab, setActiveTab] = useState("conversations");
  const [conversations, setConversations] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [polls, setPolls] = useState([]);
  const [photos, setPhotos] = useState([]);
  const [newPost, setNewPost] = useState("");
  const [dues, setDues] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (token) {
      fetchUserData();
    }
  }, [token]);

  const fetchUserData = async () => {
    setLoading(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      
      // Fetch dues
      try {
        const duesRes = await axios.get(`${API_BASE}/dashboard/admin`, { headers });
        setDues(duesRes.data?.pending_dues || 0);
      } catch (err) {
        console.log("Dues fetch not available");
      }

      // Fetch announcements (mock data for now)
      setAnnouncements([
        {
          id: 1,
          title: "Draft Minutes of SGM held on 10th. May 2026",
          content: "Dear Members, The General Body Meeting was held on May 10th, 2026. Please review the draft minutes attached.",
          date: "15-May-2026, 9:49 AM",
          author: "Admin",
        },
        {
          id: 2,
          title: "Maintenance Charges for June 2026",
          content: "The maintenance charges for June 2026 have been finalized. Please make payment by 30th June.",
          date: "14-May-2026, 10:30 AM",
          author: "Society Admin",
        },
        {
          id: 3,
          title: "Swimming Pool Maintenance Schedule",
          content: "The swimming pool will be closed on 20th-22nd May for maintenance. We apologize for the inconvenience.",
          date: "13-May-2026, 2:15 PM",
          author: "Operations Team",
        },
      ]);

      // Fetch conversations (mock data)
      setConversations([
        {
          id: 1,
          author: "Jasbir Gohal",
          role: "2G04 Owner",
          content: "Can someone help with parking issue? My guest's car is locked in.",
          timestamp: "7 months ago",
          comments: 5,
          removed: false,
        },
        {
          id: 2,
          author: "Priya Kumar",
          role: "3H12 Owner",
          content: "Great initiative by the management for the garden maintenance!",
          timestamp: "6 months ago",
          comments: 12,
          removed: false,
        },
      ]);

      // Fetch polls (mock data)
      setPolls([
        {
          id: 1,
          question: "Should we install solar panels on the building?",
          options: [
            { text: "Yes, for better sustainability", votes: 45 },
            { text: "No, too expensive", votes: 23 },
            { text: "Need more information", votes: 18 },
          ],
          totalVotes: 86,
          hasVoted: false,
        },
      ]);

      // Fetch photos (mock data)
      setPhotos([
        {
          id: 1,
          title: "Building Garden Renovation",
          description: "Beautiful new garden area completed",
          date: "May 2026",
          imageUrl: "🌳",
        },
        {
          id: 2,
          title: "Community Event - Sports Day",
          description: "Residents participated in various sports activities",
          date: "April 2026",
          imageUrl: "🏃",
        },
      ]);
    } catch (error) {
      setMessage("Error loading data");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handlePostSubmit = async (e) => {
    e.preventDefault();
    if (!newPost.trim()) {
      setMessage("Please write something to post");
      return;
    }

    try {
      // API call would go here
      setConversations([
        {
          id: conversations.length + 1,
          author: user.full_name,
          role: "Owner",
          content: newPost,
          timestamp: "just now",
          comments: 0,
          removed: false,
        },
        ...conversations,
      ]);
      setNewPost("");
      setMessage("Post published successfully!");
      setTimeout(() => setMessage(""), 3000);
    } catch (error) {
      setMessage("Failed to post");
    }
  };

  const handleVote = (pollId, optionIndex) => {
    setPolls(
      polls.map((poll) =>
        poll.id === pollId
          ? {
              ...poll,
              options: poll.options.map((opt, idx) => ({
                ...opt,
                votes: idx === optionIndex ? opt.votes + 1 : opt.votes,
              })),
              totalVotes: poll.totalVotes + 1,
              hasVoted: true,
            }
          : poll
      )
    );
    setMessage("Vote recorded successfully!");
    setTimeout(() => setMessage(""), 3000);
  };

  const renderConversations = () => (
    <div className="feed-section">
      {conversations.map((conv) => (
        <div key={conv.id} className="feed-card">
          <div className="feed-header">
            <div className="avatar">{conv.author.charAt(0)}</div>
            <div className="feed-info">
              <h4>{conv.author}</h4>
              <p className="role">{conv.role}</p>
            </div>
            <span className="timestamp">{conv.timestamp}</span>
          </div>
          <div className="feed-content">{conv.content}</div>
          <div className="feed-footer">
            <button className="comment-btn">💬 {conv.comments} Comments</button>
            <button className="like-btn">👍 Like</button>
            <button className="share-btn">↗️ Share</button>
          </div>
        </div>
      ))}
    </div>
  );

  const renderAnnouncements = () => (
    <div className="announcements-section">
      <div className="announcements-grid">
        {announcements.map((ann, idx) => (
          <div key={ann.id} className="announcement-card">
            <div className="announcement-header">
              <h3>{ann.title}</h3>
            </div>
            <p className="announcement-excerpt">{ann.content.substring(0, 100)}...</p>
            <div className="announcement-footer">
              <span className="date">📅 {ann.date}</span>
              <a href="#" className="read-more">
                Read more →
              </a>
            </div>
          </div>
        ))}
      </div>

      <div className="view-all-section">
        <button className="view-all-btn">View All Announcements</button>
      </div>
    </div>
  );

  const renderPolls = () => (
    <div className="polls-section">
      {polls.map((poll) => (
        <div key={poll.id} className="poll-card">
          <div className="poll-question">{poll.question}</div>
          <div className="poll-options">
            {poll.options.map((option, idx) => (
              <div key={idx} className="poll-option">
                <button
                  className={`poll-option-btn ${poll.hasVoted ? "disabled" : ""}`}
                  onClick={() => !poll.hasVoted && handleVote(poll.id, idx)}
                  disabled={poll.hasVoted}
                >
                  <div className="option-text">{option.text}</div>
                  <div className="option-bar">
                    <div
                      className="option-fill"
                      style={{
                        width: `${(option.votes / poll.totalVotes) * 100}%`,
                      }}
                    ></div>
                  </div>
                  <span className="option-votes">
                    {option.votes} ({((option.votes / poll.totalVotes) * 100).toFixed(1)}%)
                  </span>
                </button>
              </div>
            ))}
          </div>
          <div className="poll-stats">Total votes: {poll.totalVotes}</div>
        </div>
      ))}
    </div>
  );

  const renderPhotos = () => (
    <div className="photos-section">
      <div className="photos-grid">
        {photos.map((photo) => (
          <div key={photo.id} className="photo-card">
            <div className="photo-image">{photo.imageUrl}</div>
            <div className="photo-info">
              <h4>{photo.title}</h4>
              <p>{photo.description}</p>
              <span className="photo-date">{photo.date}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="resident-dashboard">
      <header className="resident-header">
        <div className="header-top">
          <div className="header-brand">
            <span className="brand-tag">My ADDA</span>
            <h1>Ruby Isle CHSL</h1>
          </div>
          <div className="header-actions">
            <button className="search-btn">🔍</button>
            <button className="notification-btn">🔔</button>
            <div className="user-profile-header">
              <div className="profile-avatar">{user?.full_name?.charAt(0)}</div>
              <span>{user?.full_name?.split(" ")[0]}</span>
            </div>
          </div>
        </div>

        <div className="header-sub">
          <div className="dues-banner banner-card">
            <div className="dues-icon">💰</div>
            <div className="dues-info">
              <span className="dues-label">Due:</span>
              <span className="dues-amount">₹ {dues ? dues.toFixed(2) : "0.00"}</span>
            </div>
            <button className="pay-now-btn">Pay Now</button>
          </div>
          <div className="quick-post-bar banner-card">
            <div className="post-avatar post-avatar-small">{user?.full_name?.charAt(0)}</div>
            <input
              type="text"
              placeholder="Start a Conversation or Poll"
              value={newPost}
              onChange={(e) => setNewPost(e.target.value)}
              className="quick-post-input"
            />
            <button className="quick-post-submit" onClick={handlePostSubmit}>
              Post
            </button>
          </div>
        </div>
      </header>

      <div className="resident-container">
        <aside className={`resident-sidebar ${sidebarOpen ? "open" : ""}`}>
          <div className="sidebar-brand">
            <h2>Ruby Isle</h2>
            <p className="society-name">CHSL Community</p>
          </div>

          <nav className="sidebar-nav">
            <div className="nav-section">
              <a href="#" className="nav-item active">
                <span className="nav-icon">🏠</span>
                <span className="nav-label">My ADDA</span>
              </a>
              <a href="#" className="nav-item">
                <span className="nav-icon">🏘️</span>
                <span className="nav-label">My Unit</span>
              </a>
              <a href="#" className="nav-item">
                <span className="nav-icon">👥</span>
                <span className="nav-label">Directory</span>
              </a>
              <a href="#" className="nav-item">
                <span className="nav-icon">🆘</span>
                <span className="nav-label">Helpdesk</span>
              </a>
            </div>

            <div className="nav-section">
              <a href="#" className="nav-item">
                <span className="nav-icon">📋</span>
                <span className="nav-label">Community Forms</span>
              </a>
              <a href="#" className="nav-item">
                <span className="nav-icon">⛳</span>
                <span className="nav-label">Amenities</span>
              </a>
              <a href="#" className="nav-item">
                <span className="nav-icon">🎉</span>
                <span className="nav-label">Events</span>
              </a>
              <a href="#" className="nav-item">
                <span className="nav-icon">📄</span>
                <span className="nav-label">Documents</span>
              </a>
            </div>

            <div className="nav-section">
              <a href="#" className="nav-item">
                <span className="nav-icon">💳</span>
                <span className="nav-label">My Billing</span>
              </a>
              <a href="#" className="nav-item">
                <span className="nav-icon">🎫</span>
                <span className="nav-label">My Tickets</span>
              </a>
              <a href="#" className="nav-item">
                <span className="nav-icon">⚙️</span>
                <span className="nav-label">Settings</span>
              </a>
            </div>
          </nav>

          <div className="sidebar-footer">
            <p className="app-promo">ADDA is best experienced in the App</p>
            <div className="app-buttons">
              <button className="app-btn">App Store</button>
              <button className="app-btn">Google Play</button>
            </div>
          </div>
        </aside>

        <main className="resident-main">
          <div className="dashboard-grid">
            <section className="feed-panel">
              {message && <div className="toast-message">{message}</div>}
              <div className="feed-card spotlight-card">
                <div className="feed-header">
                  <div className="avatar">{conversations[0]?.author?.charAt(0)}</div>
                  <div className="feed-info">
                    <h4>{conversations[0]?.author || "Resident"}</h4>
                    <p className="role">{conversations[0]?.role || "Owner"}</p>
                  </div>
                  <span className="timestamp">{conversations[0]?.timestamp || "7 months ago"}</span>
                </div>
                <div className="feed-content removed-notice">
                  The post has been removed by the Moderator of your Community.
                  <div className="removed-reason">Reason : Ticket already generated</div>
                </div>
                <div className="feed-footer">
                  <button className="comment-btn">💬 0 Comment</button>
                </div>
              </div>

              <div className="section-heading">
                <h2>Latest Conversations</h2>
              </div>
              {renderConversations()}
            </section>

            <aside className="announcement-panel">
              <div className="panel-heading">
                <h2>Announcements</h2>
                <div className="panel-actions">
                  <button className="panel-btn">Previous</button>
                  <button className="panel-btn">Next</button>
                </div>
              </div>
              {renderAnnouncements()}
            </aside>
          </div>
        </main>
      </div>
    </div>
  );
}
