import type {
  AvailabilityRule,
  AvailabilityRuleCreate,
  Booking,
  BookingStatus,
  InstanceSettings,
  InstanceSettingsUpdate,
  LicenseStatus,
  Service,
  ServiceCreate,
  ServiceUpdate,
  TeamMember,
  TeamMemberCreate,
  TeamMemberUpdate,
  User,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api";

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignorieren – plain text body
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export const auth = {
  me: () => request<User>("/auth/me"),
  login: (email: string, password: string) =>
    request<User>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  setup: (email: string, password: string, display_name: string) =>
    request<User>("/auth/setup", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    }),
};

// ── Services ──────────────────────────────────────────────────────────────────

export const services = {
  list: () => request<Service[]>("/admin/services"),
  create: (data: ServiceCreate) =>
    request<Service>("/admin/services", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: ServiceUpdate) =>
    request<Service>(`/admin/services/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  delete: (id: string) => request<void>(`/admin/services/${id}`, { method: "DELETE" }),
};

// ── Team-Mitglieder ───────────────────────────────────────────────────────────

export const teamMembers = {
  list: () => request<TeamMember[]>("/admin/team-members"),
  create: (data: TeamMemberCreate) =>
    request<TeamMember>("/admin/team-members", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: string, data: TeamMemberUpdate) =>
    request<TeamMember>(`/admin/team-members/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  listRules: (memberId: string) =>
    request<AvailabilityRule[]>(
      `/admin/team-members/${memberId}/availability-rules`,
    ),
  createRule: (memberId: string, data: AvailabilityRuleCreate) =>
    request<AvailabilityRule>(
      `/admin/team-members/${memberId}/availability-rules`,
      { method: "POST", body: JSON.stringify(data) },
    ),
  deleteRule: (memberId: string, ruleId: string) =>
    request<void>(
      `/admin/team-members/${memberId}/availability-rules/${ruleId}`,
      { method: "DELETE" },
    ),
};

// ── Buchungen ─────────────────────────────────────────────────────────────────

export const bookings = {
  list: (status?: BookingStatus) =>
    request<Booking[]>(`/admin/bookings${status ? `?status=${status}` : ""}`),
  confirm: (id: string) =>
    request<Booking>(`/admin/bookings/${id}/confirm`, { method: "POST" }),
  cancel: (id: string) =>
    request<Booking>(`/admin/bookings/${id}/cancel`, { method: "POST" }),
  update: (id: string, data: { internal_notes?: string | null }) =>
    request<Booking>(`/admin/bookings/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

// ── Einstellungen ─────────────────────────────────────────────────────────────

export const settings = {
  get: () => request<InstanceSettings>("/admin/settings"),
  update: (data: InstanceSettingsUpdate) =>
    request<InstanceSettings>("/admin/settings", {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

// ── Lizenzstatus ──────────────────────────────────────────────────────────────

export const license = {
  status: () => request<LicenseStatus>("/license/status"),
};
