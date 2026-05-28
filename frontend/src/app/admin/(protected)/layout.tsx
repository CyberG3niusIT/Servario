import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { LicenseBanner } from "@/components/LicenseBanner";
import type { LicenseStatus, User } from "@/lib/types";

const BACKEND = process.env.BACKEND_URL ?? "http://backend:8000";

async function fetchMe(): Promise<User | null> {
  try {
    const cookieStore = await cookies();
    const res = await fetch(`${BACKEND}/api/auth/me`, {
      headers: { cookie: cookieStore.toString() },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function fetchLicenseStatus(): Promise<LicenseStatus | null> {
  try {
    const res = await fetch(`${BACKEND}/api/license/status`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await fetchMe();
  if (!user) {
    redirect("/admin/login");
  }

  const licenseStatus = await fetchLicenseStatus();

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        {licenseStatus && licenseStatus.status !== "active" && (
          <LicenseBanner licenseStatus={licenseStatus} />
        )}
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
