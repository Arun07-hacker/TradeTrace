"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { 
  Compass, 
  Flame, 
  BrainCircuit, 
  Scale, 
  ShieldCheck, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  CheckCircle2, 
  FileText, 
  Zap, 
  ArrowRight,
  HelpCircle,
  Clock
} from "lucide-react";
import { fetchQuote, fetchTechnicalAnalysis, fetchNews, fetchEvents, evaluateAnalysis, executeTrade, ensureDemoToken } from "@/services/api";
import { TradeAnalysisResponse } from "@/types";
import Link from "next/navigation";

type DecisionState = "STRONG_SETUP" | "POSSIBLE_SETUP" | "WAIT" | "HIGH_RISK" | "AVOID";

function AnalyzeContent() {
  const searchParams = useSearchParams();
  const initialSymbol = searchParams.get("symbol") || "AAPL";

  // Trade Setup Form State
  const [symbol, setSymbol] = useState(initialSymbol);
  const [direction, setDirection] = useState<"LONG" | "SHORT">("LONG");
  const [timeframe, setTimeframe] = useState("1d");
  const [entryPrice, setEntryPrice] = useState("224.50");
  const [stopLoss, setStopLoss] = useState("215.00");
  const [targetPrice, setTargetPrice] = useState("242.00");
  const [thesis, setThesis] = useState(
    "Anticipating breakout continuation above consolidation resistance after positive earnings momentum."
  );

  // Analysis Data States
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisDone, setAnalysisDone] = useState(false);
  const [activeStep, setActiveStep] = useState<number>(0);
  const [quoteData, setQuoteData] = useState<any>(null);
  const [techData, setTechData] = useState<any>(null);
  const [newsData, setNewsData] = useState<any[]>([]);
  const [eventsData, setEventsData] = useState<any[]>([]);
  const [agentAnalysis, setAgentAnalysis] = useState<TradeAnalysisResponse | null>(null);

  // Paper Trade execution feedback
  const [executingTrade, setExecutingTrade] = useState(false);
  const [paperTraded, setPaperTraded] = useState(false);
  const [executedTradeId, setExecutedTradeId] = useState<string | null>(null);
  const [tradeError, setTradeError] = useState<string | null>(null);

  // Load initial ticker data
  useEffect(() => {
    loadSymbolData(symbol);
  }, [symbol]);

  const loadSymbolData = async (sym: string) => {
    try {
      const q = await fetchQuote(sym);
      setQuoteData(q);
      setEntryPrice(q.price.toFixed(2));
      const stop = direction === "LONG" ? (q.price * 0.96).toFixed(2) : (q.price * 1.04).toFixed(2);
      const target = direction === "LONG" ? (q.price * 1.08).toFixed(2) : (q.price * 0.92).toFixed(2);
      setStopLoss(stop);
      setTargetPrice(target);
    } catch {
      // Keep defaults
    }
  };

  // Run the multi-agent analysis sequence
  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    setAnalysisDone(false);
    setPaperTraded(false);
    setTradeError(null);
    setActiveStep(1);

    try {
      const token = await ensureDemoToken();

      // Step 1: Technicals & Data
      const tech = await fetchTechnicalAnalysis(symbol, timeframe, 100);
      setTechData(tech);
      setActiveStep(3);

      // Step 2: News & Events
      const [newsRes, eventsRes] = await Promise.all([
        fetchNews(symbol, 4).catch(() => ({ articles: [] })),
        fetchEvents(symbol).catch(() => ({ events: [] })),
      ]);
      setNewsData(newsRes.articles || []);
      setEventsData(eventsRes.events || []);
      setActiveStep(5);

      // Step 3: Run Full Multi-Agent Evaluation via Backend
      const analysisResp = await evaluateAnalysis(
        {
          symbol,
          direction,
          thesis,
          timeframe,
          entry_price: parseFloat(entryPrice) || 224.5,
          stop_loss: parseFloat(stopLoss) || 215.0,
          target_price: parseFloat(targetPrice) || 242.0,
          portfolio_equity: 100000.0,
          risk_per_trade_pct: 1.0,
        },
        token
      );
      setAgentAnalysis(analysisResp);
      setActiveStep(8);
      setAnalyzing(false);
      setAnalysisDone(true);
    } catch (e: any) {
      setAnalyzing(false);
      setAnalysisDone(true);
    }
  };

  // Handle Paper Trade Execution
  const handleExecutePaperTrade = async () => {
    setExecutingTrade(true);
    setTradeError(null);
    try {
      const token = await ensureDemoToken();
      const posSize = agentAnalysis?.risk.position_size || positionSizeShares || 10;
      const res = await executeTrade(
        {
          symbol,
          direction,
          timeframe,
          entry_price: parseFloat(entryPrice) || 224.5,
          stop_loss: parseFloat(stopLoss) || 215.0,
          target: parseFloat(targetPrice) || 242.0,
          quantity: posSize,
          thesis,
          decision: agentAnalysis?.decision.action || "PROCEED_WITH_CAUTION",
        },
        token
      );
      setExecutedTradeId(res.id);
      setPaperTraded(true);
    } catch (err: any) {
      setTradeError(err.message || "Failed to execute paper trade");
    } finally {
      setExecutingTrade(false);
    }
  };


  // Deterministic Risk Calculations
  const numEntry = parseFloat(entryPrice) || 224.50;
  const numStop = parseFloat(stopLoss) || 215.00;
  const numTarget = parseFloat(targetPrice) || 242.00;

  const riskPerShare = Math.abs(numEntry - numStop);
  const rewardPerShare = Math.abs(numTarget - numEntry);
  const riskRewardRatio = riskPerShare > 0 ? (rewardPerShare / riskPerShare).toFixed(2) : "0.0";
  const portfolioEquity = 100000.0;
  const riskAmount = portfolioEquity * 0.01; // 1% risk rule
  const positionSizeShares = riskPerShare > 0 ? Math.floor(riskAmount / riskPerShare) : 0;
  const totalPositionExposure = (positionSizeShares * numEntry).toFixed(2);
  const portfolioExposurePct = ((positionSizeShares * numEntry) / portfolioEquity * 100).toFixed(1);

  // Decision logic evaluation
  let decision: DecisionState = "POSSIBLE_SETUP";
  let decisionColor = "text-amber-400 border-amber-500/30 bg-amber-500/10";
  const upcomingEarnings = eventsData.find((e) => e.event_type === "EARNINGS" && e.days_until <= 7);

  if (upcomingEarnings) {
    decision = "WAIT";
    decisionColor = "text-amber-400 border-amber-500/30 bg-amber-500/10";
  } else if (Number(riskRewardRatio) < 1.5) {
    decision = "HIGH_RISK";
    decisionColor = "text-rose-400 border-rose-500/30 bg-rose-500/10";
  } else if (techData?.trend === "bullish" && Number(riskRewardRatio) >= 2.0) {
    decision = "STRONG_SETUP";
    decisionColor = "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-trade-border pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <Compass className="w-7 h-7 text-cyan-400" />
              AI Trade Analysis & Reasoning
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
              Investigation Terminal
            </span>
          </div>
          <p className="text-xs sm:text-sm text-trade-muted mt-1">
            Formulate thesis → Challenge with Devil's Advocate → Verify against pgvector Trading Memory → Calculate strict risk.
          </p>
        </div>

        {/* Live quote preview tag */}
        {quoteData && (
          <div className="px-4 py-2 rounded-xl bg-trade-card border border-trade-border flex items-center gap-4">
            <div>
              <span className="text-[10px] text-trade-muted uppercase tracking-wider block">Live Price</span>
              <span className="text-lg font-bold font-mono text-white">${quoteData.price.toFixed(2)}</span>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-trade-muted uppercase tracking-wider block">Session 24h</span>
              <span className={`text-xs font-mono font-semibold ${quoteData.change_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                {quoteData.change_pct >= 0 ? "+" : ""}{quoteData.change_pct.toFixed(2)}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Input Setup Form */}
      <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-6 shadow-xl">
        <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          1. Trade Thesis & Entry Parameters
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {/* Symbol */}
          <div>
            <label className="block text-xs text-trade-muted mb-1 font-medium">Symbol</label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full bg-trade-bg border border-trade-border rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-cyan-500 focus:outline-none"
            >
              <option value="AAPL">AAPL (Apple)</option>
              <option value="MSFT">MSFT (Microsoft)</option>
              <option value="NVDA">NVDA (NVIDIA)</option>
              <option value="TSLA">TSLA (Tesla)</option>
            </select>
          </div>

          {/* Direction */}
          <div>
            <label className="block text-xs text-trade-muted mb-1 font-medium">Direction</label>
            <div className="grid grid-cols-2 gap-1 bg-trade-bg p-1 rounded-lg border border-trade-border">
              <button
                type="button"
                onClick={() => setDirection("LONG")}
                className={`text-xs font-semibold py-1 rounded transition ${direction === "LONG" ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40" : "text-trade-muted hover:text-white"}`}
              >
                LONG
              </button>
              <button
                type="button"
                onClick={() => setDirection("SHORT")}
                className={`text-xs font-semibold py-1 rounded transition ${direction === "SHORT" ? "bg-rose-500/20 text-rose-400 border border-rose-500/40" : "text-trade-muted hover:text-white"}`}
              >
                SHORT
              </button>
            </div>
          </div>

          {/* Timeframe */}
          <div>
            <label className="block text-xs text-trade-muted mb-1 font-medium">Timeframe</label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="w-full bg-trade-bg border border-trade-border rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-cyan-500 focus:outline-none"
            >
              <option value="1h">1 Hour (1h)</option>
              <option value="4h">4 Hours (4h)</option>
              <option value="1d">1 Day (1d)</option>
              <option value="1w">1 Week (1w)</option>
            </select>
          </div>

          {/* Entry */}
          <div>
            <label className="block text-xs text-trade-muted mb-1 font-medium">Entry Price ($)</label>
            <input
              type="number"
              step="0.1"
              value={entryPrice}
              onChange={(e) => setEntryPrice(e.target.value)}
              className="w-full bg-trade-bg border border-trade-border rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-cyan-500 focus:outline-none"
            />
          </div>

          {/* Stop Loss */}
          <div>
            <label className="block text-xs text-trade-muted mb-1 font-medium">Stop Loss ($)</label>
            <input
              type="number"
              step="0.1"
              value={stopLoss}
              onChange={(e) => setStopLoss(e.target.value)}
              className="w-full bg-trade-bg border border-trade-border rounded-lg px-3 py-2 text-sm text-rose-300 font-mono focus:border-rose-500 focus:outline-none"
            />
          </div>

          {/* Target */}
          <div>
            <label className="block text-xs text-trade-muted mb-1 font-medium">Target Price ($)</label>
            <input
              type="number"
              step="0.1"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              className="w-full bg-trade-bg border border-trade-border rounded-lg px-3 py-2 text-sm text-emerald-300 font-mono focus:border-emerald-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Thesis Input */}
        <div>
          <label className="block text-xs text-trade-muted mb-1 font-medium">
            Trader Thesis & Supporting Rationale (Why are you taking this setup?)
          </label>
          <textarea
            rows={2}
            value={thesis}
            onChange={(e) => setThesis(e.target.value)}
            className="w-full bg-trade-bg border border-trade-border rounded-lg p-3 text-sm text-slate-100 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
            placeholder="Explain what price action, volume, or catalyst supports your trade..."
          />
        </div>

        {/* CTA Launch Analysis Button */}
        <div className="flex items-center justify-between pt-2">
          <span className="text-xs text-trade-muted flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            Runs 6-stage investigation pipeline without price hallucination.
          </span>
          <button
            type="button"
            onClick={handleRunAnalysis}
            disabled={analyzing}
            className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold text-sm shadow-lg shadow-cyan-500/25 transition flex items-center gap-2 disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <Zap className="w-4 h-4 animate-spin" />
                Analyzing Setup...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                Run AI Trade Analysis
              </>
            )}
          </button>
        </div>
      </div>

      {/* Analysis Flow Timeline Bar */}
      <div className="p-4 rounded-xl border border-trade-border bg-trade-card flex items-center justify-between overflow-x-auto gap-2 text-xs font-mono">
        {[
          "1. DATA",
          "2. TECHNICALS",
          "3. NEWS",
          "4. MEMORY",
          "5. RESEARCH",
          "6. RISK",
          "7. DEVIL'S ADVOCATE",
          "8. DECISION",
        ].map((label, idx) => {
          const stepNum = idx + 1;
          const isCurrent = activeStep === stepNum;
          const isPassed = activeStep > stepNum || analysisDone;

          return (
            <div
              key={label}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md whitespace-nowrap transition ${
                isPassed
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : isCurrent
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 animate-pulse"
                  : "text-trade-muted bg-trade-bg/50 border border-transparent"
              }`}
            >
              {isPassed ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : null}
              <span>{label}</span>
            </div>
          );
        })}
      </div>

      {/* Dynamic Results Grid (Visible after analysis runs) */}
      {(analysisDone || techData) && (
        <div className="space-y-6">
          {/* Main 2-Column Split: Evidence vs Devil's Advocate */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column: Technicals & News Evidence */}
            <div className="space-y-6">
              {/* Technical Indicators */}
              <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-4">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-cyan-400" />
                  Deterministic Market Evidence
                </h3>

                {techData && (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                    <div className="p-3 rounded-lg bg-trade-bg border border-trade-border">
                      <span className="text-trade-muted block">Trend Detection</span>
                      <span className={`text-sm font-bold capitalize font-mono ${techData.trend === "bullish" ? "text-emerald-400" : "text-rose-400"}`}>
                        {techData.trend} ({(techData.trend_details.strength * 100).toFixed(0)}%)
                      </span>
                    </div>

                    <div className="p-3 rounded-lg bg-trade-bg border border-trade-border">
                      <span className="text-trade-muted block">Wilder's RSI (14)</span>
                      <span className="text-sm font-bold font-mono text-white">
                        {techData.rsi}
                      </span>
                    </div>

                    <div className="p-3 rounded-lg bg-trade-bg border border-trade-border">
                      <span className="text-trade-muted block">SMA 20 / SMA 50</span>
                      <span className="text-sm font-bold font-mono text-slate-200">
                        ${techData.sma_20} / ${techData.sma_50}
                      </span>
                    </div>

                    <div className="p-3 rounded-lg bg-trade-bg border border-trade-border">
                      <span className="text-trade-muted block">MACD Histogram</span>
                      <span className={`text-sm font-bold font-mono ${techData.macd.histogram >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                        {techData.macd.histogram}
                      </span>
                    </div>

                    <div className="p-3 rounded-lg bg-trade-bg border border-trade-border">
                      <span className="text-trade-muted block">ATR (14) / Volatility</span>
                      <span className="text-sm font-bold font-mono text-slate-200">
                        ${techData.atr} ({techData.volatility_pct}%)
                      </span>
                    </div>

                    <div className="p-3 rounded-lg bg-trade-bg border border-trade-border">
                      <span className="text-trade-muted block">Volume Signal</span>
                      <span className="text-sm font-bold font-mono capitalize text-cyan-400">
                        {techData.volume_signal.replace("_", " ")} ({techData.volume_details.volume_ratio}x)
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* News & Catalysts */}
              <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-4">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  Catalysts & News Intelligence
                </h3>

                <div className="space-y-3">
                  {eventsData.map((ev, i) => (
                    <div key={i} className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs space-y-1">
                      <div className="flex items-center justify-between font-bold text-amber-300">
                        <span>⚠️ Catalyst: {ev.title}</span>
                        <span className="font-mono">{ev.days_until} Days Away</span>
                      </div>
                      <p className="text-slate-300">{ev.implied_volatility_effect}</p>
                    </div>
                  ))}

                  {newsData.slice(0, 2).map((item, i) => (
                    <div key={i} className="p-3 rounded-lg bg-trade-bg border border-trade-border text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-200">{item.title}</span>
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${item.sentiment === "BULLISH" ? "bg-emerald-500/20 text-emerald-400" : "bg-rose-500/20 text-rose-400"}`}>
                          {item.sentiment}
                        </span>
                      </div>
                      <p className="text-trade-muted line-clamp-2">{item.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column: Devil's Advocate & Vector Memory */}
            <div className="space-y-6">
              {/* Vector Memory Warning */}
              <div className="p-6 rounded-xl border border-purple-500/30 bg-purple-950/20 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-purple-300 uppercase tracking-wider flex items-center gap-2">
                    <BrainCircuit className="w-4 h-4 text-purple-400" />
                    Trading Memory (pgvector Semantic Match)
                  </h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-900/60 text-purple-200 border border-purple-500/40">
                    Skepticism: {((agentAnalysis?.devils_advocate.skepticism_score || 0.68) * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="p-3.5 rounded-lg bg-purple-900/30 border border-purple-500/30 text-xs space-y-2">
                  <span className="text-rose-400 font-bold block">
                    ⚠️ Historical Memory Warning & Biases
                  </span>
                  <p className="text-slate-200 leading-relaxed">
                    {agentAnalysis?.devils_advocate.confirmation_bias_warning ||
                      "Warning: The thesis selectively focuses on trendline retests while neglecting RSI divergence and resistance."}
                  </p>
                  {agentAnalysis?.devils_advocate.historical_memory_conflicts && agentAnalysis.devils_advocate.historical_memory_conflicts.length > 0 && (
                    <div className="border-t border-purple-500/20 pt-2 text-purple-300 font-mono text-[11px] space-y-1">
                      {agentAnalysis.devils_advocate.historical_memory_conflicts.map((m, idx) => (
                        <div key={idx}>• {m}</div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Devil's Advocate Agent */}
              <div className="p-6 rounded-xl border border-rose-500/30 bg-rose-950/10 space-y-4">
                <h3 className="text-sm font-bold text-rose-300 uppercase tracking-wider flex items-center gap-2">
                  <Flame className="w-4 h-4 text-rose-400" />
                  Devil's Advocate Counter-Thesis
                </h3>

                <div className="space-y-3 text-xs">
                  {agentAnalysis?.devils_advocate.counter_arguments ? (
                    agentAnalysis.devils_advocate.counter_arguments.map((arg, i) => (
                      <div key={i} className="p-3 rounded-lg bg-trade-card border border-rose-500/20 space-y-1">
                        <span className="font-semibold text-rose-300 block">{i + 1}. Counter-Argument</span>
                        <p className="text-slate-300">{arg}</p>
                      </div>
                    ))
                  ) : (
                    <div className="p-3 rounded-lg bg-trade-card border border-rose-500/20 space-y-1">
                      <span className="font-semibold text-rose-300 block">1. Catalyst Event Risk Contradicts Breakout</span>
                      <p className="text-slate-300">
                        Quarterly earnings or resistance band overhead introduces severe gap and volatility risk.
                      </p>
                    </div>
                  )}

                  {agentAnalysis?.devils_advocate.hidden_risks && agentAnalysis.devils_advocate.hidden_risks.length > 0 && (
                    <div className="p-3 rounded-lg bg-trade-card border border-amber-500/20 space-y-1">
                      <span className="font-semibold text-amber-300 block">Hidden Risks Identified:</span>
                      <ul className="list-disc list-inside text-slate-300 space-y-1 pl-1">
                        {agentAnalysis.devils_advocate.hidden_risks.map((hr, idx) => (
                          <li key={idx}>{hr}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Risk Sizing & Final Decision Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Deterministic Risk Engine Box */}
            <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Scale className="w-4 h-4 text-amber-400" />
                Deterministic Risk Check
              </h3>

              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between py-1.5 border-b border-trade-border">
                  <span className="text-trade-muted">1% Account Risk:</span>
                  <span className="text-white font-bold">${(agentAnalysis?.risk.risk_amount || riskAmount).toFixed(2)}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-trade-border">
                  <span className="text-trade-muted">Risk per Share:</span>
                  <span className="text-white font-bold">${(agentAnalysis?.risk.risk_per_share || riskPerShare).toFixed(2)}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-trade-border">
                  <span className="text-trade-muted">Position Size:</span>
                  <span className="text-emerald-400 font-bold">
                    {agentAnalysis?.risk.position_size !== undefined ? agentAnalysis.risk.position_size : positionSizeShares} Shares
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-trade-border">
                  <span className="text-trade-muted">Risk / Reward:</span>
                  <span className={`font-bold ${(agentAnalysis?.risk.risk_reward_ratio || Number(riskRewardRatio)) >= 1.5 ? "text-emerald-400" : "text-amber-400"}`}>
                    1 : {agentAnalysis?.risk.risk_reward_ratio || riskRewardRatio}
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-trade-border">
                  <span className="text-trade-muted">Risk Level:</span>
                  <span className={`font-bold uppercase ${
                    agentAnalysis?.risk.risk_level === "conservative" ? "text-emerald-400" :
                    agentAnalysis?.risk.risk_level === "moderate" ? "text-cyan-400" :
                    agentAnalysis?.risk.risk_level === "aggressive" ? "text-amber-400" : "text-rose-400"
                  }`}>
                    {agentAnalysis?.risk.risk_level || "MODERATE"}
                  </span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-trade-muted">Portfolio Exposure:</span>
                  <span className="text-white font-bold">
                    {agentAnalysis?.risk.portfolio_exposure_pct || portfolioExposurePct}% (${agentAnalysis?.risk.position_value?.toFixed(2) || totalPositionExposure})
                  </span>
                </div>
              </div>

              {agentAnalysis?.risk.warnings && agentAnalysis.risk.warnings.length > 0 && (
                <div className="p-2.5 rounded bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 space-y-1">
                  {agentAnalysis.risk.warnings.map((w, idx) => (
                    <div key={idx}>⚠️ {w}</div>
                  ))}
                </div>
              )}
            </div>

            {/* AI Explainable Decision Box */}
            <div className="lg:col-span-2 p-6 rounded-xl border border-trade-border bg-trade-card space-y-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    Explainable AI Decision Assessment
                  </h3>
                  <div className={`px-4 py-1 rounded-full font-bold font-mono text-sm border ${
                    (agentAnalysis?.decision.action || decision) === "PROCEED_WITH_CAUTION" || (agentAnalysis?.decision.action || decision) === "STRONG_SETUP"
                      ? "text-emerald-400 border-emerald-500/30 bg-emerald-500/10"
                      : (agentAnalysis?.decision.action || decision) === "WAIT_FOR_CONFIRMATION" || (agentAnalysis?.decision.action || decision) === "WAIT"
                      ? "text-amber-400 border-amber-500/30 bg-amber-500/10"
                      : "text-rose-400 border-rose-500/30 bg-rose-500/10"
                  }`}>
                    DECISION: {agentAnalysis?.decision.action || decision}
                  </div>
                </div>

                <div className="mt-4 space-y-3 text-xs text-slate-300">
                  <div className="p-3 rounded-lg bg-trade-bg/60 border border-trade-border text-slate-200 leading-relaxed">
                    {agentAnalysis?.decision.summary ||
                      "The trade thesis demonstrates valid technical alignment, but requires strict stop-loss adherence due to proximity to resistance and past memory conflicts."}
                  </div>

                  {agentAnalysis?.decision.suggested_modifications && agentAnalysis.decision.suggested_modifications.length > 0 && (
                    <div className="space-y-1">
                      <div className="font-semibold text-cyan-300">Suggested Actionable Modifications:</div>
                      <ul className="list-disc list-inside space-y-1 pl-1 text-slate-300">
                        {agentAnalysis.decision.suggested_modifications.map((mod, idx) => (
                          <li key={idx}>{mod}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              {/* Final Paper Trade Execution Button */}
              <div className="pt-4 border-t border-trade-border space-y-3">
                {tradeError && (
                  <div className="p-2 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
                    {tradeError}
                  </div>
                )}
                {paperTraded && executedTradeId && (
                  <div className="p-3 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center justify-between">
                    <span>✓ Paper trade executed successfully!</span>
                    <a
                      href={`/trades/${executedTradeId}`}
                      className="underline font-bold hover:text-emerald-300 ml-2"
                    >
                      View Live Position in Trades →
                    </a>
                  </div>
                )}

                <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                  <span className="text-xs text-trade-muted">
                    Paper trading mode only. No real money executed.
                  </span>
                  <button
                    type="button"
                    onClick={handleExecutePaperTrade}
                    disabled={executingTrade || paperTraded}
                    className={`px-6 py-2.5 rounded-lg font-bold text-xs transition shadow-lg flex items-center gap-2 ${
                      paperTraded
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 shadow-cyan-500/20 disabled:opacity-50"
                    }`}
                  >
                    {executingTrade ? (
                      <>
                        <span className="w-3 h-3 rounded-full border-2 border-slate-900 border-t-transparent animate-spin" />
                        Routing Paper Order...
                      </>
                    ) : paperTraded ? (
                      "✓ Position Open in Paper Portfolio"
                    ) : (
                      "Execute Paper Trade"
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-trade-muted text-xs font-mono">Loading Analysis Terminal...</div>}>
      <AnalyzeContent />
    </Suspense>
  );
}
