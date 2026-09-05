import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.db.base import Base
from app.db.session import init_db
from app.models.user import User, UserPreference
from app.models.market import Symbol, MarketData
from app.models.news import News
from app.models.portfolio import Portfolio, Position
from app.models.trade import Trade, TradeAnalysis, TradeEvent, TradeMemory, TradeLesson
from app.models.alert import Alert


@pytest.fixture
async def test_session():
    # Use in-memory SQLite async engine for lightning-fast, self-contained model verification
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    await init_db(engine)
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_all_tables_created(test_session: AsyncSession):
    """Verify that all required tables are registered in the metadata."""
    expected_tables = {
        "users",
        "user_preferences",
        "symbols",
        "market_data",
        "news",
        "portfolio",
        "positions",
        "trades",
        "trade_analysis",
        "trade_events",
        "trade_memory",
        "trade_lessons",
        "alerts",
    }
    actual_tables = set(Base.metadata.tables.keys())
    for table in expected_tables:
        assert table in actual_tables, f"Missing table: {table}"


@pytest.mark.asyncio
async def test_user_and_preferences(test_session: AsyncSession):
    """Test User creation with UserPreference relationship."""
    user = User(
        name="Alex Trader",
        email="alex@tradetrace.io",
        hashed_password="mockhashedpassword123",
    )
    pref = UserPreference(
        user=user,
        preferred_market="US_EQUITIES",
        risk_preference="MODERATE",
        default_risk_pct=1.0,
        max_portfolio_exposure_pct=50.0,
    )
    test_session.add_all([user, pref])
    await test_session.commit()

    stmt = select(User).where(User.email == "alex@tradetrace.io")
    result = await test_session.execute(stmt)
    saved_user = result.scalar_one()

    assert saved_user.id is not None
    assert isinstance(saved_user.id, uuid.UUID)
    assert saved_user.created_at is not None
    assert saved_user.name == "Alex Trader"


@pytest.mark.asyncio
async def test_market_data_and_symbols(test_session: AsyncSession):
    """Test Symbol and MarketData time series OHLCV storage."""
    sym = Symbol(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
    bar = MarketData(
        symbol="AAPL",
        timeframe="1d",
        timestamp=datetime.now(timezone.utc),
        open=220.0,
        high=225.0,
        low=218.0,
        close=224.5,
        volume=50000000,
        vwap=223.1,
    )
    test_session.add_all([sym, bar])
    await test_session.commit()

    stmt = select(MarketData).where(MarketData.symbol == "AAPL")
    result = await test_session.execute(stmt)
    saved_bar = result.scalar_one()
    assert saved_bar.close == 224.5
    assert saved_bar.volume == 50000000


@pytest.mark.asyncio
async def test_news_entity(test_session: AsyncSession):
    """Test normalized News persistence with sentiment and relevance scores."""
    news_item = News(
        symbol="NVDA",
        title="NVIDIA Announces Next-Gen AI Architecture",
        description="Major catalyst for semiconductor sector momentum.",
        source="Bloomberg",
        url="https://example.com/news/nvda-1",
        published_at=datetime.now(timezone.utc),
        sentiment="BULLISH",
        sentiment_score=0.85,
        relevance="HIGH",
        relevance_score=0.95,
        event_type="PRODUCT",
        impact="HIGH",
    )
    test_session.add(news_item)
    await test_session.commit()

    stmt = select(News).where(News.symbol == "NVDA")
    result = await test_session.execute(stmt)
    saved_news = result.scalar_one()
    assert saved_news.sentiment == "BULLISH"
    assert saved_news.relevance_score == 0.95


@pytest.mark.asyncio
async def test_portfolio_and_positions(test_session: AsyncSession):
    """Test paper trading Portfolio and Position lifecycle."""
    user = User(
        name="Portfolio Tester",
        email="portfolio@tradetrace.io",
        hashed_password="pw",
    )
    test_session.add(user)
    await test_session.flush()

    portfolio = Portfolio(
        user_id=user.id,
        initial_balance=100000.0,
        cash_balance=90000.0,
        total_equity=102000.0,
        realized_pnl=0.0,
        unrealized_pnl=2000.0,
    )
    test_session.add(portfolio)
    await test_session.flush()

    pos = Position(
        portfolio_id=portfolio.id,
        symbol="AAPL",
        direction="LONG",
        quantity=50.0,
        entry_price=200.0,
        current_price=220.0,
        stop_loss=190.0,
        target=230.0,
        unrealized_pnl=1000.0,
        unrealized_pnl_pct=10.0,
    )
    test_session.add(pos)
    await test_session.commit()

    stmt = select(Portfolio).where(Portfolio.user_id == user.id)
    res = await test_session.execute(stmt)
    saved_p = res.scalar_one()
    assert saved_p.total_equity == 102000.0


@pytest.mark.asyncio
async def test_trade_lifecycle_and_memory(test_session: AsyncSession):
    """Test full Trade, TradeAnalysis, TradeEvent, TradeMemory and TradeLesson."""
    user = User(name="Trader One", email="trader1@tradetrace.io", hashed_password="pw")
    test_session.add(user)
    await test_session.flush()

    trade = Trade(
        user_id=user.id,
        symbol="TSLA",
        direction="LONG",
        timeframe="1d",
        entry_price=250.0,
        stop_loss=240.0,
        target=280.0,
        quantity=100.0,
        risk_amount=1000.0,
        risk_reward_ratio=3.0,
        thesis="Breakout above key consolidation resistance",
        decision="POSSIBLE_SETUP",
        status="OPEN",
    )
    test_session.add(trade)
    await test_session.flush()

    # Trade Analysis
    analysis = TradeAnalysis(
        trade_id=trade.id,
        market_summary="Consolidation range with increasing volume.",
        technical_summary="RSI at 58, 20 EMA above 50 EMA.",
        news_summary="Neutral EV market sentiment.",
        supporting_factors=["Volume surge", "Moving average crossover"],
        risk_factors=["Upcoming delivery report"],
        devils_advocate_findings=["Volume is lower than prior quarterly breakout."],
        thesis_strength=0.72,
        confidence=0.68,
        decision_rationale=["Acceptable risk-reward", "Resistance breakout confirmed"],
    )

    # Trade Event
    event = TradeEvent(
        trade_id=trade.id,
        event_type="STATUS_CHANGED",
        description="Trade executed in paper portfolio at 250.0",
        severity="INFO",
    )

    # Vector Memory Record (e.g. 1536 dim mock vector)
    mock_vector = [0.01 * (i % 10) for i in range(1536)]
    memory = TradeMemory(
        user_id=user.id,
        trade_id=trade.id,
        symbol="TSLA",
        setup_title="Consolidation breakout into earnings",
        original_thesis=trade.thesis,
        setup_tags=["breakout", "consolidation", "earnings_leadup"],
        devils_advocate_warnings=["Devil's advocate warned of earnings event risk"],
        outcome="LOSS",
        mistake="Entered breakout 2 days prior to earnings without volume confirmation",
        lesson="Do not enter breakout setups immediately prior to earnings.",
        embedding=mock_vector,
    )

    # Trade Lesson
    lesson = TradeLesson(
        user_id=user.id,
        trade_id=trade.id,
        title="Pre-earnings breakout failure rule",
        setup_type="Breakout",
        mistake_type="Event Volatility Ignored",
        lesson="High event volatility invalidates tight stop breakout trades.",
        future_rule="Avoid breakout entries within 3 days of earnings announcement.",
        embedding=mock_vector,
    )

    test_session.add_all([analysis, event, memory, lesson])
    await test_session.commit()

    # Query Memory
    mem_stmt = select(TradeMemory).where(TradeMemory.trade_id == trade.id)
    mem_res = await test_session.execute(mem_stmt)
    saved_mem = mem_res.scalar_one()

    assert saved_mem.outcome == "LOSS"
    assert "breakout" in saved_mem.setup_tags
    assert len(saved_mem.embedding) == 1536
    assert saved_mem.lesson is not None


@pytest.mark.asyncio
async def test_alerts_creation(test_session: AsyncSession):
    """Test Alert notification model."""
    user = User(name="Alert User", email="alert@tradetrace.io", hashed_password="pw")
    test_session.add(user)
    await test_session.flush()

    alert = Alert(
        user_id=user.id,
        symbol="AAPL",
        alert_type="STOP_APPROACHING",
        title="AAPL Price Approaching Stop Loss",
        message="Current price $213 is within 1.5% of stop level $212.",
        severity="WARNING",
        is_read=False,
    )
    test_session.add(alert)
    await test_session.commit()

    stmt = select(Alert).where(Alert.user_id == user.id)
    res = await test_session.execute(stmt)
    saved_alert = res.scalar_one()
    assert saved_alert.severity == "WARNING"
    assert saved_alert.is_read is False
