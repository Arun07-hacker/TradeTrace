"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { BrainCircuit, Lock, Mail, ArrowRight, AlertCircle } from "lucide-react";
import { loginUser } from "@/services/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await loginUser({ email, password });
      if (typeof window !== "undefined") {
        localStorage.setItem("tradetrace_token", res.access_token);
      }
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to authenticate");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md p-8 rounded-2xl border border-trade-border bg-trade-card shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-2">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Welcome Back to TradeTrace</h1>
          <p className="text-xs text-trade-muted">
            Access your AI paper trading terminal and cognitive memory journal.
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
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-trade-bg border border-trade-border rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 text-slate-950 font-bold text-xs transition shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In to Terminal"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="text-center text-xs text-trade-muted">
          Don't have an account?{" "}
          <Link href="/register" className="text-cyan-400 hover:underline font-medium">
            Create Paper Account
          </Link>
        </div>
      </div>
    </div>
  );
}
