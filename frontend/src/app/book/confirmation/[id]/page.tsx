import { CheckCircle, CalendarDays, Clock, XCircle } from "lucide-react";
import type { Booking, BookingStatus } from "@/lib/types";

// Server-Komponente: lädt Buchung direkt vom Backend

const BACKEND = process.env.BACKEND_URL ?? "http://backend:8000";
const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api";

async function fetchBooking(id: string): Promise<Booking | null> {
  try {
    const res = await fetch(`${BACKEND}/api/public/bookings/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

const STATUS_LABELS: Record<BookingStatus, string> = {
  pending:   "Ausstehend – wir melden uns in Kürze",
  confirmed: "Bestätigt",
  cancelled: "Storniert",
  completed: "Abgeschlossen",
};

function formatDt(iso: string) {
  return new Date(iso).toLocaleString("de-DE", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString("de-DE", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function ConfirmationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const booking = await fetchBooking(id);

  if (!booking) {
    return (
      <div className="text-center py-16">
        <XCircle className="mx-auto text-red-400 mb-4" size={48} />
        <h1 className="text-xl font-semibold text-gray-900 mb-2">
          Buchung nicht gefunden
        </h1>
        <p className="text-sm text-gray-500 mb-6">
          Die Buchungs-ID ist ungültig oder die Buchung wurde gelöscht.
        </p>
        <a
          href="/book"
          className="text-sm text-brand-600 hover:underline font-medium"
        >
          Neuen Termin buchen
        </a>
      </div>
    );
  }

  const isCancelled = booking.status === "cancelled";

  return (
    <div className="text-center">
      {isCancelled ? (
        <XCircle className="mx-auto text-red-400 mb-4" size={56} />
      ) : (
        <CheckCircle className="mx-auto text-green-500 mb-4" size={56} />
      )}

      <h1 className="text-2xl font-bold text-gray-900 mb-2">
        {isCancelled ? "Buchung storniert" : "Buchung erfolgreich!"}
      </h1>
      <p className="text-sm text-gray-500 mb-8">
        {STATUS_LABELS[booking.status]}
      </p>

      {/* Buchungsdetails */}
      <div className="bg-white rounded-xl border border-gray-200 text-left p-5 space-y-4 mb-6">
        <div className="flex items-start gap-3">
          <CalendarDays size={18} className="text-gray-400 mt-0.5 shrink-0" />
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-0.5">Datum &amp; Zeit</p>
            <p className="font-medium text-gray-900">{formatDt(booking.start_at)}</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Clock size={18} className="text-gray-400 mt-0.5 shrink-0" />
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-0.5">Dauer</p>
            <p className="font-medium text-gray-900">
              {formatTime(booking.start_at)} – {formatTime(booking.end_at)}
            </p>
          </div>
        </div>
        <div className="pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Buchungs-ID</p>
          <code className="text-xs font-mono bg-gray-100 rounded px-2 py-1 text-gray-700">
            {booking.id}
          </code>
        </div>
      </div>

      {!isCancelled && (
        <p className="text-sm text-gray-500 mb-6">
          Bitte speichere deine Buchungs-ID für eventuelle Rückfragen.
        </p>
      )}

      {booking.customer_notes && (
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 text-left mb-6">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Deine Anmerkung</p>
          <p className="text-sm text-gray-700">{booking.customer_notes}</p>
        </div>
      )}

      <a
        href="/book"
        className="text-sm text-brand-600 hover:underline font-medium"
      >
        Weiteren Termin buchen
      </a>
    </div>
  );
}
