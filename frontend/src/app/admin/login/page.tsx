"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { auth, ApiError } from "@/lib/api";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await auth.login(email, password);
      router.push("/admin/bookings");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.status === 401
          ? "E-Mail oder Passwort falsch."
          : err.status === 403
          ? "Account ist deaktiviert."
          : err.detail);
      } else {
        setError("Verbindung zum Server fehlgeschlagen.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Servario</h1>
          <p className="mt-1 text-sm text-gray-500">Anmelden</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 flex flex-col gap-4"
        >
          <Input
            id="email"
            label="E-Mail"
            type="email"
            required
            autoFocus
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            id="password"
            label="Passwort"
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && (
            <p className="text-sm text-red-600 bg-red-50 rounded-md px-3 py-2">
              {error}
            </p>
          )}

          <Button type="submit" disabled={loading} className="w-full justify-center">
            {loading ? "Wird angemeldet …" : "Anmelden"}
          </Button>
        </form>

        <p className="mt-4 text-center text-xs text-gray-400">
          Noch kein Account?{" "}
          <a href="/setup" className="text-brand-600 hover:underline">
            Einrichtung starten
          </a>
        </p>
      </div>
    </div>
  );
}
