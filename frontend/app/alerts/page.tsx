"use client";

import React, { useState, useEffect } from "react";
import { Bell, AlertTriangle, CheckCircle2, ShieldAlert, Zap, Clock, RefreshCw } from "lucide-react";
import { fetchAlerts, markAlertRead, markAllAlertsRead, runMonitoringCheck, ensureDemoToken } from "@/services/api";
import { AlertItem } from "@/types";

const defaultMockAlerts: AlertItem[] = [
  {
    id: "alt-1",
    user_id: "demo",
    symbol: "TSLA",
    alert_type: "MAJOR_NEWS",
    title: "Earnings Catalyst Approaching",
    message: "Q3 Earnings announcement scheduled in 6 days. Historical memory warning active for pre-earnings breakout setups.",
    severity: "CRITICAL",
    is_read: false,
    created_at: new Date(Date.now() - 12 * 60000).toISOString(),
  },
  {
    id: "alt-2",
    user_id: "demo",
    symbol: "AAPL",
    alert_type: "STOP_APPROACHING",
    title: "Price Approaching Stop Loss",
    message: "AAPL price ($221.20) is within 1.5% of protective paper stop loss ($218.00).",
    severity: "WARNING",
    is_read: false,
    created_at: new Date(Date.now() - 60 * 60000).toISOString(),
  },
  {
    id: "alt-3",
    user_id: "demo",
    symbol: "NVDA",
    alert_type: "TARGET_APPROACHING",
    title: "Price Approaching Profit Target",
    message: "NVDA price ($126.80) is within 2.0% of primary take-profit level ($129.50).",
    severity: "INFO",
    is_read: true,
    created_at: new Date(Date.now() - 180 * 60000).toISOString(),
  },
];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>(defaultMockAlerts);
  const [scanning, setScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState<string | null>(null);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const token = await ensureDemoToken();
      const live = await fetchAlerts(token);
      if (live && live.length > 0) {
        setAlerts(live);
      } else {
        setAlerts(defaultMockAlerts);
      }
    } catch {
      setAlerts(defaultMockAlerts);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      const token = await ensureDemoToken();
      await markAllAlertsRead(token);
      setAlerts(alerts.map((a) => ({ ...a, is_read: true })));
    } catch {
      setAlerts(alerts.map((a) => ({ ...a, is_read: true })));
    }
  };

  const handleMarkRead = async (id: string) => {
    try {
      const token = await ensureDemoToken();
      await markAlertRead(id, token);
      setAlerts(alerts.map((a) => (a.id === id ? { ...a, is_read: true } : a)));
    } catch {
      setAlerts(alerts.map((a) => (a.id === id ? { ...a, is_read: true } : a)));
    }
  };

  const handleRunScan = async () => {
    setScanning(true);
    setScanMessage(null);
    try {
      const token = await ensureDemoToken();
      const res = await runMonitoringCheck(token);
      setScanMessage(
        `Scan complete: Checked ${res.checked_trades_count} open trades, triggered ${res.triggered_events_count} events, created ${res.alerts_created_count} alerts.`
      );
      await loadAlerts();
    } catch (err: any) {
      setScanMessage(err.message || "Failed to execute scan");
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-trade-border pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Bell className="w-7 h-7 text-cyan-400" />
            Alerts & Notification Center
          </h1>
          <p className="text-xs sm:text-sm text-trade-muted mt-1">
            Real-time monitoring triggers, stop-loss proximity warnings, and memory conflict signals.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleRunScan}
            disabled={scanning}
            className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-xs text-slate-950 font-bold transition flex items-center gap-1.5 shadow-lg shadow-cyan-500/20"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${scanning ? "animate-spin" : ""}`} />
            {scanning ? "Scanning Open Trades..." : "Run Monitoring Scan"}
          </button>
          <button
            type="button"
            onClick={handleMarkAllRead}
            className="px-3.5 py-1.5 rounded-lg bg-trade-card hover:bg-trade-cardHover text-xs text-slate-300 border border-trade-border transition"
          >
            Mark all as read
          </button>
        </div>
      </div>

      {scanMessage && (
        <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs flex items-center gap-2">
          <Zap className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>{scanMessage}</span>
        </div>
      )}

      {/* Alerts List */}
      <div className="space-y-3">
        {alerts.map((alert) => {
          const isCritical = alert.severity === "CRITICAL";
          const isWarning = alert.severity === "WARNING";

          return (
            <div
              key={alert.id}
              className={`p-5 rounded-xl border transition flex items-start justify-between gap-4 ${
                !alert.is_read
                  ? isCritical
                    ? "bg-rose-950/20 border-rose-500/40"
                    : isWarning
                    ? "bg-amber-950/20 border-amber-500/40"
                    : "bg-cyan-950/20 border-cyan-500/40"
                  : "bg-trade-card border-trade-border opacity-70"
              }`}
            >
              <div className="flex items-start gap-3.5">
                <div className="mt-0.5">
                  {isCritical && <ShieldAlert className="w-5 h-5 text-rose-400" />}
                  {isWarning && <AlertTriangle className="w-5 h-5 text-amber-400" />}
                  {!isCritical && !isWarning && <Zap className="w-5 h-5 text-cyan-400" />}
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {alert.symbol && (
                      <span className="font-mono text-xs font-bold text-white bg-trade-bg px-2 py-0.5 rounded border border-trade-border">
                        {alert.symbol}
                      </span>
                    )}
                    <h3 className="text-sm font-semibold text-white">{alert.title}</h3>
                    <span className="text-[10px] font-mono text-trade-muted">• {alert.alert_type}</span>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">{alert.message}</p>

                  <div className="flex items-center gap-1.5 text-[10px] text-trade-muted font-mono pt-1">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(alert.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {!alert.is_read && (
                <button
                  type="button"
                  onClick={() => handleMarkRead(alert.id)}
                  className="text-xs text-trade-muted hover:text-white transition shrink-0"
                >
                  Mark read
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
