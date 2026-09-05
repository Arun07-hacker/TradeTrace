export interface HealthStatus {
  status: string;
  app: string;
  version: string;
  environment: string;
  demo_mode: boolean;
  tagline: string;
  providers: {
    llm: string;
    market_data: string;
    news: string;
  };
  timestamp: string;
}

export type TradeDirection = "LONG" | "SHORT";

export type TradeDecisionState =
  | "STRONG_SETUP"
  | "POSSIBLE_SETUP"
  | "WAIT"
  | "HIGH_RISK"
  | "AVOID";

export type TradeStatus =
  | "PLANNED"
  | "OPEN"
  | "TARGET_HIT"
  | "STOP_HIT"
  | "CLOSED_MANUALLY"
  | "CANCELLED";

export interface MarketDataPoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface UserPreference {
  id: string;
  user_id: string;
  preferred_market: string;
  risk_preference: string;
  default_risk_pct: number;
  max_portfolio_exposure_pct: number;
  enable_memory_warnings: boolean;
  enable_monitoring_alerts: boolean;
  created_at: string;
  updated_at: string;
}

export interface PortfolioSummary {
  id: string;
  initial_balance: number;
  cash_balance: number;
  total_equity: number;
  realized_pnl: number;
  unrealized_pnl: number;
  win_count: number;
  loss_count: number;
  max_drawdown_pct: number;
  current_exposure_pct: number;
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  preference?: UserPreference;
  portfolio?: PortfolioSummary;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export interface TechnicalIndicators {
  symbol: string;
  current_price: number;
  trend: string;
  trend_details: {
    trend: string;
    strength: number;
    description: string;
  };
  rsi: number;
  sma_20: number;
  sma_50: number;
  sma_200?: number | null;
  ema_12: number;
  ema_26: number;
  macd: {
    macd: number;
    signal: number;
    histogram: number;
  };
  atr: number;
  volatility_pct: number;
  volume_signal: string;
  volume_details: {
    volume_signal: string;
    current_volume: number;
    avg_volume_20: number;
    volume_ratio: number;
  };
  support_resistance: {
    support_levels: number[];
    resistance_levels: number[];
    key_support: number;
    key_resistance: number;
  };
  generated_at: string;
  is_demo: boolean;
}

export interface NewsArticle {
  symbol: string;
  title: string;
  description: string;
  source: string;
  url: string;
  published_at: string;
  sentiment: "BULLISH" | "BEARISH" | "NEUTRAL";
  sentiment_score: number;
  relevance: "HIGH" | "MEDIUM" | "LOW";
  relevance_score: number;
  event_type: string;
  impact: "HIGH" | "MEDIUM" | "LOW";
}

export interface MarketEvent {
  event_id: string;
  symbol: string;
  title: string;
  event_type: string;
  event_date: string;
  days_until: number;
  impact: string;
  description: string;
  implied_volatility_effect: string;
}

// ----------------------------------------------------
// Risk Management Types
// ----------------------------------------------------
export interface RiskCalculationRequest {
  symbol: string;
  direction: string;
  entry_price: number;
  stop_loss: number;
  target_price: number;
  portfolio_equity: number;
  risk_per_trade_pct: number;
  current_drawdown_pct?: number;
  max_exposure_pct?: number;
}

export interface RiskCalculationResponse {
  symbol: string;
  direction: string;
  entry_price: number;
  stop_loss: number;
  target: number;
  risk_per_share: number;
  reward_per_share: number;
  risk_amount: number;
  potential_reward: number;
  position_size: number;
  risk_reward_ratio: number;
  position_value: number;
  portfolio_exposure: number;
  portfolio_exposure_pct: number;
  risk_level: "conservative" | "moderate" | "aggressive" | "excessive";
  is_valid: boolean;
  warnings: string[];
  drawdown_adjusted: boolean;
}

// ----------------------------------------------------
// Multi-Agent Analysis Types
// ----------------------------------------------------
export interface ResearchAgentOutput {
  technical_evaluation: string;
  catalyst_evaluation: string;
  supporting_points: string[];
  risk_points: string[];
  alignment_score: number;
}

export interface DevilsAdvocateOutput {
  counter_arguments: string[];
  hidden_risks: string[];
  confirmation_bias_warning: string;
  historical_memory_conflicts: string[];
  skepticism_score: number;
}

export interface DecisionAgentOutput {
  action: "PROCEED_WITH_CAUTION" | "WAIT_FOR_CONFIRMATION" | "REJECT" | "REVISE_PARAMETERS";
  thesis_strength: number;
  confidence: number;
  summary: string;
  supporting_factors: string[];
  risk_factors: string[];
  devils_advocate_findings: string[];
  memory_warnings: string[];
  suggested_modifications: string[];
}

export interface TradeAnalysisRequest {
  symbol: string;
  direction: string;
  thesis: string;
  timeframe?: string;
  entry_price: number;
  stop_loss: number;
  target_price: number;
  portfolio_equity?: number;
  risk_per_trade_pct?: number;
}

export interface TradeAnalysisResponse {
  symbol: string;
  direction: string;
  thesis: string;
  timeframe: string;
  research: ResearchAgentOutput;
  devils_advocate: DevilsAdvocateOutput;
  risk: RiskCalculationResponse;
  decision: DecisionAgentOutput;
  created_at: string;
}

// ----------------------------------------------------
// Paper Trading & Positions Types
// ----------------------------------------------------
export interface TradeEvent {
  id: string;
  trade_id: string;
  event_type: string;
  description: string;
  severity: "INFO" | "WARNING" | "CRITICAL";
  created_at: string;
}

export interface TradeItem {
  id: string;
  user_id: string;
  symbol: string;
  direction: TradeDirection;
  timeframe: string;
  entry_price: number;
  stop_loss: number;
  target: number;
  quantity: number;
  risk_amount: number;
  risk_reward_ratio: number;
  thesis: string;
  decision: string;
  status: TradeStatus;
  exit_price?: number | null;
  realized_pnl?: number | null;
  realized_pnl_pct?: number | null;
  closed_at?: string | null;
  created_at: string;
  events?: TradeEvent[];
}

export interface PositionItem {
  id: string;
  portfolio_id: string;
  trade_id?: string | null;
  symbol: string;
  direction: TradeDirection;
  quantity: number;
  entry_price: number;
  current_price: number;
  stop_loss: number;
  target: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  created_at: string;
}

export interface PortfolioDetail extends PortfolioSummary {
  positions: PositionItem[];
}

export interface TradeCreatePayload {
  symbol: string;
  direction: string;
  timeframe?: string;
  entry_price: number;
  stop_loss: number;
  target: number;
  quantity: number;
  thesis: string;
  decision?: string;
}

export interface TradeClosePayload {
  exit_price?: number;
  reason?: string;
}

// ----------------------------------------------------
// Post-Trade Autopsy Types
// ----------------------------------------------------
export interface TradeAutopsyResponse {
  trade_id: string;
  symbol: string;
  outcome: "WIN" | "LOSS" | "BREAKEVEN";
  realized_pnl: number;
  realized_pnl_pct: number;
  execution_grade: string;
  discipline_score: number;
  key_mistake: string;
  lesson_learned: string;
  future_rule: string;
  indexed_in_memory: boolean;
  created_at: string;
}

// ----------------------------------------------------
// Trading Memory & Lessons Types
// ----------------------------------------------------
export interface TradeLesson {
  id: string;
  user_id: string;
  trade_id?: string | null;
  title: string;
  setup_type: string;
  mistake_type: string;
  lesson: string;
  future_rule: string;
  times_applied: number;
  created_at: string;
}

export interface TradeMemoryItem {
  id: string;
  user_id: string;
  trade_id: string;
  symbol: string;
  setup_title: string;
  original_thesis: string;
  setup_tags: string[];
  outcome: string;
  mistake?: string | null;
  lesson?: string | null;
  created_at: string;
}

export interface MemorySearchResultItem {
  id: string;
  type: "lesson" | "trade_memory";
  title: string;
  symbol?: string | null;
  outcome?: string | null;
  content: string;
  rule_or_mistake?: string | null;
  similarity_score: number;
}

export interface MemorySearchResponse {
  query: string;
  total_results: number;
  results: MemorySearchResultItem[];
}

// ----------------------------------------------------
// Alerts & Notifications Types
// ----------------------------------------------------
export interface AlertItem {
  id: string;
  user_id: string;
  trade_id?: string | null;
  symbol?: string | null;
  alert_type: string;
  title: string;
  message: string;
  severity: "INFO" | "WARNING" | "CRITICAL";
  is_read: boolean;
  created_at: string;
}

export interface MonitoringCheckResponse {
  checked_trades_count: number;
  triggered_events_count: number;
  alerts_created_count: number;
  details: string[];
}

