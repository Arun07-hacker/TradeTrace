import pytest
import math
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.session import get_db, init_db
from app.services.memory.embedding import EmbeddingService
from app.services.memory.memory_service import MemoryService
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
async def memory_db_and_client():
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
        yield session_factory, client

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_embedding_service_properties():
    # 1. Dimension and normalization check
    text = "AAPL earnings momentum breakout strategy"
    emb = await EmbeddingService.get_embedding(text)
    assert len(emb) == 1536
    norm = math.sqrt(sum(x * x for x in emb))
    assert abs(norm - 1.0) < 1e-4

    # 2. Semantic similarity ranking
    similar_text = "breakout earnings report high volume"
    unrelated_text = "classical piano concerto sheet music orchestra"

    emb_similar = await EmbeddingService.get_embedding(similar_text)
    emb_unrelated = await EmbeddingService.get_embedding(unrelated_text)

    sim_related = EmbeddingService.cosine_similarity(emb, emb_similar)
    sim_unrelated = EmbeddingService.cosine_similarity(emb, emb_unrelated)

    # Cosine similarity for related trading text should be noticeably higher
    assert sim_related > sim_unrelated
    assert sim_related > 0.5


@pytest.mark.asyncio
async def test_memory_service_lessons_and_search(memory_db_and_client):
    session_factory, _ = memory_db_and_client
    async with session_factory() as db:
        # Create a test user
        user = User(
            email=f"memtest_{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=get_password_hash("Secret123!"),
            name="Memory Test User",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # 1. Seed default lessons
        lessons = await MemoryService.seed_default_lessons(db, user.id)
        assert len(lessons) >= 5

        # 2. Search relevant lessons for "earnings"
        results = await MemoryService.search_relevant_lessons(
            db, user_id=user.id, query="chasing earnings announcement"
        )
        assert len(results) > 0
        top_lesson, score = results[0]
        assert "Earnings" in top_lesson.title or "Earnings" in top_lesson.setup_type
        assert score > 0.5

        # 3. Create a trade memory record
        trade_id = uuid.uuid4()
        mem = await MemoryService.index_trade_memory(
            db=db,
            user_id=user.id,
            trade_id=trade_id,
            symbol="TSLA",
            setup_title="TSLA Cup and Handle Breakout",
            original_thesis="Broke above $200 resistance with heavy volume",
            setup_tags=["Breakout", "Resistance"],
            outcome="LOSS",
            mistake="Failed to respect stop loss when market rotated",
            lesson="Always honor stop loss",
        )
        assert mem.id is not None

        # 4. Search trade memory
        mem_results = await MemoryService.search_similar_memories(
            db, user_id=user.id, query="TSLA breakout above resistance", symbol="TSLA"
        )
        assert len(mem_results) == 1
        assert mem_results[0][0].symbol == "TSLA"


@pytest.mark.asyncio
async def test_memory_api_endpoints(memory_db_and_client):
    _, client = memory_db_and_client
    # 1. Register a test user
    email = f"memapi_{uuid.uuid4().hex[:8]}@example.com"
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "name": "Memory API User",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. GET /memory/lessons
    lessons_resp = await client.get("/api/v1/memory/lessons", headers=headers)
    assert lessons_resp.status_code == 200
    lessons = lessons_resp.json()
    assert len(lessons) >= 5

    # 3. POST /memory/lessons
    new_lesson_payload = {
        "title": "Do not trade during Fed FOMC rate announcements",
        "setup_type": "Macro Volatility",
        "mistake_type": "Whipsaw / Slippage",
        "lesson": "Spreads widen and slippage destroys stop orders during FOMC minutes",
        "future_rule": "Flat all day-trading positions 15 minutes before FOMC statement",
    }
    create_resp = await client.post(
        "/api/v1/memory/lessons", json=new_lesson_payload, headers=headers
    )
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["title"] == new_lesson_payload["title"]

    # 4. GET /memory/search
    search_resp = await client.get(
        "/api/v1/memory/search",
        params={"q": "earnings breakout gamble", "limit": 3},
        headers=headers,
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["total_results"] > 0
    assert len(search_data["results"]) > 0
    assert "similarity_score" in search_data["results"][0]
