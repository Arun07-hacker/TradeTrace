# TradeTrace 📊🧠

**AI Trading Research, Risk & Learning Assistant**

> **Tagline:** *Research → Challenge → Decide → Monitor → Trace → Learn*

TradeTrace is **not** a stock-price prediction system and does **not** blindly output "BUY" or "SELL".
Instead, it serves as a rigorous cognitive copilot and trading memory system that helps traders systematically formulate theses, challenge confirmation bias, strictly govern risk, monitor active positions, autopsy closed trades, and learn from past mistakes.

---

## The Core Concept: Trading Memory

Traditional trading journals record only:
- Entry Price, Exit Price, P&L

**TradeTrace additionally remembers:**
- Why the trader entered (Thesis & Rationale)
- What evidence supported the trade
- What warnings the Devil's Advocate raised
- Which risks were identified vs. ignored
- How the trade behaved post-entry
- Root causes of success or failure
- Concrete lessons learned
- Semantic embeddings of setups and market conditions

When a trader proposes a new setup (e.g. *“Breakout trade right before quarterly earnings”*), TradeTrace detects historical similarity using **pgvector** and warns:
> ⚠️ *"Historical Memory Warning: This setup resembles 2 previous trades that suffered losses due to event-related volatility."*

---

## Architectural Stack

- **Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS, Recharts, Lucide Icons.
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, Pandas, NumPy, SQLAlchemy.
- **Database:** PostgreSQL with `pgvector` extension for semantic trade memory embeddings.
- **AI Agent Orchestrator:** Modular agent architecture with swappable LLM provider abstraction (OpenAI, Anthropic, Gemini, or Mock provider for 100% offline development).
- **Execution Mode:** 100% Paper Trading (no real-money broker execution).

---

## Project Structure

```
tradetrace/
├── backend/
│   ├── app/
│   │   ├── agents/          # Research, Devil's Advocate, Risk, Decision, Monitoring, Post-Trade
│   │   ├── analysis/        # Deterministic Python technical analysis engine
│   │   ├── api/             # FastAPI routes & endpoints (v1)
│   │   ├── core/            # Config, security, logging
│   │   ├── db/              # SQLAlchemy session & pgvector helpers
│   │   ├── models/          # PostgreSQL data models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Market data, news providers, portfolio service
│   │   └── workers/         # Trade monitoring background worker
│   ├── tests/               # Pytest suite
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # Reusable UI components & dark terminal theme
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility helpers
│   ├── services/            # API client
│   └── types/               # TypeScript interfaces
├── docker-compose.yml       # Multi-container orchestration (Postgres+pgvector, API, Web)
├── .env.example             # Environment configuration template
└── README.md
```

---

## Getting Started

### 1. Environment Setup
```bash
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8000
```
Interactive API docs will be available at: `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The user interface will be available at: `http://localhost:3000`.

---

## 20-Phase Development Roadmap (100% Completed)

- [x] **Phase 1: Project Setup** (Monorepo scaffold, typed config, health checks, test suite)
- [x] **Phase 2: PostgreSQL + Database Models** (13 SQLAlchemy models with adaptive 1536-dim vector memory)
- [x] **Phase 3: FastAPI Backend Core & Auth** (Salted bcrypt hashing, JWT tokens, $100k paper portfolio auto-provisioning)
- [x] **Phase 4: Market Data + Mock Provider** (Swappable provider, stochastic OHLCV bars for AAPL, MSFT, NVDA, TSLA)
- [x] **Phase 5: Technical Analysis Engine** (Deterministic indicators: SMA, EMA, RSI, MACD, ATR, Volatility, Pivots, Volume)
- [x] **Phase 6: News & Event Service** (Deduplicated articles, sentiment analysis, scheduled earnings/catalyst tracking)
- [x] **Phase 7: Risk Management Engine** (1% sizing, R:R >= 1.5 check, dynamic drawdown scaling, max exposure limit)
- [x] **Phase 8: Trading Memory + pgvector** (1536-dim vector embeddings, cosine similarity search, seeded pitfalls)
- [x] **Phase 9: Multi-Agent Architecture & Base Agent** (Swappable LLM provider abstraction, MockLLMProvider)
- [x] **Phase 10: Research & Devil's Advocate Agents** (Hypothesis evaluation, confirmation bias challenges, trap detection)
- [x] **Phase 11: Decision Agent & Orchestrator** (Explainable assessment: PROCEED, WAIT, REVISE, REJECT; no buy/sell)
- [x] **Phase 12: Paper Trading Engine** (Paper trading execution, order logging, cash accounting, position tracking)
- [x] **Phase 13: Monitoring Agent** (Live price checks, automated stop/target breach execution, alert notifications)
- [x] **Phase 14: Post-Trade Analysis Agent** (Autopsy execution, discipline scoring, lesson formulation, memory loop)
- [x] **Phase 15: State Management & API Client** (Typed Next.js API client covering all endpoints with demo token support)
- [x] **Phase 16: Multi-Agent Analysis UI** (Interactive `/analyze` terminal with live agent outputs and risk calculations)
- [x] **Phase 17: Paper Trading Execution UI** (One-click paper order execution directly into active portfolio)
- [x] **Phase 18: Trade Monitoring & Autopsy Flow** (Detailed trade lifecycle tracker with post-mortem lesson extraction)
- [x] **Phase 19: Trading Memory & Journal UI** (Live vector search bar with cosine similarity ranking and lesson creation)
- [x] **Phase 20: Comprehensive Testing & Docker Orchestration** (55/55 backend pytest pass, 14/14 Next.js routes built)

