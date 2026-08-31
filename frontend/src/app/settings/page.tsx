"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppNav } from "@/components/AppNav";
import { Me, getMe, loadToken, setOpenAIKey } from "@/lib/api";

export default function SettingsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [me, setMe] = useState<Me | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const t = loadToken();
    if (!t) {
      router.replace("/login");
      return;
    }
    setToken(t);
    getMe(t)
      .then(setMe)
      .catch(() => router.replace("/login"));
  }, [router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token || !me) return;
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      const res = await setOpenAIKey(token, me.workspace.id, apiKey);
      setSuccess(`Key saved (…${res.openai_key_last4})`);
      setApiKey("");
      const refreshed = await getMe(token);
      setMe(refreshed);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save key");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <AppNav />
      <main className="mx-auto max-w-xl px-6 py-10">
        <h1 className="text-2xl font-semibold text-ink">Settings</h1>
        <p className="mt-1 text-sm text-ink-secondary">
          Docutalk is free. Embeddings and chat use your OpenAI account.
        </p>

        <div className="surface-metal mt-8 p-6">
          <p className="text-sm text-ink-secondary">
            Signed in as <span className="font-medium text-ink">{me?.email}</span>
          </p>
          <p className="mt-2 text-sm text-ink-secondary">
            Current key:{" "}
            {me?.workspace.openai_key_last4
              ? `sk-…${me.workspace.openai_key_last4}`
              : "not configured"}
          </p>

          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <div>
              <label className="mb-1 block text-sm text-ink-secondary">
                OpenAI API key
              </label>
              <input
                className="input-metal"
                type="password"
                placeholder="sk-…"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                required
                minLength={10}
              />
            </div>
            {error && <p className="text-sm text-danger">{error}</p>}
            {success && <p className="text-sm text-success">{success}</p>}
            <button type="submit" className="btn-brand" disabled={loading}>
              {loading ? "Validating…" : "Save key"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
