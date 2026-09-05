"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  History, 
  ArrowLeft, 
  BrainCircuit, 
  Flame, 
  CheckCircle2, 
  XCircle, 
  ShieldAlert, 
  BookOpen, 
  Calendar,
  Clock,
  Sparkles,
  ArrowDownRight,
  TrendingUp,
  TrendingDown
} from "lucide-react";
import { fetchTradeById, closeTrade, runTradeAutopsy, ensureDemoToken } from "@/services/api";
import { TradeItem, TradeAutopsyResponse } from "@/types";

export default function TradeDetailPage({ params }: { params: { id: string } }) {
  const [trade, setTrade] = useState<TradeItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [closing, setClosing] = useState(false);
  const [runningAutopsy, setRunningAutopsy] = useState(false);
  const [traderNotes, setTraderNotes] = useState("");
  const [autopsyResult, setAutopsyResult] = useState<TradeAutopsyResponse | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    loadTrade();
  }, [params.id]);

  const loadTrade = async () => {
    try {
      const token = await ensureDemoToken();
      const res = await fetchTradeById(params.id, token);
      setTrade(res);
    } catch {
      // Fallback for demo mock IDs if not found in db
      setTrade(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseTrade = async (reason: string = "CLOSED_MANUALLY") => {
    setClosing(true);
    setActionError(null);
    try {
      const token = await ensureDemoToken();
      const res = await closeTrade(params.id, { reason }, token);
      setTrade(res);
    } catch (err: any) {
      setActionError(err.message || "Failed to close trade");
    } finally {
      setClosing(false);
    }
  };

  const handleRunAutopsy = async () => {
    setRunningAutopsy(true);
    setActionError(null);
    try {
      const token = await ensureDemoToken();
      const res = await runTradeAutopsy(params.id, traderNotes, token);
      setAutopsyResult(res);
    } catch (err: any) {
      setActionError(err.message || "Failed to execute post-trade autopsy");
    } finally {
      setRunningAutopsy(false);
    }
  };

  const isMock = !trade;
  const isLoss = isMock ? params.id === "tr-003" : (trade?.realized_pnl || 0) < 0;
  const pnl = trade ? trade.realized_pnl || 0 : (isLoss ? -990.0 : 946.0);
  const pnlPct = trade ? trade.realized_pnl_pct || 0 : (isLoss ? -3.54 : 3.51);
  const symbol = trade ? trade.symbol : (isLoss ? "TSLA" : "NVDA");
  const direction = trade ? trade.direction : "LONG";
  const status = trade ? trade.status : (isLoss ? "STOP_HIT" : "OPEN");

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back button */}
      <div>
        <Link href="/trades" className="inline-flex items-center gap-1.5 text-xs text-trade-muted hover:text-cyan-400 transition">
          <ArrowLeft className="w-4 h-4" />
          Back to All Trades
        </Link>
      </div>

      {actionError && (
        <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
          {actionError}
        </div>
      )}

      {/* Trade Summary Banner */}
      <div className="p-6 rounded-xl border border-trade-border bg-trade-card flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              Trade Overview: <span className="text-cyan-400">{symbol} {direction}</span>
            </h1>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold border ${
              status === "OPEN"
                ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/30"
                : status === "TARGET_HIT" || !isLoss
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                : "bg-rose-500/10 text-rose-400 border-rose-500/30"
            }`}>

              {status}
            </span>
          </div>
          <p className="text-xs text-trade-muted mt-1 flex items-center gap-2 font-mono">
            <Calendar className="w-3.5 h-3.5" /> ID: {params.id} • Timeframe: {trade?.timeframe || "1d"}
          </p>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-right">
            <span className="text-xs text-trade-muted block">Realized P&L</span>
            <span className={`text-2xl font-bold font-mono ${pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
              {pnl >= 0 ? "+" : ""}${pnl.toFixed(2)} ({pnlPct >= 0 ? "+" : ""}{pnlPct.toFixed(2)}%)
            </span>
          </div>

          {status === "OPEN" && (
            <button
              onClick={() => handleCloseTrade("CLOSED_MANUALLY")}
              disabled={closing}
              className="px-4 py-2 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30 hover:bg-rose-500/30 font-bold text-xs transition flex items-center gap-1.5"
            >
              {closing ? "Closing..." : "Close Trade Now"}
            </button>
          )}
        </div>
      </div>

      {/* Trade Parameters & Thesis Box */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl border border-trade-border bg-trade-card">
          <span className="text-xs text-trade-muted block">Entry Price</span>
          <span className="text-base font-bold font-mono text-white">${(trade?.entry_price || 220.0).toFixed(2)}</span>
        </div>
        <div className="p-4 rounded-xl border border-trade-border bg-trade-card">
          <span className="text-xs text-trade-muted block">Stop Loss</span>
          <span className="text-base font-bold font-mono text-rose-400">${(trade?.stop_loss || 212.0).toFixed(2)}</span>
        </div>
        <div className="p-4 rounded-xl border border-trade-border bg-trade-card">
          <span className="text-xs text-trade-muted block">Target Price</span>
          <span className="text-base font-bold font-mono text-emerald-400">${(trade?.target || 236.0).toFixed(2)}</span>
        </div>
        <div className="p-4 rounded-xl border border-trade-border bg-trade-card">
          <span className="text-xs text-trade-muted block">Position Size</span>
          <span className="text-base font-bold font-mono text-cyan-400">{(trade?.quantity || 100)} Shares</span>
        </div>
      </div>

      {/* Thesis and Decision */}
      <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-3">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-cyan-400" />
          Pre-Trade Thesis & AI Assessment
        </h2>
        <div className="p-3.5 rounded-lg bg-trade-bg border border-trade-border text-xs text-slate-200 leading-relaxed">
          {trade?.thesis || "Breakout continuation above consolidation resistance with positive momentum."}
        </div>
      </div>

      {/* Execution Timeline Events */}
      {trade?.events && trade.events.length > 0 && (
        <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-400" />
            Execution & Monitoring Timeline
          </h2>
          <div className="space-y-2">
            {trade.events.map((ev, idx) => (
              <div key={idx} className="flex items-start gap-3 text-xs p-2.5 rounded bg-trade-bg/60 border border-trade-border">
                <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold ${
                  ev.severity === "CRITICAL" ? "bg-rose-500/20 text-rose-300" :
                  ev.severity === "WARNING" ? "bg-amber-500/20 text-amber-300" : "bg-cyan-500/20 text-cyan-300"
                }`}>
                  {ev.event_type}
                </span>
                <span className="text-slate-300 flex-1">{ev.description}</span>
                <span className="text-trade-muted font-mono text-[10px]">
                  {new Date(ev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Post-Trade Autopsy Section */}
      {status !== "OPEN" && (
        <div className="p-6 rounded-xl border border-purple-500/30 bg-purple-950/20 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-purple-300 uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Post-Trade AI Autopsy & Continuous Learning
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-900/60 text-purple-200 border border-purple-500/40">
              Cognitive Loop
            </span>
          </div>

          {!autopsyResult && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs text-trade-muted mb-1">
                  Trader Reflection Notes (Optional):
                </label>
                <textarea
                  value={traderNotes}
                  onChange={(e) => setTraderNotes(e.target.value)}
                  placeholder="Reflect on your execution: Did you feel FOMO? Did you follow your stops?"
                  rows={3}
                  className="w-full bg-trade-bg border border-trade-border rounded-lg p-3 text-xs text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <button
                onClick={handleRunAutopsy}
                disabled={runningAutopsy}
                className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-400 hover:to-indigo-400 text-white font-bold text-xs transition shadow-lg flex items-center gap-2 disabled:opacity-50"
              >
                {runningAutopsy ? "Running AI Autopsy..." : "Run Post-Trade Autopsy & Index to Memory"}
              </button>
            </div>
          )}

          {autopsyResult && (
            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-purple-900/30 border border-purple-500/30">
                  <span className="text-purple-300 font-bold block">Execution Grade</span>
                  <span className="text-2xl font-bold font-mono text-white mt-1 block">
                    {autopsyResult.execution_grade}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-purple-900/30 border border-purple-500/30">
                  <span className="text-purple-300 font-bold block">Discipline Score</span>
                  <span className="text-2xl font-bold font-mono text-emerald-400 mt-1 block">
                    {(autopsyResult.discipline_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="p-3.5 rounded-lg bg-purple-900/30 border border-purple-500/30 space-y-1">
                <span className="text-rose-400 font-bold block">Primary Mistake Diagnosed:</span>
                <p className="text-slate-200">{autopsyResult.key_mistake}</p>
              </div>

              <div className="p-3.5 rounded-lg bg-purple-900/30 border border-purple-500/30 space-y-1">
                <span className="text-cyan-300 font-bold block">Core Lesson Learned:</span>
                <p className="text-slate-200">{autopsyResult.lesson_learned}</p>
              </div>

              <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30 space-y-1">
                <span className="text-emerald-300 font-bold block">Permanent Operating Rule Vectorized:</span>
                <p className="text-emerald-100 font-mono text-xs">{autopsyResult.future_rule}</p>
              </div>

              <div className="p-2.5 rounded bg-purple-900/40 border border-purple-500/40 text-[11px] text-purple-200 flex items-center justify-between">
                <span>✓ Successfully committed to pgvector Cognitive Trading Memory.</span>
                <Link href="/memory" className="underline font-bold hover:text-white">
                  View Memory Bank →
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
