"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { 
  TrendingUp, 
  TrendingDown, 
  ShieldAlert, 
  BrainCircuit, 
  Sparkles, 
  ArrowUpRight, 
  Layers, 
  DollarSign, 
  Activity, 
  Compass 
} from "lucide-react";
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart, 
  Bar 
} from "recharts";
import { fetchSymbols } from "@/services/api";

const performanceData = [
  { date: "Day 1", equity: 100000 },
  { date: "Day 5", equity: 101200 },
  { date: "Day 10", equity: 100800 },
  { date: "Day 15", equity: 102450 },
  { date: "Day 20", equity: 101900 },
  { date: "Day 25", equity: 103800 },
  { date: "Day 30", equity: 104250 },
];

const distributionData = [
  { name: "Wins", count: 17, fill: "#10b981" },
  { name: "Losses", count: 8, fill: "#f43f5e" },
  { name: "Breakeven", count: 3, fill: "#94a3b8" },
];

export default function DashboardPage() {
  const [symbols, setSymbols] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSymbols()
      .then((data) => {
        setSymbols(data);
        setLoading(false);
      })
      .catch(() => {
        // Fallback default symbols
        setSymbols([
          { symbol: "AAPL", name: "Apple Inc.", current_price: 224.50, daily_change_pct: 1.25 },
          { symbol: "MSFT", name: "Microsoft Corp.", current_price: 448.20, daily_change_pct: -0.45 },
          { symbol: "NVDA", name: "NVIDIA Corp.", current_price: 126.80, daily_change_pct: 3.10 },
          { symbol: "TSLA", name: "Tesla, Inc.", current_price: 248.60, daily_change_pct: -1.80 },
        ]);
        setLoading(false);
      });
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-trade-border pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Layers className="w-7 h-7 text-cyan-400" />
            Trading Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-trade-muted mt-1">
            Real-time paper portfolio analytics, market watch, and memory-driven AI signals.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/analyze"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-semibold text-xs transition shadow-lg shadow-cyan-500/20"
          >
            <Compass className="w-4 h-4" />
            New Analysis
          </Link>
        </div>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl border border-trade-border bg-trade-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-trade-muted">
            <span>Portfolio Value</span>
            <DollarSign className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-mono text-white">$104,250.00</div>
            <div className="text-xs text-emerald-400 font-medium flex items-center gap-1 mt-1">
              <TrendingUp className="w-3.5 h-3.5" />
              +$4,250.00 (+4.25% Total)
            </div>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-trade-border bg-trade-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-trade-muted">
            <span>Available Paper Cash</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-mono text-white">$78,400.00</div>
            <div className="text-xs text-trade-muted mt-1">
              Exposure: <span className="text-slate-200 font-mono">24.8%</span> / 50% Max
            </div>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-trade-border bg-trade-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-trade-muted">
            <span>Win Rate</span>
            <Sparkles className="w-4 h-4 text-purple-400" />
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-mono text-white">68.0%</div>
            <div className="text-xs text-trade-muted mt-1">
              17 Wins / 8 Losses (Avg R:R 2.4)
            </div>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-trade-border bg-trade-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-trade-muted">
            <span>Max Drawdown</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-mono text-white">2.1%</div>
            <div className="text-xs text-emerald-400 mt-1">
              Well within 5.0% safety limit
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Equity Curve Chart */}
        <div className="lg:col-span-2 p-6 rounded-xl border border-trade-border bg-trade-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-white">Paper Portfolio Equity Curve</h2>
              <p className="text-xs text-trade-muted">Cumulative portfolio trajectory (30 days)</p>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Up +4.25%
            </span>
          </div>

          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#475569" fontSize={11} tickLine={false} />
                <YAxis stroke="#475569" fontSize={11} tickLine={false} domain={["dataMin - 1000", "dataMax + 1000"]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f1624",
                    borderColor: "#1e293b",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Area type="monotone" dataKey="equity" stroke="#38bdf8" strokeWidth={2} fillOpacity={1} fill="url(#equityGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Trade Distribution Chart */}
        <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-semibold text-white">Outcome Distribution</h2>
            <p className="text-xs text-trade-muted">Closed paper trade post-mortem results</p>
          </div>

          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distributionData}>
                <XAxis dataKey="name" stroke="#475569" fontSize={11} tickLine={false} />
                <YAxis stroke="#475569" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f1624",
                    borderColor: "#1e293b",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center text-xs border-t border-trade-border pt-3">
            <div>
              <span className="text-emerald-400 font-bold block">17</span>
              <span className="text-trade-muted text-[10px]">Wins</span>
            </div>
            <div>
              <span className="text-rose-400 font-bold block">8</span>
              <span className="text-trade-muted text-[10px]">Losses</span>
            </div>
            <div>
              <span className="text-slate-400 font-bold block">3</span>
              <span className="text-trade-muted text-[10px]">Even</span>
            </div>
          </div>
        </div>
      </div>

      {/* Market Watch & Active Positions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Watchlist */}
        <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Watchlist & Market Watch
            </h2>
            <span className="text-xs text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 font-mono">
              Live Mock Feeds
            </span>
          </div>

          <div className="divide-y divide-trade-border">
            {symbols.map((item) => {
              const isPositive = item.daily_change_pct >= 0;
              return (
                <div key={item.symbol} className="py-3 flex items-center justify-between hover:bg-trade-cardHover/50 px-2 rounded-lg transition">
                  <div>
                    <span className="font-bold text-sm text-white">{item.symbol}</span>
                    <span className="text-xs text-trade-muted block">{item.name}</span>
                  </div>
                  <div className="text-right flex items-center gap-4">
                    <div>
                      <div className="text-sm font-mono font-semibold text-white">
                        ${Number(item.current_price).toFixed(2)}
                      </div>
                      <div className={`text-xs font-mono font-medium flex items-center justify-end gap-0.5 ${isPositive ? "text-emerald-400" : "text-rose-400"}`}>
                        {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                        {isPositive ? "+" : ""}{Number(item.daily_change_pct).toFixed(2)}%
                      </div>
                    </div>
                    <Link
                      href={`/analyze?symbol=${item.symbol}`}
                      className="p-1.5 rounded bg-trade-border hover:bg-cyan-500/20 hover:text-cyan-400 text-trade-muted transition"
                      title="Analyze Ticker"
                    >
                      <ArrowUpRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* AI Memory & Active Warnings */}
        <div className="p-6 rounded-xl border border-purple-500/20 bg-gradient-to-b from-purple-950/20 to-trade-card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-purple-300 flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-purple-400" />
              AI Cognitive Insights & Memory
            </h2>
            <Link href="/memory" className="text-xs text-purple-400 hover:underline">
              View All Memories →
            </Link>
          </div>

          <div className="space-y-3">
            <div className="p-3.5 rounded-lg bg-purple-950/30 border border-purple-500/30 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-purple-200">Memory Warning Precedent</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400">High Risk</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Tesla earnings announcement in 6 days. Your trading memory contains 2 past trades with identical breakout setups before earnings that resulted in losses due to event volatility.
              </p>
            </div>

            <div className="p-3.5 rounded-lg bg-trade-cardHover/60 border border-trade-border space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-cyan-300">Strongest Current Setup</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400">Bullish Trend</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                NVIDIA (NVDA): RSI at 64.2, SMA-20 crossing above SMA-50 with 1.34x volume surge. Devil's Advocate flags export regulation review as primary invalidation risk.
              </p>
            </div>

            <div className="p-3.5 rounded-lg bg-trade-cardHover/60 border border-trade-border space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-emerald-300">Recent Lesson Ingested</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-trade-card text-trade-muted">Rule #14</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                "Do not widen stop-loss levels during high volatility; accept the planned 1% risk exit."
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
