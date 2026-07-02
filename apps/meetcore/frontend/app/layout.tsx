import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MeetCore — Meeting Assistant",
  description: "AI-powered meeting recording and summarization",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="hu">
      <body className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900">
        {children}
      </body>
    </html>
  );
}
