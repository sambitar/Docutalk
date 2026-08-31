"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppNav } from "@/components/AppNav";
import {
  Document,
  deleteDocument,
  getMe,
  listDocuments,
  loadToken,
  uploadDocument,
} from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [docs, setDocs] = useState<Document[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const refresh = useCallback(async (t: string, wid: string) => {
    const list = await listDocuments(t, wid);
    setDocs(list);
  }, []);

  useEffect(() => {
    const t = loadToken();
    if (!t) {
      router.replace("/login");
      return;
    }
    setToken(t);
    getMe(t)
      .then(async (me) => {
        setWorkspaceId(me.workspace.id);
        await refresh(t, me.workspace.id);
      })
      .catch(() => {
        router.replace("/login");
      });
  }, [router, refresh]);

  async function onUpload(file: File | null) {
    if (!file || !token || !workspaceId) return;
    setError(null);
    setUploading(true);
    try {
      await uploadDocument(token, workspaceId, file);
      await refresh(token, workspaceId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function onDelete(id: string) {
    if (!token || !workspaceId) return;
    setError(null);
    try {
      await deleteDocument(token, workspaceId, id);
      await refresh(token, workspaceId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  }

  return (
    <div className="min-h-screen">
      <AppNav />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <h1 className="text-2xl font-semibold text-ink">Documents</h1>
        <p className="mt-1 text-sm text-ink-secondary">
          Upload PDF, TXT, or Markdown. Max 20 docs, 10 MB each.
        </p>

        <div className="surface-metal mt-8 p-6">
          <label className="btn-metal cursor-pointer">
            {uploading ? "Uploading…" : "Upload file"}
            <input
              type="file"
              accept=".pdf,.txt,.md,.markdown"
              className="hidden"
              disabled={uploading}
              onChange={(e) => onUpload(e.target.files?.[0] ?? null)}
            />
          </label>
          {error && <p className="mt-3 text-sm text-danger">{error}</p>}
        </div>

        <ul className="mt-8 space-y-3">
          {docs.length === 0 && (
            <li className="text-sm text-ink-muted">No documents yet.</li>
          )}
          {docs.map((d) => (
            <li
              key={d.id}
              className="surface-metal flex items-center justify-between gap-4 px-4 py-3"
            >
              <div>
                <p className="font-medium text-ink">{d.title}</p>
                <p className="text-xs text-ink-secondary">
                  {d.source_filename} · {(d.byte_size / 1024).toFixed(1)} KB
                </p>
              </div>
              <button
                type="button"
                className="text-sm text-danger"
                onClick={() => onDelete(d.id)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
