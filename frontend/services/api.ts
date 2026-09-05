import { HealthStatus, AuthTokenResponse, UserProfile, UserPreference } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE_URL}/health`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch health status: ${res.statusText}`);
  }
  return res.json();
}

export async function registerUser(payload: {
  name: string;
  email: string;
  password: string;
  preferred_market?: string;
  risk_preference?: string;
}): Promise<AuthTokenResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Registration failed");
  }
  return res.json();
}

export async function loginUser(payload: {
  email: string;
  password: string;
}): Promise<AuthTokenResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Login failed");
  }
  return res.json();
}

export function getStoredToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("tradetrace_token");
  }
  return null;
}

export async function ensureDemoToken(): Promise<string> {
  const existing = getStoredToken();
  if (existing) return existing;

  try {
    const res = await loginUser({ email: "demo@tradetrace.io", password: "DemoPassword123!" });
    if (typeof window !== "undefined") {
      localStorage.setItem("tradetrace_token", res.access_token);
    }
    return res.access_token;
  } catch {
    try {
      const reg = await registerUser({
        name: "Demo Trader",
        email: "demo@tradetrace.io",
        password: "DemoPassword123!",
      });
      if (typeof window !== "undefined") {
        localStorage.setItem("tradetrace_token", reg.access_token);
      }
      return reg.access_token;
    } catch {
      return "";
    }
  }
}

export async function getCurrentUser(token: string): Promise<UserProfile> {
  const res = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch user profile");
  }
  return res.json();
}


export async function updateUserPreferences(
  token: string,
  preferences: Partial<UserPreference>
): Promise<UserPreference> {
  const res = await fetch(`${API_BASE_URL}/auth/preferences`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(preferences),
  });
  if (!res.ok) {
    throw new Error("Failed to update preferences");
  }
  return res.json();
}

export async function fetchSymbols(): Promise<any[]> {
  const res = await fetch(`${API_BASE_URL}/market/symbols`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Failed to fetch supported symbols");
  }
  return res.json();
}

export async function fetchQuote(symbol: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/market/${encodeURIComponent(symbol)}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch quote for ${symbol}`);
  }
  return res.json();
}

export async function fetchHistory(
  symbol: string,
  timeframe: string = "1d",
  limit: number = 100
): Promise<any> {
  const res = await fetch(
    `${API_BASE_URL}/market/${encodeURIComponent(symbol)}/history?timeframe=${timeframe}&limit=${limit}`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch history for ${symbol}`);
  }
  return res.json();
}

export async function fetchTechnicalAnalysis(
  symbol: string,
  timeframe: string = "1d",
  limit: number = 100
): Promise<any> {
  const res = await fetch(
    `${API_BASE_URL}/technical/${encodeURIComponent(symbol)}?timeframe=${timeframe}&limit=${limit}`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch technical analysis for ${symbol}`);
  }
  return res.json();
}

export async function fetchNews(symbol: string, limit: number = 10): Promise<any> {
  const res = await fetch(
    `${API_BASE_URL}/news/${encodeURIComponent(symbol)}?limit=${limit}`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch news for ${symbol}`);
  }
  return res.json();
}

export async function fetchEvents(symbol: string): Promise<any> {
  const res = await fetch(
    `${API_BASE_URL}/news/${encodeURIComponent(symbol)}/events`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch market events for ${symbol}`);
  }
  return res.json();
}

// ----------------------------------------------------
// Risk Management Engine
// ----------------------------------------------------
export async function calculateRisk(
  payload: import("@/types").RiskCalculationRequest
): Promise<import("@/types").RiskCalculationResponse> {
  const res = await fetch(`${API_BASE_URL}/risk/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Risk calculation failed");
  }
  return res.json();
}

// ----------------------------------------------------
// Multi-Agent Analysis Pipeline
// ----------------------------------------------------
export async function evaluateAnalysis(
  payload: import("@/types").TradeAnalysisRequest,
  token: string
): Promise<import("@/types").TradeAnalysisResponse> {
  const res = await fetch(`${API_BASE_URL}/analysis/evaluate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Multi-agent evaluation failed");
  }
  return res.json();
}

// ----------------------------------------------------
// Paper Trading Execution & Positions
// ----------------------------------------------------
export async function executeTrade(
  payload: import("@/types").TradeCreatePayload,
  token: string
): Promise<import("@/types").TradeItem> {
  const res = await fetch(`${API_BASE_URL}/trades`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Paper trade execution failed");
  }
  return res.json();
}

export async function fetchTrades(
  token: string,
  status?: string,
  symbol?: string
): Promise<import("@/types").TradeItem[]> {
  let url = `${API_BASE_URL}/trades`;
  const params = new URLSearchParams();
  if (status) params.append("status", status);
  if (symbol) params.append("symbol", symbol);
  if (params.toString()) url += `?${params.toString()}`;

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch paper trades");
  return res.json();
}

export async function fetchTradeById(
  id: string,
  token: string
): Promise<import("@/types").TradeItem> {
  const res = await fetch(`${API_BASE_URL}/trades/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch trade details");
  return res.json();
}

export async function closeTrade(
  id: string,
  payload: import("@/types").TradeClosePayload,
  token: string
): Promise<import("@/types").TradeItem> {
  const res = await fetch(`${API_BASE_URL}/trades/${id}/close`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to close trade");
  }
  return res.json();
}

export async function fetchPortfolio(
  token: string
): Promise<import("@/types").PortfolioDetail> {
  const res = await fetch(`${API_BASE_URL}/portfolio`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch portfolio summary");
  return res.json();
}

export async function resetPortfolio(
  token: string
): Promise<import("@/types").PortfolioDetail> {
  const res = await fetch(`${API_BASE_URL}/portfolio/reset`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to reset paper portfolio");
  return res.json();
}

// ----------------------------------------------------
// Monitoring & Alerts
// ----------------------------------------------------
export async function runMonitoringCheck(
  token: string
): Promise<import("@/types").MonitoringCheckResponse> {
  const res = await fetch(`${API_BASE_URL}/monitoring/check-now`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to run monitoring scan");
  return res.json();
}

export async function fetchAlerts(
  token: string
): Promise<import("@/types").AlertItem[]> {
  const res = await fetch(`${API_BASE_URL}/alerts`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
}

export async function markAlertRead(
  alertId: string,
  token: string
): Promise<import("@/types").AlertItem> {
  const res = await fetch(`${API_BASE_URL}/alerts/${alertId}/read`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to mark alert read");
  return res.json();
}

export async function markAllAlertsRead(
  token: string
): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE_URL}/alerts/mark-all-read`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to mark all alerts read");
  return res.json();
}

// ----------------------------------------------------
// Post-Trade Autopsy Engine
// ----------------------------------------------------
export async function runTradeAutopsy(
  tradeId: string,
  traderNotes?: string,
  token?: string
): Promise<import("@/types").TradeAutopsyResponse> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE_URL}/trades/${tradeId}/autopsy`, {
    method: "POST",
    headers,
    body: JSON.stringify({ trader_notes: traderNotes }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to execute post-trade autopsy");
  }
  return res.json();
}

// ----------------------------------------------------
// Trading Memory & Lessons Engine
// ----------------------------------------------------
export async function searchTradingMemory(
  query: string,
  token: string,
  limit: number = 5
): Promise<import("@/types").MemorySearchResponse> {
  const res = await fetch(
    `${API_BASE_URL}/memory/search?q=${encodeURIComponent(query)}&limit=${limit}`,
    {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    }
  );
  if (!res.ok) throw new Error("Failed to search trading memory");
  return res.json();
}

export async function fetchTradeLessons(
  token: string
): Promise<import("@/types").TradeLesson[]> {
  const res = await fetch(`${API_BASE_URL}/memory/lessons`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch trade lessons");
  return res.json();
}

export async function createTradeLesson(
  payload: {
    title: string;
    setup_type: string;
    mistake_type: string;
    lesson: string;
    future_rule: string;
  },
  token: string
): Promise<import("@/types").TradeLesson> {
  const res = await fetch(`${API_BASE_URL}/memory/lessons`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to save trading lesson");
  return res.json();
}

export async function fetchTradeMemoryHistory(
  token: string
): Promise<import("@/types").TradeMemoryItem[]> {
  const res = await fetch(`${API_BASE_URL}/memory/history`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch trade memory history");
  return res.json();
}

