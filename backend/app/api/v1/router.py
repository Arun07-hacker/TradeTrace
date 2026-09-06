from fastapi import APIRouter
from app.api.v1 import health, auth, market, technical, news, risk, memory, analysis, trades, portfolio, monitoring, autopsy, tools

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(market.router)
api_router.include_router(technical.router)
api_router.include_router(news.router)
api_router.include_router(risk.router)
api_router.include_router(memory.router)
api_router.include_router(analysis.router)
api_router.include_router(trades.router)
api_router.include_router(portfolio.router)
api_router.include_router(monitoring.router)
api_router.include_router(autopsy.router)
api_router.include_router(tools.router)






