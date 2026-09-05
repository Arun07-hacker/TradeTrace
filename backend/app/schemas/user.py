import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserPreferenceBase(BaseModel):
    preferred_market: str = Field("US_EQUITIES", description="Market focus (e.g. US_EQUITIES, CRYPTO, FOREX)")
    risk_preference: str = Field("MODERATE", description="Risk tolerance (CONSERVATIVE, MODERATE, AGGRESSIVE)")
    default_risk_pct: float = Field(1.0, ge=0.1, le=10.0, description="Risk per trade percentage")
    max_portfolio_exposure_pct: float = Field(50.0, ge=5.0, le=100.0, description="Max total portfolio exposure percentage")
    enable_memory_warnings: bool = Field(True, description="Enable pgvector memory warnings on similar losing setups")
    enable_monitoring_alerts: bool = Field(True, description="Enable active position monitoring alerts")


class UserPreferenceUpdate(BaseModel):
    preferred_market: Optional[str] = None
    risk_preference: Optional[str] = None
    default_risk_pct: Optional[float] = Field(None, ge=0.1, le=10.0)
    max_portfolio_exposure_pct: Optional[float] = Field(None, ge=5.0, le=100.0)
    enable_memory_warnings: Optional[bool] = None
    enable_monitoring_alerts: Optional[bool] = None


class UserPreferenceOut(UserPreferenceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioSummaryOut(BaseModel):
    id: uuid.UUID
    initial_balance: float
    cash_balance: float
    total_equity: float
    realized_pnl: float
    unrealized_pnl: float
    win_count: int
    loss_count: int
    max_drawdown_pct: float
    current_exposure_pct: float

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User unique email address")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Plaintext password")
    preferred_market: Optional[str] = "US_EQUITIES"
    risk_preference: Optional[str] = "MODERATE"


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User login email")
    password: str = Field(..., description="User login password")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserOut(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    preference: Optional[UserPreferenceOut] = None
    portfolio: Optional[PortfolioSummaryOut] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
