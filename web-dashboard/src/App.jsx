import React, { useEffect, useState } from "react";
import axios from "axios";
import "./styles.css";

const API_BASE = "http://localhost:8000/api/v1";

const defaultSocietyForm = { name: "", address: "", city: "", state: "", pincode: "" };
const defaultRegisterForm = { full_name: "", phone: "", email: "", password: "", society_id: "" };
const defaultLoginForm = { email: "", password: "" };

export default function App() {
  const [view, setView] = useState("home");
  const [societies, setSocieties] = useState([]);
  const [pendingSocieties, setPendingSocieties] = useState([]);
  const [pendingResidents, setPendingResidents] = useState([]);
  const [message, setMessage] = useState("");
  const [token, setToken] = useState(localStorage.getItem("sm_token") || "");
  const [user, setUser] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [societyForm, setSocietyForm] = useState(defaultSocietyForm);
  const [registerForm, setRegisterForm] = useState(defaultRegisterForm);
  const [loginForm, setLoginForm] = useState(defaultLoginForm);
  const [loginMode, setLoginMode] = useState("society");
  const [verificationRequired, setVerificationRequired] = useState(false);
  const [passwordChangeRequired, setPasswordChangeRequired] = useState(false);
  const [verificationCode, setVerificationCode] = useState("");
  const [newPassword, setNewPassword] = useState("");

  useEffect(() => {
    loadSocieties();
    if (window.location.pathname === "/admin") {
      setLoginMode("developer");
      setView("login");
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchCurrentUser().then((profile) => {
        if (profile?.role === "admin") {
          setView("developerPanel");
        } else if (profile?.role === "society_admin") {
          setView("societyPanel");
        } else {
          setView("home");
        }
      });
      fetchDashboard();
      fetchPendingLists();
    }
  }, [token]);

  const getAuthClient = () =>
    axios.create({
      baseURL: API_BASE,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

  const loadSocieties = async () => {
    try {
      const res = await axios.get(`${API_BASE}/societies`);
      setSocieties(res.data);
    } catch (error) {
      setMessage("Unable to load societies. Please ensure the backend is running.");
    }
  };

  const fetchCurrentUser = async () => {
    try {
      const res = await getAuthClient().get("/users/me");
      setUser(res.data);
      return res.data;
    } catch (error) {
      setMessage("Unable to validate session. Please log in again.");
      clearSession();
      return null;
    }
  };

  const fetchDashboard = async () => {
    try {
      const res = await getAuthClient().get("/dashboard/admin");
      setDashboard(res.data);
    } catch (error) {
      setDashboard(null);
    }
  };

  const fetchPendingLists = async () => {
    if (!token) {
      return;
    }

    try {
      const [societyRes, userRes] = await Promise.all([
        getAuthClient().get("/societies/pending"),
        getAuthClient().get("/users/pending"),
      ]);
      setPendingSocieties(societyRes.data || []);
      setPendingResidents(userRes.data || []);
    } catch (error) {
      setPendingSocieties([]);
      setPendingResidents([]);
    }
  };

  const clearSession = () => {
    setToken("");
    setUser(null);
    setDashboard(null);
    setPendingSocieties([]);
    setPendingResidents([]);
    localStorage.removeItem("sm_token");
  };

  const updateView = (nextView, nextMode) => {
    setView(nextView);
    if (nextMode) {
      setLoginMode(nextMode);
    }
    if (nextView === "login" && nextMode === "developer") {
      window.history.replaceState({}, "", "/admin");
    } else {
      window.history.replaceState({}, "", "/");
    }
  };

  const handleSocietySubmit = async (event) => {
    event.preventDefault();
    setMessage("");

    try {
      await axios.post(`${API_BASE}/societies`, societyForm);
      setMessage("Society registered successfully. Developer admin approval is required before residents may onboard.");
      setSocietyForm(defaultSocietyForm);
      updateView("home");
      loadSocieties();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to register society.");
    }
  };

  const handleRegisterSubmit = async (event) => {
    event.preventDefault();
    setMessage("");

    if (!registerForm.society_id) {
      setMessage("Please select a registered society before signing up.");
      return;
    }

    try {
      await axios.post(`${API_BASE}/users/register`, {
        ...registerForm,
        role: "resident",
        society_id: Number(registerForm.society_id),
      });
      setMessage("Registration submitted. Society admin approval is required before you can log in.");
      setRegisterForm(defaultRegisterForm);
      updateView("login", "society");
    } catch (err) {
      setMessage(err.response?.data?.detail || "User registration failed.");
    }
  };

  const handleLoginSubmit = async (event) => {
    event.preventDefault();
    setMessage("");

    try {
      const res = await axios.post(`${API_BASE}/auth/login`, loginForm);
      if (res.data.verification_required) {
        setVerificationRequired(true);
        setPasswordChangeRequired(res.data.password_change_required || false);
        setMessage(res.data.message || "A verification code has been sent to your email.");
        setView("verifyAdmin");
        return;
      }

      setToken(res.data.access_token);
      localStorage.setItem("sm_token", res.data.access_token);
      setMessage("Login successful.");
      setLoginForm(defaultLoginForm);
      const profile = await fetchCurrentUser();
      fetchDashboard();
      fetchPendingLists();
      if (profile?.role === "admin") {
        setView("developerPanel");
      } else if (profile?.role === "society_admin") {
        setView("societyPanel");
      } else {
        setView("home");
      }
    } catch (err) {
      setMessage(err.response?.data?.detail || "Login failed. Check your credentials.");
    }
  };

  const handleVerificationSubmit = async (event) => {
    event.preventDefault();
    setMessage("");

    try {
      const payload = {
        email: loginForm.email,
        code: verificationCode,
      };
      if (passwordChangeRequired) {
        payload.new_password = newPassword;
      }

      const res = await axios.post(`${API_BASE}/auth/verify`, payload);
      setToken(res.data.access_token);
      localStorage.setItem("sm_token", res.data.access_token);
      setMessage("Verification succeeded. Logged in successfully.");
      setLoginForm(defaultLoginForm);
      setVerificationRequired(false);
      setPasswordChangeRequired(false);
      setVerificationCode("");
      setNewPassword("");
      const profile = await fetchCurrentUser();
      fetchDashboard();
      fetchPendingLists();
      if (profile?.role === "admin") {
        setView("developerPanel");
      } else if (profile?.role === "society_admin") {
        setView("societyPanel");
      } else {
        setView("home");
      }
    } catch (err) {
      setMessage(err.response?.data?.detail || "Verification failed. Check your code.");
    }
  };

  const handleApproveSociety = async (id) => {
    setMessage("");
    try {
      await getAuthClient().post(`/societies/${id}/approve`);
      setMessage("Society approved successfully.");
      fetchPendingLists();
      loadSocieties();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to approve society.");
    }
  };

  const handleApproveResident = async (id) => {
    setMessage("");
    try {
      await getAuthClient().post(`/users/${id}/approve`);
      setMessage("Resident approved successfully.");
      fetchPendingLists();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to approve resident.");
    }
  };

  const handleLogout = () => {
    clearSession();
    setView("home");
    setMessage("Logged out successfully.");
  };

  const navItems = [
    { label: "Home", view: "home" },
    { label: "Register Society", view: "registerSociety" },
    { label: "Register Resident", view: "registerUser" },
    { label: "Society Admin Login", view: "login" },
  ];

  return (
    <div className="layout-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">SocietyMan</p>
          <h1>Admin and Resident Portal</h1>
          <p className="subtitle">Centralized society registration, resident onboarding, and admin KPI tracking.</p>
        </div>
        <nav className="topnav">
          {navItems.map((item) => (
            <button
              key={item.view}
              className={`nav-link ${view === item.view ? "active" : ""}`}
              onClick={() => {
                if (item.view === "login") {
                  updateView("login", "society");
                } else {
                  updateView(item.view);
                }
              }}
            >
              {item.label}
            </button>
          ))}
          {user?.role === "admin" && (
            <button className={`nav-link ${view === "developerPanel" ? "active" : ""}`} onClick={() => setView("developerPanel")}> 
              Developer Management
            </button>
          )}
          {user?.role === "society_admin" && (
            <button className={`nav-link ${view === "societyPanel" ? "active" : ""}`} onClick={() => setView("societyPanel")}>
              Society Admin
            </button>
          )}
          {token && (
            <button className="nav-link secondary" onClick={handleLogout}>
              Logout
            </button>
          )}
        </nav>
      </header>

      <main className="page-content">
        <section className="hero-panel">
          <div className="hero-copy">
            <h2>Delivering modern society administration with rich operational intelligence.</h2>
            <p>Register a society, enroll residents, and use the admin portal to validate membership and monitor KPIs.</p>
          </div>
          <div className="hero-cards">
            <article className="stat-card">
              <span className="stat-label">Society registration</span>
              <strong>Pre-register societies first</strong>
            </article>
            <article className="stat-card">
              <span className="stat-label">Resident onboarding</span>
              <strong>Residents join only approved societies</strong>
            </article>
            <article className="stat-card">
              <span className="stat-label">Admin access</span>
              <strong>Developer and society admin roles</strong>
            </article>
          </div>
        </section>

        {message && <div className="toast-alert">{message}</div>}

        {view === "home" && (
          <section className="grid-layout">
            <article className="panel card-panel card-hero">
              <h3>Portal workflow</h3>
              <p>Register a society first. Approved societies allow residents to sign up, then society admin approves each resident account.</p>
              <div className="actions-row">
                <button className="primary-button" onClick={() => setView("registerSociety")}>Register Society</button>
                <button className="secondary-button" onClick={() => setView("registerUser")}>Register Resident</button>
              </div>
              <div className="actions-row">
                <button
                  className="secondary-button"
                  onClick={() => {
                    window.history.pushState({}, "", "/admin");
                    setLoginMode("developer");
                    setView("login");
                  }}
                >
                  Developer Admin Page
                </button>
                <button className="secondary-button" onClick={() => { setLoginMode("society"); setView("login"); }}>
                  Society Admin Login
                </button>
              </div>
            </article>
            <article className="panel card-panel">
              <h3>Why this portal?</h3>
              <ul>
                <li>Only approved societies can onboard residents.</li>
                <li>Developer admin manages society registrations.</li>
                <li>Society admin authorizes resident access.</li>
              </ul>
            </article>
            <article className="panel card-panel">
              <h3>Approved societies</h3>
              <ol>
                {societies.length > 0 ? societies.map((society) => (
                  <li key={society.id}>{society.name} — {society.city}</li>
                )) : <li>No approved societies available yet.</li>}
              </ol>
            </article>
          </section>
        )}

        {view === "registerSociety" && (
          <section className="panel form-panel">
            <h2>Register Society</h2>
            <form onSubmit={handleSocietySubmit}>
              <FormField label="Society name" value={societyForm.name} onChange={(value) => setSocietyForm((prev) => ({ ...prev, name: value }))} />
              <FormField label="Address" value={societyForm.address} onChange={(value) => setSocietyForm((prev) => ({ ...prev, address: value }))} />
              <FormField label="City" value={societyForm.city} onChange={(value) => setSocietyForm((prev) => ({ ...prev, city: value }))} />
              <FormField label="State" value={societyForm.state} onChange={(value) => setSocietyForm((prev) => ({ ...prev, state: value }))} />
              <FormField label="Pincode" value={societyForm.pincode} onChange={(value) => setSocietyForm((prev) => ({ ...prev, pincode: value }))} />
              <button className="primary-button" type="submit">Submit society</button>
            </form>
          </section>
        )}

        {view === "registerUser" && (
          <section className="panel form-panel">
            <h2>Register Resident</h2>
            <form onSubmit={handleRegisterSubmit}>
              <FormField label="Full name" value={registerForm.full_name} onChange={(value) => setRegisterForm((prev) => ({ ...prev, full_name: value }))} />
              <FormField label="Phone" value={registerForm.phone} onChange={(value) => setRegisterForm((prev) => ({ ...prev, phone: value }))} />
              <FormField label="Email" value={registerForm.email} onChange={(value) => setRegisterForm((prev) => ({ ...prev, email: value }))} />
              <FormField label="Password" type="password" value={registerForm.password} onChange={(value) => setRegisterForm((prev) => ({ ...prev, password: value }))} />
              <label className="field-group">
                <span>Society</span>
                <select value={registerForm.society_id} onChange={(event) => setRegisterForm((prev) => ({ ...prev, society_id: event.target.value }))}>
                  <option value="">Select society</option>
                  {societies.map((society) => (
                    <option key={society.id} value={society.id}>{society.name} — {society.city}</option>
                  ))}
                </select>
              </label>
              <button className="primary-button" type="submit">Submit resident application</button>
            </form>
          </section>
        )}

        {view === "login" && (
          <section className="panel form-panel">
            <h2>{loginMode === "developer" || window.location.pathname === "/admin" ? "Developer Admin Login" : "Society Admin Login"}</h2>
            <p className="subtitle">Use your registered account to sign in to the portal.</p>
            <form onSubmit={handleLoginSubmit}>
              <FormField label="Email" value={loginForm.email} onChange={(value) => setLoginForm((prev) => ({ ...prev, email: value }))} />
              <FormField label="Password" type="password" value={loginForm.password} onChange={(value) => setLoginForm((prev) => ({ ...prev, password: value }))} />
              <button className="primary-button" type="submit">Sign in</button>
            </form>
            <p className="note-text">A verification code will be sent to your registered email for admin login.</p>
          </section>
        )}

        {view === "verifyAdmin" && (
          <section className="panel form-panel">
            <h2>Admin verification</h2>
            <p className="subtitle">Enter the code sent to your registered email to complete admin login.</p>
            <form onSubmit={handleVerificationSubmit}>
              <FormField label="Verification code" value={verificationCode} onChange={(value) => setVerificationCode(value)} />
              {passwordChangeRequired && (
                <FormField label="New password" type="password" value={newPassword} onChange={(value) => setNewPassword(value)} />
              )}
              <button className="primary-button" type="submit">Verify and continue</button>
            </form>
          </section>
        )}

        {view === "dashboard" && (
          <section className="panel grid-layout dashboard-grid">
            <article className="panel card-panel">
              <h2>Admin dashboard</h2>
              {user ? <p>Welcome back, {user.full_name}</p> : <p>Loading user profile…</p>}
            </article>
            {dashboard ? (
              Object.entries(dashboard).map(([label, value]) => (
                <article className="metric-card" key={label}>
                  <span>{label.replace(/_/g, " ")}</span>
                  <strong>{value}</strong>
                </article>
              ))
            ) : (
              <article className="panel card-panel">Loading dashboard metrics...</article>
            )}
          </section>
        )}

        {view === "developerPanel" && (
          <section className="panel grid-layout dashboard-grid">
            <article className="panel card-panel">
              <h2>Developer Admin Management</h2>
              <p>Approve society registration requests and oversee resident onboarding.</p>
            </article>
            <article className="panel card-panel">
              <h3>Pending societies</h3>
              {pendingSocieties.length > 0 ? (
                pendingSocieties.map((society) => (
                  <div key={society.id} className="pending-row">
                    <span>{society.name} — {society.city}</span>
                    <button className="secondary-button" onClick={() => handleApproveSociety(society.id)}>Approve</button>
                  </div>
                ))
              ) : (
                <p>No societies awaiting approval.</p>
              )}
            </article>
            <article className="panel card-panel">
              <h3>Pending resident approvals</h3>
              {pendingResidents.length > 0 ? (
                pendingResidents.map((resident) => (
                  <div key={resident.id} className="pending-row">
                    <span>{resident.full_name} — {resident.email}</span>
                    <button className="secondary-button" onClick={() => handleApproveResident(resident.id)}>Approve</button>
                  </div>
                ))
              ) : (
                <p>No pending residents at this time.</p>
              )}
            </article>
          </section>
        )}

        {view === "societyPanel" && (
          <section className="panel grid-layout dashboard-grid">
            <article className="panel card-panel">
              <h2>Society Admin Onboarding</h2>
              <p>Review pending resident registrations for your society and approve accounts.</p>
            </article>
            <article className="panel card-panel">
              <h3>Pending residents</h3>
              {pendingResidents.length > 0 ? (
                pendingResidents.map((resident) => (
                  <div key={resident.id} className="pending-row">
                    <span>{resident.full_name} — {resident.email}</span>
                    <button className="secondary-button" onClick={() => handleApproveResident(resident.id)}>Approve</button>
                  </div>
                ))
              ) : (
                <p>No pending residents to approve.</p>
              )}
            </article>
          </section>
        )}
      </main>
    </div>
  );
}

function FormField({ label, value, onChange, type = "text" }) {
  return (
    <label className="field-group">
      <span>{label}</span>
      <input type={type} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
