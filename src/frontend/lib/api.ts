export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

export type Role = "broker" | "admin";

// ===== Broker & inventory types =====
export type Broker = {
  id: number;
  email: string;
  name: string;
  phone: string;
  kyc_status: "pending" | "approved" | "rejected";
  pan_number: string;
  aadhaar_number: string;
  gst_number: string;
  rera_number: string;
  bank_account: string;
  ifsc: string;
  agreement_accepted: boolean;
  created_at: string;
};

export type Plot = {
  id: number;
  plot_number: string;
  size_sq_yds: string;
  facing: string;
  facing_display: string;
  status: "available" | "on_hold" | "sold";
  bsp: string;
  plc_pct: string;
  discount_pct: string;
  total_cost: number;
};

export type Project = {
  id: number;
  name: string;
  code: string;
  location: string;
  status: string;
  description: string;
  created_at: string;
  total_plots: number;
  available: number;
  on_hold: number;
  sold: number;
  plots?: Plot[];
};

// ===== HTTP helper =====
export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  token?: string | null;
};

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, token } = options;
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;

  const headers: Record<string, string> = {};
  if (!isFormData) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Token ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body:
      body === undefined
        ? undefined
        : isFormData
          ? (body as FormData)
          : JSON.stringify(body),
  });

  const raw = await res.text();
  let data: unknown = null;
  if (raw) {
    try {
      data = JSON.parse(raw);
    } catch {
      data = raw;
    }
  }

  if (!res.ok) {
    const detail =
      data && typeof data === "object" && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : `Request failed (${res.status})`;
    throw new ApiError(detail, res.status);
  }
  return data as T;
}

// ===== Auth endpoints =====
export const requestOtp = (email: string) =>
  api<{ detail: string; email: string; dev_code?: string }>("/api/auth/request-otp/", {
    method: "POST",
    body: { email },
  });

export const verifyOtp = (email: string, code: string) =>
  api<{ token: string; role: Role; is_staff: boolean; broker: Broker }>(
    "/api/auth/verify-otp/",
    { method: "POST", body: { email, code } }
  );

// ===== Project & inventory endpoints =====
export const fetchProjects = (token: string) => api<Project[]>("/api/projects/", { token });

export const fetchProject = (token: string, id: number | string) =>
  api<Project>(`/api/projects/${id}/`, { token });

// ===== Broker profile =====
export const fetchMe = (token: string) => api<Broker>("/api/me/", { token });

export const updateMe = (token: string, payload: Partial<Broker>) =>
  api<Broker>("/api/me/", { method: "PATCH", body: payload, token });

// ===== Customers =====
export type Customer = {
  id: number;
  name: string;
  email: string;
  phone: string;
  address: string;
  created_at: string;
};

export const fetchCustomers = (token: string) => api<Customer[]>("/api/customers/", { token });

export const createCustomer = (token: string, payload: Partial<Customer>) =>
  api<Customer>("/api/customers/", { method: "POST", body: payload, token });

// ===== Bookings =====
export type Booking = {
  id: number;
  broker: number;
  broker_name: string;
  customer: number;
  customer_name: string;
  plot: number;
  plot_details: Plot;
  token_amount: string;
  payment_mode: string;
  commission_pct: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  decided_at: string | null;
  commission: number | null;
};

export const fetchBookings = (token: string) => api<Booking[]>("/api/bookings/", { token });

export const createBooking = (
  token: string,
  payload: { customer: number; plot: number; token_amount: number; payment_mode: string }
) => api<Booking>("/api/bookings/", { method: "POST", body: payload, token });

// ===== Commissions =====
export type Commission = {
  id: number;
  booking: number;
  broker_id: number;
  broker_name: string;
  customer_name: string;
  plot_label: string;
  project_name: string;
  amount: string;
  tds_pct: string;
  tds_amount: string;
  net_amount: string;
  released: boolean;
  released_at: string | null;
  created_at: string;
};

export const fetchCommissions = (token: string) => api<Commission[]>("/api/commissions/", { token });

// ===== Administration =====
export type AdminStats = {
  brokers: number;
  kyc_pending: number;
  kyc_approved: number;
  projects: number;
  plots: number;
  available_plots: number;
  on_hold_plots: number;
  sold_plots: number;
  pending_bookings: number;
  approved_bookings: number;
  rejected_bookings: number;
  commissions: number;
  unreleased_commissions: number;
};

export const fetchAdminStats = (token: string) => api<AdminStats>("/api/admin/stats/", { token });

export const fetchAdminBookings = (token: string, status?: string) =>
  api<Booking[]>(`/api/admin/bookings/${status ? `?status=${status}` : ""}`, { token });

export const decideBooking = (token: string, id: number, action: "approve" | "reject") =>
  api<Booking>(`/api/admin/bookings/${id}/decide/`, {
    method: "POST",
    body: { action },
    token,
  });

export const releaseCommission = (token: string, id: number) =>
  api<Commission>(`/api/admin/commissions/${id}/release/`, { method: "POST", token });

export const fetchAdminCommissions = (token: string) =>
  api<Commission[]>("/api/admin/commissions/", { token });

// ===== Documents =====
export type Document = {
  id: number;
  kind: string;
  kind_display: string;
  title: string;
  download_url: string;
  content_type: string;
  size_bytes: number;
  size_kb: number;
  booking: number | null;
  created_at: string;
};

export const fetchDocuments = (token: string, kind?: string) =>
  api<Document[]>(`/api/documents/${kind ? `?kind=${kind}` : ""}`, { token });

export const uploadKycDocument = (
  token: string,
  formData: FormData
): Promise<Document> =>
  api<Document>("/api/documents/", { method: "POST", body: formData, token });

export const deleteDocument = (token: string, id: number) =>
  api<void>(`/api/documents/${id}/`, { method: "DELETE", token });

export const generatePriceList = (token: string, projectId: number) =>
  api<Document>(`/api/projects/${projectId}/price-list/`, { method: "POST", token });

export const generateDemandLetter = (token: string, bookingId: number) =>
  api<Document>(`/api/bookings/${bookingId}/demand-letter/`, { method: "POST", token });

// ===== Notifications =====
export type Notification = {
  id: number;
  title: string;
  body: string;
  kind: string;
  kind_display: string;
  link: string;
  read: boolean;
  created_at: string;
};

export const fetchNotifications = (token: string, unreadOnly = false) =>
  api<Notification[]>(`/api/notifications/${unreadOnly ? "?unread=1" : ""}`, { token });

export const fetchUnreadCount = (token: string) =>
  api<{ unread: number }>("/api/notifications/unread-count/", { token });

export const markNotificationsRead = (token: string, ids?: number[]) =>
  api<{ marked_read: number }>("/api/notifications/mark-read/", {
    method: "POST",
    body: ids ? { ids } : {},
    token,
  });

// ===== Support =====
export type SupportTicket = {
  id: number;
  broker: number;
  broker_name: string;
  subject: string;
  message: string;
  status: "open" | "in_progress" | "resolved";
  priority: "low" | "normal" | "high";
  response: string;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
};

export type CompanyProfile = {
  name: string;
  support_email: string;
  support_phone: string;
  rm_name: string;
  rm_phone: string;
  rm_email: string;
};

export const fetchTickets = (token: string) =>
  api<SupportTicket[]>("/api/tickets/", { token });

export const createTicket = (
  token: string,
  payload: { subject: string; message: string; priority: string }
) => api<SupportTicket>("/api/tickets/", { method: "POST", body: payload, token });

export const fetchCompanyProfile = (token: string) =>
  api<CompanyProfile>("/api/company/", { token });

// ===== Administration extras =====
export type AuditEntry = {
  id: number;
  actor_name: string;
  action: string;
  entity_type: string;
  entity_id: string;
  details: Record<string, unknown>;
  created_at: string;
};

export const fetchAuditLog = (token: string) =>
  api<AuditEntry[]>("/api/admin/audit-log/", { token });

export const fetchAdminBrokers = (token: string) =>
  api<Broker[]>("/api/admin/brokers/", { token });

export const updateBrokerKyc = (token: string, id: number, kyc_status: string) =>
  api<Broker>("/api/admin/brokers/", {
    method: "POST",
    body: { id, kyc_status },
    token,
  });

export const fetchAdminTickets = (token: string, status?: string) =>
  api<SupportTicket[]>(`/api/admin/tickets/${status ? `?status=${status}` : ""}`, { token });

export const updateAdminTicket = (
  token: string,
  payload: { id: number; status: string; response?: string }
) => api<SupportTicket>("/api/admin/tickets/", { method: "POST", body: payload, token });

export const createProject = (
  token: string,
  payload: {
    name: string;
    code: string;
    location: string;
    status: string;
    description: string;
  }
) => api<Project>("/api/admin/projects/", { method: "POST", body: payload, token });

export const fetchAdminProjects = (token: string) =>
  api<Project[]>("/api/admin/projects/", { token });

export const updateProject = (
  token: string,
  id: number,
  payload: Partial<{
    name: string;
    code: string;
    location: string;
    status: string;
    description: string;
  }>
) => api<Project>(`/api/admin/projects/${id}/`, { method: "PATCH", body: payload, token });

export const deleteProject = (token: string, id: number) =>
  api<void>(`/api/admin/projects/${id}/`, { method: "DELETE", token });

export type PlotInput = {
  id?: number;
  plot_number: string;
  size_sq_yds: string;
  facing: string;
  status: string;
  bsp: string;
  plc_pct: string;
  discount_pct: string;
};

export const fetchAdminPlots = (token: string, projectId: number) =>
  api<PlotInput[]>(`/api/admin/projects/${projectId}/plots/`, { token });

export const createPlots = (token: string, projectId: number, plots: PlotInput[]) =>
  api<PlotInput[]>(`/api/admin/projects/${projectId}/plots/`, {
    method: "POST",
    body: { plots },
    token,
  });

export const updatePlot = (token: string, id: number, payload: Partial<PlotInput>) =>
  api<PlotInput>(`/api/admin/plots/${id}/`, { method: "PATCH", body: payload, token });

export const deletePlot = (token: string, id: number) =>
  api<void>(`/api/admin/plots/${id}/`, { method: "DELETE", token });

export const broadcastNotification = (
  token: string,
  payload: { title: string; body: string; kind: string; link?: string }
) =>
  api<{ sent: number }>("/api/admin/broadcast/", {
    method: "POST",
    body: payload,
    token,
  });

// ===== Formatting helpers =====
export function formatMoney(value: number | string | null | undefined): string {  if (value === null || value === undefined || value === "") return "—";
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(n)) return "—";
  return "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

export function formatDate(value: string | null): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}
