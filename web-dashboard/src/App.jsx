import React, { useEffect, useState } from "react";
import axios from "axios";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "./styles.css";

const API_BASE = "http://localhost:8000/api/v1";

const defaultSocietyForm = {
  name: "",
  address: "",
  city: "",
  state: "",
  pincode: "",
  admin_contact_name: "",
  admin_contact_email: "",
  admin_contact_phone: "",
};
const defaultRegisterForm = { full_name: "", phone: "", email: "", password: "", society_id: "" };
const defaultDeveloperUserForm = {
  full_name: "",
  phone: "",
  email: "",
  password: "Admin@123",
  role: "society_admin",
  society_id: "",
};
const defaultLoginForm = { email: "", phone: "", password: "" };

export default function App() {
  const [view, setView] = useState("home");
  const [societies, setSocieties] = useState([]);
  const [pendingSocieties, setPendingSocieties] = useState([]);
  const [pendingResidents, setPendingResidents] = useState([]);
  const [message, setMessage] = useState("");
  const [token, setToken] = useState(localStorage.getItem("sm_token") || "");
  const [user, setUser] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [systemSummary, setSystemSummary] = useState(null);
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminSocieties, setAdminSocieties] = useState([]);
  const [societyUsers, setSocietyUsers] = useState([]);
  const [selectedSocietyId, setSelectedSocietyId] = useState(null);
  const [dbInfo, setDbInfo] = useState(null);
  const [adminSection, setAdminSection] = useState("overview");
  const [societySection, setSocietySection] = useState("pendingResidents");
  const [societyForm, setSocietyForm] = useState(defaultSocietyForm);
  const [developerSocietyForm, setDeveloperSocietyForm] = useState(defaultSocietyForm);
  const [developerUserForm, setDeveloperUserForm] = useState(defaultDeveloperUserForm);
  const [registerForm, setRegisterForm] = useState(defaultRegisterForm);
  const [loginForm, setLoginForm] = useState(defaultLoginForm);
  const [adminUpdateForm, setAdminUpdateForm] = useState({
    admin_contact_name: "",
    admin_contact_email: "",
    admin_contact_phone: "",
  });
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
      fetchAdminOverview();
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
    if (!token) return null;
    try {
      const res = await axios.get(`${API_BASE}/users/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(res.data);
      return res.data;
    } catch (error) {
      setMessage("Unable to validate session. Please log in again.");
      clearSession();
      return null;
    }
  };

  const fetchDashboard = async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API_BASE}/dashboard/admin`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboard(res.data);
    } catch (error) {
      setDashboard(null);
    }
  };

  const fetchAdminOverview = async () => {
    if (!token) {
      return;
    }

    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [summaryRes, usersRes, societiesRes, dbInfoRes] = await Promise.all([
        axios.get(`${API_BASE}/dashboard/admin/summary`, { headers }),
        axios.get(`${API_BASE}/dashboard/admin/users`, { headers }),
        axios.get(`${API_BASE}/dashboard/admin/societies`, { headers }),
        axios.get(`${API_BASE}/dashboard/admin/db-info`, { headers }),
      ]);
      setSystemSummary(summaryRes.data);
      setAdminUsers(usersRes.data);
      setAdminSocieties(societiesRes.data);
      setDbInfo(dbInfoRes.data);
      if (!selectedSocietyId && societiesRes.data.length > 0) {
        setSelectedSocietyId(societiesRes.data[0].id);
      }
    } catch (error) {
      setSystemSummary(null);
      setAdminUsers([]);
      setAdminSocieties([]);
      setDbInfo(null);
    }
  };

  const fetchSocietyUsers = async (societyId) => {
    if (!token || !societyId) {
      return;
    }
    try {
      const res = await axios.get(`${API_BASE}/users/society/${societyId}/users`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSocietyUsers(res.data);
    } catch (error) {
      setSocietyUsers([]);
      setMessage("Unable to load society users. Please ensure you have access.");
    }
  };

  useEffect(() => {
    if (token && user?.role === "admin" && selectedSocietyId) {
      fetchSocietyUsers(selectedSocietyId);
    }
  }, [selectedSocietyId, token, user]);

  const updateUserAccess = async (userId, updatePayload) => {
    try {
      const res = await axios.patch(`${API_BASE}/users/${userId}/access`, updatePayload, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSocietyUsers((prev) => prev.map((user) => (user.id === userId ? res.data : user)));
      setAdminUsers((prev) => prev.map((user) => (user.id === userId ? res.data : user)));
      setMessage("User access updated successfully.");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Failed to update user access.");
    }
  };

  const toggleUserActive = async (user) => {
    await updateUserAccess(user.id, { is_active: !user.is_active });
  };

  const toggleUserPermission = async (user, field) => {
    await updateUserAccess(user.id, { [field]: !user[field] });
  };

  const fetchPendingLists = async () => {
    if (!token) {
      return;
    }

    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [societyRes, userRes] = await Promise.all([
        axios.get(`${API_BASE}/societies/pending`, { headers }),
        axios.get(`${API_BASE}/users/pending`, { headers }),
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
    setSystemSummary(null);
    setAdminUsers([]);
    setAdminSocieties([]);
    setDbInfo(null);
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

  const handleDeveloperCreateSociety = async (event) => {
    event.preventDefault();
    setMessage("");

    try {
      await axios.post(`${API_BASE}/societies`, developerSocietyForm, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage("Society created successfully. Approval is required from developer admin.");
      setDeveloperSocietyForm(defaultSocietyForm);
      fetchAdminOverview();
      loadSocieties();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to create society.");
    }
  };

  const handleDeveloperCreateUser = async (event) => {
    event.preventDefault();
    setMessage("");

    if (!developerUserForm.role || !developerUserForm.phone || !developerUserForm.email) {
      setMessage("Please complete user name, email, phone, and role.");
      return;
    }

    try {
      await axios.post(`${API_BASE}/users`, {
        ...developerUserForm,
        society_id: developerUserForm.society_id ? Number(developerUserForm.society_id) : null,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage("User created successfully.");
      setDeveloperUserForm(defaultDeveloperUserForm);
      fetchAdminOverview();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to create user.");
    }
  };

  const handleLoginSubmit = async (event) => {
    event.preventDefault();
    setMessage("");

    try {
      const res = await axios.post(`${API_BASE}/auth/login`, {
        email: loginForm.email || undefined,
        phone: loginForm.phone || undefined,
        password: loginForm.password,
      });
      if (res.data.verification_required) {
        setVerificationRequired(true);
        setPasswordChangeRequired(res.data.password_change_required || false);
        setMessage(res.data.message || "A verification code has been sent to your registered contact.");
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
        updateView("developerPanel");
      } else if (profile?.role === "society_admin") {
        updateView("societyPanel");
      } else {
        updateView("home");
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
        code: verificationCode,
        new_password: passwordChangeRequired ? newPassword : undefined,
      };
      if (loginForm.email) {
        payload.email = loginForm.email;
      }
      if (loginForm.phone) {
        payload.phone = loginForm.phone;
      }

      const res = await axios.post(`${API_BASE}/auth/verify`, payload);
      const newToken = res.data.access_token;
      setToken(newToken);
      localStorage.setItem("sm_token", newToken);
      setMessage("Verification succeeded. Logged in successfully.");
      setLoginForm(defaultLoginForm);
      setVerificationRequired(false);
      setPasswordChangeRequired(false);
      setVerificationCode("");
      setNewPassword("");
      
      // Fetch user profile with the new token directly (avoid race condition)
      try {
        const userRes = await axios.get(`${API_BASE}/users/me`, {
          headers: { Authorization: `Bearer ${newToken}` }
        });
        setUser(userRes.data);
        
        // Fetch admin data only if admin role
        if (userRes.data.role === "admin") {
          await Promise.all([
            axios.get(`${API_BASE}/dashboard/admin`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setDashboard(r.data)).catch(() => {}),
            axios.get(`${API_BASE}/dashboard/admin/summary`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setSystemSummary(r.data)).catch(() => {}),
            axios.get(`${API_BASE}/dashboard/admin/users`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setAdminUsers(r.data)).catch(() => {}),
            axios.get(`${API_BASE}/dashboard/admin/societies`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setAdminSocieties(r.data)).catch(() => {}),
            axios.get(`${API_BASE}/dashboard/admin/db-info`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setDbInfo(r.data)).catch(() => {}),
            axios.get(`${API_BASE}/societies/pending`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setPendingSocieties(r.data || [])).catch(() => {}),
            axios.get(`${API_BASE}/users/pending`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setPendingResidents(r.data || [])).catch(() => {})
          ]);
        }
        
        if (userRes.data.role === "admin") {
          updateView("developerPanel");
        } else if (userRes.data.role === "society_admin") {
          updateView("societyPanel");
        } else {
          updateView("home");
        }
      } catch (profileErr) {
        setMessage("Failed to load user profile after verification. Please log in again.");
        clearSession();
      }
    } catch (err) {
      setMessage(err.response?.data?.detail || "Verification failed. Check your code.");
    }
  };

  const handleApproveSociety = async (id) => {
    setMessage("");
    try {
      await axios.post(`${API_BASE}/societies/${id}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage("Society approved successfully.");
      fetchPendingLists();
      loadSocieties();
      fetchAdminOverview();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to approve society.");
    }
  };

  const handleApproveResident = async (id) => {
    setMessage("");
    try {
      await axios.post(`${API_BASE}/users/${id}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage("Resident approved successfully.");
      fetchPendingLists();
      fetchAdminOverview();
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

  const developerNavItems = [
    { label: "Overview", key: "overview" },
    { label: "Society Management", key: "societyManagement", subItems: [
      { label: "Approve Societies", key: "pendingSocieties" },
      { label: "All Societies", key: "allSocieties" },
      { label: "Register Society", key: "createSociety" },
      { label: "Society User Access", key: "societyUserAccess" },
    ] },
    { label: "User Management", key: "userManagement", subItems: [
      { label: "Approve Residents", key: "pendingResidents" },
      { label: "All Users", key: "allUsers" },
      { label: "Create User", key: "createUser" },
    ] },
    { label: "Society Admin Contact", key: "adminContact", subItems: [
      { label: "Update Admin Email/Phone", key: "updateAdminContact" },
    ] },
    { label: "System Info", key: "systemInfo", subItems: [
      { label: "Database Info", key: "dbInfo" },
      { label: "Summary Metrics", key: "summary" },
    ] },
  ];

  const societyNavItems = [
    { label: "Overview", key: "overview" },
    { label: "Resident Approvals", key: "pendingResidents" },
  ];

  const developerSectionContent = () => {
    switch (adminSection) {
      case "pendingSocieties":
        return (
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
        );
      case "allSocieties":
        return (
          <article className="panel card-panel ag-theme-alpine grid-panel">
            <h3>All societies</h3>
            {adminSocieties.length > 0 ? (
              <div className="ag-grid-wrapper">
                <AgGridReact
                  rowData={adminSocieties}
                  columnDefs={[
                    { field: "name", headerName: "Society", flex: 1 },
                    { field: "city", headerName: "City", flex: 1 },
                    { field: "state", headerName: "State", flex: 1 },
                    { field: "pincode", headerName: "Pincode", flex: 1 },
                    {
                      field: "is_approved",
                      headerName: "Approved",
                      valueFormatter: (params) => (params.value ? "Yes" : "No"),
                      flex: 1,
                    },
                    { field: "admin_contact_name", headerName: "Admin Name", flex: 1 },
                    { field: "admin_contact_email", headerName: "Admin Email", flex: 1 },
                    { field: "admin_contact_phone", headerName: "Admin Phone", flex: 1 },
                  ]}
                  defaultColDef={{ sortable: true, filter: true, resizable: true, minWidth: 120 }}
                />
              </div>
            ) : (
              <p>No societies available.</p>
            )}
          </article>
        );
      case "allUsers":
        return (
          <article className="panel card-panel ag-theme-alpine grid-panel">
            <h3>All users</h3>
            {adminUsers.length > 0 ? (
              <div className="ag-grid-wrapper">
                <AgGridReact
                  rowData={adminUsers}
                  columnDefs={[
                    { field: "full_name", headerName: "Name", flex: 1 },
                    { field: "email", headerName: "Email", flex: 1 },
                    { field: "phone", headerName: "Phone", flex: 1 },
                    { field: "role", headerName: "Role", flex: 1 },
                    {
                      field: "is_active",
                      headerName: "Active",
                      valueFormatter: (params) => (params.value ? "Yes" : "No"),
                      flex: 1,
                    },
                    { field: "society_id", headerName: "Society ID", flex: 1 },
                  ]}
                  defaultColDef={{ sortable: true, filter: true, resizable: true, minWidth: 120 }}
                />
              </div>
            ) : (
              <p>No users loaded.</p>
            )}
          </article>
        );
      case "createSociety":
        return (
          <article className="panel form-panel">
            <h3>Create society</h3>
            <form onSubmit={handleDeveloperCreateSociety}>
              <FormField label="Society name" value={developerSocietyForm.name} onChange={(value) => setDeveloperSocietyForm((prev) => ({ ...prev, name: value }))} />
              <FormField label="Address" value={developerSocietyForm.address} onChange={(value) => setDeveloperSocietyForm((prev) => ({ ...prev, address: value }))} />
              <FormField label="City" value={developerSocietyForm.city} onChange={(value) => setDeveloperSocietyForm((prev) => ({ ...prev, city: value }))} />
              <FormField label="State" value={developerSocietyForm.state} onChange={(value) => setDeveloperSocietyForm((prev) => ({ ...prev, state: value }))} />
              <FormField label="Pincode" value={developerSocietyForm.pincode} onChange={(value) => setDeveloperSocietyForm((prev) => ({ ...prev, pincode: value }))} />
              <hr className="section-divider" />
              <h4>Admin contact</h4>
              <FormField label="Admin name" value={developerSocietyForm.admin_contact_name} onChange={(value) => setDeveloperSocietyForm((prev) => ({ ...prev, admin_contact_name: value }))} />
              <FormField label="Admin email" value={developerSocietyForm.admin_contact_email} onChange={(value) => setDeveloperSocietyForm((prev) => ({ ...prev, admin_contact_email: value }))} />
              <FormField label="Admin phone" value={developerSocietyForm.admin_contact_phone} onChange={(value) => setDeveloperSocietyForm((prev) => ({ ...prev, admin_contact_phone: value }))} />
              <button className="primary-button" type="submit">Create society</button>
            </form>
          </article>
        );
      case "createUser":
        return (
          <article className="panel form-panel">
            <h3>Create user</h3>
            <form onSubmit={handleDeveloperCreateUser}>
              <FormField label="Full name" value={developerUserForm.full_name} onChange={(value) => setDeveloperUserForm((prev) => ({ ...prev, full_name: value }))} />
              <FormField label="Phone" value={developerUserForm.phone} onChange={(value) => setDeveloperUserForm((prev) => ({ ...prev, phone: value }))} />
              <FormField label="Email" value={developerUserForm.email} onChange={(value) => setDeveloperUserForm((prev) => ({ ...prev, email: value }))} />
              <FormField label="Password" type="password" value={developerUserForm.password} onChange={(value) => setDeveloperUserForm((prev) => ({ ...prev, password: value }))} />
              <label className="field-group">
                <span>Role</span>
                <select value={developerUserForm.role} onChange={(event) => setDeveloperUserForm((prev) => ({ ...prev, role: event.target.value }))}>
                  <option value="admin">Developer Admin</option>
                  <option value="society_admin">Society Admin</option>
                  <option value="manager">Manager</option>
                  <option value="gatekeeper">Gatekeeper</option>
                  <option value="vendor">Vendor</option>
                </select>
              </label>
              <label className="field-group">
                <span>Society</span>
                <select value={developerUserForm.society_id} onChange={(event) => setDeveloperUserForm((prev) => ({ ...prev, society_id: event.target.value }))}>
                  <option value="">Select society</option>
                  {adminSocieties.map((society) => (
                    <option key={society.id} value={society.id}>{society.name} — {society.city}</option>
                  ))}
                </select>
              </label>
              <button className="primary-button" type="submit">Create user</button>
            </form>
          </article>
        );
      case "updateAdminContact":
        return (
          <article className="panel card-panel">
            <h3>Update society admin contact</h3>
            <div className="field-group">
              <span>Select society</span>
              <select
                value={selectedSocietyId || ""}
                onChange={(event) => {
                  const selectId = event.target.value ? Number(event.target.value) : null;
                  setSelectedSocietyId(selectId);
                  setAdminUpdateForm({ admin_contact_name: "", admin_contact_email: "", admin_contact_phone: "" });
                }}
              >
                <option value="">Select society</option>
                {adminSocieties.map((society) => (
                  <option key={society.id} value={society.id}>
                    {society.name} — {society.city}
                  </option>
                ))}
              </select>
            </div>
            {selectedSocietyId ? (
              <form
                onSubmit={async (event) => {
                  event.preventDefault();
                  setMessage("");
                  const payload = {};
                  if (adminUpdateForm.admin_contact_name) payload.admin_contact_name = adminUpdateForm.admin_contact_name;
                  if (adminUpdateForm.admin_contact_email) payload.admin_contact_email = adminUpdateForm.admin_contact_email;
                  if (adminUpdateForm.admin_contact_phone) payload.admin_contact_phone = adminUpdateForm.admin_contact_phone;
                  if (!Object.keys(payload).length) {
                    setMessage("Enter at least one contact field to update.");
                    return;
                  }
                  try {
                    await axios.patch(`${API_BASE}/societies/${selectedSocietyId}/admin-contact`, payload, {
                      headers: { Authorization: `Bearer ${token}` },
                    });
                    setMessage("Admin contact updated. Default password is Admin@123.");
                    setAdminUpdateForm({ admin_contact_name: "", admin_contact_email: "", admin_contact_phone: "" });
                    fetchAdminOverview();
                  } catch (err) {
                    setMessage(err.response?.data?.detail || "Failed to update admin contact.");
                  }
                }}
              >
                <FormField label="Admin name" value={adminUpdateForm.admin_contact_name} onChange={(value) => setAdminUpdateForm((prev) => ({ ...prev, admin_contact_name: value }))} />
                <FormField label="Admin email" value={adminUpdateForm.admin_contact_email} onChange={(value) => setAdminUpdateForm((prev) => ({ ...prev, admin_contact_email: value }))} />
                <FormField label="Admin phone" value={adminUpdateForm.admin_contact_phone} onChange={(value) => setAdminUpdateForm((prev) => ({ ...prev, admin_contact_phone: value }))} />
                <button className="primary-button" type="submit">Update admin contact</button>
              </form>
            ) : (
              <p>Select a society to change its admin contact details.</p>
            )}
          </article>
        );
      case "dbInfo":
        return (
          <article className="panel card-panel">
            <h3>Database info</h3>
            {dbInfo ? (
              <div>
                <p><strong>Type:</strong> {dbInfo.database_type}</p>
                {dbInfo.database_file && <p><strong>File:</strong> {dbInfo.database_file}</p>}
                {dbInfo.database_url && <p><strong>URL:</strong> {dbInfo.database_url}</p>}
              </div>
            ) : (
              <p>Loading DB info…</p>
            )}
          </article>
        );
      case "summary":
        return (
          <article className="panel card-panel">
            <h3>Summary metrics</h3>
            {systemSummary ? (
              Object.entries(systemSummary).map(([label, value]) => (
                <div key={label} className="metric-row">
                  <span>{label.replace(/_/g, " ")}</span>
                  <strong>{value}</strong>
                </div>
              ))
            ) : (
              <p>Loading summary metrics…</p>
            )}
          </article>
        );
      case "societyUserAccess":
        return (
          <article className="panel card-panel">
            <h3>Society user access</h3>
            <div className="field-group">
              <span>Select society</span>
              <select
                value={selectedSocietyId || ""}
                onChange={(event) => {
                  const value = event.target.value;
                  setSelectedSocietyId(value ? Number(value) : null);
                }}
              >
                <option value="">Select society</option>
                {adminSocieties.map((society) => (
                  <option key={society.id} value={society.id}>
                    {society.name} — {society.city}
                  </option>
                ))}
              </select>
            </div>
            {societyUsers.length > 0 ? (
              <div className="table-card">
                <div className="table-row table-header">
                  <span>Name</span>
                  <span>Role</span>
                  <span>Status</span>
                  <span>Modules</span>
                  <span>Actions</span>
                </div>
                {societyUsers.map((userItem) => (
                  <div key={userItem.id} className="table-row">
                    <span>{userItem.full_name}</span>
                    <span>{userItem.role}</span>
                    <span>{userItem.is_active ? "Active" : "Disabled"}</span>
                    <span className="module-badges">
                      {userItem.access_erp && <strong>ERP</strong>}
                      {userItem.access_gatekeeper && <strong>Gatekeeper</strong>}
                      {userItem.access_billing && <strong>Billing</strong>}
                      {userItem.access_payments && <strong>Payments</strong>}
                      {userItem.access_communications && <strong>Comm</strong>}
                      {userItem.access_reports && <strong>Reports</strong>}
                      {userItem.access_documents && <strong>Docs</strong>}
                      {userItem.access_visitor_management && <strong>Visitor</strong>}
                    </span>
                    <span className="actions-column">
                      <button className="secondary-button" onClick={() => toggleUserActive(userItem)}>
                        {userItem.is_active ? "Disable" : "Enable"}
                      </button>
                    </span>
                    <div className="access-toggles">
                      {[
                        ["access_erp", "ERP"],
                        ["access_gatekeeper", "Gatekeeper"],
                        ["access_billing", "Billing"],
                        ["access_payments", "Payments"],
                        ["access_communications", "Comm"],
                        ["access_reports", "Reports"],
                        ["access_documents", "Docs"],
                        ["access_visitor_management", "Visitor"],
                      ].map(([field, label]) => (
                        <button
                          key={field}
                          className={`sidebar-subitem ${userItem[field] ? "active" : ""}`}
                          onClick={() => toggleUserPermission(userItem, field)}
                          type="button"
                        >
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : selectedSocietyId ? (
              <p>No users found for the selected society.</p>
            ) : (
              <p>Select a society to review access and user permissions.</p>
            )}
          </article>
        );
      default:
        return (
          <>
            <article className="panel card-panel">
              <h2>Developer Admin Management</h2>
              <p>Manage the application from here. Click a left menu item to open the section you need.</p>
            </article>
            <article className="metric-card">
              <span>Current dashboard</span>
              <strong>{dashboard ? "Loaded" : "Loading…"}</strong>
            </article>
          </>
        );
    }
  };

  const societySectionContent = () => {
    switch (societySection) {
      case "pendingResidents":
        return (
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
        );
      default:
        return (
          <article className="panel card-panel">
            <h2>Society Admin Onboarding</h2>
            <p>Review pending resident registrations for your society and approve accounts.</p>
          </article>
        );
    }
  };

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
            <button className={`nav-link ${view === "developerPanel" ? "active" : ""}`} onClick={() => updateView("developerPanel")}>
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
        {user && (
          <div className="user-profile">
            <strong>{user.full_name}</strong>
            <span>{user.role.replace("_", " ")}</span>
            <span>{user.email || user.phone}</span>
            <span>{user.society_id ? `Society ID: ${user.society_id}` : "Developer admin"}</span>
          </div>
        )}
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
              <hr className="section-divider" />
              <h3>Admin contact details</h3>
              <FormField label="Admin name" value={societyForm.admin_contact_name} onChange={(value) => setSocietyForm((prev) => ({ ...prev, admin_contact_name: value }))} />
              <FormField label="Admin email" value={societyForm.admin_contact_email} onChange={(value) => setSocietyForm((prev) => ({ ...prev, admin_contact_email: value }))} />
              <FormField label="Admin phone" value={societyForm.admin_contact_phone} onChange={(value) => setSocietyForm((prev) => ({ ...prev, admin_contact_phone: value }))} />
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
              <FormField label="Email (optional)" value={loginForm.email} onChange={(value) => setLoginForm((prev) => ({ ...prev, email: value }))} />
              <FormField label="Phone (optional)" value={loginForm.phone} onChange={(value) => setLoginForm((prev) => ({ ...prev, phone: value }))} />
              <FormField label="Password" type="password" value={loginForm.password} onChange={(value) => setLoginForm((prev) => ({ ...prev, password: value }))} />
              <button className="primary-button" type="submit">Sign in</button>
            </form>
            <p className="note-text">Use your registered email or phone. Admin login sends a verification code if required.</p>
          </section>
        )}

        {view === "verifyAdmin" && (
          <section className="panel form-panel">
            <h2>Admin verification</h2>
            <p className="subtitle">Enter the code sent to your registered email to complete admin login.</p>
            <p className="note-text">If email is not configured locally, the verification code is written to <strong>scripts/last_admin_code.txt</strong> for development testing.</p>
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
          <section className="panel-layout">
            <aside className="sidebar">
              <div className="sidebar-header">
                <h3>Developer Features</h3>
                <p>Click a section to show its activity.</p>
              </div>
              {developerNavItems.map((item) => (
                <div key={item.key} className="sidebar-group">
                  <button
                    className={`sidebar-link ${adminSection === item.key || item.subItems?.some((sub) => sub.key === adminSection) ? "active" : ""}`}
                    onClick={() => setAdminSection(item.key)}
                  >
                    {item.label}
                  </button>
                  {item.subItems && (
                    <div className="sidebar-sublist">
                      {item.subItems.map((sub) => (
                        <button
                          key={sub.key}
                          className={`sidebar-subitem ${adminSection === sub.key ? "active" : ""}`}
                          onClick={() => setAdminSection(sub.key)}
                        >
                          {sub.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </aside>
            <div className="panel-content">
              {developerSectionContent()}
            </div>
          </section>
        )}

        {view === "societyPanel" && (
          <section className="panel-layout">
            <aside className="sidebar">
              <div className="sidebar-header">
                <h3>Society Admin</h3>
                <p>Choose the activity you want to perform.</p>
              </div>
              {societyNavItems.map((item) => (
                <div key={item.key} className="sidebar-group">
                  <button
                    className={`sidebar-link ${societySection === item.key ? "active" : ""}`}
                    onClick={() => setSocietySection(item.key)}
                  >
                    {item.label}
                  </button>
                </div>
              ))}
            </aside>
            <div className="panel-content">
              {societySectionContent()}
            </div>
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
