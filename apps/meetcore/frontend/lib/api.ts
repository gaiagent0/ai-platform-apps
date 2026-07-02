const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5167";

export interface Meeting {
  id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
  duration_seconds: number;
  transcript?: string;
  summary?: string;
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

export async function fetchMeetings(): Promise<MeetingListItem[]> {
  const res = await fetch(`${API_BASE}/api/meetings/`);
  if (!res.ok) throw new Error("Failed to fetch meetings");
  return res.json();
}

export async function createMeeting(title: string): Promise<Meeting> {
  const formData = new FormData();
  formData.append("title", title);
  const res = await fetch(`${API_BASE}/api/meetings/`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to create meeting");
  return res.json();
}

export async function getMeeting(id: string): Promise<Meeting> {
  const res = await fetch(`${API_BASE}/api/meetings/${id}`);
  if (!res.ok) throw new Error("Meeting not found");
  return res.json();
}

export async function uploadRecording(meetingId: string, file: File): Promise<Meeting> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/meetings/${meetingId}/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to upload recording");
  return res.json();
}

export async function processMeeting(meetingId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/meetings/${meetingId}/process`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to process meeting");
  return res.json();
}

export async function deleteMeeting(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/meetings/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete meeting");
}

export async function askQuestion(meetingId: string, question: string): Promise<string> {
  const formData = new FormData();
  formData.append("meeting_id", meetingId);
  formData.append("question", question);
  const res = await fetch(`${API_BASE}/api/chat/`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to get answer");
  const data = await res.json();
  return data.answer;
}
