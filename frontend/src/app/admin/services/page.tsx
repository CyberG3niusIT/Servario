"use client";

import { useEffect, useState } from "react";
import { Plus, Pencil, Trash2 } from "lucide-react";
import { services as servicesApi, ApiError } from "@/lib/api";
import type { Service, ServiceCreate } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";

type FormData = {
  name: string;
  description: string;
  duration_minutes: string;
  price_cents: string;
  currency: string;
  is_active: boolean;
};

const EMPTY_FORM: FormData = {
  name: "", description: "", duration_minutes: "60",
  price_cents: "", currency: "EUR", is_active: true,
};

function serviceToForm(s: Service): FormData {
  return {
    name: s.name,
    description: s.description ?? "",
    duration_minutes: String(s.duration_minutes),
    price_cents: s.price_cents != null ? String(s.price_cents) : "",
    currency: s.currency ?? "EUR",
    is_active: s.is_active,
  };
}

function formToPayload(f: FormData): ServiceCreate {
  return {
    name: f.name,
    description: f.description || null,
    duration_minutes: parseInt(f.duration_minutes, 10),
    price_cents: f.price_cents ? parseInt(f.price_cents, 10) : null,
    currency: f.price_cents ? f.currency || "EUR" : null,
    is_active: f.is_active,
  };
}

export default function ServicesPage() {
  const [items, setItems] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Service | null>(null);
  const [form, setForm] = useState<FormData>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function load() {
    setLoading(true);
    try { setItems(await servicesApi.list()); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  function openCreate() {
    setEditTarget(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  }

  function openEdit(s: Service) {
    setEditTarget(s);
    setForm(serviceToForm(s));
    setFormError(null);
    setModalOpen(true);
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    setSaving(true);
    try {
      if (editTarget) {
        const updated = await servicesApi.update(editTarget.id, formToPayload(form));
        setItems((prev) => prev.map((s) => (s.id === editTarget.id ? updated : s)));
      } else {
        const created = await servicesApi.create(formToPayload(form));
        setItems((prev) => [...prev, created]);
      }
      setModalOpen(false);
    } catch (e) {
      setFormError(e instanceof ApiError ? e.detail : "Speichern fehlgeschlagen");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(s: Service) {
    if (!confirm(`Leistung „${s.name}" wirklich löschen?`)) return;
    try {
      await servicesApi.delete(s.id);
      setItems((prev) => prev.filter((x) => x.id !== s.id));
    } catch (e) {
      alert(e instanceof ApiError ? e.detail : "Fehler beim Löschen");
    }
  }

  const field = (key: keyof FormData) => ({
    value: String(form[key]),
    onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value })),
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">Leistungen</h1>
        <Button onClick={openCreate}>
          <Plus size={14} /> Neue Leistung
        </Button>
      </div>

      {loading ? (
        <p className="text-sm text-gray-500">Wird geladen …</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-500">Noch keine Leistungen angelegt.</p>
      ) : (
        <div className="rounded-lg border border-gray-200 overflow-hidden bg-white">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Name</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Dauer</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Preis</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {items.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-900">{s.name}</td>
                  <td className="px-4 py-3 text-gray-600">{s.duration_minutes} Min.</td>
                  <td className="px-4 py-3 text-gray-600">
                    {s.price_cents != null
                      ? `${(s.price_cents / 100).toFixed(2)} ${s.currency ?? "EUR"}`
                      : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={s.is_active ? "green" : "gray"}>
                      {s.is_active ? "Aktiv" : "Inaktiv"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-2">
                      <Button variant="ghost" size="sm" onClick={() => openEdit(s)}>
                        <Pencil size={13} />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(s)}>
                        <Trash2 size={13} className="text-red-500" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editTarget ? "Leistung bearbeiten" : "Neue Leistung"}
      >
        <form onSubmit={handleSave} className="flex flex-col gap-4">
          <Input id="name" label="Name *" required {...field("name")} />
          <Input id="description" label="Beschreibung" {...field("description")} />
          <div className="grid grid-cols-2 gap-3">
            <Input
              id="duration"
              label="Dauer (Minuten) *"
              type="number"
              min={5}
              required
              {...field("duration_minutes")}
            />
            <Input
              id="price"
              label="Preis (Cent)"
              type="number"
              min={0}
              placeholder="z.B. 5000"
              {...field("price_cents")}
            />
          </div>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
              className="rounded border-gray-300"
            />
            Leistung ist buchbar (aktiv)
          </label>

          {formError && (
            <p className="text-sm text-red-600 bg-red-50 rounded px-3 py-2">{formError}</p>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="secondary" type="button" onClick={() => setModalOpen(false)}>
              Abbrechen
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Wird gespeichert …" : "Speichern"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
