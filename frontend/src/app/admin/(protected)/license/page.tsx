"use client";

import { useEffect, useState } from "react";
import { RefreshCw, ShieldCheck, ShieldAlert, ShieldX, ShieldOff } from "lucide-react";
import { license as licenseApi, ApiError } from "@/lib/api";
import type { LicenseStatus, LicenseStatusValue } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

type BadgeVariant = "green" | "yellow" | "red" | "gray" | "orange" | "blue";

const STATUS_INFO: Record<
  LicenseStatusValue,
  { label: string; variant: BadgeVariant; icon: React.ReactNode; description: string }
> = {
  active: {
    label: "Aktiv",
    variant: "green",
    icon: <ShieldCheck size={20} className="text-green-600" />,
    description: "Lizenz ist gültig und aktiv. Alle Funktionen sind verfügbar.",
  },
  missing: {
    label: "Keine Lizenz",
    variant: "yellow",
    icon: <ShieldOff size={20} className="text-yellow-600" />,
    description:
      "Kein Lizenzschlüssel konfiguriert. Demo/Evaluierungsmodus aktiv (begrenzte Funktionen).",
  },
  invalid: {
    label: "Ungültig",
    variant: "red",
    icon: <ShieldX size={20} className="text-red-600" />,
    description:
      "Die Lizenz konnte nicht verifiziert werden. Neue Buchungen sind gesperrt. " +
      "Kein Demo-Fallback verfügbar.",
  },
  expired: {
    label: "Abgelaufen",
    variant: "red",
    icon: <ShieldAlert size={20} className="text-red-600" />,
    description: "Die Lizenz ist abgelaufen und die Nachfrist ist verstrichen.",
  },
  grace: {
    label: "Nachfrist",
    variant: "orange",
    icon: <ShieldAlert size={20} className="text-orange-500" />,
    description:
      "Lizenz abgelaufen, Betrieb aber noch innerhalb der Nachfrist möglich. " +
      "Bitte erneuere die Lizenz.",
  },
  revoked: {
    label: "Widerrufen",
    variant: "red",
    icon: <ShieldX size={20} className="text-red-600" />,
    description: "Die Lizenz wurde vom Aussteller widerrufen. Neue Buchungen sind gesperrt.",
  },
  server_unreachable: {
    label: "Server nicht erreichbar",
    variant: "orange",
    icon: <ShieldAlert size={20} className="text-orange-500" />,
    description:
      "Online-Validierung konnte nicht durchgeführt werden. " +
      "Betrieb läuft bis Ablauf der Nachfrist weiter.",
  },
};

const EDITION_LABELS: Record<string, string> = {
  starter:      "Starter",
  professional: "Professional",
  business:     "Business",
};

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("de-DE", {
    day: "2-digit", month: "long", year: "numeric",
  });
}

function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start gap-4 py-3 border-b border-gray-100 last:border-0">
      <span className="w-44 shrink-0 text-sm text-gray-500">{label}</span>
      <span className="text-sm text-gray-900">{value}</span>
    </div>
  );
}

export default function LicensePage() {
  const [status, setStatus] = useState<LicenseStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setStatus(await licenseApi.status());
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Fehler beim Laden");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  if (loading) {
    return <p className="text-sm text-gray-500">Wird geladen …</p>;
  }

  if (error || !status) {
    return (
      <p className="text-sm text-red-600 bg-red-50 rounded px-3 py-2">
        {error ?? "Unbekannter Fehler"}
      </p>
    );
  }

  const info = STATUS_INFO[status.status];

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">Lizenzstatus</h1>
        <Button variant="ghost" size="sm" onClick={load} disabled={loading}>
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Aktualisieren
        </Button>
      </div>

      {/* Status-Karte */}
      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="flex items-center gap-3 mb-4">
          {info.icon}
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-900">{info.label}</span>
              <Badge variant={info.variant}>{info.label}</Badge>
            </div>
            <p className="text-sm text-gray-600 mt-0.5">{info.description}</p>
          </div>
        </div>

        <div className="divide-y divide-gray-100">
          <InfoRow label="Buchungen erlaubt" value={
            status.bookings_allowed
              ? <Badge variant="green">Ja</Badge>
              : <Badge variant="red">Nein</Badge>
          } />
          <InfoRow
            label="Edition"
            value={
              status.edition
                ? EDITION_LABELS[status.edition] ?? status.edition
                : "Demo/Eval (keine Lizenz)"
            }
          />
          <InfoRow label="Ablaufdatum" value={formatDate(status.expires_at)} />
          <InfoRow label="Nachfrist bis" value={formatDate(status.grace_until)} />
          <InfoRow
            label="Instanz-ID"
            value={
              <code className="text-xs bg-gray-100 rounded px-1.5 py-0.5 font-mono">
                {status.instance_id}
              </code>
            }
          />
        </div>
      </div>

      {/* Demo-Limits (nur wenn status = missing) */}
      {status.status === "missing" && (
        <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-5">
          <h2 className="font-semibold text-yellow-900 mb-3">Demo-/Evaluierungsgrenzen</h2>
          <div className="space-y-1 text-sm text-yellow-800">
            <p>• Max. 5 Buchungen</p>
            <p>• Max. 2 Mitarbeiter</p>
            <p>• Max. 3 Leistungen</p>
            <p>• 30 Tage ab Erststart</p>
          </div>
          {status.demo_limits_reached && (
            <p className="mt-3 font-semibold text-red-700">
              Demo-Grenzen erreicht — keine neuen Buchungen möglich.
            </p>
          )}
          <p className="mt-4 text-sm text-yellow-700">
            Um Servario produktiv zu nutzen, wird ein gültiger Lizenzschlüssel benötigt.
            Konfiguriere die Umgebungsvariable{" "}
            <code className="font-mono bg-yellow-100 px-1 rounded">SERVARIO_LICENSE_KEY</code>.
          </p>
        </div>
      )}

      {/* Systeminformation */}
      {status.message && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3">
          <p className="text-xs font-semibold text-gray-500 uppercase mb-1">Systemmeldung</p>
          <p className="text-sm text-gray-700">{status.message}</p>
        </div>
      )}
    </div>
  );
}
