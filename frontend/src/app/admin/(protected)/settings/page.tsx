"use client";

import { useEffect, useState } from "react";
import { settings as settingsApi } from "@/lib/api";
import type { InstanceSettings, InstanceSettingsUpdate } from "@/lib/types";

export default function SettingsPage() {
  const [data, setData] = useState<InstanceSettings | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // SMTP-Passwort wird separat gehalten und nie vom Server zurückgegeben
  const [smtpPassword, setSmtpPassword] = useState("");

  useEffect(() => {
    settingsApi.get().then(setData).catch(() => setError("Einstellungen konnten nicht geladen werden."));
  }, []);

  if (!data) {
    return (
      <div className="p-8 text-zinc-500">
        {error ?? "Lade Einstellungen …"}
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    const form = e.currentTarget;
    const fd = new FormData(form);

    const update: InstanceSettingsUpdate = {
      business_name: fd.get("business_name") as string || null,
      business_email: fd.get("business_email") as string || null,
      business_phone: fd.get("business_phone") as string || null,
      business_address: fd.get("business_address") as string || null,
      booking_page_title: fd.get("booking_page_title") as string || null,
      booking_page_description: fd.get("booking_page_description") as string || null,
      timezone: fd.get("timezone") as string || "UTC",
      smtp_host: fd.get("smtp_host") as string || null,
      smtp_port: fd.get("smtp_port") ? Number(fd.get("smtp_port")) : null,
      smtp_user: fd.get("smtp_user") as string || null,
    };

    if (smtpPassword) {
      update.smtp_password = smtpPassword;
    }

    try {
      const updated = await settingsApi.update(update);
      setData(updated);
      setSmtpPassword("");
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Fehler beim Speichern.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-semibold mb-6">Einstellungen</h1>

      {error && (
        <div className="mb-4 rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 rounded-md bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
          Einstellungen gespeichert.
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Geschäftsdaten */}
        <section>
          <h2 className="text-base font-semibold mb-4 pb-2 border-b border-zinc-200">
            Geschäftsdaten
          </h2>
          <div className="grid gap-4">
            <Field label="Name des Unternehmens" name="business_name" defaultValue={data.business_name ?? ""} />
            <Field label="E-Mail" name="business_email" type="email" defaultValue={data.business_email ?? ""} />
            <Field label="Telefon" name="business_phone" defaultValue={data.business_phone ?? ""} />
            <TextareaField label="Adresse" name="business_address" defaultValue={data.business_address ?? ""} />
          </div>
        </section>

        {/* Buchungsseite */}
        <section>
          <h2 className="text-base font-semibold mb-4 pb-2 border-b border-zinc-200">
            Buchungsseite
          </h2>
          <div className="grid gap-4">
            <Field label="Seitentitel" name="booking_page_title" defaultValue={data.booking_page_title ?? ""} />
            <TextareaField
              label="Beschreibung"
              name="booking_page_description"
              defaultValue={data.booking_page_description ?? ""}
            />
            <Field label="Zeitzone" name="timezone" defaultValue={data.timezone} placeholder="z.B. Europe/Berlin" />
          </div>
        </section>

        {/* SMTP */}
        <section>
          <h2 className="text-base font-semibold mb-4 pb-2 border-b border-zinc-200">
            E-Mail (SMTP)
          </h2>
          {data.smtp_configured && (
            <p className="text-sm text-green-700 bg-green-50 rounded-md px-3 py-2 mb-4">
              SMTP ist konfiguriert. Passwortfeld leer lassen, um es nicht zu ändern.
            </p>
          )}
          <div className="grid gap-4">
            <Field label="SMTP-Host" name="smtp_host" defaultValue={data.smtp_host ?? ""} placeholder="smtp.beispiel.de" />
            <Field label="SMTP-Port" name="smtp_port" type="number" defaultValue={String(data.smtp_port ?? 587)} />
            <Field label="Benutzername" name="smtp_user" defaultValue={data.smtp_user ?? ""} />
            <div className="grid gap-1.5">
              <label className="text-sm font-medium text-zinc-700">
                Passwort {data.smtp_configured && <span className="text-zinc-400 font-normal">(leer = unverändert)</span>}
              </label>
              <input
                type="password"
                autoComplete="new-password"
                className="border border-zinc-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={smtpPassword}
                onChange={(e) => setSmtpPassword(e.target.value)}
              />
            </div>
          </div>
        </section>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium px-5 py-2.5 rounded-md transition-colors"
          >
            {saving ? "Wird gespeichert …" : "Speichern"}
          </button>
        </div>
      </form>
    </div>
  );
}

function Field({
  label,
  name,
  defaultValue = "",
  type = "text",
  placeholder,
}: {
  label: string;
  name: string;
  defaultValue?: string;
  type?: string;
  placeholder?: string;
}) {
  return (
    <div className="grid gap-1.5">
      <label htmlFor={name} className="text-sm font-medium text-zinc-700">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        defaultValue={defaultValue}
        placeholder={placeholder}
        className="border border-zinc-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
}

function TextareaField({
  label,
  name,
  defaultValue = "",
}: {
  label: string;
  name: string;
  defaultValue?: string;
}) {
  return (
    <div className="grid gap-1.5">
      <label htmlFor={name} className="text-sm font-medium text-zinc-700">
        {label}
      </label>
      <textarea
        id={name}
        name={name}
        defaultValue={defaultValue}
        rows={3}
        className="border border-zinc-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
      />
    </div>
  );
}
