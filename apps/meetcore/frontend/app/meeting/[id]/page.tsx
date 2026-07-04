"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { getMeeting, uploadRecording, processMeeting, askQuestion, deleteMeeting, type Meeting } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useTheme } from "@/hooks/useTheme";
import { AudioRecorder } from "@/components/meeting/AudioRecorder";

const STATUS_MAP: Record<string, { label: string; variant: "default" | "success" | "warning" | "recording" | "destructive" | "secondary" }> = {
  recording: { label: "Rögzítés", variant: "recording" },
  processing: { label: "Feldolgozás", variant: "warning" },
  transcribed: { label: "Lefordítva", variant: "success" },
  summarized: { label: "Összefoglalva", variant: "default" },
  completed: { label: "Kész", variant: "success" },
  failed: { label: "Hiba", variant: "destructive" },
};

export default function MeetingDetailPage() {
  const { theme, toggleTheme } = useTheme();
  const params = useParams();
  const router = useRouter();
  const meetingId = params.id as string;

  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [question, setQuestion] = useState("");
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState("");

  const loadMeeting = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getMeeting(meetingId);
      setMeeting(data);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Hiba a betöltés során");
    } finally {
      setLoading(false);
    }
  }, [meetingId]);

  useEffect(() => { loadMeeting(); }, [loadMeeting]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadRecording(meetingId, file);
      await loadMeeting();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Hiba a feltöltés során");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleProcess = async () => {
    setProcessing(true);
    try {
      await processMeeting(meetingId);
      await loadMeeting();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Hiba a feldolgozás során");
    } finally {
      setProcessing(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    setChatLoading(true);
    try {
      const res = await askQuestion(meetingId, question);
      setChatAnswer(res.answer);
    } catch (e) {
      setChatAnswer("Hiba: " + (e instanceof Error ? e.message : "ismeretlen hiba"));
    } finally {
      setChatLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Biztosan törölni szeretnéd?")) return;
    try {
      await deleteMeeting(meetingId);
      router.push("/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Hiba a törlés során");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-muted-foreground">Találkozó nem található</p>
        <Button variant="outline" onClick={() => router.push("/")}>Vissza</Button>
      </div>
    );
  }

  const s = STATUS_MAP[meeting.status] || { label: meeting.status, variant: "secondary" as const };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-md">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center gap-4">
          <button onClick={() => router.push("/")} className="p-2 rounded-lg hover:bg-muted transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/></svg>
          </button>
          <div className="flex-1 min-w-0">
            <h1 className="font-semibold truncate">{meeting.title || "Névtelen találkozó"}</h1>
          </div>
          <Badge variant={s.variant}>{s.label}</Badge>
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-muted transition-colors ml-2"
            title={theme === "dark" ? "Világos mód" : "Sötét mód"}
          >
            {theme === "dark" ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
            )}
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm dark:bg-red-950 dark:border-red-800 dark:text-red-300">
            {error}
          </div>
        )}

        {/* Action Bar */}
        <div className="flex flex-wrap items-center gap-3 mb-6">
          <label className="cursor-pointer">
            <input type="file" accept="audio/*,video/*" onChange={handleUpload} className="hidden" />
            <Button variant="outline" size="sm" disabled={uploading}>
              <span>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>
                </svg>
                {uploading ? "Feltöltés..." : "Fájl feltöltése"}
              </span>
            </Button>
          </label>
          <Button variant="outline" size="sm" onClick={handleProcess} disabled={processing}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1.5">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            {processing ? "Feldolgozás..." : "Feldolgozás"}
          </Button>
          <div className="flex-1" />
          <Button variant="destructive" size="sm" onClick={handleDelete}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1.5">
              <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
            </svg>
            Törlés
          </Button>
        </div>

        {/* Audio Recorder */}
        <div className="mb-6">
          <AudioRecorder
            onUpload={async (blob) => {
              const file = new File([blob], "recording.webm", { type: "audio/webm" });
              await uploadRecording(meetingId, file);
              await loadMeeting();
            }}
            disabled={uploading}
          />
        </div>

        {/* Tabs */}
        <Tabs defaultValue="transcript">
          <TabsList>
            <TabsTrigger value="transcript">Átirat</TabsTrigger>
            <TabsTrigger value="summary">Összefoglaló</TabsTrigger>
            <TabsTrigger value="chat">AI Chat</TabsTrigger>
          </TabsList>

          {/* Transcript Tab */}
          <TabsContent value="transcript">
            <Card>
              <CardHeader><CardTitle className="text-lg">Átirat</CardTitle></CardHeader>
              <CardContent>
                {meeting.transcript ? (
                  <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap leading-relaxed">
                    {meeting.transcript}
                  </div>
                ) : meeting.transcripts && meeting.transcripts.length > 0 ? (
                  <div className="space-y-4">
                    {meeting.transcripts.map((t, i) => (
                      <div key={t.id || i} className="text-sm leading-relaxed">
                        <span className="text-muted-foreground text-xs mr-2">[{t.timestamp || "--:--"}]</span>
                        {t.text}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <p>Még nincs átirat. Tölts fel egy hangfájlt és dolgozd fel.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Summary Tab */}
          <TabsContent value="summary">
            <Card>
              <CardHeader><CardTitle className="text-lg">Összefoglaló</CardTitle></CardHeader>
              <CardContent>
                {meeting.summary ? (
                  <div className="space-y-6">
                    <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap leading-relaxed">
                      {meeting.summary}
                    </div>
                    {meeting.action_items && meeting.action_items.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2">Tennivalók</h4>
                        <ul className="space-y-1.5">
                          {meeting.action_items.map((item, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary mt-0.5 shrink-0"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <p>Még nincs összefoglaló. Feldolgozással generálható.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat">
            <Card>
              <CardHeader><CardTitle className="text-lg">AI Chat</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Kérdezz a találkozóról..."
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleAsk()}
                      disabled={chatLoading}
                    />
                    <Button onClick={handleAsk} disabled={chatLoading || !question.trim()}>
                      {chatLoading ? (
                        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" x2="11" y1="2" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                      )}
                    </Button>
                  </div>
                  {chatAnswer && (
                    <div className="p-4 rounded-lg bg-muted/50 text-sm leading-relaxed whitespace-pre-wrap">
                      {chatAnswer}
                    </div>
                  )}
                  {!chatAnswer && !chatLoading && (
                    <div className="text-center py-8 text-muted-foreground text-sm">
                      <p>Kérdezhetsz a találkozó tartalmáról, döntésekről, tennivalókról.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
