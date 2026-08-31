"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppNav } from "@/components/AppNav";
import { ChatResponse, chat, getMe, loadToken } from "@/lib/api";

export default function ChatPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const t = loadToken();
    if (!t) {
      router.replace("/login");
      return;
    }
    setToken(t);
    getMe(t)
      .then((me) => setWorkspaceId(me.workspace.id))
      .catch(() => router.replace("/login"));
  }, [router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token || !workspaceId || !question.trim()) return;
    setError(null);
    setLoading(true);
    try {
      const res = await chat(token, workspaceId, question.trim());
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <AppNav />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="text-2xl font-semibold text-ink">Chat</h1>
        <p className="mt-1 text-sm text-ink-secondary">
          Answers are grounded in your uploaded documents.
        </p>

        <form onSubmit={onSubmit} className="surface-metal mt-8 space-y-4 p-6">
          <textarea
            className="input-metal min-h-28"
            placeholder="Ask a question about your documents…"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            required
          />
          {error && <p className="text-sm text-danger">{error}</p>}
          <button type="submit" className="btn-brand" disabled={loading}>
            {loading ? "Thinking…" : "Ask"}
          </button>
        </form>

        {result && (
          <section className="surface-metal mt-8 p-6">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-secondary">
              Answer
            </h2>
            <p className="mt-3 whitespace-pre-wrap text-ink">{result.answer}</p>
            {result.sources.length > 0 && (
              <div className="mt-6 border-t border-metal-subtle pt-4">
                <h3 className="text-sm font-semibold text-ink">Sources</h3>
                <ul className="mt-3 space-y-3">
                  {result.sources.map((s, i) => (
                    <li key={s.chunk_id} className="text-sm text-ink-secondary">
                      <span className="font-medium text-brand">[{i + 1}]</span>{" "}
                      {s.page != null ? `Page ${s.page} — ` : ""}
                      {s.snippet}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
