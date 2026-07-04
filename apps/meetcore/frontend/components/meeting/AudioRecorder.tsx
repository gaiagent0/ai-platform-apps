"use client";

import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface AudioRecorderProps {
  onUpload: (blob: Blob) => Promise<void>;
  disabled?: boolean;
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export function AudioRecorder({ onUpload, disabled }: AudioRecorderProps) {
  const {
    isRecording, isPaused, duration, audioBlob, audioUrl,
    startRecording, stopRecording, pauseRecording, resumeRecording, clearRecording, error,
  } = useAudioRecorder();

  const handleUpload = async () => {
    if (!audioBlob) return;
    await onUpload(audioBlob);
    clearRecording();
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" x2="12" y1="19" y2="22"/>
          </svg>
          Hangrögzítés
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm dark:bg-red-950 dark:border-red-800 dark:text-red-300">
            {error}
          </div>
        )}

        {/* Timer + Visualizer */}
        <div className="flex items-center justify-center">
          <div className={`text-4xl font-mono tabular-nums transition-colors ${isRecording && !isPaused ? "text-red-500" : "text-muted-foreground"}`}>
            {formatDuration(duration)}
          </div>
        </div>

        {/* Recording Controls */}
        <div className="flex items-center justify-center gap-2">
          {!isRecording && !audioBlob && (
            <Button onClick={startRecording} disabled={disabled} className="rounded-full w-12 h-12 p-0 bg-red-500 hover:bg-red-600">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" x2="12" y1="19" y2="22"/>
              </svg>
            </Button>
          )}
          {isRecording && (
            <>
              <Button onClick={stopRecording} variant="destructive" className="rounded-full w-12 h-12 p-0">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="6" width="12" height="12" rx="1"/>
                </svg>
              </Button>
              {!isPaused ? (
                <Button onClick={pauseRecording} variant="outline" size="icon" className="rounded-full">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>
                  </svg>
                </Button>
              ) : (
                <Button onClick={resumeRecording} variant="outline" size="icon" className="rounded-full">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                </Button>
              )}
            </>
          )}
        </div>

        {/* Playback + Upload */}
        {audioBlob && !isRecording && (
          <div className="space-y-3">
            <audio controls src={audioUrl || undefined} className="w-full h-10" />
            <div className="flex gap-2">
              <Button variant="outline" onClick={clearRecording} className="flex-1">
                Újrakezdés
              </Button>
              <Button onClick={handleUpload} disabled={disabled} className="flex-1">
                Feltöltés és feldolgozás
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
