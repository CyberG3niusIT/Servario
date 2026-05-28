"use client";

import { clsx } from "clsx";
import { AlertTriangle, XCircle } from "lucide-react";
import type { LicenseStatus } from "@/lib/types";

interface LicenseBannerProps {
  licenseStatus: LicenseStatus;
}

export function LicenseBanner({ licenseStatus }: LicenseBannerProps) {
  const { status, message, bookings_allowed } = licenseStatus;

  if (status === "active") return null;

  const isError = status === "invalid" || status === "revoked" || status === "expired";
  const isWarning =
    status === "grace" || status === "server_unreachable" || status === "missing";

  return (
    <div
      className={clsx(
        "flex items-start gap-3 px-4 py-3 text-sm",
        isError && "bg-red-50 border-b border-red-200 text-red-800",
        isWarning && "bg-yellow-50 border-b border-yellow-200 text-yellow-800",
      )}
    >
      {isError ? (
        <XCircle size={16} className="mt-0.5 shrink-0" />
      ) : (
        <AlertTriangle size={16} className="mt-0.5 shrink-0" />
      )}
      <div>
        <span className="font-medium">Lizenzhinweis:</span> {message}
        {!bookings_allowed && (
          <span className="ml-2 font-semibold">Neue Buchungen sind gesperrt.</span>
        )}
      </div>
    </div>
  );
}
