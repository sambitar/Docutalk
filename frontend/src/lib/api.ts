const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Workspace = {
  id: string;
  name: string;
  openai_key_last4: string | null;
  openai_key_validated_at: string | null;
};

export type Me = {
  id: string;
  email: string;
  workspace: Workspace;
};

export type Document = {
  id: string;
  title: string;
  source_filename: string;
  byte_size: number;
  created_at: string;
};

export type ChatResponse = {
  answer: string;
  sources: {
    chunk_id: string;
    document_id: string;
    page: number | null;
    snippet: string;
  }[];
};

function authHeaders(token: string | null): HeadersInit {
  const headers: HeadersInit = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data.detail === "string") return data.detail;
    return JSON.stringify(data.detail ?? data);
  } catch {
    return res.statusText;
  }
}

export async function register(email: string, password: string): Promise<string> {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  const data = await res.json();
  return data.access_token as string;
}

export async function login(email: string, password: string): Promise<string> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  const data = await res.json();
  return data.access_token as string;
}

export async function getMe(token: string): Promise<Me> {
  const res = await fetch(`${API_URL}/me`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function setOpenAIKey(
  token: string,
  workspaceId: string,
  apiKey: string
): Promise<{ openai_key_last4: string }> {
  const res = await fetch(`${API_URL}/workspaces/${workspaceId}/openai-key`, {
    method: "PUT",
    headers: { ...authHeaders(token), "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function listDocuments(token: string, workspaceId: string): Promise<Document[]> {
  const res = await fetch(`${API_URL}/workspaces/${workspaceId}/documents`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function uploadDocument(
  token: string,
  workspaceId: string,
  file: File
): Promise<Document> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/workspaces/${workspaceId}/documents`, {
    method: "POST",
    headers: authHeaders(token),
    body: form,
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function deleteDocument(
  token: string,
  workspaceId: string,
  documentId: string
): Promise<void> {
  const res = await fetch(`${API_URL}/workspaces/${workspaceId}/documents/${documentId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(await parseError(res));
}

export async function chat(
  token: string,
  workspaceId: string,
  question: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/workspaces/${workspaceId}/chat`, {
    method: "POST",
    headers: { ...authHeaders(token), "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export const TOKEN_KEY = "docutalk_token";

export function saveToken(token: string) {
  if (typeof window !== "undefined") localStorage.setItem(TOKEN_KEY, token);
}

export function loadToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  if (typeof window !== "undefined") localStorage.removeItem(TOKEN_KEY);
}
