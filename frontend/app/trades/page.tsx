"use client";

import React, { useState, useEffect } from "react";

import Link from "next/link";
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  Search, 
  Filter, 
  ArrowUpRight, 
  History,
  FileText
} from "lucide-react";

interface MockTrade {
  id: string;
  symbol: string;
  direction: "LONG" | "SHORT";
  entry_price: number;
  current_price: number;
  stop_loss: number;
  target: number;
  quantity: number;
  status: "OPEN" | "TARGET_HIT" | "STOP_HIT" | "CLOSED_MANUALLY";
  pnl: number;
  pnl_pct: number;
  thesis: string;
  created_at: string;
}

const mockTrades: MockTrade[] = [
  {
    id: "tr-001",
    symbol: "NVDA",
    direction: "LONG",
    entry_price: 122.50,
    current_price: 126.80,
    stop_loss: 118.00,
    target: 135.00,
    quantity: 220,
    status: "OPEN",
    pnl: 946.00,
    pnl_pct: 3.51,
    thesis: "Blackwell chip yield improvement catalyst and 20 EMA bounce.",
    created_at: "2026-09-02",
  },
  {
    id: "tr-002",
    symbol: "AAPL",
    direction: "LONG",
    entry_price: 220.00,
    current_price: 224.50,
    stop_loss: 212.00,
    target: 236.00,
    quantity: 125,
    status: "OPEN",
    pnl: 562.50,
    pnl_pct: 2.05,
    thesis: "Apple Intelligence supply chain ramp-up.",
    created_at: "2026-09-03",
  },
  {
    id: "tr-003",
    symbol: "TSLA",
    direction: "LONG",
    entry_price: 254.00,
    current_price: 242.00,
    stop_loss: 245.00,
    target: 280.00,
    quantity: 110,
    status: "STOP_HIT",
    pnl: -990.00,
    pnl_pct: -3.54,
    thesis: "Breakout trade before earnings announcement.",
    created_at: "2026-08-28",
  },
  {
    id: "tr-004",
    symbol: "MSFT",
    direction: "LONG",
    entry_price: 435.00,
    current_price: 450.00,
    stop_loss: 425.00,
    target: 450.00,
    quantity: 60,
    status: "TARGET_HIT",
    pnl: 900.00,
    pnl_pct: 3.45,
    thesis: "Azure enterprise cloud booking reacceleration.",
    created_at: "2026-08-20",
  },
];

import { fetchTrades, ensureDemoToken } from "@/services/api";
import { TradeItem } from "@/types";

export default function TradesPage() {
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"ALL" | "OPEN" | "CLOSED">("ALL");
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadTrades();
  }, []);

  const loadTrades = async () => {
    try {
      const token = await ensureDemoToken();
      const live = await fetchTrades(token);
      if (live && live.length > 0) {
        setTrades(live.map(t => ({
          id: t.id,
          symbol: t.symbol,
          direction: t.direction,
          entry_price: t.entry_price,
          current_price: t.entry_price,
          stop_loss: t.stop_loss,
          target: t.target,
          quantity: t.quantity,
          status: t.status,
          pnl: t.realized_pnl !== null && t.realized_pnl !== undefined ? t.realized_pnl : (t.status === "OPEN" ? 0.0 : 0.0),
          pnl_pct: t.realized_pnl_pct !== null && t.realized_pnl_pct !== undefined ? t.realized_pnl_pct : 0.0,
          thesis: t.thesis,
          created_at: t.created_at ? t.created_at.slice(0, 10) : "2026-09-05",
        })));
      } else {
        setTrades(mockTrades);
      }
    } catch {
      setTrades(mockTrades);
    } finally {
      setLoading(false);
    }
  };

  const filtered = trades.filter((t) => {
    if (filter === "OPEN" && t.status !== "OPEN") return false;
    if (filter === "CLOSED" && t.status === "OPEN") return false;
    if (search && !t.symbol.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });


  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-trade-border pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <TrendingUp className="w-7 h-7 text-cyan-400" />
            Paper Trades
          </h1>
          <p className="text-xs sm:text-sm text-trade-muted mt-1">
            Track active positions, review executed orders, and examine post-mortem trade autopsies.
          </p>
        </div>
        <Link
          href="/analyze"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 text-slate-950 font-semibold text-xs transition shadow-lg shadow-cyan-500/20"
        >
          + Plan New Paper Trade
        </Link>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 bg-trade-card p-1 rounded-lg border border-trade-border">
          {(["ALL", "OPEN", "CLOSED"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-4 py-1.5 rounded-md text-xs font-semibold transition ${
                filter === tab
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  : "text-trade-muted hover:text-white"
              }`}
            >
              {tab} TRADES
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-trade-muted absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search ticker..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-trade-card border border-trade-border rounded-lg pl-9 pr-4 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {/* Trades Table */}
      <div className="rounded-xl border border-trade-border bg-trade-card overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-trade-bg/60 text-trade-muted uppercase tracking-wider font-mono border-b border-trade-border">
              <tr>
                <th className="py-3 px-4">Symbol / Direction</th>
                <th className="py-3 px-4">Entry</th>
                <th className="py-3 px-4">Current</th>
                <th className="py-3 px-4">Stop / Target</th>
                <th className="py-3 px-4">Quantity</th>
                <th className="py-3 px-4">P&L</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Thesis</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-trade-border">
              {filtered.map((trade) => {
                const isProfit = trade.pnl >= 0;
                return (
                  <tr key={trade.id} className="hover:bg-trade-cardHover/50 transition">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-sm">{trade.symbol}</span>
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${trade.direction === "LONG" ? "bg-emerald-500/20 text-emerald-400" : "bg-rose-500/20 text-rose-400"}`}>
                          {trade.direction}
                        </span>
                      </div>
                      <span className="text-[10px] text-trade-muted font-mono">{trade.created_at}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-200">${trade.entry_price.toFixed(2)}</td>
                    <td className="py-3.5 px-4 font-mono text-white font-semibold">${trade.current_price.toFixed(2)}</td>
                    <td className="py-3.5 px-4 font-mono text-xs">
                      <span className="text-rose-400">${trade.stop_loss.toFixed(2)}</span> /{" "}
                      <span className="text-emerald-400">${trade.target.toFixed(2)}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-200">{trade.quantity} shs</td>
                    <td className="py-3.5 px-4 font-mono">
                      <span className={`font-semibold ${isProfit ? "text-emerald-400" : "text-rose-400"}`}>
                        {isProfit ? "+" : ""}${trade.pnl.toFixed(2)} ({isProfit ? "+" : ""}{trade.pnl_pct.toFixed(2)}%)
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                        trade.status === "OPEN"
                          ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/30"
                          : trade.status === "TARGET_HIT"
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                          : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                      }`}>
                        {trade.status === "OPEN" && <Clock className="w-3 h-3" />}
                        {trade.status === "TARGET_HIT" && <CheckCircle2 className="w-3 h-3" />}
                        {trade.status === "STOP_HIT" && <XCircle className="w-3 h-3" />}
                        {trade.status.replace("_", " ")}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 max-w-xs truncate text-trade-muted" title={trade.thesis}>
                      {trade.thesis}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/trades/${trade.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-trade-border hover:bg-cyan-500/20 hover:text-cyan-400 text-trade-muted text-xs transition"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        Autopsy
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
