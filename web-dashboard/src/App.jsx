import React, { useEffect, useState } from "react";
import axios from "axios";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "./styles.css";
import ResidentDashboard from "./ResidentDashboard";
import {
  FamilyMembersSection,
  SocietyDirectorySection,
  CommunityDashboardSection,
  NoticeBoardSection,
  CommunityFeedSection,
  EmergencyContactsSection,
  EventsListSection,
  PollsListSection,
  MeetingsListSection,
  ExpensesListSection,
  ExpenseCategoriesSection,
  UtilitiesListSection,
  ParcelsListSection,
  PatrolsListSection,
  DomesticHelpSection,
} from "./CommunitySections";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

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

const societyWorkbenchModules = [
  {
    key: "dashboard",
    title: "Dashboard",
    status: "Live API",
    summary: "SMS, Notifications, and Announcements management for real-time community communication.",
    metrics: ["SMS sent", "Notifications", "Announcements"],
  },
  {
    key: "units-users",
    title: "Units & Users Management",
    status: "Live API",
    summary: "323 users and 293 units with resident approvals, tenant records, and family management.",
    metrics: ["Total users", "Total units", "Active residents"],
  },
  {
    key: "accounting",
    title: "Accounting",
    status: "Live API",
    summary: "Income Tracker, Expense Tracker, Bank & Cash management with detailed financial reports.",
    metrics: ["Total income", "Total expenses", "Bank balance"],
  },
  {
    key: "management",
    title: "Management Modules",
    status: "Live API",
    summary: "Amenity & Events, Projects & Meetings, Assets & Inventory, and Announcements management.",
    metrics: ["Events", "Projects", "Assets"],
  },
  {
    key: "staff-parking",
    title: "Staff Manager & Parking Manager",
    status: "Live API",
    summary: "Staff management, daily help tracking, vehicle registry, parking slots, and Move In/Out Tracker.",
    metrics: ["Active staff", "Parked vehicles", "Move-ins/outs"],
  },
  {
    key: "utilities-gatekeeper",
    title: "Utility Tracker & Society GateKeeper",
    status: "Live API",
    summary: "Utility tracking with ADDA GateKeeper security solution for visitor entry/exit and gate management.",
    metrics: ["Utility usage", "Visitors", "Gate passes"],
  },
  {
    key: "helpdesk",
    title: "Helpdesk Tracker",
    status: "Live API",
    summary: "Request management, complaint tracking, assignment, status tracking, and closure updates.",
    metrics: ["Open requests", "Assigned", "Resolved"],
  },
];

export default function App() {
  const [view, setView] = useState("home");
  const [societies, setSocieties] = useState([]);
  const [pendingSocieties, setPendingSocieties] = useState([]);
  const [pendingResidents, setPendingResidents] = useState([]);
  const [message, setMessage] = useState("");
  const [token, setToken] = useState(localStorage.getItem("sm_token") || "");
  const [user, setUser] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [erpOverview, setErpOverview] = useState(null);
  const [systemSummary, setSystemSummary] = useState(null);
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminSocieties, setAdminSocieties] = useState([]);
  const [adminUnits, setAdminUnits] = useState(null);
  const [adminLedger, setAdminLedger] = useState(null);
  const [adminTickets, setAdminTickets] = useState([]);
  const [billHeads, setBillHeads] = useState([]);
  const [units, setUnits] = useState([]);
  const [billingMonth, setBillingMonth] = useState("");
  const [manualInvoiceUnitId, setManualInvoiceUnitId] = useState("");
  const [manualInvoiceLineItems, setManualInvoiceLineItems] = useState([{ head_id: "", amount: "", quantity: 1 }]);
  const [newBillHead, setNewBillHead] = useState({
    name: "",
    short_code: "",
    description: "",
    is_mandatory: false,
    display_order: 0,
  });
  const [createdInvoice, setCreatedInvoice] = useState(null);
  const [billTemplates, setBillTemplates] = useState([]);
  const [templateName, setTemplateName] = useState("");
  const [templateLineItems, setTemplateLineItems] = useState([{ head_id: "", amount: "", is_percentage: false, percentage_value: 0 }]);
  const [selectedTemplateId, setSelectedTemplateId] = useState(null);
  const [generatedInvoices, setGeneratedInvoices] = useState([]);
  const [invoiceSummary, setInvoiceSummary] = useState(null);
  const [invoiceStatusFilter, setInvoiceStatusFilter] = useState("");
  const [billingTemplateMonth, setBillingTemplateMonth] = useState("");
  const [societyUsers, setSocietyUsers] = useState([]);
  const [selectedSocietyId, setSelectedSocietyId] = useState(null);
  const [dbInfo, setDbInfo] = useState(null);
  const [operationsOverview, setOperationsOverview] = useState(null);
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
    loadErpOverview();
    if (window.location.pathname === "/admin" && !token) {
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
      fetchAdminUnits();
      fetchAdminLedger();
      fetchAdminTickets();
      fetchOperationsOverview();
    }
  }, [token]);

  useEffect(() => {
    if (user?.role === "society_admin" && user?.society_id && !selectedSocietyId) {
      setSelectedSocietyId(user.society_id);
    }
  }, [user, selectedSocietyId]);

  useEffect(() => {
    if (!token || !selectedSocietyId) return;
    fetchSocietyUsers(selectedSocietyId);
  }, [token, selectedSocietyId]);

  useEffect(() => {
    if (!token || !user) return;
    if (user.role === "admin" && selectedSocietyId) {
      fetchBillHeads(selectedSocietyId);
    }
    if (user.role === "society_admin") {
      fetchBillHeads(user.society_id);
    }
    fetchUnits();
  }, [token, user, selectedSocietyId]);

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


  const loadErpOverview = async () => {
    try {
      const res = await axios.get(`${API_BASE}/erp/capabilities`);
      setErpOverview(res.data);
    } catch (error) {
      setErpOverview(null);
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

  const fetchAdminUnits = async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API_BASE}/dashboard/admin/units`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAdminUnits(res.data);
    } catch (error) {
      setAdminUnits(null);
    }
  };

  const fetchAdminLedger = async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API_BASE}/dashboard/admin/ledger`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAdminLedger(res.data);
    } catch (error) {
      setAdminLedger(null);
    }
  };

  const fetchAdminTickets = async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API_BASE}/dashboard/admin/tickets`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAdminTickets(res.data || []);
    } catch (error) {
      setAdminTickets([]);
    }
  };

  const seedDemoData = async () => {
    if (!token) return;
    try {
      const res = await axios.post(`${API_BASE}/erp/demo/seed`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage(res.data.message || "Demo data seeded successfully.");
      loadSocieties();
      fetchAdminOverview();
      fetchDashboard();
      fetchOperationsOverview(selectedSocietyId);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Failed to seed demo data.");
    }
  };

  const updateTicketStatus = async (ticketId, status) => {
    try {
      await axios.patch(`${API_BASE}/tickets/${ticketId}/status`, { status }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage(`Ticket ${ticketId} marked ${status.replace(/_/g, " ")}.`);
      fetchAdminTickets();
      fetchDashboard();
    } catch (error) {
      setMessage(error.response?.data?.detail || "Failed to update ticket status.");
    }
  };

  const fetchOperationsOverview = async (societyId = selectedSocietyId) => {
    if (!token) {
      return;
    }
    try {
      const params = societyId ? `?society_id=${societyId}` : "";
      const res = await axios.get(`${API_BASE}/operations/overview${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setOperationsOverview(res.data);
    } catch (error) {
      setOperationsOverview(null);
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

  const fetchBillHeads = async (societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id) => {
    if (!token || !societyId) return;
    try {
      const res = await axios.get(`${API_BASE}/billing-advanced/bill-heads?society_id=${societyId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setBillHeads(res.data || []);
    } catch (error) {
      setBillHeads([]);
    }
  };

  const fetchUnits = async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API_BASE}/units`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUnits(res.data || []);
    } catch (error) {
      setUnits([]);
    }
  };

  const fetchBillTemplates = async (societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id) => {
    if (!token || !societyId) return;
    try {
      const res = await axios.get(`${API_BASE}/billing-advanced/templates?society_id=${societyId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setBillTemplates(res.data || []);
    } catch (error) {
      setBillTemplates([]);
    }
  };

  const fetchInvoiceSummary = async (societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id) => {
    if (!token || !societyId) return;
    try {
      const res = await axios.get(`${API_BASE}/billing-advanced/invoices/stats/summary?society_id=${societyId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setInvoiceSummary(res.data);
    } catch (error) {
      setInvoiceSummary(null);
    }
  };

  const fetchInvoices = async (filters = {}) => {
    if (!token) return;
    const params = [];
    if (filters.society_id) params.push(`society_id=${filters.society_id}`);
    if (filters.status) params.push(`status=${filters.status}`);
    if (filters.billing_month) params.push(`billing_month=${filters.billing_month}`);
    const query = params.length ? `?${params.join("&")}` : "";
    try {
      const res = await axios.get(`${API_BASE}/billing-advanced/invoices${query}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setGeneratedInvoices(res.data || []);
    } catch (error) {
      setGeneratedInvoices([]);
    }
  };

  const handleSetupDefaultHeads = async () => {
    if (!token) return;
    const societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id;
    if (!societyId) {
      setMessage("Select a society before setting up default bill heads.");
      return;
    }

    try {
      await axios.post(`${API_BASE}/billing-advanced/bill-heads/setup-defaults`, {
        society_id: societyId,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage("Default MCS bill heads created.");
      fetchBillHeads(societyId);
      fetchBillTemplates(societyId);
      fetchInvoiceSummary(societyId);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Failed to setup default bill heads.");
    }
  };

  const handleCreateBillHead = async (event) => {
    event.preventDefault();
    if (!token) return;
    const societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id;
    if (!societyId) {
      setMessage("Select a society before adding a new billing section.");
      return;
    }

    try {
      await axios.post(`${API_BASE}/billing-advanced/bill-heads`, {
        society_id: societyId,
        name: newBillHead.name,
        short_code: newBillHead.short_code,
        description: newBillHead.description,
        is_mandatory: newBillHead.is_mandatory,
        display_order: Number(newBillHead.display_order) || 0,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setNewBillHead({ name: "", short_code: "", description: "", is_mandatory: false, display_order: 0 });
      setMessage("Billing section created.");
      fetchBillHeads(societyId);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to create billing section.");
    }
  };

  const handleAddLineItem = () => {
    setManualInvoiceLineItems((prev) => [...prev, { head_id: "", amount: "", quantity: 1 }]);
  };

  const handleRemoveLineItem = (index) => {
    setManualInvoiceLineItems((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleLineItemChange = (index, field, value) => {
    setManualInvoiceLineItems((prev) => prev.map((item, idx) => idx === index ? { ...item, [field]: value } : item));
  };

  const resetManualInvoiceForm = () => {
    setBillingMonth("");
    setManualInvoiceUnitId("");
    setManualInvoiceLineItems([{ head_id: "", amount: "", quantity: 1 }]);
  };

  const handleCreateManualInvoice = async (event) => {
    event.preventDefault();
    if (!token) return;
    const societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id;
    if (!societyId) {
      setMessage("Select a society before creating an invoice.");
      return;
    }
    if (!billingMonth) {
      setMessage("Select a billing month.");
      return;
    }
    if (!manualInvoiceUnitId) {
      setMessage("Choose a unit for the invoice.");
      return;
    }

    const payloadItems = manualInvoiceLineItems
      .map((item) => ({
        head_id: Number(item.head_id),
        amount: Number(item.amount),
        quantity: Number(item.quantity) || 1,
      }))
      .filter((item) => item.head_id && item.amount > 0);

    if (!payloadItems.length) {
      setMessage("Add at least one billed line item with an amount.");
      return;
    }

    try {
      const res = await axios.post(`${API_BASE}/billing-advanced/invoices/manual`, {
        society_id: societyId,
        unit_id: Number(manualInvoiceUnitId),
        billing_month: billingMonth,
        line_items: payloadItems,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCreatedInvoice(res.data);
      setMessage("Invoice created successfully.");
      resetManualInvoiceForm();
      fetchInvoiceSummary(societyId);
      fetchInvoices({ society_id: societyId, billing_month: billingMonth });
    } catch (error) {
      setMessage(error.response?.data?.detail || "Could not create invoice.");
    }
  };

  const handleTemplateLineItemChange = (index, field, value) => {
    setTemplateLineItems((prev) => prev.map((item, idx) => idx === index ? { ...item, [field]: value } : item));
  };

  const handleAddTemplateLineItem = () => {
    setTemplateLineItems((prev) => [...prev, { head_id: "", amount: "", is_percentage: false, percentage_value: 0 }]);
  };

  const handleRemoveTemplateLineItem = (index) => {
    setTemplateLineItems((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleCreateTemplate = async (event) => {
    event.preventDefault();
    if (!token) return;
    const societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id;
    if (!societyId) {
      setMessage("Select a society before creating a billing template.");
      return;
    }
    if (!templateName) {
      setMessage("Enter a template name.");
      return;
    }

    const payloadHeads = templateLineItems
      .map((item) => ({
        head_id: Number(item.head_id),
        amount: Number(item.amount) || 0,
        is_percentage: Boolean(item.is_percentage),
        percentage_value: Number(item.percentage_value) || 0,
      }))
      .filter((item) => item.head_id && (item.amount > 0 || item.percentage_value > 0));

    if (!payloadHeads.length) {
      setMessage("Add at least one line item to the template.");
      return;
    }

    try {
      await axios.post(`${API_BASE}/billing-advanced/templates`, {
        society_id: societyId,
        name: templateName,
        heads: payloadHeads,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setTemplateName("");
      setTemplateLineItems([{ head_id: "", amount: "", is_percentage: false, percentage_value: 0 }]);
      setMessage("Billing template created.");
      fetchBillTemplates(societyId);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to create billing template.");
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (!token) return;
    const societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id;
    try {
      await axios.delete(`${API_BASE}/billing-advanced/templates/${templateId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage("Template deleted.");
      if (templateId === selectedTemplateId) {
        setSelectedTemplateId(null);
      }
      fetchBillTemplates(societyId);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to delete template.");
    }
  };

  const handleGenerateInvoices = async (event) => {
    event.preventDefault();
    if (!token) return;
    const societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id;
    if (!societyId) {
      setMessage("Select a society before generating invoices.");
      return;
    }
    if (!selectedTemplateId) {
      setMessage("Select a billing template.");
      return;
    }
    if (!billingTemplateMonth) {
      setMessage("Select a billing month for invoice generation.");
      return;
    }

    try {
      const res = await axios.post(`${API_BASE}/billing-advanced/invoices/generate`, {
        society_id: societyId,
        template_id: Number(selectedTemplateId),
        billing_month: billingTemplateMonth,
        notes: "Generated from template",
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setGeneratedInvoices(res.data || []);
      setMessage("Invoices generated successfully.");
      fetchInvoiceSummary(societyId);
      fetchInvoices({ society_id: societyId, billing_month: billingTemplateMonth });
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to generate invoices.");
    }
  };

  const handleLoadTemplateToInvoice = (template) => {
    if (!template || !template.heads) return;
    setManualInvoiceLineItems(template.heads.map((head) => ({
      head_id: head.head_id,
      amount: head.amount,
      quantity: 1,
    })));
    setMessage(`Loaded template '${template.name}' into manual invoice.`);
  };

  useEffect(() => {
    if (token && user?.role === "admin" && selectedSocietyId) {
      fetchSocietyUsers(selectedSocietyId);
      fetchOperationsOverview(selectedSocietyId);
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
    setAdminUnits(null);
    setAdminLedger(null);
    setAdminTickets([]);
    setDbInfo(null);
    setOperationsOverview(null);
    localStorage.removeItem("sm_token");
  };

  const updateView = (nextView, nextMode) => {
    if (nextView === "login" && token && user) {
      setView(user.role === "admin" ? "developerPanel" : user.role === "society_admin" ? "societyPanel" : "home");
      return;
    }
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
    loadErpOverview();
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
    loadErpOverview();
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
            axios.get(`${API_BASE}/dashboard/admin/units`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setAdminUnits(r.data)).catch(() => {}),
            axios.get(`${API_BASE}/dashboard/admin/ledger`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setAdminLedger(r.data)).catch(() => {}),
            axios.get(`${API_BASE}/dashboard/admin/tickets`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setAdminTickets(r.data || [])).catch(() => {}),
            axios.get(`${API_BASE}/dashboard/admin/db-info`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setDbInfo(r.data)).catch(() => {}),
            axios.get(`${API_BASE}/operations/overview`, { headers: { Authorization: `Bearer ${newToken}` } }).then(r => setOperationsOverview(r.data)).catch(() => {}),
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
    loadErpOverview();
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

  const [openDropdown, setOpenDropdown] = useState(null);

  const toggleDropdown = (name) => {
    setOpenDropdown(openDropdown === name ? null : name);
  };

  const closeDropdowns = () => {
    setOpenDropdown(null);
  };

  const navItems = token
    ? [{ label: "🏠 Workspace", view: "home" }]
    : [
        { label: "🏠 Home", view: "home" },
        { 
          label: "📝 Register", 
          hasDropdown: true,
          dropdownName: "register",
          subItems: [
            { icon: "🏘️", label: "Register Society", view: "registerSociety" },
            { icon: "👤", label: "Register Resident", view: "registerUser" },
          ]
        },
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
    { label: "Units & Users", key: "unitsUsers", subItems: [
      { label: "Unit Summary", key: "unitSummary" },
      { label: "Resident Summary", key: "residentSummary" },
    ] },
    { label: "Helpdesk Tracker", key: "helpdeskTracker", subItems: [
      { label: "Open tickets", key: "openTickets" },
      { label: "Helpdesk summary", key: "helpdeskSummary" },
    ] },
    { label: "Finance Tracker", key: "financeTracker", subItems: [
      { label: "Income Tracker", key: "incomeTracker" },
      { label: "Expense Tracker", key: "expenseTracker" },
      { label: "Bank & Cash", key: "bankCash" },
      { label: "General Ledger", key: "generalLedger" },
      { label: "Utility Tracker", key: "utilityTracker" },
    ] },
    { label: "Society GateKeeper", key: "addaGatekeeper", subItems: [
      { label: "Gatekeeper activity", key: "gatekeeperActivity" },
    ] },
    { label: "Society Operations", key: "erpOperations", subItems: [
      { label: "Operations Health", key: "operationsHealth" },
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
    { label: "Members Management", key: "membersManagement", subItems: [
      { label: "View All Members", key: "allMembers" },
      { label: "Add New Member", key: "addMember" },
      { label: "Bulk Import", key: "bulkImport" },
      { label: "Member Approvals", key: "pendingResidents" },
      { label: "Family Members", key: "familyMembers" },
      { label: "Society Directory", key: "societyDirectory" },
    ]},
    { label: "Parking Management", key: "parkingManagement", subItems: [
      { label: "Parking Slots", key: "parkingSlots" },
      { label: "Vehicles", key: "vehicles" },
      { label: "Parking Reports", key: "parkingReports" },
    ]},
    { label: "Billing Management", key: "billingManagement", subItems: [
      { label: "Bills", key: "billsList" },
      { label: "Create Bill", key: "createBill" },
      { label: "Bill Payments", key: "billPayments" },
      { label: "Billing Reports", key: "billingReports" },
    ]},
    { label: "Vendor Management", key: "vendorManagement", subItems: [
      { label: "All Vendors", key: "vendorsList" },
      { label: "Add Vendor", key: "addVendor" },
      { label: "Vendor Performance", key: "vendorPerformance" },
      { label: "Vendor Payments", key: "vendorPayments" },
    ]},
    { label: "Community & Lifestyle", key: "community", subItems: [
      { label: "Community Dashboard", key: "communityDashboard" },
      { label: "Notice Board", key: "noticeBoard" },
      { label: "Community Feed", key: "communityFeed" },
      { label: "Events", key: "eventsList" },
      { label: "Poll & Voting", key: "pollsList" },
      { label: "Meetings & AGM", key: "meetingsList" },
      { label: "Emergency Contacts", key: "emergencyContacts" },
      { label: "Expense Tracking", key: "expensesList" },
      { label: "Expense Categories", key: "expenseCategories" },
      { label: "Utility Readings", key: "utilitiesList" },
    ]},
    { label: "Gate & Security", key: "gateSecurity", subItems: [
      { label: "Parcel / Delivery", key: "parcelsList" },
      { label: "Security Patrols", key: "patrolsList" },
      { label: "Domestic Help", key: "domesticHelpList" },
    ]},
    { label: "Reports", key: "reports", subItems: [
      { label: "Billing Reports", key: "billingReportsSection" },
      { label: "Member Reports", key: "memberReportsSection" },
      { label: "Operations Reports", key: "operationsReportsSection" },
      { label: "Download", key: "downloadReports" },
    ]},
    { label: "Operations Health", key: "operationsHealth" },
  ];
  const renderOperationsHealth = () => (
    <article className="panel card-panel operations-panel">
      <div className="section-heading-row light">
        <div>
          <p className="eyebrow">Society operations</p>
          <h3>Daily society operations health</h3>
        </div>
        <button className="secondary-button" type="button" onClick={() => fetchOperationsOverview()}>
          Refresh
        </button>
      </div>
      {user?.role === "admin" && (
        <label className="field-group compact-field">
          <span>Scope by society</span>
          <select
            value={selectedSocietyId || ""}
            onChange={(event) => {
              const value = event.target.value ? Number(event.target.value) : null;
              setSelectedSocietyId(value);
              fetchOperationsOverview(value);
            }}
          >
            <option value="">All societies</option>
            {adminSocieties.map((society) => (
              <option key={society.id} value={society.id}>{society.name} - {society.city}</option>
            ))}
          </select>
        </label>
      )}
      {operationsOverview ? (
        <>
          <div className="operations-metric-grid">
            {[
              ["Assets", operationsOverview.assets_total],
              ["AMC due soon", operationsOverview.assets_with_amc_due],
              ["Inventory items", operationsOverview.inventory_items],
              ["Reorder alerts", operationsOverview.inventory_reorder_alerts],
              ["Active staff", operationsOverview.staff_active],
              ["Staff checked in", operationsOverview.staff_checked_in_today],
              ["Registered vehicles", operationsOverview.registered_vehicles],
              ["Gate passes", operationsOverview.active_gate_passes],
              ["Purchase approvals", operationsOverview.open_purchase_requests],
              ["Upcoming bookings", operationsOverview.amenity_bookings_upcoming],
              ["Compliance open", operationsOverview.open_compliance_events],
              ["Privacy requests", operationsOverview.privacy_events_open],
            ].map(([label, value]) => (
              <div className="mini-metric" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div className="operations-lists">
            <div>
              <h4>Low stock items</h4>
              {operationsOverview.low_stock_items?.length ? (
                operationsOverview.low_stock_items.map((item) => (
                  <div className="ops-list-row" key={item.id}>
                    <strong>{item.name}</strong>
                    <span>{item.quantity} on hand / min {item.min_quantity}</span>
                  </div>
                ))
              ) : (
                <p>No reorder alerts.</p>
              )}
            </div>
            <div>
              <h4>AMC renewals</h4>
              {operationsOverview.upcoming_amc_assets?.length ? (
                operationsOverview.upcoming_amc_assets.map((asset) => (
                  <div className="ops-list-row" key={asset.id}>
                    <strong>{asset.name}</strong>
                    <span>{asset.location} - {asset.amc_expires_at ? new Date(asset.amc_expires_at).toLocaleDateString() : "No date"}</span>
                  </div>
                ))
              ) : (
                <p>No AMC renewals due in the next 30 days.</p>
              )}
            </div>
          </div>
        </>
      ) : (
        <p>Operations overview will load after login when society records are available.</p>
      )}
    </article>
  );

  const renderAuthenticatedHome = () => (
    <section className="workspace-shell">
      <article className="panel card-panel workspace-hero">
        <div>
          <p className="eyebrow">Signed-in workspace</p>
          <h2>{user?.role === "admin" ? "Developer control center" : "Society admin control center"}</h2>
          <p>
            {user?.role === "admin"
              ? "Manage societies, admins, users, module access, and platform-wide society operations."
              : "Run your society operations from one place: approvals, security, billing, complaints, staff, vehicles, amenities, and notices."}
          </p>
        </div>
        <div className="workspace-actions">
          {user?.role === "admin" && (
            <>
              <button className="primary-button" onClick={() => updateView("developerPanel")}>Open Developer Panel</button>
              <button className="secondary-button" onClick={seedDemoData}>Seed demo data</button>
            </>
          )}
          {user?.role === "society_admin" && (
            <button className="primary-button" onClick={() => setView("societyPanel")}>Open Society Panel</button>
          )}
          <button className="secondary-button" onClick={() => fetchOperationsOverview()}>Refresh Operations</button>
        </div>
      </article>

      <section className="operations-metric-grid">
        {[
          ["Societies", systemSummary?.total_societies ?? adminSocieties.length],
          ["Residents pending", pendingResidents.length],
          ["Open tickets", systemSummary?.open_tickets ?? dashboard?.open_tickets ?? 0],
          ["Today visitors", dashboard?.visitor_activity ?? 0],
          ["Pending dues", dashboard?.pending_dues ?? 0],
          ["Active staff", operationsOverview?.staff_active ?? 0],
          ["Vehicles", operationsOverview?.registered_vehicles ?? 0],
          ["Gate passes", operationsOverview?.active_gate_passes ?? 0],
        ].map(([label, value]) => (
          <article className="mini-metric" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </section>

      <section className="module-workbench">
        {societyWorkbenchModules.map((module) => (
          <article className="module-tile" key={module.key}>
            <div className="module-tile-header">
              <strong>{module.title}</strong>
              <span>{module.status}</span>
            </div>
            <p>{module.summary}</p>
            <div className="module-chip-row">
              {module.metrics.map((metric) => <span key={metric}>{metric}</span>)}
            </div>
          </article>
        ))}
      </section>
    </section>
  );

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
          <article className="panel card-panel grid-panel">
            <h3>All societies</h3>
            {adminSocieties.length > 0 ? (
                  <div className="ag-grid-wrapper ag-theme-alpine">
                    <AgGridReact
                      domLayout="autoHeight"
                      style={{ width: "100%", minHeight: "320px" }}
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
          <article className="panel card-panel grid-panel">
            <h3>All users</h3>
            {adminUsers.length > 0 ? (
                  <div className="ag-grid-wrapper ag-theme-alpine">
                    <AgGridReact
                      domLayout="autoHeight"
                      style={{ width: "100%", minHeight: "320px" }}
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
      case "unitsUsers":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Units & users</p>
                <h3>Platform-wide unit and resident health</h3>
              </div>
              <button className="secondary-button" type="button" onClick={() => { fetchAdminUnits(); fetchAdminLedger(); }}>
                Refresh overview
              </button>
            </div>
            {adminUnits && adminLedger ? (
              <div className="metrics-grid">
                {[
                  ["Total units", adminUnits.total_units],
                  ["Occupied units", adminUnits.occupied_units],
                  ["Total residents", adminUnits.total_residents],
                  ["Total income", adminLedger.total_income],
                  ["Vendor payables", adminLedger.vendor_payables],
                  ["Ledger balance", adminLedger.ledger_balance],
                ].map(([label, value]) => (
                  <div key={label} className="metric-card">
                    <span>{label}</span>
                    <strong>{value}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p>Loading units and users overview…</p>
            )}
          </article>
        );
      case "helpdeskTracker":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Helpdesk tracker</p>
                <h3>Ticket and support summary</h3>
              </div>
              <button className="secondary-button" type="button" onClick={() => { fetchAdminTickets(); fetchDashboard(); }}>
                Refresh helpdesk
              </button>
            </div>
            <div className="operations-metric-grid">
              {[
                ["Open tickets", dashboard?.open_tickets ?? 0],
                ["Pending dues", dashboard?.pending_dues ?? 0],
                ["Vendor payables", dashboard?.vendor_payables ?? 0],
                ["Active gate passes", operationsOverview?.active_gate_passes ?? 0],
              ].map(([label, value]) => (
                <div className="mini-metric" key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
            <p className="note-text">Use the open tickets tab to manage individual cases and update status.</p>
          </article>
        );
      case "financeTracker":
        return (
          <article className="panel card-panel">
            <h3>Finance tracker</h3>
            {adminLedger ? (
              <div className="operations-metric-grid">
                {[
                  ["Total income", adminLedger.total_income],
                  ["Total expenses", adminLedger.vendor_expenses],
                  ["Bank cash", adminLedger.bank_cash],
                  ["Ledger balance", adminLedger.ledger_balance],
                ].map(([label, value]) => (
                  <div className="mini-metric" key={label}>
                    <span>{label}</span>
                    <strong>{value}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p>Loading finance summary…</p>
            )}
          </article>
        );
      case "unitSummary":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Units & occupancy</p>
                <h3>Unit summary</h3>
              </div>
              <button className="secondary-button" type="button" onClick={fetchAdminUnits}>Refresh</button>
            </div>
            {adminUnits ? (
              <div className="operations-metric-grid">
                {[
                  ["Total units", adminUnits.total_units],
                  ["Occupied units", adminUnits.occupied_units],
                  ["Unoccupied units", adminUnits.unoccupied_units],
                  ["Total residents", adminUnits.total_residents],
                ].map(([label, value]) => (
                  <div className="mini-metric" key={label}>
                    <span>{label}</span>
                    <strong>{value}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p>Loading unit metrics…</p>
            )}
          </article>
        );
      case "residentSummary":
        return (
          <article className="panel card-panel">
            <h3>Resident summary</h3>
            <p>View global resident and active user distribution across societies.</p>
            {adminUnits ? (
              <div className="metrics-grid">
                <div className="metric-card">
                  <span>Total residents</span>
                  <strong>{adminUnits.total_residents}</strong>
                </div>
                <div className="metric-card">
                  <span>Assigned units</span>
                  <strong>{adminUnits.occupied_units}</strong>
                </div>
                <div className="metric-card">
                  <span>Unassigned units</span>
                  <strong>{adminUnits.unoccupied_units}</strong>
                </div>
              </div>
            ) : (
              <p>Loading resident summary…</p>
            )}
          </article>
        );
      case "helpdeskSummary":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Helpdesk tracker</p>
                <h3>Helpdesk summary</h3>
              </div>
              <button className="secondary-button" type="button" onClick={() => { fetchAdminTickets(); fetchDashboard(); }}>
                Refresh
              </button>
            </div>
            <div className="operations-metric-grid">
              {[
                ["Open tickets", dashboard?.open_tickets ?? 0],
                ["Pending dues", dashboard?.pending_dues ?? 0],
                ["Vendor payables", dashboard?.vendor_payables ?? 0],
                ["Active gate passes", operationsOverview?.active_gate_passes ?? 0],
              ].map(([label, value]) => (
                <div className="mini-metric" key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
            <p className="note-text">Open tickets are managed through the helpdesk pipeline and status updates are visible in the ticket tracker.</p>
          </article>
        );
      case "openTickets":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Helpdesk tracker</p>
                <h3>Open tickets</h3>
              </div>
              <button className="secondary-button" type="button" onClick={fetchAdminTickets}>
                Refresh tickets
              </button>
            </div>
            {adminTickets.length > 0 ? (
              <div className="table-card">
                <div className="table-row table-header">
                  <span>Ticket</span>
                  <span>Status</span>
                  <span>Resident</span>
                  <span>Vendor</span>
                  <span>Actions</span>
                </div>
                {adminTickets.map((ticket) => (
                  <div key={ticket.id} className="table-row">
                    <span>{ticket.title}</span>
                    <span>{ticket.status.replace(/_/g, " ")}</span>
                    <span>{ticket.resident_name || "Unknown"}</span>
                    <span>{ticket.assigned_vendor || "Unassigned"}</span>
                    <span className="actions-column">
                      {ticket.status !== "resolved" && (
                        <>
                          <button className="secondary-button" onClick={() => updateTicketStatus(ticket.id, "in_progress")}>In progress</button>
                          <button className="secondary-button" onClick={() => updateTicketStatus(ticket.id, "resolved")}>Resolve</button>
                        </>
                      )}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p>No tickets available yet.</p>
            )}
          </article>
        );
      case "incomeTracker":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Finance tracker</p>
                <h3>Income tracker</h3>
              </div>
              <button className="secondary-button" type="button" onClick={fetchAdminLedger}>
                Refresh ledger
              </button>
            </div>
            {adminLedger ? (
              <div className="operations-metric-grid">
                <div className="mini-metric">
                  <span>Total income</span>
                  <strong>{adminLedger.total_income}</strong>
                </div>
                <div className="mini-metric">
                  <span>Pending dues</span>
                  <strong>{adminLedger.pending_dues}</strong>
                </div>
                <div className="mini-metric">
                  <span>Vendor invoices</span>
                  <strong>{adminLedger.vendor_invoices}</strong>
                </div>
              </div>
            ) : (
              <p>Loading income metrics…</p>
            )}
          </article>
        );
      case "expenseTracker":
        return (
          <article className="panel card-panel">
            <h3>Expense tracker</h3>
            {adminLedger ? (
              <div className="operations-metric-grid">
                <div className="mini-metric">
                  <span>Total expenses</span>
                  <strong>{adminLedger.vendor_expenses}</strong>
                </div>
                <div className="mini-metric">
                  <span>Vendor payables</span>
                  <strong>{adminLedger.vendor_payables}</strong>
                </div>
                <div className="mini-metric">
                  <span>Utility spend</span>
                  <strong>{adminLedger.utility_spend}</strong>
                </div>
              </div>
            ) : (
              <p>Loading expense analytics…</p>
            )}
          </article>
        );
      case "bankCash":
        return (
          <article className="panel card-panel">
            <h3>Bank & cash</h3>
            {adminLedger ? (
              <div className="operations-metric-grid">
                <div className="mini-metric">
                  <span>Bank cash position</span>
                  <strong>{adminLedger.bank_cash}</strong>
                </div>
                <div className="mini-metric">
                  <span>Pending dues</span>
                  <strong>{adminLedger.pending_dues}</strong>
                </div>
                <div className="mini-metric">
                  <span>Open tickets</span>
                  <strong>{dashboard?.open_tickets ?? 0}</strong>
                </div>
              </div>
            ) : (
              <p>Loading bank position…</p>
            )}
          </article>
        );
      case "generalLedger":
        return (
          <article className="panel card-panel">
            <h3>General ledger</h3>
            {adminLedger ? (
              <div className="metrics-grid">
                {[
                  ["Total income", adminLedger.total_income],
                  ["Total expenses", adminLedger.vendor_expenses],
                  ["Ledger balance", adminLedger.ledger_balance],
                  ["Utility spend", adminLedger.utility_spend],
                ].map(([label, value]) => (
                  <div className="metric-card" key={label}>
                    <span>{label}</span>
                    <strong>{value}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p>Loading ledger summary…</p>
            )}
          </article>
        );
      case "utilityTracker":
        return (
          <article className="panel card-panel">
            <h3>Utility tracker</h3>
            {adminLedger ? (
              <div>
                <p>Utility spend is estimated from vendor invoices and expense records.</p>
                <div className="operations-metric-grid">
                  <div className="mini-metric">
                    <span>Utility spend</span>
                    <strong>{adminLedger.utility_spend}</strong>
                  </div>
                  <div className="mini-metric">
                    <span>Reorder alerts</span>
                    <strong>{operationsOverview?.inventory_reorder_alerts ?? 0}</strong>
                  </div>
                  <div className="mini-metric">
                    <span>Pending repairs</span>
                    <strong>{operationsOverview?.open_purchase_requests ?? 0}</strong>
                  </div>
                </div>
              </div>
            ) : (
              <p>Loading utility snapshot…</p>
            )}
          </article>
        );
      case "gatekeeperActivity":
      case "addaGatekeeper":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Society GateKeeper</p>
                <h3>Gate and visitor operations</h3>
              </div>
              <button className="secondary-button" type="button" onClick={() => fetchOperationsOverview()}>
                Refresh gatekeeper
              </button>
            </div>
            {operationsOverview ? (
              <div className="operations-metric-grid">
                {[
                  ["Today visitors", dashboard?.visitor_activity ?? 0],
                  ["Active gate passes", operationsOverview?.active_gate_passes ?? 0],
                  ["Staff checked in", operationsOverview?.staff_checked_in_today ?? 0],
                  ["Open purchase requests", operationsOverview?.open_purchase_requests ?? 0],
                ].map(([label, value]) => (
                  <div className="mini-metric" key={label}>
                    <span>{label}</span>
                    <strong>{value}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p>Loading gatekeeper metrics…</p>
            )}
          </article>
        );
      case "operationsHealth":
      case "erpOperations":
        return renderOperationsHealth();
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
                      {userItem.access_erp && <strong>Society Ops</strong>}
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
                        ["access_erp", "Society Ops"],
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
      case "operationsHealth":
        return renderOperationsHealth();
      case "allMembers":
        return (
          <article className="panel card-panel grid-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Members</p>
                <h3>All society members</h3>
              </div>
              <button className="secondary-button" type="button" onClick={() => setSocietySection("addMember")}>Add Member</button>
            </div>
            {societyUsers.length > 0 ? (
              <div className="ag-grid-wrapper ag-theme-alpine">
                <AgGridReact
                  domLayout="autoHeight"
                  rowData={societyUsers}
                  columnDefs={[
                    { field: "full_name", headerName: "Name", flex: 1 },
                    { field: "email", headerName: "Email", flex: 1 },
                    { field: "phone", headerName: "Phone", flex: 1 },
                    { field: "role", headerName: "Role", flex: 0.8 },
                    { 
                      field: "is_active", 
                      headerName: "Status", 
                      valueFormatter: (params) => (params.value ? "Active" : "Inactive"), 
                      flex: 0.8 
                    },
                  ]}
                  defaultColDef={{ sortable: true, filter: true, resizable: true, minWidth: 100 }}
                  style={{ width: "100%", minHeight: "320px" }}
                />
              </div>
            ) : (
              <p>No members found. Add your first member.</p>
            )}
          </article>
        );
      case "addMember":
        return (
          <article className="panel form-panel">
            <h3>Add new member</h3>
            <form onSubmit={async (e) => {
              e.preventDefault();
              const newMemberForm = {
                full_name: e.target.elements.full_name.value,
                email: e.target.elements.email.value,
                phone: e.target.elements.phone.value,
                password: e.target.elements.password.value,
                society_id: user.society_id,
                role: "resident",
              };
              try {
                await axios.post(`${API_BASE}/users/register`, newMemberForm);
                setMessage("Member added successfully. They will need approval before login.");
                e.target.reset();
                setSocietySection("allMembers");
                fetchSocietyUsers(user.society_id);
              } catch (err) {
                setMessage(err.response?.data?.detail || "Failed to add member.");
              }
            }}>
              <FormField label="Full name" value="" onChange={() => {}} />
              <FormField label="Email" value="" onChange={() => {}} />
              <FormField label="Phone" value="" onChange={() => {}} />
              <FormField label="Password" type="password" value="" onChange={() => {}} />
              <button className="primary-button" type="submit">Add Member</button>
            </form>
          </article>
        );
      case "bulkImport":
        return (
          <article className="panel card-panel">
            <h3>Bulk import members</h3>
            <p>Upload a CSV file with member details (full_name, email, phone, password, role)</p>
            <div className="field-group">
              <span>CSV File</span>
              <input type="file" accept=".csv" onChange={(e) => {
                const file = e.target.files[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onload = async (event) => {
                    try {
                      const csv = event.target.result;
                      const lines = csv.split('\n');
                      const headers = lines[0].split(',');
                      let imported = 0;
                      for (let i = 1; i < lines.length; i++) {
                        if (lines[i].trim() === '') continue;
                        const values = lines[i].split(',');
                        const memberData = {};
                        headers.forEach((header, idx) => {
                          memberData[header.trim()] = values[idx]?.trim();
                        });
                        if (memberData.full_name && memberData.email && memberData.phone) {
                          await axios.post(`${API_BASE}/users/register`, {
                            ...memberData,
                            society_id: user.society_id,
                            role: memberData.role || "resident",
                          });
                          imported++;
                        }
                      }
                      setMessage(`${imported} members imported successfully.`);
                      fetchSocietyUsers(user.society_id);
                    } catch (err) {
                      setMessage(err.message || "Error importing members.");
                    }
                  };
                  reader.readAsText(file);
                }
              }} />
            </div>
            <p className="note-text">CSV format: full_name, email, phone, password, role</p>
          </article>
        );
      case "pendingResidents":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Approvals</p>
                <h3>Pending resident approvals</h3>
              </div>
            </div>
            {pendingResidents.length > 0 ? (
              pendingResidents.map((resident) => (
                <div key={resident.id} className="pending-row">
                  <div>
                    <strong>{resident.full_name}</strong>
                    <p>{resident.email} • {resident.phone}</p>
                  </div>
                  <button className="secondary-button" onClick={() => handleApproveResident(resident.id)}>Approve</button>
                </div>
              ))
            ) : (
              <p>No pending residents to approve.</p>
            )}
          </article>
        );
      case "parkingSlots":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Parking</p>
                <h3>Parking slots</h3>
              </div>
              <button className="secondary-button" type="button">Add Slot</button>
            </div>
            <p>Parking management feature integrated with operations overview. View available slots and assignments from Operations Health.</p>
            <div className="info-section">
              {operationsOverview ? (
                <>
                  <p><strong>Registered Vehicles:</strong> {operationsOverview.registered_vehicles}</p>
                  <p><strong>Active Gate Passes:</strong> {operationsOverview.active_gate_passes}</p>
                </>
              ) : (
                <p>Loading parking data...</p>
              )}
            </div>
          </article>
        );
      case "vehicles":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Parking</p>
                <h3>Registered vehicles</h3>
              </div>
              <button className="secondary-button" type="button">Register Vehicle</button>
            </div>
            <p>Vehicle management integrated with operations. {operationsOverview?.registered_vehicles || 0} vehicles registered.</p>
            <p className="note-text">Full vehicle management with stickers and movement controls available through the operations module.</p>
          </article>
        );
      case "parkingReports":
        return (
          <article className="panel card-panel">
            <h3>Parking reports</h3>
            <div className="reports-section">
              <div className="report-card">
                <h4>Vehicle Summary</h4>
                <p><strong>Total Vehicles:</strong> {operationsOverview?.registered_vehicles || 0}</p>
                <p><strong>Active Gate Passes:</strong> {operationsOverview?.active_gate_passes || 0}</p>
                <button className="secondary-button">Download Report</button>
              </div>
            </div>
          </article>
        );
      case "billsList":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Billing</p>
                <h3>Maintenance bills</h3>
              </div>
              <button className="secondary-button" type="button" onClick={() => setSocietySection("createBill")}>Create Bill</button>
            </div>
            <p>Monthly maintenance bills for all residents. Track collection status and pending dues.</p>
            <div className="bills-summary">
              <div className="bill-stat">
                <span>Pending Dues</span>
                <strong>{dashboard?.pending_dues || 0}</strong>
              </div>
              <div className="bill-stat">
                <span>Collected</span>
                <strong>{dashboard?.collected || 0}</strong>
              </div>
            </div>
          </article>
        );
      case "createBill":
        return (
          <article className="panel form-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Advanced billing</p>
                <h3>Create manual invoice</h3>
              </div>
              <button className="secondary-button" type="button" onClick={() => {
                const societyId = user?.role === "admin" ? selectedSocietyId : user?.society_id;
                fetchBillHeads(societyId);
                fetchUnits();
                fetchBillTemplates(societyId);
                fetchInvoiceSummary(societyId);
                fetchInvoices({ society_id: societyId });
              }}>
                Refresh billing data
              </button>
            </div>
            <p>Issue an invoice using MCS Act bill headers, add custom sections, and create a manual sample invoice for any unit.</p>
            <form onSubmit={handleCreateManualInvoice}>
              <label className="field-group">
                <span>Billing month</span>
                <input type="month" value={billingMonth} onChange={(e) => setBillingMonth(e.target.value)} />
              </label>
              <label className="field-group">
                <span>Unit</span>
                {units.length > 0 ? (
                  <select value={manualInvoiceUnitId} onChange={(e) => setManualInvoiceUnitId(e.target.value)}>
                    <option value="">Select unit</option>
                    {units.map((unit) => (
                      <option key={unit.id} value={unit.id}>{unit.building} {unit.unit_number}</option>
                    ))}
                  </select>
                ) : (
                  <input type="number" placeholder="Unit ID" value={manualInvoiceUnitId} onChange={(e) => setManualInvoiceUnitId(e.target.value)} />
                )}
              </label>

              <div className="section-heading-row">
                <div>
                  <p className="eyebrow">Bill sections</p>
                  <h4>Line items</h4>
                </div>
                <button className="secondary-button" type="button" onClick={handleAddLineItem}>Add section</button>
              </div>
              {billHeads.length === 0 ? (
                <div className="panel card-panel">
                  <p>No bill headers found for this society. Create a new section or load default MCS Act headers.</p>
                  <button className="secondary-button" type="button" onClick={handleSetupDefaultHeads}>Setup default bill headers</button>
                </div>
              ) : (
                manualInvoiceLineItems.map((item, index) => (
                  <div className="field-group line-item-row" key={`line-item-${index}`}>
                    <label>
                      <span>Section</span>
                      <select value={item.head_id} onChange={(e) => handleLineItemChange(index, "head_id", e.target.value)}>
                        <option value="">Select section</option>
                        {billHeads.map((head) => (
                          <option key={head.id} value={head.id}>{head.name}</option>
                        ))}
                      </select>
                    </label>
                    <label>
                      <span>Amount</span>
                      <input type="number" step="0.01" value={item.amount} onChange={(e) => handleLineItemChange(index, "amount", e.target.value)} />
                    </label>
                    <label>
                      <span>Qty</span>
                      <input type="number" min="1" value={item.quantity} onChange={(e) => handleLineItemChange(index, "quantity", e.target.value)} />
                    </label>
                    <button className="secondary-button" type="button" onClick={() => handleRemoveLineItem(index)}>Remove</button>
                  </div>
                ))
              )}

              <button className="primary-button" type="submit">Create invoice</button>
            </form>

            <article className="panel card-panel form-panel">
              <div className="section-heading-row light">
                <div>
                  <p className="eyebrow">Templates</p>
                  <h4>Billing template builder</h4>
                </div>
              </div>
              <p>Create reusable invoice templates from configured bill heads or load an existing template into the manual invoice.</p>
              <label className="field-group">
                <span>Select template</span>
                <select value={selectedTemplateId || ""} onChange={(e) => setSelectedTemplateId(e.target.value)}>
                  <option value="">Select existing template</option>
                  {billTemplates.map((template) => (
                    <option key={template.id} value={template.id}>{template.name}</option>
                  ))}
                </select>
              </label>
              <div className="button-group">
                <button className="secondary-button" type="button" onClick={() => {
                  const template = billTemplates.find((tpl) => tpl.id === Number(selectedTemplateId));
                  handleLoadTemplateToInvoice(template);
                }} disabled={!selectedTemplateId}>Load template into invoice</button>
                <button className="secondary-button" type="button" onClick={() => handleDeleteTemplate(selectedTemplateId)} disabled={!selectedTemplateId}>Delete template</button>
              </div>
              <form onSubmit={handleCreateTemplate}>
                <FormField label="Template name" value={templateName} onChange={(value) => setTemplateName(value)} />
                {templateLineItems.map((item, index) => (
                  <div className="field-group line-item-row" key={`template-line-item-${index}`}>
                    <label>
                      <span>Section</span>
                      <select value={item.head_id} onChange={(e) => handleTemplateLineItemChange(index, "head_id", e.target.value)}>
                        <option value="">Select section</option>
                        {billHeads.map((head) => (
                          <option key={head.id} value={head.id}>{head.name}</option>
                        ))}
                      </select>
                    </label>
                    <label>
                      <span>Amount</span>
                      <input type="number" step="0.01" value={item.amount} onChange={(e) => handleTemplateLineItemChange(index, "amount", e.target.value)} />
                    </label>
                    <label>
                      <span>% Value</span>
                      <input type="number" step="0.01" value={item.percentage_value} onChange={(e) => handleTemplateLineItemChange(index, "percentage_value", e.target.value)} />
                    </label>
                    <label className="field-group compact-field">
                      <span>Use %</span>
                      <input type="checkbox" checked={item.is_percentage} onChange={(e) => handleTemplateLineItemChange(index, "is_percentage", e.target.checked)} />
                    </label>
                    <button className="secondary-button" type="button" onClick={() => handleRemoveTemplateLineItem(index)}>Remove</button>
                  </div>
                ))}
                <button className="secondary-button" type="button" onClick={handleAddTemplateLineItem}>Add template section</button>
                <button className="primary-button" type="submit">Save template</button>
              </form>
              {billTemplates.length > 0 && (
                <div className="template-list">
                  <h5>Existing templates</h5>
                  {billTemplates.map((template) => (
                    <div key={template.id} className="ops-list-row">
                      <strong>{template.name}</strong>
                      <span>{template.heads?.length || 0} sections</span>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article className="panel card-panel form-panel">
              <div className="section-heading-row light">
                <div>
                  <p className="eyebrow">Generate invoices</p>
                  <h4>Bulk generation</h4>
                </div>
              </div>
              <p>Use a saved template to generate invoices for all society units.</p>
              <form onSubmit={handleGenerateInvoices}>
                <label className="field-group">
                  <span>Template</span>
                  <select value={selectedTemplateId || ""} onChange={(e) => setSelectedTemplateId(e.target.value)}>
                    <option value="">Select template</option>
                    {billTemplates.map((template) => (
                      <option key={template.id} value={template.id}>{template.name}</option>
                    ))}
                  </select>
                </label>
                <label className="field-group">
                  <span>Billing month</span>
                  <input type="month" value={billingTemplateMonth} onChange={(e) => setBillingTemplateMonth(e.target.value)} />
                </label>
                <button className="primary-button" type="submit">Generate invoices</button>
              </form>
              {generatedInvoices.length > 0 && (
                <div className="invoice-list-summary">
                  <h5>Generated invoices</h5>
                  {generatedInvoices.slice(0, 5).map((invoice) => (
                    <div key={invoice.invoice_id} className="ops-list-row">
                      <strong>{invoice.invoice_number}</strong>
                      <span>Unit {invoice.unit_id} • {invoice.status} • ₹{invoice.net_amount}</span>
                    </div>
                  ))}
                </div>
              )}
            </article>

            {invoiceSummary && (
              <article className="panel card-panel">
                <h4>Invoice summary</h4>
                <div className="metric-row">
                  <span>Total invoices</span>
                  <strong>{invoiceSummary.total_invoices}</strong>
                </div>
                <div className="metric-row">
                  <span>Pending</span>
                  <strong>{invoiceSummary.pending}</strong>
                </div>
                <div className="metric-row">
                  <span>Paid</span>
                  <strong>{invoiceSummary.paid}</strong>
                </div>
                <div className="metric-row">
                  <span>Overdue</span>
                  <strong>{invoiceSummary.overdue}</strong>
                </div>
                <div className="metric-row">
                  <span>Outstanding</span>
                  <strong>₹{invoiceSummary.outstanding}</strong>
                </div>
              </article>
            )}

            {createdInvoice && (
              <article className="panel card-panel">
                <h4>Invoice created</h4>
                <div className="metric-row">
                  <span>Invoice number</span>
                  <strong>{createdInvoice.invoice_number}</strong>
                </div>
                <div className="metric-row">
                  <span>Total amount</span>
                  <strong>{createdInvoice.total_amount}</strong>
                </div>
                <div className="metric-row">
                  <span>Net amount</span>
                  <strong>{createdInvoice.net_amount}</strong>
                </div>
                <div className="metric-row">
                  <span>Status</span>
                  <strong>{createdInvoice.status}</strong>
                </div>
                <div className="invoice-items-preview">
                  <h5>Line items</h5>
                  {createdInvoice.line_items?.map((item) => (
                    <div className="ops-list-row" key={item.id}>
                      <strong>{item.head_name}</strong>
                      <span>{item.quantity} × {item.amount} = {item.total}</span>
                    </div>
                  ))}
                </div>
              </article>
            )}

            <article className="panel card-panel form-panel">
              <h3>Add new billing section</h3>
              <form onSubmit={handleCreateBillHead}>
                <FormField label="Section name" value={newBillHead.name} onChange={(value) => setNewBillHead((prev) => ({ ...prev, name: value }))} />
                <FormField label="Short code" value={newBillHead.short_code} onChange={(value) => setNewBillHead((prev) => ({ ...prev, short_code: value }))} />
                <label className="field-group">
                  <span>Description</span>
                  <textarea value={newBillHead.description} onChange={(e) => setNewBillHead((prev) => ({ ...prev, description: e.target.value }))} />
                </label>
                <label className="field-group compact-field">
                  <span>Mandatory</span>
                  <input type="checkbox" checked={newBillHead.is_mandatory} onChange={(e) => setNewBillHead((prev) => ({ ...prev, is_mandatory: e.target.checked }))} />
                </label>
                <label className="field-group">
                  <span>Display order</span>
                  <input type="number" value={newBillHead.display_order} onChange={(e) => setNewBillHead((prev) => ({ ...prev, display_order: e.target.value }))} />
                </label>
                <button className="primary-button" type="submit">Create section</button>
              </form>
            </article>
          </article>
        );
      case "billPayments":
        return (
          <article className="panel card-panel">
            <h3>Bill payments</h3>
            <p>Track payment status and collection progress for all maintenance bills.</p>
            <div className="payments-info">
              <p className="note-text">Payment tracking is integrated with the payment gateway module. View payment details from billing reports.</p>
            </div>
          </article>
        );
      case "billingReports":
        return (
          <article className="panel card-panel">
            <h3>Billing reports</h3>
            <div className="reports-grid">
              <div className="report-card">
                <h4>Pending Collections</h4>
                <strong>{dashboard?.pending_dues || 0}</strong>
                <button className="secondary-button">View Details</button>
              </div>
              <div className="report-card">
                <h4>Collected Amount</h4>
                <strong>{dashboard?.collected || 0}</strong>
                <button className="secondary-button">Download Report</button>
              </div>
            </div>
          </article>
        );
      case "vendorsList":
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Vendors</p>
                <h3>All vendors</h3>
              </div>
              <button className="secondary-button" type="button" onClick={() => setSocietySection("addVendor")}>Add Vendor</button>
            </div>
            <p>Manage all service vendors for your society including maintenance, repairs, and utilities.</p>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Vendor Name</th>
                  <th>Category</th>
                  <th>Contact</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Sample Vendor</td>
                  <td>Maintenance</td>
                  <td>vendor@example.com</td>
                  <td>Active</td>
                  <td><button className="secondary-button">Edit</button></td>
                </tr>
              </tbody>
            </table>
          </article>
        );
      case "addVendor":
        return (
          <article className="panel form-panel">
            <h3>Add new vendor</h3>
            <form onSubmit={async (e) => {
              e.preventDefault();
              setMessage("Vendor added successfully. They can now receive work assignments.");
              setSocietySection("vendorsList");
            }}>
              <FormField label="Vendor name" value="" onChange={() => {}} />
              <FormField label="Email" value="" onChange={() => {}} />
              <FormField label="Phone" value="" onChange={() => {}} />
              <label className="field-group">
                <span>Category</span>
                <select>
                  <option>Maintenance</option>
                  <option>Repair</option>
                  <option>Cleaning</option>
                  <option>Plumbing</option>
                  <option>Electrical</option>
                  <option>Other</option>
                </select>
              </label>
              <FormField label="Address" value="" onChange={() => {}} />
              <button className="primary-button" type="submit">Add Vendor</button>
            </form>
          </article>
        );
      case "vendorPerformance":
        return (
          <article className="panel card-panel">
            <h3>Vendor performance</h3>
            <p>Track vendor performance metrics and ratings based on completed work.</p>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>Jobs Completed</th>
                  <th>Rating</th>
                  <th>Response Time</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Sample Vendor</td>
                  <td>15</td>
                  <td>4.5/5</td>
                  <td>2 hrs</td>
                </tr>
              </tbody>
            </table>
          </article>
        );
      case "vendorPayments":
        return (
          <article className="panel card-panel">
            <h3>Vendor payments</h3>
            <p>Track and manage payments to vendors for completed work.</p>
            <div className="vendor-payment-info">
              <p className="note-text">Vendor payment tracking and billing integrated with the billing management module.</p>
            </div>
          </article>
        );
      case "billingReportsSection":
        return (
          <article className="panel card-panel">
            <h3>Billing reports</h3>
            <div className="reports-section">
              <button className="secondary-button">Monthly Billing Report</button>
              <button className="secondary-button">Outstanding Dues Report</button>
              <button className="secondary-button">Collection Report</button>
              <button className="secondary-button">Vendor Payables Report</button>
            </div>
          </article>
        );
      case "memberReportsSection":
        return (
          <article className="panel card-panel">
            <h3>Member reports</h3>
            <div className="reports-section">
              <button className="secondary-button">Member Directory</button>
              <button className="secondary-button">New Members Report</button>
              <button className="secondary-button">Member Status Report</button>
              <button className="secondary-button">Family Details Report</button>
            </div>
          </article>
        );
      case "operationsReportsSection":
        return (
          <article className="panel card-panel">
            <h3>Operations reports</h3>
            <div className="reports-section">
              <button className="secondary-button">Staff Attendance Report</button>
              <button className="secondary-button">Visitor Log Report</button>
              <button className="secondary-button">Complaint Resolution Report</button>
              <button className="secondary-button">Amenity Usage Report</button>
            </div>
          </article>
        );
      case "downloadReports":
        return (
          <article className="panel card-panel">
            <h3>Download reports</h3>
            <p>Export reports in CSV, PDF, or Excel format.</p>
            <div className="download-section">
              <div className="download-option">
                <h4>Latest Reports</h4>
                <button className="secondary-button">Download as CSV</button>
                <button className="secondary-button">Download as PDF</button>
                <button className="secondary-button">Download as Excel</button>
              </div>
            </div>
          </article>
        );
      default:
        return (
          <article className="panel card-panel">
            <div className="section-heading-row light">
              <div>
                <p className="eyebrow">Welcome</p>
                <h2>Society Admin Dashboard</h2>
              </div>
            </div>
            <p>Select a section from the left menu to manage your society operations.</p>
            <div className="dashboard-quick-links">
              <div className="quick-link" onClick={() => setSocietySection("allMembers")}>
                <strong>Members</strong>
                <p>{societyUsers.length} registered</p>
              </div>
              <div className="quick-link" onClick={() => setSocietySection("billsList")}>
                <strong>Billing</strong>
                <p>Pending: {dashboard?.pending_dues || 0}</p>
              </div>
              <div className="quick-link" onClick={() => setSocietySection("vendorsList")}>
                <strong>Vendors</strong>
                <p>Manage services</p>
              </div>
              <div className="quick-link" onClick={() => setSocietySection("parkingSlots")}>
                <strong>Parking</strong>
                <p>{operationsOverview?.registered_vehicles || 0} vehicles</p>
              </div>
            </div>
          </article>
        );
      case "familyMembers":
        return <FamilyMembersSection apiBase={API_BASE} token={token} user={user} />;
      case "societyDirectory":
        return <SocietyDirectorySection apiBase={API_BASE} token={token} user={user} />;
      case "communityDashboard":
        return <CommunityDashboardSection apiBase={API_BASE} token={token} user={user} />;
      case "noticeBoard":
        return <NoticeBoardSection apiBase={API_BASE} token={token} user={user} />;
      case "communityFeed":
        return <CommunityFeedSection apiBase={API_BASE} token={token} user={user} />;
      case "emergencyContacts":
        return <EmergencyContactsSection apiBase={API_BASE} token={token} user={user} />;
      case "eventsList":
        return <EventsListSection apiBase={API_BASE} token={token} user={user} />;
      case "pollsList":
        return <PollsListSection apiBase={API_BASE} token={token} user={user} />;
      case "meetingsList":
        return <MeetingsListSection apiBase={API_BASE} token={token} user={user} />;
      case "expensesList":
        return <ExpensesListSection apiBase={API_BASE} token={token} user={user} />;
      case "expenseCategories":
        return <ExpenseCategoriesSection apiBase={API_BASE} token={token} user={user} />;
      case "utilitiesList":
        return <UtilitiesListSection apiBase={API_BASE} token={token} user={user} />;
      case "parcelsList":
        return <ParcelsListSection apiBase={API_BASE} token={token} user={user} />;
      case "patrolsList":
        return <PatrolsListSection apiBase={API_BASE} token={token} user={user} />;
      case "domesticHelpList":
        return <DomesticHelpSection apiBase={API_BASE} token={token} user={user} />;
    }
  };

  return (
    <div className="layout-shell">
      <header className="topbar">
        <div className="header-left">
          <strong className="brand-name">🏘️ SocietyMan</strong>
        </div>
        <div className="header-right">
          <nav className="topnav">
            {navItems.map((item) => {
              if (item.hasDropdown) {
                return (
                  <div
                    key={item.dropdownName}
                    className={`nav-dropdown ${openDropdown === item.dropdownName ? "open" : ""}`}
                    onMouseEnter={() => toggleDropdown(item.dropdownName)}
                    onMouseLeave={closeDropdowns}
                  >
                    <button className="nav-dropdown-toggle" onClick={() => toggleDropdown(item.dropdownName)}>
                      {item.label}
                      <span className="arrow">▼</span>
                    </button>
                    <div className="nav-dropdown-menu">
                      {item.subItems.map((sub, idx) => (
                        <div key={sub.view}>
                          <button
                            className="nav-dropdown-item"
                            onClick={() => {
                              closeDropdowns();
                              if (sub.mode) {
                                updateView(sub.view, sub.mode);
                              } else {
                                updateView(sub.view);
                              }
                            }}
                          >
                            <span className="icon">{sub.icon}</span>
                            {sub.label}
                          </button>
                          {idx < item.subItems.length - 1 && <div className="nav-dropdown-divider" />}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }
              return (
                <button
                  key={item.view}
                  className={`nav-link ${view === item.view ? "active" : ""}`}
                  onClick={() => updateView(item.view)}
                >
                  {item.label}
                </button>
              );
            })}
            <button className={`nav-link ${view === "contact" ? "active" : ""}`} onClick={() => updateView("contact")}>
              📞 Contact
            </button>
            {!token && (
              <button className={`nav-link ${view === "login" ? "active" : ""}`} onClick={() => { setLoginMode("society"); updateView("login"); }}>
                🔑 Login
              </button>
            )}
            {user?.role === "admin" && (
              <div
                className={`nav-dropdown ${openDropdown === "devTools" ? "open" : ""}`}
                onMouseEnter={() => toggleDropdown("devTools")}
                onMouseLeave={closeDropdowns}
              >
                <button className={`nav-dropdown-toggle ${view === "developerPanel" ? "active" : ""}`} onClick={() => toggleDropdown("devTools")}>
                  ⚡ Developer
                  <span className="arrow">▼</span>
                </button>
                <div className="nav-dropdown-menu">
                  <button className="nav-dropdown-item" onClick={() => { closeDropdowns(); updateView("developerPanel"); }}>
                    <span className="icon">📊</span>
                    Control Center
                  </button>
                  <div className="nav-dropdown-divider" />
                  <button className="nav-dropdown-item" onClick={handleLogout}>
                    <span className="icon">🚪</span>
                    Logout
                  </button>
                </div>
              </div>
            )}
            {user?.role === "society_admin" && (
              <div
                className={`nav-dropdown ${openDropdown === "societyTools" ? "open" : ""}`}
                onMouseEnter={() => toggleDropdown("societyTools")}
                onMouseLeave={closeDropdowns}
              >
                <button className={`nav-dropdown-toggle ${view === "societyPanel" ? "active" : ""}`} onClick={() => toggleDropdown("societyTools")}>
                  🏢 Society
                  <span className="arrow">▼</span>
                </button>
                <div className="nav-dropdown-menu">
                  <button className="nav-dropdown-item" onClick={() => { closeDropdowns(); setView("societyPanel"); }}>
                    <span className="icon">📋</span>
                    Management Panel
                  </button>
                  <div className="nav-dropdown-divider" />
                  <button className="nav-dropdown-item" onClick={handleLogout}>
                    <span className="icon">🚪</span>
                    Logout
                  </button>
                </div>
              </div>
            )}
            {token && user?.role !== "admin" && user?.role !== "society_admin" && (
              <button className="nav-link secondary" onClick={handleLogout}>
                🚪 Logout
              </button>
            )}
          </nav>
          {user && (
            <div className="user-profile">
              <span className="user-badge">{user.full_name?.charAt(0)}</span>
              <span className="user-name">{user.full_name?.split(" ")[0]}</span>
            </div>
          )}
        </div>
      </header>

      <main className="page-content">

        {message && <div className="toast-alert">{message}</div>}

        {/* Resident Dashboard */}
        {token && user?.role === "resident" && (
          <ResidentDashboard token={token} user={user} />
        )}

        {view === "home" && token && user && renderAuthenticatedHome()}

        {view === "home" && (!token || !user) && (
          <section className="grid-layout">
            
            {erpOverview && (
              <article className="panel card-panel enterprise-showcase">
                <div className="section-heading-row">
                  <div>
                    <p className="eyebrow">Society ERP modules</p>
                    <h3>{erpOverview.platform}</h3>
                  </div>
                  <span className="status-pill">Society operations ready</span>
                </div>
                <div className="erp-module-grid">
                  {erpOverview.modules.slice(0, 10).map((module) => (
                    <div className="erp-module-card" key={module.key}>
                      <span>{module.status}</span>
                      <strong>{module.name}</strong>
                      <p>{module.description}</p>
                    </div>
                  ))}
                </div>
              </article>
            )}
            {erpOverview && (
              <article className="panel card-panel ai-command-panel">
                <div>
                  <p className="eyebrow">Society automation</p>
                  <h3>Billing reminders, complaint routing, inventory alerts, and AMC follow-ups</h3>
                </div>
                <div className="ai-insight-list">
                  {erpOverview.ai_automations.map((job) => (
                    <div className="ai-insight-item" key={job.key}>
                      <strong>{job.name}</strong>
                      <p>{job.description}</p>
                      <span>{Math.round(job.confidence_score * 100)}% confidence</span>
                    </div>
                  ))}
                </div>
              </article>
            )}
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
            {token && user ? (
              <>
                <h2>You are already signed in</h2>
                <p className="subtitle">Continue to your society operations workspace.</p>
                <button className="primary-button" onClick={() => updateView(user.role === "admin" ? "developerPanel" : user.role === "society_admin" ? "societyPanel" : "home")}>
                  Continue
                </button>
              </>
            ) : (
              <>
                <h2>{loginMode === "developer" || window.location.pathname === "/admin" ? "Developer Admin Login" : "Society Admin Login"}</h2>
                <p className="subtitle">Use your registered account to sign in to the portal.</p>
                <form onSubmit={handleLoginSubmit}>
                  <FormField label="Email (optional)" value={loginForm.email} onChange={(value) => setLoginForm((prev) => ({ ...prev, email: value }))} />
                  <FormField label="Phone (optional)" value={loginForm.phone} onChange={(value) => setLoginForm((prev) => ({ ...prev, phone: value }))} />
                  <FormField label="Password" type="password" value={loginForm.password} onChange={(value) => setLoginForm((prev) => ({ ...prev, password: value }))} />
                  <button className="primary-button" type="submit">Sign in</button>
                </form>
                <p className="note-text">Use your registered email or phone. Admin login sends a verification code if required.</p>
              </>
            )}
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

        {view === "contact" && (
          <section className="panel form-panel">
            <article className="panel card-panel">
              <h2>📞 Contact Us</h2>
              <p>Have questions or need help with SocietyMan? Reach out to us.</p>
              <div className="operations-metric-grid" style={{marginTop: "1rem"}}>
                <div className="mini-metric">
                  <span>📧 Email</span>
                  <strong>support@societyman.com</strong>
                </div>
                <div className="mini-metric">
                  <span>📞 Phone</span>
                  <strong>+91-98765-43210</strong>
                </div>
                <div className="mini-metric">
                  <span>🌐 Website</span>
                  <strong>www.societyman.com</strong>
                </div>
                <div className="mini-metric">
                  <span>📍 Address</span>
                  <strong>Mumbai, Maharashtra, India</strong>
                </div>
              </div>
              <form onSubmit={async (e) => { e.preventDefault(); setMessage("Thank you! We will get back to you soon."); }}>
                <FormField label="Your Name" value="" onChange={() => {}} />
                <FormField label="Your Email" value="" onChange={() => {}} />
                <label className="field-group">
                  <span>Message</span>
                  <textarea rows={4}></textarea>
                </label>
                <button className="primary-button" type="submit">Send Message</button>
              </form>
            </article>
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
              {developerNavItems.map((item) => {
                const hasSubItems = item.subItems && item.subItems.length > 0;
                const isExpanded = hasSubItems && item.subItems.some((sub) => sub.key === adminSection);
                const isActive = adminSection === item.key || isExpanded;
                const expandKey = `dev-${item.key}`;
                return (
                  <div key={item.key} className="sidebar-group">
                    <button
                      className={`sidebar-link ${isActive ? "active" : ""}`}
                      onClick={() => {
                        if (hasSubItems) {
                          setOpenDropdown(openDropdown === expandKey ? null : expandKey);
                        }
                        setAdminSection(item.key);
                      }}
                    >
                      <span className="sidebar-link-text">{item.label}</span>
                      {hasSubItems && <span className={`sidebar-arrow ${openDropdown === expandKey || isExpanded ? "expanded" : ""}`}>▸</span>}
                    </button>
                    {hasSubItems && (openDropdown === expandKey || isExpanded) && (
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
                );
              })}
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
              {societyNavItems.map((item) => {
                const hasSubItems = item.subItems && item.subItems.length > 0;
                const isExpanded = hasSubItems && item.subItems.some((sub) => sub.key === societySection);
                const isActive = societySection === item.key || isExpanded;
                const expandKey = `soc-${item.key}`;
                return (
                  <div key={item.key} className="sidebar-group">
                    <button
                      className={`sidebar-link ${isActive ? "active" : ""}`}
                      onClick={() => {
                        if (hasSubItems) {
                          setOpenDropdown(openDropdown === expandKey ? null : expandKey);
                        }
                        setSocietySection(item.key);
                      }}
                    >
                      <span className="sidebar-link-text">{item.label}</span>
                      {hasSubItems && <span className={`sidebar-arrow ${openDropdown === expandKey || isExpanded ? "expanded" : ""}`}>▸</span>}
                    </button>
                    {hasSubItems && (openDropdown === expandKey || isExpanded) && (
                      <div className="sidebar-sublist">
                        {item.subItems.map((sub) => (
                          <button
                            key={sub.key}
                            className={`sidebar-subitem ${societySection === sub.key ? "active" : ""}`}
                            onClick={() => setSocietySection(sub.key)}
                          >
                            {sub.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
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
