"use client";

import React, { useState, useEffect } from "react";
import { 
  BrainCircuit, 
  Search, 
  AlertTriangle, 
  Flame, 
  History, 
  CheckCircle2, 
  BookOpen, 
  Sparkles,
  Plus
} from "lucide-react";
import { searchTradingMemory, fetchTradeLessons, createTradeLesson, ensureDemoToken } from "@/services/api";
import { MemorySearchResultItem, TradeLesson } from "@/types";

const fallbackMemories: MemorySearchResultItem[] = [
  {
    id: "mem-01",
    type: "lesson",
    title: "Earnings Roulette: Chasing Breakouts Right Before Reports",
    similarity_score: 0.94,
    content: "Entering a high-volatility momentum breakout less than 48 hours prior to earnings turns disciplined setups into a 50/50 binary gamble.",
    rule_or_mistake: "NEVER enter a directional swing trade within 48 hours of an unhedged earnings announcement.",
    symbol: "TSLA",
    outcome: "LOSS",
  },
  {
    id: "mem-02",
    type: "lesson",
    title: "Averaging Down on Systematic Technical Breakdown",
    similarity_score: 0.88,
    content: "Adding shares to a losing position when key support has cracked converts controlled 1% risk into severe account drawdown.",
    rule_or_mistake: "The stop-loss is ABSOLUTE. Never add size to an underwater position.",
    symbol: "AAPL",
    outcome: "LOSS",
  },
  {
    id: "mem-03",
    type: "lesson",
    title: "Timeframe Myopia: Trading 5-Min Breakout Directly into Daily Resistance",
    similarity_score: 0.82,
    content: "A strong 5-minute green candle stalls and reverses violently when slamming directly into daily/weekly supply overhead.",
    rule_or_mistake: "Always verify Daily and 4-Hour key resistance levels before taking breakout entries.",
    symbol: "MSFT",
    outcome: "WIN",
  },
];

export default function MemoryPage() {
  const [query, setQuery] = useState("breakout before earnings");
  const [results, setResults] = useState<MemorySearchResultItem[]>(fallbackMemories);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);

  // New Lesson form
  const [newTitle, setNewTitle] = useState("");
  const [newSetupType, setNewSetupType] = useState("Breakout");
  const [newMistake, setNewMistake] = useState("");
  const [newLesson, setNewLesson] = useState("");
  const [newRule, setNewRule] = useState("");
  const [savingLesson, setSavingLesson] = useState(false);

  useEffect(() => {
    handleSearch(query);
  }, []);

  const handleSearch = async (q: string) => {
    if (!q || q.length < 2) return;
    setLoading(true);
    try {
      const token = await ensureDemoToken();
      const res = await searchTradingMemory(q, token, 6);
      if (res && res.results && res.results.length > 0) {
        setResults(res.results);
      } else {
        setResults(fallbackMemories);
      }
    } catch {
      setResults(fallbackMemories);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLesson = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingLesson(true);
    try {
      const token = await ensureDemoToken();
      await createTradeLesson(
        {
          title: newTitle,
          setup_type: newSetupType,
          mistake_type: newMistake,
          lesson: newLesson,
          future_rule: newRule,
        },
        token
      );
      setShowAddModal(false);
      setNewTitle("");
      setNewMistake("");
      setNewLesson("");
      setNewRule("");
      handleSearch(query);
    } catch (err) {
      console.error(err);
    } finally {
      setSavingLesson(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-trade-border pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
              <BrainCircuit className="w-7 h-7 text-purple-400" />
              Trading Memory & Cognitive Knowledge Bank
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/30 font-mono">
              pgvector 1536-dim Cosine Search
            </span>
          </div>
          <p className="text-xs sm:text-sm text-trade-muted mt-1">
            Semantic vector memory automatically matching upcoming setups against past lessons, autopsies, and Devil's Advocate warnings.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs transition shadow-lg shadow-purple-500/20"
        >
          <Plus className="w-4 h-4" />
          Add Trading Lesson
        </button>
      </div>

      {/* Semantic Search Box */}
      <div className="p-6 rounded-xl border border-purple-500/30 bg-gradient-to-r from-purple-950/30 via-trade-card to-trade-card space-y-4 shadow-xl">
        <label className="block text-xs font-bold text-purple-300 uppercase tracking-wider">
          Query Cognitive Trade Memory (Vector Cosine Similarity)
        </label>
        <div className="relative">
          <Search className="w-5 h-5 text-purple-400 absolute left-4 top-3.5" />
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              handleSearch(e.target.value);
            }}
            placeholder="e.g. Breakout before earnings announcement, low volume breakout..."
            className="w-full bg-trade-bg/90 border border-purple-500/40 rounded-xl pl-12 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-400 font-mono"
          />
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs text-trade-muted">
          <span>Try quick searches:</span>
          {["breakout before earnings", "averaging down on falling knife", "ignoring daily resistance", "revenge trading"].map((preset) => (
            <button
              key={preset}
              type="button"
              onClick={() => {
                setQuery(preset);
                handleSearch(preset);
              }}
              className="px-2.5 py-0.5 rounded bg-trade-card hover:bg-purple-900/40 text-purple-300 border border-purple-500/20 font-mono text-[11px] transition"
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {/* Add Lesson Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-trade-card border border-purple-500/40 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <BrainCircuit className="w-5 h-5 text-purple-400" />
              Record Permanent Operating Rule
            </h2>
            <form onSubmit={handleCreateLesson} className="space-y-3 text-xs">
              <div>
                <label className="block text-trade-muted mb-1">Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Do not trade before FOMC rate decisions"
                  className="w-full bg-trade-bg border border-trade-border rounded-lg p-2.5 text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-trade-muted mb-1">Setup Type</label>
                  <input
                    type="text"
                    required
                    value={newSetupType}
                    onChange={(e) => setNewSetupType(e.target.value)}
                    className="w-full bg-trade-bg border border-trade-border rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-trade-muted mb-1">Mistake Category</label>
                  <input
                    type="text"
                    required
                    value={newMistake}
                    onChange={(e) => setNewMistake(e.target.value)}
                    placeholder="e.g. FOMO / Slippage"
                    className="w-full bg-trade-bg border border-trade-border rounded-lg p-2.5 text-white"
                  />
                </div>
              </div>
              <div>
                <label className="block text-trade-muted mb-1">Core Lesson</label>
                <textarea
                  required
                  rows={2}
                  value={newLesson}
                  onChange={(e) => setNewLesson(e.target.value)}
                  placeholder="What was the fundamental lesson?"
                  className="w-full bg-trade-bg border border-trade-border rounded-lg p-2.5 text-white"
                />
              </div>
              <div>
                <label className="block text-purple-300 font-semibold mb-1">Actionable Future Rule (Negative Constraint)</label>
                <textarea
                  required
                  rows={2}
                  value={newRule}
                  onChange={(e) => setNewRule(e.target.value)}
                  placeholder="e.g. Flat all open day trades 15 minutes before FOMC statement."
                  className="w-full bg-trade-bg border border-purple-500/40 rounded-lg p-2.5 text-white"
                />
              </div>
              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg border border-trade-border text-trade-muted hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingLesson}
                  className="px-5 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-bold"
                >
                  {savingLesson ? "Vectorizing & Saving..." : "Save Rule to Memory"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Memory Results */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs text-trade-muted">
          <span>Found {results.length} semantically matching rules & memories</span>
          <span className="font-mono">{loading ? "Computing embeddings..." : "pgvector Cosine Match"}</span>
        </div>

        <div className="space-y-4">
          {results.map((mem) => {
            const isLoss = mem.outcome === "LOSS" || !mem.outcome;
            return (
              <div
                key={mem.id}
                className="p-6 rounded-xl border border-trade-border bg-trade-card hover:border-purple-500/40 transition space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-trade-border pb-3">
                  <div className="flex items-center gap-3 flex-wrap">
                    {mem.symbol && <span className="text-base font-bold text-white">{mem.symbol}</span>}
                    <span className="text-sm font-semibold text-slate-200">— {mem.title}</span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                      isLoss
                        ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                        : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                    }`}>
                      {mem.type.toUpperCase()}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 font-mono text-xs text-purple-300">
                    <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                    <span>Cosine Similarity: {(mem.similarity_score * 100).toFixed(1)}%</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="p-3.5 rounded-lg bg-trade-bg border border-trade-border space-y-1">
                    <span className="text-trade-muted font-medium block">Lesson & Context:</span>
                    <p className="text-slate-200 leading-relaxed">{mem.content}</p>
                  </div>

                  <div className="p-3.5 rounded-lg bg-purple-950/20 border border-purple-500/30 space-y-1">
                    <span className="text-purple-300 font-medium block flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-purple-400" />
                      Operating Rule to Adhere To:
                    </span>
                    <p className="text-purple-100 font-mono text-xs leading-relaxed">
                      {mem.rule_or_mistake || "Always respect predetermined stop loss."}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
