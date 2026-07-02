
import { useEffect, useState } from "react";
import { fetchMeetings, createMeeting, deleteMeeting, type MeetingListItem } from "@/lib/api";
import Link from "next/link";

const ICONS = {
  plus: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><path d="M12 8v8" /><path d="M8 12h8" />
    </svg>
  ),
  mic: (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line x1="12" x2="12" y1="19" y2="22" />
    </svg>
  ),
  check: (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  ),
  trash: (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
    </svg>
  ),
};

const STATUS_COLORS: Record<string, string> = {
  completed: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  transcribed: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  summarized: "bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400",
  recording: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  processing: "bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function HomePage() {
  const [meetings, setMeetings] = useState<MeetingListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTitle, setNewTitle] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => { loadMeetings(); }, []);

  async function loadMeetings() {
    try {
      setLoading(true);
      const data = await fetchMeetings();
      setMeetings(data);
    } catch (e) {
      console.error("Failed to load meetings", e);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate() {
    if (!newTitle.trim()) return;
    await createMeeting(newTitle);
    setNewTitle("");
    setShowCreate(false);
    loadMeetings();
  }

  async function handleDelete(id: string) {
    await deleteMeeting(id);
    loadMeetings();
  }

  function statusBadge(status: string) {
    const colorClass = STATUS_COLORS[status] || "bg-gray-100 text-gray-700";
    return (
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
        {status}
      </span>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <header className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            MeetCore
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Meeting recording and AI summarization
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-primary text-white rounded-xl hover:bg-primary/90 transition-all shadow-lg shadow-primary/20 font-medium"
        >
          {ICONS.plus}
          New Meeting
        </button>
      </header>

      {/* Create Meeting Card */}
      {showCreate && (
        <div className="mb-6 p-5 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <h3 className="font-medium text-slate-900 dark:text-white mb-3">Create New Meeting</h3>
          <div className="flex gap-3">
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
              placeholder="Meeting title..."
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all"
              autoFocus
            />
            <button
              onClick={handleCreate}
              className="px-5 py-2.5 bg-primary text-white rounded-xl hover:bg-primary/90 transition-all font-medium"
            >
              Create
            </button>
          </div>
        </div>
      )}

      {/* Meetings List */}
      {loading ? (
        <div className="text-center py-16 text-slate-400">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-3"></div>
          Loading meetings...
        </div>
      ) : meetings.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
            {ICONS.mic}
          </div>
          <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-1">
            No meetings yet
          </h3>
          <p className="text-slate-400 dark:text-slate-500 mb-4">
            Create your first meeting to get started
          </p>
          <button
            onClick={() => setShowCreate(true)}
            className="text-primary hover:underline font-medium"
          >
            Create a meeting
          </button>
        </div>
      ) : (
        <div className="grid gap-3">
          {meetings.map((meeting) => (
            <Link
              key={meeting.id}
              href={`/meeting/${meeting.id}`}
              className="group flex items-center justify-between p-4 bg-white dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700/50 hover:border-primary/30 hover:shadow-md transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary group-hover:bg-primary/20 transition-colors">
                  {ICONS.mic}
                </div>
                <div>
                  <h3 className="font-medium text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                    {meeting.title || "Untitled Meeting"}
                  </h3>
                  <p className="text-sm text-slate-400 dark:text-slate-500">
                    {new Date(meeting.created_at).toLocaleString("hu-HU")}
                    {meeting.duration_seconds > 0 && ` · ${Math.round(meeting.duration_seconds / 60)} min`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {meeting.has_summary && (
                  <span className="text-emerald-500" title="Has summary">{ICONS.check}</span>
                )}
                {statusBadge(meeting.status)}
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    handleDelete(meeting.id);
                  }}
                  className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                  title="Delete"
                >
                  {ICONS.trash}
                </button>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
PAGEEOF
echo 'page.tsx done'
