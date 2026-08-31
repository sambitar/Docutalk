"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken } from "@/lib/api";

const links = [
  { href: "/dashboard", label: "Documents" },
  { href: "/chat", label: "Chat" },
  { href: "/settings", label: "Settings" },
];

export function AppNav() {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    clearToken();
    router.push("/login");
  }

  return (
    <header className="border-b border-metal-subtle bg-surface/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/dashboard" className="text-lg font-semibold text-ink">
          Docutalk
        </Link>
        <nav className="flex items-center gap-1">
          {links.map((l) => {
            const active = pathname === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  active ? "bg-brand-subtle text-brand" : "text-ink-secondary hover:text-ink"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
          <button type="button" onClick={logout} className="btn-metal ml-2 !px-3 !py-1.5 text-xs">
            Log out
          </button>
        </nav>
      </div>
    </header>
  );
}
