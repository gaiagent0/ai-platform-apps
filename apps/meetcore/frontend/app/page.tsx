"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { fetchMeetings, createMeeting, deleteMeeting, type MeetingListItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { useTheme } from "@/hooks/useTheme";

const STATUS_MAP: Record<string, { label: string; variant: "default" | "success" | "warning" | "recording" | "destructive" | "secondary" }> = {
  recording: { label: "Rögzítés", variant: "recording" },
  processing: { label: "Feldolgozás", variant: "warning" },
  transcribed: { label: "Lefordítva", variant: "success" },
  summarized: { label: "Összefoglalva", variant: "default" },
  completed: { label: "Kész", variant: "success" },
  failed: { label: "Hiba", variant: "destructive" },
};

function StatusBadge({ status }: { status: string }) {
  const s = STATUS_MAP[status] || { label: status, variant: "secondary" as const };
  return <Badge variant={s.variant}>{s.label}</Badge>;
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("hu-HU", { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch { return iso; }
}

function formatDuration(seconds: number): string {
  if (!seconds) return "";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}p ${s}s` : `${s}s`;
}

export default function HomePage() {
  const { theme, toggleTheme } = useTheme();
  const [meetings, setMeetings] = useState<MeetingListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  const loadMeetings = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchMeetings();
      setMeetings(data);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Hiba a betöltés során");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadMeetings(); }, [loadMeetings]);

  const handleCreate = async () => {
    setCreating(true);
    try {
      await createMeeting(newTitle);
      setNewTitle("");
      setShowCreate(false);
      await loadMeetings();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Hiba a létrehozás során");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Biztosan törölni szeretnéd ezt a találkozót?")) return;
    try {
      await deleteMeeting(id);
      await loadMeetings();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Hiba a törlés során");
    }
  };

  const filtered = meetings.filter(m =>
    m.title.toLowerCase().includes(search.toLowerCase()) || m.id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-md">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" x2="12" y1="19" y2="22"/>
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">MeetCore</h1>
              <p className="text-xs text-muted-foreground -mt-0.5">AI Meeting Assistant</p>
            </div>
          </div>
          <Button onClick={() => setShowCreate(true)} size="sm">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1.5">
              <path d="M12 5v14"/><path d="M5 12h14"/>
            </svg>
            Új találkozó
          </Button>
                  <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-muted transition-colors"
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
        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <Input
              placeholder="Keresés találkozók között..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm dark:bg-red-950 dark:border-red-800 dark:text-red-300">
            {error}
            <button onClick={() => setError("")} className="ml-2 underline">Bezárás</button>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Empty State */}
        {!loading && filtered.length === 0 && (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-muted flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" x2="12" y1="19" y2="22"/>
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-1">
              {search ? "Nincs találat" : "Még nincsenek találkozók"}
            </h3>
            <p className="text-muted-foreground text-sm mb-6">
              {search ? "Próbálj meg más keresési kifejezést" : "Hozz létre az első találkozódat a gombbal"}
            </p>
            {!search && <Button onClick={() => setShowCreate(true)}>Új találkozó létrehozása</Button>}
          </div>
        )}

        {/* Meeting List */}
        {!loading && filtered.length > 0 && (
          <div className="grid gap-3">
            {filtered.map((m) => (
              <Link key={m.id} href={`/meeting/${m.id}`}>
                <Card className="group cursor-pointer hover:border-primary/50">
                  <CardContent className="p-4 sm:p-5">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                          <h3 className="font-semibold truncate group-hover:text-primary transition-colors">
                            {m.title || "Névtelen találkozó"}
                          </h3>
                          <StatusBadge status={m.status} />
                        </div>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
                            {formatDate(m.created_at)}
                          </span>
                          {m.duration_seconds > 0 && (
                            <span className="flex items-center gap-1">
                              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                              {formatDuration(m.duration_seconds)}
                            </span>
                          )}
                          <span className="flex items-center gap-1.5">
                            {m.has_transcript && <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" title="Átirat" />}
                            {m.has_summary && <span className="w-1.5 h-1.5 rounded-full bg-blue-500" title="Összefoglaló" />}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={(e) => handleDelete(m.id, e)}
                        className="p-2 rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all opacity-0 group-hover:opacity-100"
                        title="Törlés"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                        </svg>
                      </button>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </main>

      {/* Create Modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Új találkozó létrehozása">
        <div className="space-y-4">
          <Input
            placeholder="Találkozó címe (opcionális)"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            autoFocus
          />
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowCreate(false)}>Mégse</Button>
            <Button onClick={handleCreate} disabled={creating}>
              {creating ? "Létrehozás..." : "Létrehozás"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
