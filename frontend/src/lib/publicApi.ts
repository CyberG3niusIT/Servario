import type {
  AvailabilitySlot,
  Booking,
  PublicBookingCreate,
  Service,
  TeamMember,
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

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail ?? detail; } catch { /* ignorieren */ }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail ?? detail; } catch { /* ignorieren */ }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export const publicApi = {
  listServices: () =>
    get<Service[]>("/public/services"),

  listTeamMembers: (serviceId: string) =>
    get<TeamMember[]>(`/public/services/${serviceId}/team-members`),

  getAvailability: (serviceId: string, teamMemberId: string, date: string) =>
    get<AvailabilitySlot[]>(
      `/public/availability?service_id=${serviceId}&team_member_id=${teamMemberId}&date=${date}`,
    ),

  createBooking: (data: PublicBookingCreate) =>
    post<Booking>("/public/bookings", data),

  getBooking: (id: string) =>
    get<Booking>(`/public/bookings/${id}`),
};
