import type { Metadata } from "next";
import { Fraunces, JetBrains_Mono, Instrument_Sans } from "next/font/google";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  axes: ["opsz", "SOFT"],
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

const instrument = Instrument_Sans({
  subsets: ["latin"],
  variable: "--font-instrument",
  display: "swap",
});

export const metadata: Metadata = {
  title: "TraceGraph — Revisitable Memory Agents · Team 8 · CECS-551",
  description:
    "Graph-based retrieval and revisitable-agent system for multi-hop long-context reasoning. Console interface for Phase 3 prototype.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <style>{`
          :root {
            --font-display: ${fraunces.style.fontFamily}, "Times New Roman", serif;
            --font-mono: ${jetbrains.style.fontFamily}, "SFMono-Regular", monospace;
            --font-sans: ${instrument.style.fontFamily}, system-ui, sans-serif;
          }
        `}</style>
      </head>
      <body
        className={`${fraunces.variable} ${jetbrains.variable} ${instrument.variable}`}
      >
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
