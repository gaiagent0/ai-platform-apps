"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  getMeeting,
  uploadRecording,
  processMeeting,
  askQuestion,
  deleteMeeting,
  type Meeting,
} from "@/lib/api";

// Inline SVG icons
const ICONS = {
  back: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/></svg>,
  upload: <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>,
  process: <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>,
  transcript: <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/></svg>,
  summary: <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  chat: <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  send: <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  trash: <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>,
};

type Tab = "transcript" | "summary" | "chat";

export default function MeetingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const meetingId = params.id as string;

  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<Tab>("transcript");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (meetingId) loadMeeting();
  }, [meetingId]);

  async function loadMeeting() {
    try {
      setLoading(true);
      const data = await getMeeting(meetingId);
      setMeeting(data);
    } catch (e) {
      console.error("Failed to load meeting", e);
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !meetingId) return;
    await uploadRecording(meetingId, file);
    loadMeeting();
  }

  async function handleProcess() {
    setProcessing(true);
    try {
      await processMeeting(meetingId);
      await loadMeeting();
    } finally {
      setProcessing(false);
    }
  }

  async function handleAsk() {
    if (!question.trim()) return;
    setChatLoading(true);
    try {
      const answerText = await askQuestion(meetingId, question);
      setAnswer(answerText);
    } finally {
      setChatLoading(false);
    }
  }

  async function handleDelete() {
    await deleteMeeting(meetingId);
    router.push("/");
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center text-slate-400">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-3"></div>
        Loading...
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <h2 className="text-xl font-semibold text-slate-700 dark:text-slate-300">Meeting not found</h2>
        <button onClick={() => router.push("/")} className="text-primary hover:underline mt-2">Back to meetings</button>
      </div>
    );
  }

  const tabs: { key: Tab; label: string; icon: JSX.Element }[] = [
    { key: "transcript", label: "Transcript", icon: ICONS.transcript },
    { key: "summary", label: "Summary", icon: ICONS.summary },
    { key: "chat", label: "Chat", icon: ICONS.chat },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/")}
            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors text-slate-500"
          >
            {ICONS.back}
          </button>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              {meeting.title || "Untitled Meeting"}
            </h1>
            <p className="text-sm text-slate-400">
              {new Date(meeting.created_at).toLocaleString("hu-HU")}
              {meeting.duration_seconds > 0 && ` · ${Math.round(meeting.duration_seconds / 60)} min`}
            </p>
          </div>
        </div>
        <button onClick={handleDelete} className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all" title="Delete">
          {ICONS.trash}
        </button>
      </div>

      {/* Actions */}
      <div className="flex gap-3 mb-6">
        <label className="inline-flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 cursor-pointer transition-all text-sm font-medium">
          {ICONS.upload}
          Upload Audio
          <input type="file" accept="audio/*" onChange={handleUpload} className="hidden" />
        </label>
        {meeting.file_path && (
          <button
            onClick={handleProcess}
            disabled={processing}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-primary text-white rounded-xl hover:bg-primary/90 disabled:opacity-50 transition-all text-sm font-medium"
          >
            {processing ? (
              <><div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div> Processing...</>
            ) : (
              <>{ICONS.process} Process</>
            )}
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 p-1 bg-slate-100 dark:bg-slate-800/50 rounded-xl">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.key
                ? "bg-white dark:bg-slate-700 text-primary shadow-sm"
                : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white dark:bg-slate-800/30 rounded-2xl border border-slate-200 dark:border-slate-700/50 p-6 min-h-[300px]">
        {activeTab === "transcript" && (
          <div>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">Transcript</h2>
            {meeting.transcript ? (
              <div className="prose prose-slate dark:prose-invert max-w-none">
                <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">{meeting.transcript}</p>
              </div>
            ) : (
              <p className="text-slate-400 italic">No transcript yet. Upload audio and process the meeting.</p>
            )}
          </div>
        )}

        {activeTab === "summary" && (
          <div>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">Summary</h2>
            {meeting.summary ? (
              <div className="prose prose-slate dark:prose-invert max-w-none">
                <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">{meeting.summary}</p>
              </div>
            ) : (
              <p className="text-slate-400 italic">No summary yet. Process the meeting to generate a summary.</p>
            )}
            {meeting.action_items && meeting.action_items.length > 0 && (
              <div className="mt-6">
                <h3 className="font-semibold text-slate-900 dark:text-white mb-2">Action Items</h3>
                <ul className="space-y-1">
                  {meeting.action_items.map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-slate-700 dark:text-slate-300">
                      <span className="text-primary mt-1">&#8226;</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === "chat" && (
          <div>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">Ask about this meeting</h2>
            {!meeting.transcript ? (
              <p className="text-slate-400 italic">No transcript available yet. Process the meeting first.</p>
            ) : (
              <>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAsk()}
                    placeholder="Ask about the meeting..."
                    className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all"
                  />
                  <button
                    onClick={handleAsk}
                    disabled={chatLoading || !question.trim()}
                    className="px-4 py-2.5 bg-primary text-white rounded-xl hover:bg-primary/90 disabled:opacity-50 transition-all"
                  >
                    {chatLoading ? <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div> : ICONS.send}
                  </button>
                </div>
                {answer && (
                  <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
                    <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">{answer}</p>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
