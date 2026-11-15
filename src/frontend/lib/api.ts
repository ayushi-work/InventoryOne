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
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Token ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
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
