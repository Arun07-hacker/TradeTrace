"use client";

import React from "react";
import Link from "next/link";
import { HealthBadge } from "./HealthBadge";
import { 
  TrendingUp, 
  BrainCircuit, 
  Compass, 
  BookOpen, 
  PieChart, 
  Bell, 
  Layers 
} from "lucide-react";

export function Navbar() {
  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: PieChart },
    { label: "Analyze", href: "/analyze", icon: Compass, badge: "AI" },
    { label: "Trades", href: "/trades", icon: TrendingUp },
    { label: "Portfolio", href: "/portfolio", icon: Layers },
    { label: "Memory", href: "/memory", icon: BrainCircuit, badge: "pgvector" },
    { label: "Journal", href: "/journal", icon: BookOpen },
    { label: "Alerts", href: "/alerts", icon: Bell },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-trade-border bg-trade-bg/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Tagline */}
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-emerald-500 p-0.5 shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition">
              <div className="w-full h-full bg-trade-bg rounded-[7px] flex items-center justify-center">
                <BrainCircuit className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
              </div>
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                TradeTrace
              </span>
              <span className="hidden md:block text-[10px] text-trade-muted tracking-wider uppercase font-medium">
                Research • Challenge • Learn
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation links */}
        <nav className="hidden lg:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.label}
                href={item.href}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-cyan-400 hover:bg-trade-card rounded-md transition"
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
                {item.badge && (
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right side live status indicators */}
        <div className="flex items-center gap-3">
          <HealthBadge />
        </div>
      </div>
    </header>
  );
}
