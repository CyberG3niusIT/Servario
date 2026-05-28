"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronLeft, Check, CalendarDays, Clock, User, Layers } from "lucide-react";
import { publicApi, ApiError } from "@/lib/publicApi";
import type { AvailabilitySlot, Service, TeamMember } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";

// ── Typen ─────────────────────────────────────────────────────────────────────

type Step = "service" | "member" | "date" | "slot" | "details";

interface WizardState {
  service: Service | null;
  member: TeamMember | null;
  date: string;          // YYYY-MM-DD
  slot: AvailabilitySlot | null;
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  customerNotes: string;
}

const INITIAL: WizardState = {
  service: null, member: null, date: "", slot: null,
  customerName: "", customerEmail: "", customerPhone: "", customerNotes: "",
};

// ── Hilfsfunktionen ───────────────────────────────────────────────────────────

function todayIso(): string {
  return new Date().toISOString().split("T")[0];
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
}

function formatDate(iso: string): string {
  return new Date(iso + "T00:00:00").toLocaleDateString("de-DE", {
    weekday: "long", day: "numeric", month: "long", year: "numeric",
  });
}

function formatPrice(s: Service): string | null {
  if (!s.price) return null;
  return `${parseFloat(s.price).toFixed(2)} ${s.currency ?? "EUR"}`;
}

// ── Fortschrittsanzeige ───────────────────────────────────────────────────────

const STEPS: { key: Step; label: string; icon: React.ReactNode }[] = [
  { key: "service", label: "Leistung",   icon: <Layers size={14} /> },
  { key: "member",  label: "Mitarbeiter", icon: <User size={14} /> },
  { key: "date",    label: "Datum",       icon: <CalendarDays size={14} /> },
  { key: "slot",    label: "Uhrzeit",     icon: <Clock size={14} /> },
  { key: "details", label: "Kontakt",     icon: <Check size={14} /> },
];

function StepIndicator({ current }: { current: Step }) {
  const idx = STEPS.findIndex((s) => s.key === current);
  return (
    <div className="flex items-center gap-0 mb-8">
      {STEPS.map((s, i) => (
        <div key={s.key} className="flex items-center">
          <div
            className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-medium transition-colors ${
              i < idx
                ? "bg-brand-600 text-white"
                : i === idx
                ? "bg-brand-600 text-white ring-2 ring-brand-200"
                : "bg-gray-200 text-gray-500"
            }`}
          >
            {i < idx ? <Check size={12} /> : i + 1}
          </div>
          <span
            className={`ml-1.5 text-xs hidden sm:inline ${
              i === idx ? "text-brand-700 font-medium" : "text-gray-400"
            }`}
          >
            {s.label}
          </span>
          {i < STEPS.length - 1 && (
            <div
              className={`h-px w-6 mx-2 ${i < idx ? "bg-brand-400" : "bg-gray-200"}`}
            />
          )}
        </div>
      ))}
    </div>
  );
}

// ── Karten-Auswahl ────────────────────────────────────────────────────────────

function SelectCard({
  title, subtitle, badge, onClick, selected,
}: {
  title: string;
  subtitle?: string | null;
  badge?: string | null;
  onClick: () => void;
  selected?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-xl border p-4 transition-all hover:border-brand-400 hover:shadow-sm ${
        selected
          ? "border-brand-500 bg-brand-50 shadow-sm"
          : "border-gray-200 bg-white"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-medium text-gray-900">{title}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
        {badge && <span className="text-sm text-gray-500 shrink-0">{badge}</span>}
      </div>
    </button>
  );
}

// ── Hauptkomponente ───────────────────────────────────────────────────────────

export default function BookPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("service");
  const [state, setState] = useState<WizardState>(INITIAL);

  const [services, setServices] = useState<Service[]>([]);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Leistungen beim Start laden
  useEffect(() => {
    setLoading(true);
    publicApi.listServices()
      .then(setServices)
      .catch((e) => setError(e instanceof ApiError ? e.detail : "Ladefehler"))
      .finally(() => setLoading(false));
  }, []);

  // Mitarbeiter laden wenn Leistung gewählt
  useEffect(() => {
    if (!state.service) return;
    setLoading(true);
    setError(null);
    publicApi.listTeamMembers(state.service.id)
      .then((m) => {
        setMembers(m);
        // Wenn nur ein Mitarbeiter → automatisch wählen und weiter
        if (m.length === 1) {
          setState((s) => ({ ...s, member: m[0] }));
          setStep("date");
        }
      })
      .catch((e) => setError(e instanceof ApiError ? e.detail : "Ladefehler"))
      .finally(() => setLoading(false));
  }, [state.service]);

  // Slots laden wenn Datum gewählt
  const loadSlots = useCallback(async (date: string) => {
    if (!state.service || !state.member) return;
    setLoading(true);
    setError(null);
    try {
      const data = await publicApi.getAvailability(state.service.id, state.member.id, date);
      setSlots(data);
      if (data.length === 0) setError("Für diesen Tag sind keine Termine verfügbar.");
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Ladefehler");
    } finally {
      setLoading(false);
    }
  }, [state.service, state.member]);

  useEffect(() => {
    if (step === "slot" && state.date) loadSlots(state.date);
  }, [step, state.date, loadSlots]);

  // ── Schritte ────────────────────────────────────────────────────────────────

  function selectService(s: Service) {
    setState({ ...INITIAL, service: s });
    setMembers([]);
    setSlots([]);
    setError(null);
    setStep("member");
  }

  function selectMember(m: TeamMember) {
    setState((prev) => ({ ...prev, member: m, date: "", slot: null }));
    setSlots([]);
    setError(null);
    setStep("date");
  }

  function selectDate(date: string) {
    setState((prev) => ({ ...prev, date, slot: null }));
    setSlots([]);
    setError(null);
    setStep("slot");
  }

  function selectSlot(slot: AvailabilitySlot) {
    setState((prev) => ({ ...prev, slot }));
    setError(null);
    setStep("details");
  }

  function back() {
    setError(null);
    const order: Step[] = ["service", "member", "date", "slot", "details"];
    const idx = order.indexOf(step);
    if (idx > 0) setStep(order[idx - 1]);
  }

  async function submitBooking(e: React.FormEvent) {
    e.preventDefault();
    if (!state.service || !state.member || !state.slot) return;
    setError(null);
    setSubmitting(true);
    try {
      const booking = await publicApi.createBooking({
        service_id: state.service.id,
        team_member_id: state.member.id,
        start_at: state.slot.start_at,
        customer_name: state.customerName,
        customer_email: state.customerEmail || null,
        customer_phone: state.customerPhone || null,
        customer_notes: state.customerNotes || null,
      });
      router.push(`/book/confirmation/${booking.id}`);
    } catch (e) {
      if (e instanceof ApiError) {
        if (e.status === 409) {
          setError("Dieser Termin wurde soeben von jemand anderem gebucht. Bitte wähle eine andere Zeit.");
          setStep("slot");
        } else if (e.status === 402) {
          setError("Das Buchungssystem ist im Demo-Modus. Bitte kontaktiere den Betreiber.");
        } else {
          setError(e.detail);
        }
      } else {
        setError("Unbekannter Fehler beim Senden.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  // ── Zusammenfassungs-Sidebar ──────────────────────────────────────────────

  function Summary() {
    if (!state.service) return null;
    return (
      <div className="mb-6 rounded-xl border border-brand-100 bg-brand-50 px-4 py-3 text-sm space-y-1">
        <p><span className="text-gray-500">Leistung:</span>{" "}
          <span className="font-medium text-gray-900">{state.service.name}</span>
          {" "}({state.service.duration_minutes} Min.)
        </p>
        {state.member && (
          <p><span className="text-gray-500">Mitarbeiter:</span>{" "}
            <span className="font-medium text-gray-900">{state.member.display_name}</span>
          </p>
        )}
        {state.date && (
          <p><span className="text-gray-500">Datum:</span>{" "}
            <span className="font-medium text-gray-900">{formatDate(state.date)}</span>
          </p>
        )}
        {state.slot && (
          <p><span className="text-gray-500">Uhrzeit:</span>{" "}
            <span className="font-medium text-gray-900">
              {formatTime(state.slot.start_at)} – {formatTime(state.slot.end_at)}
            </span>
          </p>
        )}
      </div>
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div>
      <StepIndicator current={step} />

      {step !== "service" && (
        <button
          onClick={back}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <ChevronLeft size={14} /> Zurück
        </button>
      )}

      {step !== "service" && <Summary />}

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Schritt 1: Leistung wählen */}
      {step === "service" && (
        <div className="space-y-3">
          <h1 className="text-xl font-semibold text-gray-900 mb-4">Leistung wählen</h1>
          {loading && <p className="text-sm text-gray-500">Wird geladen …</p>}
          {!loading && services.length === 0 && !error && (
            <p className="text-sm text-gray-500">Keine Leistungen verfügbar.</p>
          )}
          {services.map((s) => (
            <SelectCard
              key={s.id}
              title={s.name}
              subtitle={s.description}
              badge={formatPrice(s) ?? `${s.duration_minutes} Min.`}
              onClick={() => selectService(s)}
              selected={state.service?.id === s.id}
            />
          ))}
        </div>
      )}

      {/* Schritt 2: Mitarbeiter wählen */}
      {step === "member" && (
        <div className="space-y-3">
          <h1 className="text-xl font-semibold text-gray-900 mb-4">Mitarbeiter wählen</h1>
          {loading && <p className="text-sm text-gray-500">Wird geladen …</p>}
          {!loading && members.length === 0 && !error && (
            <p className="text-sm text-gray-500">Keine Mitarbeiter verfügbar.</p>
          )}
          {members.map((m) => (
            <SelectCard
              key={m.id}
              title={m.display_name}
              subtitle={m.bio}
              onClick={() => selectMember(m)}
              selected={state.member?.id === m.id}
            />
          ))}
        </div>
      )}

      {/* Schritt 3: Datum wählen */}
      {step === "date" && (
        <div className="space-y-4">
          <h1 className="text-xl font-semibold text-gray-900 mb-4">Datum wählen</h1>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <Input
              id="date"
              label="Wunschdatum"
              type="date"
              min={todayIso()}
              value={state.date}
              onChange={(e) => setState((s) => ({ ...s, date: e.target.value, slot: null }))}
            />
            <Button
              className="mt-4"
              disabled={!state.date}
              onClick={() => state.date && selectDate(state.date)}
            >
              Verfügbare Zeiten anzeigen
            </Button>
          </div>
        </div>
      )}

      {/* Schritt 4: Uhrzeit wählen */}
      {step === "slot" && (
        <div className="space-y-3">
          <h1 className="text-xl font-semibold text-gray-900 mb-4">
            Uhrzeit wählen
            <span className="block text-sm font-normal text-gray-500 mt-1">
              {state.date && formatDate(state.date)}
            </span>
          </h1>
          {loading && <p className="text-sm text-gray-500">Verfügbare Zeiten werden geladen …</p>}
          {!loading && slots.length === 0 && !error && (
            <p className="text-sm text-gray-500">Keine freien Termine an diesem Tag.</p>
          )}
          <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
            {slots.map((s) => (
              <button
                key={s.start_at}
                onClick={() => selectSlot(s)}
                className={`rounded-lg border py-2.5 text-sm font-medium transition-colors ${
                  state.slot?.start_at === s.start_at
                    ? "border-brand-500 bg-brand-50 text-brand-700"
                    : "border-gray-200 bg-white hover:border-brand-300 hover:bg-brand-50"
                }`}
              >
                {formatTime(s.start_at)}
              </button>
            ))}
          </div>
          {state.slot && (
            <Button
              className="mt-2"
              onClick={() => setStep("details")}
            >
              Weiter
            </Button>
          )}
        </div>
      )}

      {/* Schritt 5: Kontaktdaten */}
      {step === "details" && (
        <div>
          <h1 className="text-xl font-semibold text-gray-900 mb-4">Deine Kontaktdaten</h1>
          <form onSubmit={submitBooking} className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
            <Input
              id="name"
              label="Name *"
              required
              autoFocus
              value={state.customerName}
              onChange={(e) => setState((s) => ({ ...s, customerName: e.target.value }))}
            />
            <Input
              id="email"
              label="E-Mail"
              type="email"
              value={state.customerEmail}
              onChange={(e) => setState((s) => ({ ...s, customerEmail: e.target.value }))}
            />
            <Input
              id="phone"
              label="Telefon"
              type="tel"
              value={state.customerPhone}
              onChange={(e) => setState((s) => ({ ...s, customerPhone: e.target.value }))}
            />
            <div className="flex flex-col gap-1">
              <label htmlFor="notes" className="text-sm font-medium text-gray-700">
                Anmerkungen
              </label>
              <textarea
                id="notes"
                rows={3}
                className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                value={state.customerNotes}
                onChange={(e) => setState((s) => ({ ...s, customerNotes: e.target.value }))}
              />
            </div>

            <p className="text-xs text-gray-400">
              Deine Daten werden ausschließlich zur Buchungsabwicklung verwendet.
            </p>

            <Button
              type="submit"
              disabled={submitting || !state.customerName}
              className="w-full justify-center"
            >
              {submitting ? "Buchung wird gesendet …" : "Termin verbindlich buchen"}
            </Button>
          </form>
        </div>
      )}
    </div>
  );
}
