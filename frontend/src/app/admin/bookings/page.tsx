"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, X, RefreshCw } from "lucide-react";
import { bookings as bookingsApi, ApiError } from "@/lib/api";
import type { Booking, BookingStatus } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

const STATUS_LABELS: Record<BookingStatus, string> = {
  pending:   "Ausstehend",
  confirmed: "Bestätigt",
  cancelled: "Storniert",
  completed: "Abgeschlossen",
};

const STATUS_BADGE: Record<BookingStatus, "yellow" | "green" | "gray" | "blue"> = {
  pending:   "yellow",
  confirmed: "green",
  cancelled: "gray",
  completed: "blue",
};

const FILTERS: Array<{ label: string; value: BookingStatus | "" }> = [
  { label: "Alle", value: "" },
  { label: "Ausstehend", value: "pending" },
  { label: "Bestätigt", value: "confirmed" },
  { label: "Storniert", value: "cancelled" },
  { label: "Abgeschlossen", value: "completed" },
];

function formatDt(iso: string) {
  return new Date(iso).toLocaleString("de-DE", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

export default function BookingsPage() {
  const [filter, setFilter] = useState<BookingStatus | "">("");
  const [items, setItems] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await bookingsApi.list(filter || undefined);
      setItems(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Ladefehler");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  async function handleConfirm(id: string) {
    setActionId(id);
    try {
      const updated = await bookingsApi.confirm(id);
      setItems((prev) => prev.map((b) => (b.id === id ? updated : b)));
    } catch (e) {
      alert(e instanceof ApiError ? e.detail : "Fehler");
    } finally {
      setActionId(null);
    }
  }

  async function handleCancel(id: string) {
    if (!confirm("Buchung wirklich stornieren?")) return;
    setActionId(id);
    try {
      const updated = await bookingsApi.cancel(id);
      setItems((prev) => prev.map((b) => (b.id === id ? updated : b)));
    } catch (e) {
      alert(e instanceof ApiError ? e.detail : "Fehler");
    } finally {
      setActionId(null);
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">Buchungen</h1>
        <Button variant="ghost" size="sm" onClick={load} disabled={loading}>
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Aktualisieren
        </Button>
      </div>

      {/* Filter-Tabs */}
      <div className="flex gap-1 border-b border-gray-200 pb-0">
        {FILTERS.map(({ label, value }) => (
          <button
            key={value}
            onClick={() => setFilter(value)}
            className={`px-3 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
              filter === value
                ? "border-brand-600 text-brand-700"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 rounded-md px-3 py-2">{error}</p>
      )}

      {loading && items.length === 0 ? (
        <p className="text-sm text-gray-500">Wird geladen …</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-500">Keine Buchungen gefunden.</p>
      ) : (
        <div className="rounded-lg border border-gray-200 overflow-hidden bg-white">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Datum &amp; Zeit</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Buchungs-ID</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Aktionen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {items.map((b) => (
                <tr key={b.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-900 tabular-nums">
                    {formatDt(b.start_at)}
                    <span className="text-gray-400 mx-1">–</span>
                    {new Date(b.end_at).toLocaleTimeString("de-DE", {
                      hour: "2-digit", minute: "2-digit",
                    })}
                  </td>
                  <td className="px-4 py-3 text-gray-400 font-mono text-xs">
                    {b.id.slice(0, 8)}…
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={STATUS_BADGE[b.status]}>
                      {STATUS_LABELS[b.status]}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      {b.status === "pending" && (
                        <Button
                          variant="secondary"
                          size="sm"
                          disabled={actionId === b.id}
                          onClick={() => handleConfirm(b.id)}
                        >
                          <Check size={12} />
                          Bestätigen
                        </Button>
                      )}
                      {(b.status === "pending" || b.status === "confirmed") && (
                        <Button
                          variant="danger"
                          size="sm"
                          disabled={actionId === b.id}
                          onClick={() => handleCancel(b.id)}
                        >
                          <X size={12} />
                          Stornieren
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
