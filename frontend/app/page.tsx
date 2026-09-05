import Link from "next/link";
import {
  BrainCircuit,
  Flame,
  ShieldCheck,
  Scale,
  Sparkles,
  ArrowRight,
  TrendingUp,
  History,
  AlertOctagon,
  Radar,
  FileSearch,
} from "lucide-react";

export default function HomePage() {
  const steps = [
    {
      title: "1. Research & Data",
      desc: "Deterministic technical indicators, news events, and multi-factor research synthesis.",
      icon: FileSearch,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
      border: "border-blue-500/20",
    },
    {
      title: "2. Devil's Advocate",
      desc: "Aggressively checks contradictory indicators, weak volume, upcoming catalysts, and invalidation criteria.",
      icon: Flame,
      color: "text-rose-400",
      bg: "bg-rose-500/10",
      border: "border-rose-500/20",
    },
    {
      title: "3. Deterministic Risk",
      desc: "Stop-loss calibration, 1% risk-per-trade position sizing, and portfolio drawdown protection.",
      icon: Scale,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
    },
    {
      title: "4. Vector Memory Warning",
      desc: "pgvector semantic lookup matches new setups against past mistakes and warning precedents.",
      icon: BrainCircuit,
      color: "text-purple-400",
      bg: "bg-purple-500/10",
      border: "border-purple-500/20",
    },
    {
      title: "5. Decision & Paper Trade",
      desc: "Explainable state (STRONG, POSSIBLE, WAIT, HIGH RISK, AVOID) with zero real-money risk.",
      icon: ShieldCheck,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
    },
    {
      title: "6. Post-Trade Autopsy",
      desc: "Automated analysis comparing thesis vs. reality, generating persistent lessons for the future.",
      icon: History,
      color: "text-cyan-400",
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/20",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Hero Section */}
      <div className="relative rounded-2xl border border-trade-border bg-gradient-to-b from-trade-card via-trade-card/70 to-trade-bg p-8 sm:p-12 overflow-hidden shadow-2xl">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-8 -ml-8 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-mono tracking-wide">
            <Sparkles className="w-3.5 h-3.5" />
            Phase 1 Setup Active • Architecture Ready
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Stop repeating past mistakes.{" "}
            <span className="bg-gradient-to-r from-cyan-400 via-emerald-400 to-teal-300 bg-clip-text text-transparent">
              Trade with Memory.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed">
            TradeTrace is an AI research, deterministic risk, and cognitive journal assistant.
            It challenges your confirmation bias, tracks paper positions, and searches past trade autopsies
            via semantic vector embeddings so you never walk blindly into the same loss twice.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              href="/analyze"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-semibold text-sm shadow-lg shadow-cyan-500/25 transition-all transform hover:-translate-y-0.5"
            >
              Launch Trade Analysis
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-trade-card hover:bg-trade-cardHover text-slate-200 border border-trade-border text-sm font-medium transition"
            >
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              View Dashboard
            </Link>
          </div>
        </div>
      </div>

      {/* Memory Differentiator Banner */}
      <div className="rounded-xl border border-purple-500/30 bg-purple-950/20 p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-purple-300 font-semibold text-sm">
            <BrainCircuit className="w-4 h-4 text-purple-400" />
            The Key Differentiator: Closed-Loop Vector Memory
          </div>
          <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
            Most platforms only track entry, exit, and P&L. TradeTrace records <span className="text-white font-medium">why</span> you entered, what the <span className="text-rose-300 font-medium">Devil's Advocate</span> warned against, and what <span className="text-emerald-300 font-medium">lesson</span> was learned. Future similar setups trigger real-time memory warnings.
          </p>
        </div>
        <div className="px-4 py-2 rounded-lg bg-purple-900/40 border border-purple-500/30 font-mono text-xs text-purple-200 whitespace-nowrap">
          PostgreSQL + pgvector
        </div>
      </div>

      {/* Flow Steps */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
            <Radar className="w-5 h-5 text-cyan-400" />
            The TradeTrace 6-Stage Analytical Pipeline
          </h2>
          <span className="text-xs text-trade-muted font-mono">End-to-End Governance</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <div
                key={step.title}
                className={`p-5 rounded-xl border ${step.border} ${step.bg} flex flex-col justify-between space-y-3 hover:scale-[1.01] transition-transform`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-sm text-slate-200">{step.title}</span>
                  <Icon className={`w-5 h-5 ${step.color}`} />
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{step.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Disclaimer reminder as mandated by financial safety requirement */}
      <div className="rounded-lg border border-trade-border bg-trade-card/50 p-4 text-xs text-trade-muted flex items-center gap-3">
        <AlertOctagon className="w-4 h-4 text-amber-400 shrink-0" />
        <span>
          <strong>Financial Safety Note:</strong> TradeTrace is designed for trading research, risk management, and retrospective learning in paper trading mode. It does not predict market prices and never executes real-money orders.
        </span>
      </div>
    </div>
  );
}
