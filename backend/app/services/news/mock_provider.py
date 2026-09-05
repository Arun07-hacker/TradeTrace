from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from app.services.news.base import NewsProvider
from app.schemas.news import NewsArticleItem, MarketEventItem

# Realistic financial news database
MOCK_ARTICLES: Dict[str, List[Dict[str, Any]]] = {
    "AAPL": [
        {
            "title": "Apple Prepares For Q3 Earnings Announcement Amid Channel Inventory Normalization",
            "description": "Wall Street analysts expect modest revenue growth in Services while hardware margins face scrutiny ahead of Thursday's quarterly release.",
            "source": "Bloomberg Markets",
            "url": "https://tradetrace.io/news/aapl/earnings-preview-q3",
            "hours_ago": 2,
            "sentiment": "NEUTRAL",
            "sentiment_score": 0.05,
            "relevance": "HIGH",
            "relevance_score": 0.95,
            "event_type": "EARNINGS",
            "impact": "HIGH",
        },
        {
            "title": "Supply Chain Checks Indicate Accelerated Apple Intelligence Device Adoption",
            "description": "Component suppliers in Taiwan report steady ramp-up for custom silicon chips powering on-device artificial intelligence features.",
            "source": "Reuters",
            "url": "https://tradetrace.io/news/aapl/ai-supply-chain-ramp",
            "hours_ago": 14,
            "sentiment": "BULLISH",
            "sentiment_score": 0.72,
            "relevance": "HIGH",
            "relevance_score": 0.88,
            "event_type": "PRODUCT",
            "impact": "MEDIUM",
        },
        {
            "title": "Department of Justice App Store Ecosystem Review Progresses to Discovery Phase",
            "description": "Legal proceedings regarding developer fee structures and default browser placement enter technical documentation review.",
            "source": "Wall Street Journal",
            "url": "https://tradetrace.io/news/aapl/doj-regulatory-review",
            "hours_ago": 36,
            "sentiment": "BEARISH",
            "sentiment_score": -0.45,
            "relevance": "MEDIUM",
            "relevance_score": 0.65,
            "event_type": "REGULATORY",
            "impact": "MEDIUM",
        },
    ],
    "MSFT": [
        {
            "title": "Microsoft Azure Enterprise AI Copilot Seat Growth Tops Consensus Estimates",
            "description": "Commercial cloud bookings expanded 21% year-over-year as Fortune 500 enterprises standardize generative AI workflows.",
            "source": "Financial Times",
            "url": "https://tradetrace.io/news/msft/azure-copilot-acceleration",
            "hours_ago": 3,
            "sentiment": "BULLISH",
            "sentiment_score": 0.80,
            "relevance": "HIGH",
            "relevance_score": 0.92,
            "event_type": "PRODUCT",
            "impact": "HIGH",
        },
        {
            "title": "Capital Expenditure Run-Rate Projected to Expand for Cloud Infrastructure Expansion",
            "description": "Management signals persistent investment in next-gen data centers and specialized power infrastructure through the next fiscal half.",
            "source": "CNBC",
            "url": "https://tradetrace.io/news/msft/datacenter-capex-expansion",
            "hours_ago": 18,
            "sentiment": "NEUTRAL",
            "sentiment_score": -0.10,
            "relevance": "MEDIUM",
            "relevance_score": 0.75,
            "event_type": "MACRO",
            "impact": "MEDIUM",
        },
    ],
    "NVDA": [
        {
            "title": "NVIDIA Blackwell Architecture Production Yields Exceed Hyperscaler Benchmarks",
            "description": "Foundry partners report packaging efficiency improvements, reducing lead times for Tier-1 cloud service provider deliveries.",
            "source": "Reuters Tech",
            "url": "https://tradetrace.io/news/nvda/blackwell-packaging-yields",
            "hours_ago": 1,
            "sentiment": "BULLISH",
            "sentiment_score": 0.88,
            "relevance": "HIGH",
            "relevance_score": 0.98,
            "event_type": "PRODUCT",
            "impact": "HIGH",
        },
        {
            "title": "Export Control Regulations Update Under Review for Specialized Accelerator Chips",
            "description": "Commerce Department evaluates revised bandwidth thresholds for international artificial intelligence accelerators.",
            "source": "Wall Street Journal",
            "url": "https://tradetrace.io/news/nvda/export-control-thresholds",
            "hours_ago": 22,
            "sentiment": "BEARISH",
            "sentiment_score": -0.55,
            "relevance": "HIGH",
            "relevance_score": 0.85,
            "event_type": "REGULATORY",
            "impact": "HIGH",
        },
    ],
    "TSLA": [
        {
            "title": "Tesla Robotaxi Autonomous Regulatory Approval Filings Advance in Key Municipalities",
            "description": "Permit applications for commercial autonomous ride-hailing testing submit safety validation telematics data.",
            "source": "Electrek",
            "url": "https://tradetrace.io/news/tsla/robotaxi-permit-filings",
            "hours_ago": 4,
            "sentiment": "BULLISH",
            "sentiment_score": 0.65,
            "relevance": "HIGH",
            "relevance_score": 0.90,
            "event_type": "PRODUCT",
            "impact": "HIGH",
        },
        {
            "title": "Automotive Gross Margins Face Pressure Amid Financing Incentive Programs",
            "description": "Promotional financing packages to support volume targets compress vehicle margins prior to upcoming quarterly disclosures.",
            "source": "Bloomberg",
            "url": "https://tradetrace.io/news/tsla/gross-margin-financing-pressures",
            "hours_ago": 28,
            "sentiment": "BEARISH",
            "sentiment_score": -0.62,
            "relevance": "HIGH",
            "relevance_score": 0.88,
            "event_type": "EARNINGS",
            "impact": "HIGH",
        },
    ],
}

MOCK_EVENTS: Dict[str, List[Dict[str, Any]]] = {
    "AAPL": [
        {
            "title": "Q3 Fiscal Earnings Announcement & Conference Call",
            "event_type": "EARNINGS",
            "days_until": 4,
            "impact": "HIGH",
            "description": "Quarterly earnings release. Implied option volatility elevates event risk; breakouts directly prior to release carry high failure rates.",
            "implied_volatility_effect": "High event volatility - risk of post-earnings gap against breakout direction.",
        },
        {
            "title": "Federal Reserve FOMC Interest Rate Decision",
            "event_type": "MACRO",
            "days_until": 12,
            "impact": "HIGH",
            "description": "Broad market liquidity and rate trajectory announcement.",
            "implied_volatility_effect": "Moderate market-wide beta volatility.",
        },
    ],
    "MSFT": [
        {
            "title": "Quarterly Financial Earnings Release",
            "event_type": "EARNINGS",
            "days_until": 18,
            "impact": "HIGH",
            "description": "Enterprise cloud revenue disclosures and forward guidance.",
            "implied_volatility_effect": "Medium event volatility.",
        },
    ],
    "NVDA": [
        {
            "title": "GTC Global Technology AI Developer Keynote",
            "event_type": "PRODUCT_LAUNCH",
            "days_until": 9,
            "impact": "HIGH",
            "description": "Flagship developer conference announcing hardware roadmap and enterprise partnerships.",
            "implied_volatility_effect": "Elevated momentum volatility.",
        },
        {
            "title": "Quarterly Earnings Disclosures",
            "event_type": "EARNINGS",
            "days_until": 24,
            "impact": "HIGH",
            "description": "Data center segment revenue disclosures.",
            "implied_volatility_effect": "High implied volatility expansion.",
        },
    ],
    "TSLA": [
        {
            "title": "Q3 Quarterly Financial Report & Webcast",
            "event_type": "EARNINGS",
            "days_until": 6,
            "impact": "HIGH",
            "description": "Vehicle delivery margins and energy storage profitability disclosures.",
            "implied_volatility_effect": "Extreme event volatility - historical average earnings move exceeds 8%.",
        },
    ],
}


class MockNewsProvider(NewsProvider):
    """
    Simulated news and catalyst event provider with deduplication,
    sentiment classification, and upcoming event tracking.
    """

    async def get_news_for_symbol(self, symbol: str, limit: int = 10) -> List[NewsArticleItem]:
        sym = symbol.upper().strip()
        raw_items = MOCK_ARTICLES.get(sym)

        now = datetime.now(timezone.utc)
        if not raw_items:
            # Generate realistic generic news item if ticker not predefined
            raw_items = [
                {
                    "title": f"{sym} Industry Updates: Market Participants Monitor Institutional Accumulation",
                    "description": f"Trading volume in {sym} reflects balanced institutional positioning ahead of broader sector rebalancing.",
                    "source": "MarketWatch",
                    "url": f"https://tradetrace.io/news/{sym.lower()}/institutional-flows",
                    "hours_ago": 5,
                    "sentiment": "NEUTRAL",
                    "sentiment_score": 0.10,
                    "relevance": "MEDIUM",
                    "relevance_score": 0.60,
                    "event_type": "GENERAL",
                    "impact": "LOW",
                }
            ]

        # Deduplication tracking by title and url
        seen_titles = set()
        seen_urls = set()
        articles: List[NewsArticleItem] = []

        for item in raw_items:
            norm_title = item["title"].strip().lower()
            norm_url = item["url"].strip().lower()
            if norm_title in seen_titles or norm_url in seen_urls:
                continue

            seen_titles.add(norm_title)
            seen_urls.add(norm_url)

            published_time = now - timedelta(hours=item.get("hours_ago", 6))
            articles.append(
                NewsArticleItem(
                    symbol=sym,
                    title=item["title"],
                    description=item["description"],
                    source=item["source"],
                    url=item["url"],
                    published_at=published_time,
                    sentiment=item["sentiment"],
                    sentiment_score=item["sentiment_score"],
                    relevance=item["relevance"],
                    relevance_score=item["relevance_score"],
                    event_type=item["event_type"],
                    impact=item["impact"],
                )
            )
            if len(articles) >= limit:
                break

        return articles

    async def get_upcoming_events_for_symbol(self, symbol: str) -> List[MarketEventItem]:
        sym = symbol.upper().strip()
        raw_events = MOCK_EVENTS.get(sym, [])

        now = datetime.now(timezone.utc)
        events: List[MarketEventItem] = []

        for i, ev in enumerate(raw_events):
            days = ev["days_until"]
            event_dt = now + timedelta(days=days)
            events.append(
                MarketEventItem(
                    event_id=f"{sym}-EVT-{i+1}",
                    symbol=sym,
                    title=ev["title"],
                    event_type=ev["event_type"],
                    event_date=event_dt,
                    days_until=days,
                    impact=ev["impact"],
                    description=ev["description"],
                    implied_volatility_effect=ev["implied_volatility_effect"],
                )
            )

        return events
