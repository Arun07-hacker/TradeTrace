"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Layers, 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  ShieldCheck, 
  PieChart as PieIcon, 
  ArrowUpRight,
  RotateCcw
} from "lucide-react";
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip 
} from "recharts";
import { fetchPortfolio, resetPortfolio, ensureDemoToken } from "@/services/api";
import { PortfolioDetail } from "@/types";

const defaultDemoPositions = [
  {
    id: "pos-1",
    symbol: "NVDA",
    direction: "LONG" as const,
    quantity: 220,
    entry_price: 122.50,
    current_price: 126.80,
    unrealized_pnl: 946.00,
    unrealized_pnl_pct: 3.51,
  },
  {
    id: "pos-2",
    symbol: "AAPL",
    direction: "LONG" as const,
    quantity: 125,
    entry_price: 220.00,
    current_price: 224.50,
    unrealized_pnl: 562.50,
    unrealized_pnl_pct: 2.05,
  },
];

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<PortfolioDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [resetting, setResetting] = useState(false);

  useEffect(() => {
    loadPortfolio();
  }, []);

  const loadPortfolio = async () => {
    try {
      const token = await ensureDemoToken();
      const res = await fetchPortfolio(token);
      setPortfolio(res);
    } catch {
      // Keep demo fallback
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Are you sure you want to reset your paper portfolio to $100,000 cash?")) return;
    setResetting(true);
    try {
      const token = await ensureDemoToken();
      const res = await resetPortfolio(token);
      setPortfolio(res);
    } catch (e) {
      console.error(e);
    } finally {
      setResetting(false);
    }
  };

  const totalEquity = portfolio ? portfolio.total_equity : 104250.0;
  const cashBalance = portfolio ? portfolio.cash_balance : 48292.0;
  const unrealizedPnL = portfolio ? portfolio.unrealized_pnl : 1508.50;
  const realizedPnL = portfolio ? portfolio.realized_pnl : 2741.50;
  const exposurePct = portfolio ? portfolio.current_exposure_pct : 53.6;
  const rawPositions = portfolio && portfolio.positions && portfolio.positions.length > 0 
    ? portfolio.positions 
    : defaultDemoPositions;

  // Chart data
  const colors = ["#10b981", "#38bdf8", "#818cf8", "#fbbf24", "#f43f5e"];
  const allocationData = [
    ...rawPositions.map((pos, idx) => ({
      name: pos.symbol,
      value: Math.round(pos.quantity * (pos.current_price || pos.entry_price)),
      color: colors[idx % colors.length],
    })),
    {
      name: "Cash Reserve",
      value: Math.round(cashBalance),
      color: "#334155",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-trade-border pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Layers className="w-7 h-7 text-cyan-400" />
            Paper Portfolio Management
          </h1>
          <p className="text-xs sm:text-sm text-trade-muted mt-1">
            Capital allocation, cash reserves, unrealized/realized returns, and risk exposure limits.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleReset}
            disabled={resetting}
            className="text-xs font-mono px-3 py-1.5 rounded-lg bg-trade-card border border-trade-border text-trade-muted hover:text-white transition flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            {resetting ? "Resetting..." : "Reset $100k"}
          </button>
          <span className="text-xs font-mono px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Paper Trading: Real-money disabled
          </span>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl border border-trade-border bg-trade-card">
          <span className="text-xs text-trade-muted block">Total Portfolio Value</span>
          <div className="text-2xl font-bold font-mono text-white mt-1">
            ${totalEquity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-xs text-emerald-400 font-medium mt-1 inline-block">
            Realized: ${realizedPnL.toFixed(2)}
          </span>
        </div>

        <div className="p-5 rounded-xl border border-trade-border bg-trade-card">
          <span className="text-xs text-trade-muted block">Available Cash</span>
          <div className="text-2xl font-bold font-mono text-white mt-1">
            ${cashBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-xs text-trade-muted mt-1 inline-block">Initial: $100,000.00</span>
        </div>

        <div className="p-5 rounded-xl border border-trade-border bg-trade-card">
          <span className="text-xs text-trade-muted block">Unrealized P&L</span>
          <div className={`text-2xl font-bold font-mono mt-1 ${unrealizedPnL >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
            {unrealizedPnL >= 0 ? "+" : ""}${unrealizedPnL.toFixed(2)}
          </div>
          <span className="text-xs text-trade-muted mt-1 inline-block">
            Win: {portfolio?.win_count || 1} • Loss: {portfolio?.loss_count || 0}
          </span>
        </div>

        <div className="p-5 rounded-xl border border-trade-border bg-trade-card">
          <span className="text-xs text-trade-muted block">Current Risk Exposure</span>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">
            {exposurePct.toFixed(1)}%
          </div>
          <span className="text-xs text-trade-muted mt-1 inline-block">Target Limit: 50.0%</span>
        </div>
      </div>

      {/* Allocation & Active Positions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Allocation Chart */}
        <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <PieIcon className="w-4 h-4 text-cyan-400" />
            Capital Allocation
          </h2>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(val: number) => [`$${val.toLocaleString()}`, "Value"]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", fontSize: "12px", borderRadius: "8px" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 border-t border-trade-border pt-4">
            {allocationData.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-300 font-medium">{item.name}</span>
                </div>
                <span className="font-mono text-white font-semibold">
                  ${item.value.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Active Positions Table */}
        <div className="lg:col-span-2 p-6 rounded-xl border border-trade-border bg-trade-card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Open Market Positions ({rawPositions.length})
            </h2>
            <Link href="/analyze" className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
              New Trade <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-trade-border text-trade-muted font-medium">
                  <th className="pb-3">Asset</th>
                  <th className="pb-3">Shares</th>
                  <th className="pb-3">Entry</th>
                  <th className="pb-3">Current</th>
                  <th className="pb-3">Market Value</th>
                  <th className="pb-3 text-right">Unrealized P&L</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-trade-border/50 font-mono">
                {rawPositions.map((pos, idx) => {
                  const currentP = pos.current_price || pos.entry_price;
                  const mktVal = pos.quantity * currentP;
                  const posPnl = pos.unrealized_pnl || 0;
                  const posPnlPct = pos.unrealized_pnl_pct || 0;
                  return (
                    <tr key={idx} className="hover:bg-trade-bg/40 transition">
                      <td className="py-3.5">
                        <div className="flex items-center gap-2">
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            {pos.direction}
                          </span>
                          <span className="font-sans font-bold text-white text-sm">{pos.symbol}</span>
                        </div>
                      </td>
                      <td className="py-3.5 text-slate-300">{pos.quantity}</td>
                      <td className="py-3.5 text-slate-300">${pos.entry_price.toFixed(2)}</td>
                      <td className="py-3.5 text-white font-bold">${currentP.toFixed(2)}</td>
                      <td className="py-3.5 text-slate-300">${mktVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                      <td className="py-3.5 text-right">
                        <span className={`font-bold ${posPnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                          {posPnl >= 0 ? "+" : ""}${posPnl.toFixed(2)} ({posPnlPct >= 0 ? "+" : ""}{posPnlPct.toFixed(2)}%)
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
