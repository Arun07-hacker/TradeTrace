import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.session import get_db, init_db
from app.agents.research_agent import ResearchAgent
from app.agents.devil_advocate_agent import DevilsAdvocateAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.orchestrator import AgentOrchestrator
from app.schemas.agent import TradeAnalysisRequest
from app.services.market_data.mock_provider import MockMarketDataProvider
from app.services.news.mock_provider import MockNewsProvider
from app.analysis.engine import TechnicalAnalysisEngine
from app.analysis.risk_engine import RiskEngine
from app.schemas.risk import RiskCalculationRequest


@pytest.fixture
async def agent_test_client():
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    await init_db(test_engine)
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, session_factory

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_individual_agents_pipeline():
    market = MockMarketDataProvider()
    news = MockNewsProvider()
    bars = await market.get_historical_bars("AAPL", limit=50)
    technicals = TechnicalAnalysisEngine.analyze("AAPL", bars, is_demo=True)
    articles = await news.get_news_for_symbol("AAPL", limit=3)
    events = await news.get_upcoming_events_for_symbol("AAPL")


    # 1. Research Agent
    research_agent = ResearchAgent()
    res_out = await research_agent.analyze(
        symbol="AAPL",
        direction="LONG",
        thesis="Breakout above $150 consolidation band with strong volume",
        technicals=technicals,
        articles=articles,
        events=events,
    )
    assert res_out.alignment_score > 0.0
    assert len(res_out.supporting_points) > 0
    assert len(res_out.risk_points) > 0

    # 2. Devil's Advocate Agent
    devil_agent = DevilsAdvocateAgent()
    devil_out = await devil_agent.challenge(
        symbol="AAPL",
        direction="LONG",
        thesis="Breakout above $150 consolidation band",
        research=res_out,
        technicals=technicals,
        memory_items=[],
    )
    assert devil_out.skepticism_score > 0.0
    assert len(devil_out.counter_arguments) > 0
    assert devil_out.confirmation_bias_warning != ""

    # 3. Decision Agent
    risk_calc = RiskEngine.calculate_risk(
        RiskCalculationRequest(
            symbol="AAPL",
            direction="LONG",
            entry_price=150.0,
            stop_loss=145.0,
            target_price=165.0,
            portfolio_equity=100000.0,
        )
    )
    decision_agent = DecisionAgent()
    dec_out = await decision_agent.decide(
        symbol="AAPL",
        direction="LONG",
        thesis="Breakout above $150 consolidation band",
        research=res_out,
        devils_advocate=devil_out,
        risk=risk_calc,
    )
    # Validate critical constraint: No BUY or SELL signals
    assert dec_out.action in ["PROCEED_WITH_CAUTION", "WAIT_FOR_CONFIRMATION", "REVISE_PARAMETERS", "REJECT"]
    assert dec_out.thesis_strength > 0.0
    assert dec_out.confidence > 0.0


@pytest.mark.asyncio
async def test_full_agent_api_endpoint(agent_test_client):
    client, _ = agent_test_client

    # 1. Register user & authenticate
    email = f"agentuser_{uuid.uuid4().hex[:8]}@example.com"
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "name": "Agent User",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Run analysis endpoint
    payload = {
        "symbol": "AAPL",
        "direction": "LONG",
        "thesis": "Bullish ascending triangle breakout above 150 with heavy accumulation volume",
        "timeframe": "1d",
        "entry_price": 150.0,
        "stop_loss": 145.0,
        "target_price": 165.0,
        "portfolio_equity": 100000.0,
        "risk_per_trade_pct": 1.0,
    }
    resp = await client.post("/api/v1/analysis/evaluate", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "AAPL"
    assert data["direction"] == "LONG"
    assert "research" in data
    assert "devils_advocate" in data
    assert "risk" in data
    assert "decision" in data
    assert data["decision"]["action"] in ["PROCEED_WITH_CAUTION", "WAIT_FOR_CONFIRMATION", "REVISE_PARAMETERS", "REJECT"]
    assert data["risk"]["position_size"] == 200
    assert data["risk"]["risk_reward_ratio"] == 3.0
