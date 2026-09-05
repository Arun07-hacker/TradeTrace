import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "TradeTrace — AI Trading Research, Risk & Learning Assistant",
  description:
    "Research -> Challenge -> Decide -> Monitor -> Trace -> Learn. The paper trading terminal with vector trading memory.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-trade-bg text-slate-100 min-h-screen flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="border-t border-trade-border py-4 px-6 text-center text-xs text-trade-muted">
          <p>
            TradeTrace is an analytical research and learning tool. Paper trading only. Not financial advice.
          </p>
        </footer>
      </body>
    </html>
  );
}
