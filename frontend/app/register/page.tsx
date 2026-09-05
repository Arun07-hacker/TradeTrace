"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { BrainCircuit, Lock, Mail, User as UserIcon, ArrowRight, AlertCircle, ShieldCheck } from "lucide-react";
import { registerUser } from "@/services/api";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [preferredMarket, setPreferredMarket] = useState("US_EQUITIES");
  const [riskPreference, setRiskPreference] = useState("MODERATE");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await registerUser({
        name,
        email,
        password,
        preferred_market: preferredMarket,
        risk_preference: riskPreference,
      });
      if (typeof window !== "undefined") {
        localStorage.setItem("tradetrace_token", res.access_token);
      }
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to create account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md p-8 rounded-2xl border border-trade-border bg-trade-card shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-2">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Create Trader Account</h1>
          <p className="text-xs text-trade-muted">
            Provisions a $100,000 paper trading portfolio with vector cognitive memory.
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-trade-muted mb-1 font-medium">Full Name</label>
            <div className="relative">
              <UserIcon className="w-4 h-4 text-trade-muted absolute left-3 top-2.5" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alex Morgan"
                className="w-full bg-trade-bg border border-trade-border rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-trade-muted mb-1 font-medium">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-trade-muted absolute left-3 top-2.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="trader@tradetrace.io"
                className="w-full bg-trade-bg border border-trade-border rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-trade-muted mb-1 font-medium">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-trade-muted absolute left-3 top-2.5" />
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-trade-bg border border-trade-border rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-trade-muted mb-1 font-medium">Market Focus</label>
              <select
                value={preferredMarket}
                onChange={(e) => setPreferredMarket(e.target.value)}
                className="w-full bg-trade-bg border border-trade-border rounded-lg px-2.5 py-2 text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="US_EQUITIES">US Equities</option>
                <option value="CRYPTO">Crypto</option>
                <option value="FOREX">Forex</option>
              </select>
            </div>

            <div>
              <label className="block text-trade-muted mb-1 font-medium">Risk Tolerance</label>
              <select
                value={riskPreference}
                onChange={(e) => setRiskPreference(e.target.value)}
                className="w-full bg-trade-bg border border-trade-border rounded-lg px-2.5 py-2 text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="CONSERVATIVE">Conservative</option>
                <option value="MODERATE">Moderate (1%)</option>
                <option value="AGGRESSIVE">Aggressive</option>
              </select>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-[11px] flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 shrink-0 text-cyan-400" />
            <span>Includes auto-provisioned $100,000 paper trading cash.</span>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 text-slate-950 font-bold text-xs transition shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? "Provisioning Account..." : "Create Paper Trading Account"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="text-center text-xs text-trade-muted">
          Already have an account?{" "}
          <Link href="/login" className="text-cyan-400 hover:underline font-medium">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
