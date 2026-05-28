// ── Benutzer ──────────────────────────────────────────────────────────────────
export type UserRole = "owner" | "admin" | "staff";

export interface User {
  id: string;
  email: string;
  display_name: string;
  role: UserRole;
  is_active: boolean;
}

// ── Service ───────────────────────────────────────────────────────────────────
export interface Service {
  id: string;
  name: string;
  description: string | null;
  duration_minutes: number;
  price: string | null;   // Decimal-Wert als String (z.B. "49.90")
  currency: string | null;
  is_active: boolean;
}

export interface ServiceCreate {
  name: string;
  description?: string | null;
  duration_minutes: number;
  price?: string | null;
  currency?: string | null;
  is_active?: boolean;
}

export interface ServiceUpdate extends Partial<ServiceCreate> {}

// ── Team-Mitglied ─────────────────────────────────────────────────────────────
export interface TeamMember {
  id: string;
  display_name: string;
  email: string | null;
  bio: string | null;
  is_active: boolean;
  user_id: string | null;
}

export interface TeamMemberCreate {
  display_name: string;
  email?: string | null;
  bio?: string | null;
  is_active?: boolean;
  service_ids?: string[];
}

export interface TeamMemberUpdate extends Partial<TeamMemberCreate> {}

export interface AvailabilityRule {
  id: string;
  team_member_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_active: boolean;
}

export interface AvailabilityRuleCreate {
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_active?: boolean;
}

// ── Buchung ───────────────────────────────────────────────────────────────────
export type BookingStatus = "pending" | "confirmed" | "cancelled" | "completed";

export interface Booking {
  id: string;
  service_id: string;
  team_member_id: string;
  customer_id: string;
  start_at: string;
  end_at: string;
  status: BookingStatus;
  customer_notes: string | null;
  internal_notes: string | null;
}

// ── Öffentliche Buchung ───────────────────────────────────────────────────────
export interface AvailabilitySlot {
  start_at: string;
  end_at: string;
}

export interface PublicBookingCreate {
  service_id: string;
  team_member_id: string;
  start_at: string;
  customer_name: string;
  customer_email?: string | null;
  customer_phone?: string | null;
  customer_notes?: string | null;
}

// ── Lizenzstatus ──────────────────────────────────────────────────────────────
export type LicenseStatusValue =
  | "missing"
  | "invalid"
  | "active"
  | "expired"
  | "grace"
  | "revoked"
  | "server_unreachable";

export type LicenseEdition = "starter" | "professional" | "business";

export interface LicenseStatus {
  status: LicenseStatusValue;
  edition: LicenseEdition | null;
  max_staff: number | null;
  max_services: number | null;
  expires_at: string | null;
  grace_until: string | null;
  message: string;
  bookings_allowed: boolean;
  instance_id: string;
  demo_limits_reached: boolean;
}
