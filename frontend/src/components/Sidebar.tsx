"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clsx } from "clsx";
import {
  CalendarDays,
  Layers,
  Settings,
  Users,
  ShieldCheck,
  LogOut,
} from "lucide-react";
import { auth } from "@/lib/api";

const navItems = [
  { href: "/admin/bookings",     label: "Buchungen",      icon: CalendarDays },
  { href: "/admin/services",     label: "Leistungen",     icon: Layers },
  { href: "/admin/team-members", label: "Team",           icon: Users },
  { href: "/admin/settings",     label: "Einstellungen",  icon: Settings },
  { href: "/admin/license",      label: "Lizenz",         icon: ShieldCheck },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  async function handleLogout() {
    try {
      await auth.logout();
    } finally {
      router.push("/admin/login");
    }
  }

  return (
    <aside className="flex h-full w-56 flex-col bg-gray-900 text-gray-100">
      {/* Logo */}
      <div className="flex h-14 items-center px-5 border-b border-gray-700">
        <span className="text-lg font-bold tracking-tight text-white">Servario</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-0.5">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              pathname.startsWith(href)
                ? "bg-brand-600 text-white"
                : "text-gray-400 hover:bg-gray-800 hover:text-white",
            )}
          >
            <Icon size={16} />
            {label}
          </Link>
        ))}
      </nav>

      {/* Abmelden */}
      <div className="border-t border-gray-700 p-2">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut size={16} />
          Abmelden
        </button>
      </div>
    </aside>
  );
}
