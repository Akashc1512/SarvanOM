#!/usr/bin/env python3
"""
Stooq Provider - SarvanOM v2

Implements Stooq CSV API integration for market data (keyless)
with normalized data schema and proper error handling.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import csv
import io
import structlog

logger = structlog.get_logger(__name__)

class StooqProvider:
    """Stooq CSV API provider (keyless)"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.base_url = "https://stooq.com/q/l"
        self.timeout = 800  # 800ms timeout as per requirements
        
    async def fetch_markets(self, query: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch market data from Stooq CSV API"""
        start_time = time.time()
        
        try:
            # Extract ticker symbols from query or constraints
            tickers = self._extract_tickers(query, constraints)
            
            if not tickers:
                return {
                    "provider": "stooq",
                    "status": "error",
                    "items": [],
                    "latency_ms": 0,
                    "error": "No ticker symbols found"
                }
            
            # Fetch data for each ticker
            normalized_items = []
            for ticker in tickers[:5]:  # Limit to 5 tickers for performance
                try:
                    item = await self._fetch_ticker_data(ticker)
                    if item:
                        normalized_items.append(item)
                except Exception as e:
                    logger.warning(f"Failed to fetch data for ticker {ticker}: {e}")
                    continue
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "provider": "stooq",
                "status": "healthy",
                "items": normalized_items,
                "latency_ms": latency_ms,
                "total_results": len(normalized_items),
                "rate_limit_remaining": None,  # Stooq doesn't provide this
                "cache_hit": False
            }
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Stooq API failed: {e}")
            return {
                "provider": "stooq",
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
        return list(set(tickers))[:5]
    
    async def _fetch_ticker_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch data for a single ticker"""
        try:
            # Stooq CSV endpoint
            url = f"{self.base_url}/?s={ticker}&f=sd2t2ohlcv&h&e=csv"
            
            async with httpx.AsyncClient(timeout=self.timeout / 1000) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Parse CSV response
                csv_content = response.text
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                
                for row in csv_reader:
                    return self._normalize_market_data(ticker, row)
                
                return None
                
        except Exception as e:
            logger.warning(f"Failed to fetch Stooq data for {ticker}: {e}")
            return None
    
    def _normalize_market_data(self, ticker: str, data: Dict[str, str]) -> Dict[str, Any]:
        """Normalize Stooq market data to common schema"""
        try:
            # Extract price data
            current_price = self._safe_float(data.get("Close", "0"))
            open_price = self._safe_float(data.get("Open", "0"))
            high_price = self._safe_float(data.get("High", "0"))
            low_price = self._safe_float(data.get("Low", "0"))
            volume = self._safe_int(data.get("Volume", "0"))
            
            # Calculate change
            change_absolute = current_price - open_price if open_price > 0 else 0
            change_percentage = (change_absolute / open_price * 100) if open_price > 0 else 0
            
            # Extract date
            date_str = data.get("Date", "")
            timestamp = None
            if date_str:
                try:
                    # Stooq date format is usually YYYY-MM-DD
                    timestamp = datetime.fromisoformat(date_str).isoformat()
                except:
                    timestamp = datetime.utcnow().isoformat()
            else:
                timestamp = datetime.utcnow().isoformat()
            
            # Generate unique ID
            market_id = f"stooq_{ticker}_{date_str}"
            
            return {
                "id": market_id,
                "symbol": ticker,
                "name": ticker,  # Stooq doesn't provide company names
                "type": "stock",
                "price": {
                    "current": current_price,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "previous_close": open_price  # Use open as previous close
                },
                "change": {
                    "absolute": change_absolute,
                    "percentage": change_percentage
                },
                "volume": volume,
                "market_cap": None,  # Stooq doesn't provide market cap
                "currency": "USD",  # Assume USD
                "exchange": "Unknown",  # Stooq doesn't provide exchange info
                "sector": None,
                "industry": None,
                "timestamp": timestamp,
                "metadata": {
                    "provider": "stooq",
                    "provider_id": market_id,
                    "ingested_at": datetime.utcnow().isoformat(),
                    "confidence": 0.8
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to normalize Stooq data for {ticker}: {e}")
            return None
    
    def _safe_float(self, value: str) -> float:
        """Safely convert string to float"""
        try:
            return float(value) if value and value != "N/A" else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_int(self, value: str) -> int:
        """Safely convert string to int"""
        try:
            return int(value) if value and value != "N/A" else 0
        except (ValueError, TypeError):
            return 0
