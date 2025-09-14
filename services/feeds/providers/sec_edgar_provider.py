#!/usr/bin/env python3
"""
SEC EDGAR Provider - SarvanOM v2

Implements SEC EDGAR API integration for market data (keyless)
with normalized data schema and proper error handling.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import structlog

logger = structlog.get_logger(__name__)

class SECEDGARProvider:
    """SEC EDGAR API provider (keyless)"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.base_url = "https://data.sec.gov/api/xbrl/companyfacts"
        self.timeout = 800  # 800ms timeout as per requirements
        
    async def fetch_markets(self, query: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch market data from SEC EDGAR API"""
        start_time = time.time()
        
        try:
            # Extract ticker symbols from query or constraints
            tickers = self._extract_tickers(query, constraints)
            
            if not tickers:
                return {
                    "provider": "sec_edgar",
                    "status": "error",
                    "items": [],
                    "latency_ms": 0,
                    "error": "No ticker symbols found"
                }
            
            # Fetch data for each ticker
            normalized_items = []
            for ticker in tickers[:3]:  # Limit to 3 tickers for performance
                try:
                    item = await self._fetch_ticker_data(ticker)
                    if item:
                        normalized_items.append(item)
                except Exception as e:
                    logger.warning(f"Failed to fetch SEC data for ticker {ticker}: {e}")
                    continue
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "provider": "sec_edgar",
                "status": "healthy",
                "items": normalized_items,
                "latency_ms": latency_ms,
                "total_results": len(normalized_items),
                "rate_limit_remaining": None,  # SEC doesn't provide this
                "cache_hit": False
            }
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"SEC EDGAR API failed: {e}")
            return {
                "provider": "sec_edgar",
                "status": "error",
                "items": [],
                "latency_ms": latency_ms,
                "error": str(e)
            }
    
    def _extract_tickers(self, query: str, constraints: Dict[str, Any] = None) -> List[str]:
        """Extract ticker symbols from query or constraints"""
        tickers = []
        
        # Check constraints first
        if constraints and constraints.get("tickers"):
            tickers.extend(constraints["tickers"])
        
        # Extract from query (simple pattern matching)
        import re
        # Look for common ticker patterns (3-5 uppercase letters)
        ticker_pattern = r'\b[A-Z]{3,5}\b'
        found_tickers = re.findall(ticker_pattern, query.upper())
        tickers.extend(found_tickers)
        
        # Remove duplicates and limit
        return list(set(tickers))[:3]
    
    async def _fetch_ticker_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch data for a single ticker from SEC EDGAR"""
        try:
            # SEC EDGAR company facts endpoint
            url = f"{self.base_url}/CIK{ticker}.json"
            
            headers = {
                "User-Agent": "SarvanOM/1.0 (contact@example.com)",  # SEC requires User-Agent
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout / 1000) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                return self._normalize_market_data(ticker, data)
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"SEC EDGAR: No data found for ticker {ticker}")
                return None
            else:
                logger.warning(f"SEC EDGAR HTTP error for {ticker}: {e.response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"Failed to fetch SEC data for {ticker}: {e}")
            return None
    
    def _normalize_market_data(self, ticker: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize SEC EDGAR data to common schema"""
        try:
            # Extract company information
            entity_name = data.get("entityName", ticker)
            cik = data.get("cik", "")
            
            # Extract financial data from facts
            facts = data.get("facts", {})
            us_gaap = facts.get("us-gaap", {})
            
            # Try to extract recent financial data
            current_price = None
            market_cap = None
            revenue = None
            
            # Look for common financial metrics
            if "Assets" in us_gaap:
                assets_data = us_gaap["Assets"]
                if "units" in assets_data and "USD" in assets_data["units"]:
                    recent_assets = self._get_latest_value(assets_data["units"]["USD"])
                    if recent_assets:
                        market_cap = recent_assets  # Use assets as proxy for market cap
            
            if "Revenues" in us_gaap:
                revenue_data = us_gaap["Revenues"]
                if "units" in revenue_data and "USD" in revenue_data["units"]:
                    recent_revenue = self._get_latest_value(revenue_data["units"]["USD"])
                    if recent_revenue:
                        revenue = recent_revenue
            
            # Generate unique ID
            market_id = f"sec_edgar_{ticker}_{cik}"
            
            return {
                "id": market_id,
                "symbol": ticker,
                "name": entity_name,
                "type": "stock",
                "price": {
                    "current": current_price,
                    "open": None,
                    "high": None,
                    "low": None,
                    "previous_close": None
                },
                "change": {
                    "absolute": None,
                    "percentage": None
                },
                "volume": None,
                "market_cap": market_cap,
                "currency": "USD",
                "exchange": "Unknown",
                "sector": None,
                "industry": None,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "provider": "sec_edgar",
                    "provider_id": market_id,
                    "ingested_at": datetime.utcnow().isoformat(),
                    "confidence": 0.9,
                    "cik": cik,
                    "revenue": revenue
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to normalize SEC data for {ticker}: {e}")
            return None
    
    def _get_latest_value(self, data_list: List[Dict[str, Any]]) -> Optional[float]:
        """Get the latest value from SEC EDGAR data list"""
        try:
            if not data_list:
                return None
            
            # Sort by end date (most recent first)
            sorted_data = sorted(data_list, key=lambda x: x.get("end", ""), reverse=True)
            
            # Get the most recent value
            latest = sorted_data[0]
            return float(latest.get("val", 0))
            
        except (ValueError, TypeError, KeyError):
            return None
