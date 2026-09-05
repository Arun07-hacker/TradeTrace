from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.db.session import get_db
from app.models.user import User, UserPreference
from app.models.portfolio import Portfolio
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserOut,
    UserPreferenceOut,
    UserPreferenceUpdate,
    Token,
)
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new trader account:
    - Creates user credentials (bcrypt hashed)
    - Initializes default trading preferences
    - Automatically provisions paper trading portfolio with initial paper cash
    - Returns JWT access token
    """
    # Check if email is already registered
    existing_stmt = select(User).where(User.email == user_in.email.lower())
    existing_res = await db.execute(existing_stmt)
    if existing_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    # 1. Create User
    new_user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_verified=True,
    )
    db.add(new_user)
    await db.flush()

    # 2. Create User Preference
    pref = UserPreference(
        user_id=new_user.id,
        preferred_market=user_in.preferred_market or "US_EQUITIES",
        risk_preference=user_in.risk_preference or "MODERATE",
        default_risk_pct=settings.DEFAULT_RISK_PER_TRADE_PCT,
        max_portfolio_exposure_pct=settings.MAX_PORTFOLIO_EXPOSURE_PCT,
    )
    db.add(pref)

    # 3. Provision Initial Paper Trading Portfolio
    portfolio = Portfolio(
        user_id=new_user.id,
        initial_balance=settings.INITIAL_PAPER_BALANCE,
        cash_balance=settings.INITIAL_PAPER_BALANCE,
        total_equity=settings.INITIAL_PAPER_BALANCE,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        win_count=0,
        loss_count=0,
        max_drawdown_pct=0.0,
        current_exposure_pct=0.0,
    )
    db.add(portfolio)
    await db.commit()

    # Refresh user with relationships loaded
    stmt = (
        select(User)
        .options(selectinload(User.preference), selectinload(User.portfolio))
        .where(User.id == new_user.id)
    )
    res = await db.execute(stmt)
    user_loaded = res.scalar_one()

    access_token = create_access_token(subject=str(user_loaded.id))
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user_loaded),
    )


@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate trader with email and password, returning JWT access token."""
    stmt = (
        select(User)
        .options(selectinload(User.preference), selectinload(User.portfolio))
        .where(User.email == user_in.email.lower().strip())
    )
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled")

    access_token = create_access_token(subject=str(user.id))
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/login-form", response_model=Token, include_in_schema=False)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Swagger UI compatible OAuth2 form login."""
    return await login(
        UserLogin(email=form_data.username, password=form_data.password),
        db=db,
    )


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve the active user profile, trading preferences, and portfolio summary."""
    return UserOut.model_validate(current_user)


@router.put("/preferences", response_model=UserPreferenceOut)
async def update_preferences(
    pref_in: UserPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user risk and trading preferences."""
    stmt = select(UserPreference).where(UserPreference.user_id == current_user.id)
    res = await db.execute(stmt)
    pref = res.scalar_one_or_none()

    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    update_data = pref_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pref, field, value)

    await db.commit()
    await db.refresh(pref)
    return UserPreferenceOut.model_validate(pref)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
):
    """Stateless logout confirmation."""
    return {"message": "Logged out successfully", "user_id": str(current_user.id)}
