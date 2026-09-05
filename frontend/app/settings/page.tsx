"use client";

import React, { useState } from "react";
import { Settings as SettingsIcon, Shield, Sliders, Bell, User, CheckCircle2 } from "lucide-react";

export default function SettingsPage() {
  const [preferredMarket, setPreferredMarket] = useState("US_EQUITIES");
  const [riskPreference, setRiskPreference] = useState("MODERATE");
  const [riskPerTrade, setRiskPerTrade] = useState("1.0");
  const [maxExposure, setMaxExposure] = useState("50.0");
  const [enableMemoryWarnings, setEnableMemoryWarnings] = useState(true);
  const [enableMonitoringAlerts, setEnableMonitoringAlerts] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-trade-border pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <SettingsIcon className="w-7 h-7 text-cyan-400" />
            Trading Preferences & Risk Settings
          </h1>
          <p className="text-xs sm:text-sm text-trade-muted mt-1">
            Configure risk tolerance parameters, market preferences, and vector memory guardrails.
          </p>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Risk Governance Section */}
        <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-6">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Shield className="w-4 h-4 text-amber-400" />
            Risk Governance Parameters
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs text-trade-muted mb-1 font-medium">Risk Tolerance Profile</label>
              <select
                value={riskPreference}
                onChange={(e) => setRiskPreference(e.target.value)}
                className="w-full bg-trade-bg border border-trade-border rounded-lg px-3 py-2 text-xs text-white focus:border-cyan-500 focus:outline-none"
              >
                <option value="CONSERVATIVE">Conservative (0.5% max risk)</option>
                <option value="MODERATE">Moderate (1.0% standard risk)</option>
                <option value="AGGRESSIVE">Aggressive (2.0% max risk)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-trade-muted mb-1 font-medium">Preferred Market</label>
              <select
                value={preferredMarket}
                onChange={(e) => setPreferredMarket(e.target.value)}
                className="w-full bg-trade-bg border border-trade-border rounded-lg px-3 py-2 text-xs text-white focus:border-cyan-500 focus:outline-none"
              >
                <option value="US_EQUITIES">US Equities (NASDAQ / NYSE)</option>
                <option value="CRYPTO">Cryptocurrencies</option>
                <option value="FOREX">Global Foreign Exchange</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-trade-muted mb-1 font-medium">Default Risk per Trade (%)</label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="5.0"
                value={riskPerTrade}
                onChange={(e) => setRiskPerTrade(e.target.value)}
                className="w-full bg-trade-bg border border-trade-border rounded-lg px-3 py-2 text-xs text-white font-mono focus:border-cyan-500 focus:outline-none"
              />
              <span className="text-[11px] text-trade-muted mt-1 block">Recommended: 1.0% per setup.</span>
            </div>

            <div>
              <label className="block text-xs text-trade-muted mb-1 font-medium">Maximum Total Portfolio Exposure (%)</label>
              <input
                type="number"
                step="1.0"
                min="10.0"
                max="100.0"
                value={maxExposure}
                onChange={(e) => setMaxExposure(e.target.value)}
                className="w-full bg-trade-bg border border-trade-border rounded-lg px-3 py-2 text-xs text-white font-mono focus:border-cyan-500 focus:outline-none"
              />
              <span className="text-[11px] text-trade-muted mt-1 block">Caps aggregate open paper capital.</span>
            </div>
          </div>
        </div>

        {/* AI & Memory Toggles */}
        <div className="p-6 rounded-xl border border-trade-border bg-trade-card space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-purple-400" />
            Trading Memory & Monitoring Guardrails
          </h2>

          <div className="space-y-4 text-xs">
            <label className="flex items-center justify-between p-3 rounded-lg bg-trade-bg border border-trade-border cursor-pointer">
              <div>
                <span className="font-semibold text-white block">Enable Vector Memory Warnings</span>
                <span className="text-trade-muted">
                  Automatically alert when a new setup matches historical trades that suffered losses.
                </span>
              </div>
              <input
                type="checkbox"
                checked={enableMemoryWarnings}
                onChange={(e) => setEnableMemoryWarnings(e.target.checked)}
                className="w-4 h-4 accent-cyan-500 rounded"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-lg bg-trade-bg border border-trade-border cursor-pointer">
              <div>
                <span className="font-semibold text-white block">Enable Position Monitoring Alerts</span>
                <span className="text-trade-muted">
                  Trigger notifications when price approaches stop loss or high-impact news occurs.
                </span>
              </div>
              <input
                type="checkbox"
                checked={enableMonitoringAlerts}
                onChange={(e) => setEnableMonitoringAlerts(e.target.checked)}
                className="w-4 h-4 accent-cyan-500 rounded"
              />
            </label>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex items-center justify-between">
          {saved && (
            <span className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
              <CheckCircle2 className="w-4 h-4" /> Preferences saved successfully.
            </span>
          )}
          <div className="ml-auto">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 text-slate-950 font-bold text-xs transition shadow-lg shadow-cyan-500/20"
            >
              Save Preferences
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
