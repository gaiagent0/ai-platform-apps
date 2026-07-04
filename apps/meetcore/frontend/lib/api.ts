// Direct backend URL for client-side API calls.
// NEXT_PUBLIC_API_URL is baked in at build time by Next.js.
// Falls back to relative URLs (" ") when the env var is not set.
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

if (process.env.NODE_ENV === "development" && !process.env.NEXT_PUBLIC_API_URL) {
  console.warn(
    "[meetcore] NEXT_PUBLIC_API_URL is not set. API calls will go to the " +
    "same origin (Next.js dev server), which has no /api routes. " +
    "Set NEXT_PUBLIC_API_URL=http://localhost:5167 in your .env.local."
  );
}

export interface Meeting {
  id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at?: string;
  duration_seconds: number;
  transcript?: string;
  summary?: string;
  transcripts?: Array<{ id: string; text: string; timestamp?: string }>;
  action_items?: string[];
  topics?: string[];
  language: string;
}

export interface MeetingListItem {
  id: string;
  title: string;
  status: string;
  created_at: string;
  duration_seconds: number;
  has_transcript: boolean;
  has_summary: boolean;
}

export interface ChatResponse {
  answer: string;
  meeting_id: string;
  model_used: string;
}

/**
 * Generic API helper. Custom headers from options.headers are merged
 * with Content-Type: application/json. The spread order is fixed so
 * user-supplied headers always win without overwriting the defaults.
 */
async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const { headers: customHeaders, ...rest } = options || {};
  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...customHeaders,
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body || res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function fetchMeetings(): Promise<MeetingListItem[]> {
  return api<MeetingListItem[]>("/api/meetings/");
}

export async function getMeeting(id: string): Promise<Meeting> {
  return api<Meeting>(`/api/meetings/${id}`);
}

export async function createMeeting(title: string = "", language: string = "hu"): Promise<Meeting> {
  const formData = new URLSearchParams();
  formData.append("title", title);
  formData.append("language", language);
  return api<Meeting>("/api/meetings/", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });
}

export async function uploadRecording(meetingId: string, file: File): Promise<void> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/meetings/${meetingId}/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`Upload failed: ${res.status} ${body || res.statusText}`);
  }
}

export async function processMeeting(meetingId: string): Promise<void> {
  await api(`/api/meetings/${meetingId}/process`, { method: "POST" });
}

export async function deleteMeeting(id: string): Promise<void> {
  await api(`/api/meetings/${id}`, { method: "DELETE" });
}

export async function askQuestion(
  meetingId: string,
  question: string,
  model: string = "openrouter-default"
): Promise<ChatResponse> {
  const formData = new URLSearchParams();
  formData.append("meeting_id", meetingId);
  formData.append("question", question);
  formData.append("model", model);
  return api<ChatResponse>("/api/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });
}

export async function transcribeAudio(file: File, language: string = "hu"): Promise<{ text: string; segments: Array<{ start: number; end: number; text: string }> }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("language", language);
  const res = await fetch(`${API_BASE}/api/transcribe/`, { method: "POST", body: formData });
  if (!res.ok) throw new Error(`Transcribe failed: ${res.status}`);
  return res.json();
}
