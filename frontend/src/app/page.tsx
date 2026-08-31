"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10"
        style={{ background: "var(--gradient-hero)" }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 top-10 h-72 w-72 rounded-full opacity-30 blur-3xl"
        style={{ background: "var(--color-brand-subtle)" }}
      />

      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
        <span className="text-lg font-semibold tracking-tight text-ink">Docutalk</span>
        <nav className="flex items-center gap-3">
          <Link href="/login" className="btn-metal">
            Log in
          </Link>
          <Link href="/register" className="btn-brand">
            Get started
          </Link>
        </nav>
      </header>

      <section className="mx-auto flex max-w-5xl flex-col px-6 pb-24 pt-16 md:pt-28">
        <h1 className="max-w-2xl text-5xl font-semibold tracking-tight text-ink md:text-6xl">
          Docutalk
        </h1>
        <p className="mt-5 max-w-xl text-lg text-ink-secondary">
          Ask your documents anything. Free multi-tenant RAG — bring your own OpenAI
          key; we never bill for tokens.
        </p>
        <div className="mt-10 flex flex-wrap gap-3">
          <Link href="/register" className="btn-brand">
            Create free account
          </Link>
          <Link href="/login" className="btn-metal">
            Sign in
          </Link>
        </div>
        <div
          className="mt-16 h-48 w-full max-w-3xl rounded-2xl border border-metal-border shadow-metal"
          style={{ background: "var(--gradient-metal)" }}
        />
      </section>
    </main>
  );
}
