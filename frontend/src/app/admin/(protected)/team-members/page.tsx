"use client";

import { useEffect, useState } from "react";
import { Plus, Pencil, ChevronDown, ChevronUp, Trash2 } from "lucide-react";
import { teamMembers as tmApi, services as servicesApi, ApiError } from "@/lib/api";
import type { AvailabilityRule, Service, TeamMember } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";

const DAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
const DAY_FULL = [
  "Montag", "Dienstag", "Mittwoch", "Donnerstag",
  "Freitag", "Samstag", "Sonntag",
];

type MemberForm = {
  display_name: string;
  email: string;
  bio: string;
  is_active: boolean;
  service_ids: string[];
};

const EMPTY_FORM: MemberForm = {
  display_name: "", email: "", bio: "", is_active: true, service_ids: [],
};

function memberToForm(m: TeamMember): MemberForm {
  return {
    display_name: m.display_name,
    email: m.email ?? "",
    bio: m.bio ?? "",
    is_active: m.is_active,
    service_ids: m.service_ids ?? [],
  };
}

export default function TeamMembersPage() {
  const [items, setItems] = useState<TeamMember[]>([]);
  const [allServices, setAllServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<TeamMember | null>(null);
  const [form, setForm] = useState<MemberForm>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [rulesMap, setRulesMap] = useState<Record<string, AvailabilityRule[]>>({});

  async function load() {
    setLoading(true);
    try {
      const [members, svcs] = await Promise.all([tmApi.list(), servicesApi.list()]);
      setItems(members);
      setAllServices(svcs);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function toggleExpand(id: string) {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(id);
    if (!rulesMap[id]) {
      const rules = await tmApi.listRules(id);
      setRulesMap((m) => ({ ...m, [id]: rules }));
    }
  }

  async function handleDeleteRule(memberId: string, ruleId: string) {
    if (!confirm("Regel löschen?")) return;
    await tmApi.deleteRule(memberId, ruleId);
    setRulesMap((m) => ({
      ...m,
      [memberId]: m[memberId].filter((r) => r.id !== ruleId),
    }));
  }

  function openCreate() {
    setEditTarget(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  }

  function openEdit(m: TeamMember) {
    setEditTarget(m);
    setForm(memberToForm(m));
    setFormError(null);
    setModalOpen(true);
  }

  function toggleService(id: string) {
    setForm((f) => ({
      ...f,
      service_ids: f.service_ids.includes(id)
        ? f.service_ids.filter((s) => s !== id)
        : [...f.service_ids, id],
    }));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    setSaving(true);
    const payload = {
      display_name: form.display_name,
      email: form.email || null,
      bio: form.bio || null,
      is_active: form.is_active,
      service_ids: form.service_ids,
    };
    try {
      if (editTarget) {
        const updated = await tmApi.update(editTarget.id, payload);
        setItems((prev) => prev.map((m) => (m.id === editTarget.id ? updated : m)));
      } else {
        const created = await tmApi.create(payload);
        setItems((prev) => [...prev, created]);
      }
      setModalOpen(false);
    } catch (e) {
      setFormError(e instanceof ApiError ? e.detail : "Fehler beim Speichern");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">Team-Mitglieder</h1>
        <Button onClick={openCreate}>
          <Plus size={14} /> Neues Mitglied
        </Button>
      </div>

      {loading ? (
        <p className="text-sm text-gray-500">Wird geladen …</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-500">Noch keine Team-Mitglieder angelegt.</p>
      ) : (
        <div className="space-y-2">
          {items.map((m) => (
            <div key={m.id} className="rounded-lg border border-gray-200 bg-white overflow-hidden">
              {/* Kopfzeile */}
              <div className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-sm font-bold">
                    {m.display_name[0].toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{m.display_name}</p>
                    {m.email && (
                      <p className="text-xs text-gray-500">{m.email}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={m.is_active ? "green" : "gray"}>
                    {m.is_active ? "Aktiv" : "Inaktiv"}
                  </Badge>
                  <Button variant="ghost" size="sm" onClick={() => openEdit(m)}>
                    <Pencil size={13} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleExpand(m.id)}
                    aria-expanded={expandedId === m.id}
                  >
                    {expandedId === m.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </Button>
                </div>
              </div>

              {/* Verfügbarkeitsregeln */}
              {expandedId === m.id && (
                <div className="border-t border-gray-100 px-4 py-3 bg-gray-50">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                    Verfügbarkeitsregeln
                  </p>
                  {(rulesMap[m.id] ?? []).length === 0 ? (
                    <p className="text-sm text-gray-400">Keine Regeln hinterlegt.</p>
                  ) : (
                    <div className="space-y-1">
                      {(rulesMap[m.id] ?? []).map((r) => (
                        <div
                          key={r.id}
                          className="flex items-center justify-between text-sm text-gray-700"
                        >
                          <span>
                            <span className="font-medium w-12 inline-block">
                              {DAY_FULL[r.day_of_week]}
                            </span>{" "}
                            {r.start_time} – {r.end_time}
                          </span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteRule(m.id, r.id)}
                          >
                            <Trash2 size={12} className="text-red-400" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                  <AddRuleInline
                    memberId={m.id}
                    onAdded={(rule) =>
                      setRulesMap((prev) => ({
                        ...prev,
                        [m.id]: [...(prev[m.id] ?? []), rule],
                      }))
                    }
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modal: Erstellen / Bearbeiten */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editTarget ? "Mitglied bearbeiten" : "Neues Mitglied"}
      >
        <form onSubmit={handleSave} className="flex flex-col gap-4">
          <Input
            id="display_name"
            label="Name *"
            required
            value={form.display_name}
            onChange={(e) => setForm((f) => ({ ...f, display_name: e.target.value }))}
          />
          <Input
            id="email"
            label="E-Mail"
            type="email"
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
          />
          <Input
            id="bio"
            label="Bio"
            value={form.bio}
            onChange={(e) => setForm((f) => ({ ...f, bio: e.target.value }))}
          />

          {allServices.length > 0 && (
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Leistungen zuweisen</p>
              <div className="space-y-1">
                {allServices.map((s) => (
                  <label key={s.id} className="flex items-center gap-2 text-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.service_ids.includes(s.id)}
                      onChange={() => toggleService(s.id)}
                      className="rounded border-gray-300"
                    />
                    {s.name}
                  </label>
                ))}
              </div>
            </div>
          )}

          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
              className="rounded border-gray-300"
            />
            Mitglied ist aktiv
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

// ── Inline-Regel-Hinzufügen ────────────────────────────────────────────────────

function AddRuleInline({
  memberId,
  onAdded,
}: {
  memberId: string;
  onAdded: (rule: AvailabilityRule) => void;
}) {
  const [open, setOpen] = useState(false);
  const [day, setDay] = useState("0");
  const [start, setStart] = useState("09:00");
  const [end, setEnd] = useState("17:00");
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      const rule = await tmApi.createRule(memberId, {
        day_of_week: parseInt(day, 10),
        start_time: start,
        end_time: end,
      });
      onAdded(rule);
      setOpen(false);
    } finally {
      setSaving(false);
    }
  }

  if (!open) {
    return (
      <button
        className="mt-2 text-xs text-brand-600 hover:underline"
        onClick={() => setOpen(true)}
      >
        + Regel hinzufügen
      </button>
    );
  }

  return (
    <div className="mt-3 flex flex-wrap items-end gap-2">
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-500">Tag</label>
        <select
          value={day}
          onChange={(e) => setDay(e.target.value)}
          className="rounded border border-gray-300 px-2 py-1 text-sm"
        >
          {DAYS.map((d, i) => (
            <option key={i} value={i}>{d}</option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-500">Von</label>
        <input
          type="time"
          value={start}
          onChange={(e) => setStart(e.target.value)}
          className="rounded border border-gray-300 px-2 py-1 text-sm"
        />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-500">Bis</label>
        <input
          type="time"
          value={end}
          onChange={(e) => setEnd(e.target.value)}
          className="rounded border border-gray-300 px-2 py-1 text-sm"
        />
      </div>
      <Button size="sm" disabled={saving} onClick={save}>
        {saving ? "…" : "Hinzufügen"}
      </Button>
      <Button size="sm" variant="ghost" onClick={() => setOpen(false)}>
        Abbrechen
      </Button>
    </div>
  );
}
