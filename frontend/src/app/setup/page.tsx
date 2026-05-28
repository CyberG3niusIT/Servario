"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api";
import { ApiError } from "@/lib/api";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export default function SetupPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    display_name: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await auth.setup(form.email, form.password, form.display_name);
      router.push("/admin/login");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.status === 409
          ? "Einrichtung bereits abgeschlossen. Bitte melde dich an."
          : err.detail);
      } else {
        setError("Unbekannter Fehler.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Servario einrichten</h1>
          <p className="mt-2 text-sm text-gray-600">
            Erstelle den ersten Admin-Account.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 flex flex-col gap-4"
        >
          <Input
            id="display_name"
            label="Name"
            type="text"
            required
            autoFocus
            value={form.display_name}
            onChange={(e) => setForm((f) => ({ ...f, display_name: e.target.value }))}
          />
          <Input
            id="email"
            label="E-Mail"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
          />
          <Input
            id="password"
            label="Passwort"
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
          />

          {error && (
            <p className="text-sm text-red-600 bg-red-50 rounded-md px-3 py-2">
              {error}
            </p>
          )}

          <Button type="submit" disabled={loading} className="w-full justify-center">
            {loading ? "Wird eingerichtet …" : "Einrichtung abschließen"}
          </Button>
        </form>
      </div>
    </div>
  );
}
