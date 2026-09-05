"use client";

import React, { useEffect, useState } from "react";
import { HealthStatus } from "@/types";
import { fetchHealth } from "@/services/api";
import { Activity, CheckCircle2, AlertTriangle, ShieldCheck } from "lucide-react";

export function HealthBadge() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    fetchHealth()
      .then((data) => {
        if (mounted) {
          setHealth(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="flex items-center gap-2 text-xs">
      {/* Demo Data Tag as mandated */}
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-medium">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
        Demo Data Mode
      </span>

      {/* Backend Status */}
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-trade-card border border-trade-border">
        {loading ? (
          <>
            <Activity className="w-3.5 h-3.5 text-trade-muted animate-pulse" />
            <span className="text-trade-muted">Connecting Backend...</span>
          </>
        ) : error ? (
          <>
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
            <span className="text-rose-400 font-mono">Backend Offline</span>
          </>
        ) : (
          <>
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            <span className="text-emerald-400 font-mono">
              API v{health?.version} OK
            </span>
          </>
        )}
      </div>

      {/* Safety Badge */}
      <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
        <ShieldCheck className="w-3.5 h-3.5" />
        Paper Trading Only
      </span>
    </div>
  );
}
