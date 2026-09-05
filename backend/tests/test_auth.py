import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.base import Base
from app.db.session import get_db, init_db
from app.core.security import get_password_hash, verify_password


@pytest.fixture
async def auth_test_client():
    # In-memory SQLite async engine
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
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


def test_password_hashing():
    """Verify password hashing security and verification."""
    raw = "TraderSecretPass2026!"
    hashed = get_password_hash(raw)
    assert raw != hashed
    assert not hashed.startswith("TraderSecret")
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False


@pytest.mark.asyncio
async def test_user_registration_success(auth_test_client: AsyncClient):
    """Test trader registration, portfolio provisioning and JWT issuance."""
    payload = {
        "name": "Sarah Connor",
        "email": "sarah@tradetrace.io",
        "password": "SecurePassword123!",
        "preferred_market": "US_EQUITIES",
        "risk_preference": "CONSERVATIVE",
    }
    response = await auth_test_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    user = data["user"]
    assert user["name"] == "Sarah Connor"
    assert user["email"] == "sarah@tradetrace.io"
    assert "id" in user
    
    # Verify preferences were auto-initialized
    assert user["preference"] is not None
    assert user["preference"]["preferred_market"] == "US_EQUITIES"
    assert user["preference"]["risk_preference"] == "CONSERVATIVE"

    # Verify initial paper trading portfolio was provisioned
    assert user["portfolio"] is not None
    assert user["portfolio"]["cash_balance"] == 100000.0
    assert user["portfolio"]["total_equity"] == 100000.0


@pytest.mark.asyncio
async def test_duplicate_email_registration_fails(auth_test_client: AsyncClient):
    """Ensure duplicate email registration is rejected with 400 Bad Request."""
    payload = {
        "name": "Duplicate User",
        "email": "dup@tradetrace.io",
        "password": "Password123!",
    }
    res1 = await auth_test_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await auth_test_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_user_login_flow(auth_test_client: AsyncClient):
    """Test login with valid credentials and failure on invalid password."""
    register_payload = {
        "name": "Login Tester",
        "email": "login@tradetrace.io",
        "password": "ValidPassword99!",
    }
    reg_res = await auth_test_client.post("/api/v1/auth/register", json=register_payload)
    assert reg_res.status_code == 201

    # Login with wrong password
    bad_login = await auth_test_client.post(
        "/api/v1/auth/login",
        json={"email": "login@tradetrace.io", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401

    # Login with correct password
    good_login = await auth_test_client.post(
        "/api/v1/auth/login",
        json={"email": "login@tradetrace.io", "password": "ValidPassword99!"},
    )
    assert good_login.status_code == 200
    token_data = good_login.json()
    assert "access_token" in token_data


@pytest.mark.asyncio
async def test_get_current_user_profile(auth_test_client: AsyncClient):
    """Test authenticated profile lookup via /auth/me."""
    reg_res = await auth_test_client.post(
        "/api/v1/auth/register",
        json={"name": "Profile User", "email": "me@tradetrace.io", "password": "Password123!"},
    )
    token = reg_res.json()["access_token"]

    # Request without token
    unauth_res = await auth_test_client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401

    # Request with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await auth_test_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == "me@tradetrace.io"
    assert user_data["portfolio"]["cash_balance"] == 100000.0


@pytest.mark.asyncio
async def test_update_user_preferences(auth_test_client: AsyncClient):
    """Test updating user risk preferences and market settings."""
    reg_res = await auth_test_client.post(
        "/api/v1/auth/register",
        json={"name": "Pref User", "email": "pref@tradetrace.io", "password": "Password123!"},
    )
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "risk_preference": "AGGRESSIVE",
        "default_risk_pct": 2.5,
        "max_portfolio_exposure_pct": 40.0,
    }
    update_res = await auth_test_client.put(
        "/api/v1/auth/preferences",
        headers=headers,
        json=update_payload,
    )
    assert update_res.status_code == 200
    pref_data = update_res.json()
    assert pref_data["risk_preference"] == "AGGRESSIVE"
    assert pref_data["default_risk_pct"] == 2.5
    assert pref_data["max_portfolio_exposure_pct"] == 40.0


@pytest.mark.asyncio
async def test_logout_endpoint(auth_test_client: AsyncClient):
    """Test logout confirmation endpoint."""
    reg_res = await auth_test_client.post(
        "/api/v1/auth/register",
        json={"name": "Logout User", "email": "logout@tradetrace.io", "password": "Password123!"},
    )
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_res = await auth_test_client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert "Logged out successfully" in logout_res.json()["message"]
