"use client";

import React, { useState } from "react";
import { BookOpen, Sparkles, Filter, Calendar, Tag, ShieldCheck, CheckCircle2 } from "lucide-react";

interface LessonCard {
  id: string;
  rule_number: number;
  title: string;
  setup_type: string;
  mistake_type: string;
  lesson: string;
  future_rule: string;
  times_applied: number;
}

const mockLessons: LessonCard[] = [
  {
    id: "les-01",
    rule_number: 1,
    title: "Pre-Earnings Breakout Trap Avoidance",
    setup_type: "Breakout",
    mistake_type: "Event Volatility Ignored",
    lesson: "High implied event volatility crushes breakout validity 70% of the time, resulting in immediate false breaks and gap risk.",
    future_rule: "Never initiate breakout trades within 4 days of an upcoming quarterly earnings report.",
    times_applied: 5,
  },
  {
    id: "les-02",
    rule_number: 2,
    title: "Breakout Volume Confirmation Requirement",
    setup_type: "Resistance Breakout",
    mistake_type: "Low Volume Traps",
    lesson: "Entering breakouts without institutional volume expansion leaves the trade vulnerable to mean-reversion retests.",
    future_rule: "Require breakout candle volume to exceed 1.4x the 20-day average volume before entry.",
    times_applied: 8,
  },
  {
    id: "les-03",
    rule_number: 3,
    title: "1% Maximum Risk Discipline",
    setup_type: "Position Sizing",
    mistake_type: "Emotional Over-Leverage",
    lesson: "Widening stop losses or exceeding 1% portfolio risk per trade destroys equity curves during adverse market volatility regimes.",
    future_rule: "Calculate position size strictly as (1% Account Risk) / (Entry - Stop). Never widen a stop.",
    times_applied: 19,
  },
];

export default function JournalPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-trade-border pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <BookOpen className="w-7 h-7 text-cyan-400" />
            Trading Journal & Lesson Repository
          </h1>
          <p className="text-xs sm:text-sm text-trade-muted mt-1">
            Curated operating rules generated from closed trade autopsies to prevent repeated cognitive biases.
          </p>
        </div>
      </div>

      {/* Rules Bank */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs text-trade-muted">
          <span>Active Operating Rules ({mockLessons.length})</span>
          <span className="font-mono">Auto-Queried During Setup Analysis</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockLessons.map((item) => (
            <div
              key={item.id}
              className="p-6 rounded-xl border border-trade-border bg-trade-card flex flex-col justify-between space-y-4 hover:border-cyan-500/40 transition shadow-lg"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    Rule #{item.rule_number}
                  </span>
                  <span className="text-[10px] font-mono text-trade-muted flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    Applied {item.times_applied}x
                  </span>
                </div>

                <h3 className="text-base font-bold text-white leading-snug">{item.title}</h3>

                <div className="space-y-2 text-xs">
                  <div className="p-3 rounded-lg bg-trade-bg border border-trade-border space-y-1">
                    <span className="text-trade-muted block text-[10px] uppercase font-mono">Autopsy Lesson</span>
                    <p className="text-slate-300 leading-relaxed">{item.lesson}</p>
                  </div>

                  <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/30 space-y-1">
                    <span className="text-emerald-400 block text-[10px] uppercase font-mono font-bold">Future Operating Rule</span>
                    <p className="text-emerald-200 leading-relaxed font-medium">{item.future_rule}</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-trade-border text-[10px] text-trade-muted font-mono">
                <span>Setup: {item.setup_type}</span>
                <span className="text-rose-400">Mistake: {item.mistake_type}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
