"""
MCP Server for Stock Prediction System
Provides MCP interface to the multi-agent stock prediction system.
Uses existing CloudOrchestrator to communicate with A2A agents.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("MCP package not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types

# Try to import the orchestrator
try:
    from agents.cloud_orchestrator import CloudOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import CloudOrchestrator: {e}")
    print("MCP server will run in limited mode without agent orchestration.")
    ORCHESTRATOR_AVAILABLE = False

# Import tools for direct data access
try:
    from tools.polygon_fetcher import (
        get_fundamentals,
        get_price_history,
        get_latest_price,
        get_stock_news
    )
    from tools.fred_fetcher import get_macro_indicators
    from tools.sec_edgar_fetcher import get_recent_filings
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import tools: {e}")
    TOOLS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockPredictionMCPServer:
    """MCP Server for Stock Prediction System"""
    
    def __init__(self):
        self.server = Server("stock-prediction-system")
        self.orchestrator = None
        
        if ORCHESTRATOR_AVAILABLE:
            try:
                self.orchestrator = CloudOrchestrator()
                logger.info("✅ CloudOrchestrator initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize CloudOrchestrator: {e}")
                self.orchestrator = None
        
        # Register handlers
        self.server.list_tools()(self.handle_list_tools)
        self.server.call_tool()(self.handle_call_tool)
        self.server.list_resources()(self.handle_list_resources)
        self.server.read_resource()(self.handle_read_resource)
        
        logger.info("✅ Stock Prediction MCP Server initialized")
    
    async def handle_list_tools(self) -> List[types.Tool]:
        """List all available tools"""
        tools = []
        
        # Full analysis tool
        tools.append(types.Tool(
            name="analyze_stock",
            description="Complete stock analysis using 6 AI agents (fundamental, technical, sentiment, macro, regulatory, predictor)",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string", 
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA, MSFT)"
                    },
                    "horizon": {
                        "type": "string",
                        "description": "Prediction horizon",
                        "enum": ["next_week", "next_month", "next_quarter", "next_year"],
                        "default": "next_quarter"
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Show detailed intermediate outputs",
                        "default": False
                    }
                },
                "required": ["ticker"]
            }
        ))
        
        # Individual analysis tools
        if TOOLS_AVAILABLE:
            tools.append(types.Tool(
                name="get_stock_fundamentals",
                description="Get fundamental financial data for a stock",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        }
                    },
                    "required": ["ticker"]
                }
            ))
            
            tools.append(types.Tool(
                name="get_stock_technical",
                description="Get technical analysis data and indicators",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days of historical data",
                            "default": 365
                        }
                    },
                    "required": ["ticker"]
                }
            ))
            
            tools.append(types.Tool(
                name="get_stock_sentiment",
                description="Get news sentiment analysis for a stock",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of news articles",
                            "default": 10
                        }
                    },
                    "required": ["ticker"]
                }
            ))
            
            tools.append(types.Tool(
                name="get_macro_indicators",
                description="Get macroeconomic indicators",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of indicators to fetch (GDP, CPI, UNRATE, FEDFUNDS)",
                            "default": ["GDP", "CPI", "UNRATE", "FEDFUNDS"]
                        }
                    }
                }
            ))
        
        # System tools
        tools.append(types.Tool(
            name="health_check",
            description="Check health status of the stock prediction system",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ))
        
        tools.append(types.Tool(
            name="list_available_tickers",
            description="List example tickers that can be analyzed",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ))
        
        return tools
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle tool execution"""
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        
        try:
            if name == "analyze_stock":
                return await self._analyze_stock(arguments)
            elif name == "get_stock_fundamentals":
                return await self._get_stock_fundamentals(arguments)
            elif name == "get_stock_technical":
                return await self._get_stock_technical(arguments)
            elif name == "get_stock_sentiment":
                return await self._get_stock_sentiment(arguments)
            elif name == "get_macro_indicators":
                return await self._get_macro_indicators(arguments)
            elif name == "health_check":
                return await self._health_check(arguments)
            elif name == "list_available_tickers":
                return await self._list_available_tickers(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error executing tool {name}: {str(e)}"
            )]
    
    async def _analyze_stock(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Perform complete stock analysis using orchestrator"""
        ticker = arguments.get("ticker", "").upper().strip()
        horizon = arguments.get("horizon", "next_quarter")
        verbose = arguments.get("verbose", False)
        
        if not ticker:
            raise ValueError("Ticker symbol is required")
        
        if not self.orchestrator:
            return [types.TextContent(
                type="text",
                text="Orchestrator not available. Please ensure A2A agents are running."
            )]
        
        # Perform analysis
        result = self.orchestrator.analyze_stock(
            ticker=ticker,
            horizon=horizon,
            verbose=verbose
        )
        
        # Format result for MCP
        formatted_result = self._format_analysis_result(result)
        
        return [types.TextContent(
            type="text",
            text=formatted_result
        )]
    
    async def _get_stock_fundamentals(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get fundamental data for a stock"""
        ticker = arguments.get("ticker", "").upper().strip()
        
        if not ticker:
            raise ValueError("Ticker symbol is required")
        
        if not TOOLS_AVAILABLE:
            return [types.TextContent(
                type="text",
                text="Data tools not available. Please check imports."
            )]
        
        fundamentals = get_fundamentals(ticker)
        latest_price = get_latest_price(ticker)
        
        result = {
            "ticker": ticker,
            "fundamentals": fundamentals,
            "latest_price": latest_price,
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    async def _get_stock_technical(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get technical analysis data"""
        ticker = arguments.get("ticker", "").upper().strip()
        days = arguments.get("days", 365)
        
        if not ticker:
            raise ValueError("Ticker symbol is required")
        
        if not TOOLS_AVAILABLE:
            return [types.TextContent(
                type="text",
                text="Data tools not available. Please check imports."
            )]
        
        price_history = get_price_history(ticker, days=days)
        latest_price = get_latest_price(ticker)
        
        result = {
            "ticker": ticker,
            "price_history": price_history,
            "latest_price": latest_price,
            "analysis_period_days": days,
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    async def _get_stock_sentiment(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get news sentiment analysis"""
        ticker = arguments.get("ticker", "").upper().strip()
        limit = arguments.get("limit", 10)
        
        if not ticker:
            raise ValueError("Ticker symbol is required")
        
        if not TOOLS_AVAILABLE:
            return [types.TextContent(
                type="text",
                text="Data tools not available. Please check imports."
            )]
        
        news = get_stock_news(ticker, limit=limit)
        
        # Simple sentiment analysis based on news titles
        positive_keywords = ["beat", "surge", "gain", "rise", "up", "bullish", "positive", "growth"]
        negative_keywords = ["fall", "drop", "decline", "down", "bearish", "negative", "loss", "miss"]
        
        sentiment_score = 0
        analyzed_news = []
        
        for article in news:
            title = article.get("title", "").lower()
            sentiment = 0
            
            for keyword in positive_keywords:
                if keyword in title:
                    sentiment += 1
            
            for keyword in negative_keywords:
                if keyword in title:
                    sentiment -= 1
            
            analyzed_news.append({
                "title": article.get("title", ""),
                "source": article.get("source", ""),
                "published_date": article.get("published_date", ""),
                "sentiment": sentiment
            })
            
            sentiment_score += sentiment
        
        result = {
            "ticker": ticker,
            "total_news": len(news),
            "sentiment_score": sentiment_score,
            "average_sentiment": sentiment_score / max(len(news), 1),
            "news_articles": analyzed_news,
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    async def _get_macro_indicators(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get macroeconomic indicators"""
        indicators = arguments.get("indicators", ["GDP", "CPI", "UNRATE", "FEDFUNDS"])
        
        if not TOOLS_AVAILABLE:
            return [types.TextContent(
                type="text",
                text="Data tools not available. Please check imports."
            )]
        
        macro_data = {}
        for indicator in indicators:
            try:
                data = get_macro_indicators([indicator])
                macro_data[indicator] = data
            except Exception as e:
                macro_data[indicator] = {"error": str(e)}
        
        result = {
            "indicators": macro_data,
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    async def _health_check(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Check system health"""
        health_status = {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Check orchestrator
        if self.orchestrator:
            health_status["components"]["orchestrator"] = "available"
            try:
                agent_health = self.orchestrator.check_agents_health()
                health_status["components"]["agents_health"] = agent_health
                
                # Count online agents
                online_count = sum(1 for status in agent_health.values() if status == "online")
                health_status["agents_online"] = f"{online_count}/6"
            except Exception as e:
                health_status["components"]["agents_health"] = f"error: {str(e)}"
        else:
            health_status["components"]["orchestrator"] = "unavailable"
            health_status["status"] = "degraded"
        
        # Check tools
        health_status["components"]["data_tools"] = "available" if TOOLS_AVAILABLE else "unavailable"
        
        if not TOOLS_AVAILABLE:
            health_status["status"] = "degraded"
        
        return [types.TextContent(
            type="text",
            text=json.dumps(health_status, indent=2)
        )]
    
    async def _list_available_tickers(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """List example tickers"""
        example_tickers = [
            "AAPL",  # Apple
            "GOOGL", # Google
            "MSFT",  # Microsoft
            "TSLA",  # Tesla
            "AMZN",  # Amazon
            "META",  # Meta
            "NVDA",  # NVIDIA
            "JPM",   # JPMorgan Chase
            "JNJ",   # Johnson & Johnson
            "V",     # Visa
            "WMT",   # Walmart
            "PG",    # Procter & Gamble
            "DIS",   # Disney
            "NFLX",  # Netflix
            "BAC",   # Bank of America
        ]
        
        result = {
            "available_tickers": example_tickers,
            "count": len(example_tickers),
            "note": "These are example tickers. Most US stocks are supported.",
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def handle_list_resources(self) -> List[types.Resource]:
        """List available resources"""
        return [
            types.Resource(
                uri="stock-prediction://system/info",
                name="System Information",
                description="Information about the Stock Prediction System",
                mimeType="application/json"
            ),
            types.Resource(
                uri="stock-prediction://agents/status",
                name="Agents Status",
                description="Status of all AI agents in the system",
                mimeType="application/json"
            )
        ]
    
    async def handle_read_resource(self, uri: str) -> types.ResourceContents:
        """Read resource content"""
        if uri == "stock-prediction://system/info":
            info = {
                "system": "Stock Prediction AI System",
                "version": "1.0.0",
                "architecture": "Multi-Agent A2A with MCP Interface",
                "agents": 6,
                "mcp_interface": True,
                "timestamp": datetime.now().isoformat()
            }
            return types.ResourceContents(
                contents=[types.TextContent(
                    type="text",
                    text=json.dumps(info, indent=2)
                )]
            )
        
        elif uri == "stock-prediction://agents/status":
            if self.orchestrator:
                try:
                    agent_health = self.orchestrator.check_agents_health()
                    status = {
                        "agents": agent_health,
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    status = {
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                status = {
                    "error": "Orchestrator not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            return types.ResourceContents(
                contents=[types.TextContent(
                    type="text",
                    text=json.dumps(status, indent=2)
                )]
            )
        
        raise ValueError(f"Unknown resource: {uri}")
    
    def _format_analysis_result(self, result: Dict[str, Any]) -> str:
        """Format analysis result for display"""
        # Create a formatted string from the analysis result
        lines = []
        
        lines.append("=" * 70)
        lines.append(f"📊 STOCK PREDICTION REPORT: {result.get('ticker', 'N/A')}")
        lines.append("=" * 70)
        lines.append("")
        
        # Main prediction
        recommendation = result.get('recommendation', 'N/A')
        confidence = result.get('confidence', 0)
        risk_level = result.get('risk_level', 'N/A')
        
        rec_symbol = {
            "BUY": "🟢 BUY",
            "HOLD": "🟡 HOLD",
            "SELL": "🔴 SELL"
        }.get(recommendation, recommendation)
        
        lines.append(f"RECOMMENDATION:    {rec_symbol}")
        lines.append(f"CONFIDENCE:        {confidence}%")
        lines.append(f"RISK LEVEL:        {risk_level}")
        
        if result.get('weighted_signal'):
            lines.append(f"WEIGHTED SIGNAL:   {result['weighted_signal']:+.3f}")
        
        lines.append("")
        lines.append("=" * 70)
        lines.append("📝 ANALYSIS RATIONALE")
        lines.append("=" * 70)
        
        rationale = result.get('rationale', 'No rationale available')
        # Split rationale into lines if it's a string
        if isinstance(rationale, str):
            lines.extend(rationale.split('\n'))
        else:
            lines.append(str(rationale))
        
        # Agent reports
        if result.get('analysis_reports'):
            lines.append("")
            lines.append("=" * 70)
            lines.append("🔍 AGENT ANALYSIS REPORTS")
            lines.append("=" * 70)
            
            for agent_type, report in result['analysis_reports'].items():
                if isinstance(report, dict):
                    signal = report.get('directional_signal', 0)
                    confidence = report.get('confidence_score', 0)
                    
                    agent_name = agent_type.replace('_', ' ').title()
                    signal_emoji = "🟢" if signal > 0.3 else "🔴" if signal < -0.3 else "🟡"
                    
                    lines.append(f"{agent_name}: {signal_emoji} Signal: {signal:+.2f}, Confidence: {confidence:.0f}%")
        
        # Timing info
        lines.append("")
        lines.append("=" * 70)
        elapsed = result.get('elapsed_seconds', 0)
        timestamp = result.get('timestamp', '')
        lines.append(f"⏱️  Analysis completed in {elapsed:.2f} seconds")
        lines.append(f"🕐 Timestamp: {timestamp}")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    async def run(self):
        """Run the MCP server"""
        logger.info("🚀 Starting Stock Prediction MCP Server...")
        
        # Run with stdio transport (for MCP protocol)
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="stock-prediction-system",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        tools=True,
                        resources=True
                    )
                )
            )


async def main():
    """Main entry point"""
    server = StockPredictionMCPServer()
    await server.run()


if __name__ == "__main__":
    # Run the MCP server
    asyncio.run(main())