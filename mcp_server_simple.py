"""
Simplified MCP Server for Stock Prediction System
Works without requiring A2A agents to be running.
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
    MCP_AVAILABLE = True
except ImportError:
    print("MCP package not installed. Run: pip install mcp")
    MCP_AVAILABLE = False
    sys.exit(1)

# Try to import tools (optional)
try:
    from tools.polygon_fetcher import (
        get_fundamentals,
        get_price_history,
        get_latest_price,
        get_stock_news
    )
    TOOLS_AVAILABLE = True
except ImportError:
    print("⚠️  Tools not available. Some features will be limited.")
    TOOLS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleStockPredictionMCPServer:
    """Simplified MCP Server that works without A2A agents"""
    
    def __init__(self):
        self.server = Server("stock-prediction-simple")
        
        # Register handlers
        self.server.list_tools()(self.handle_list_tools)
        self.server.call_tool()(self.handle_call_tool)
        
        logger.info("✅ Simple Stock Prediction MCP Server initialized")
        logger.info("💡 This version works without requiring A2A agents")
    
    async def handle_list_tools(self) -> List[types.Tool]:
        """List all available tools"""
        tools = []
        
        # Basic analysis tool (simulated)
        tools.append(types.Tool(
            name="analyze_stock",
            description="Simulated stock analysis (doesn't require A2A agents)",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string", 
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
                    },
                    "horizon": {
                        "type": "string",
                        "description": "Prediction horizon",
                        "enum": ["next_week", "next_month", "next_quarter", "next_year"],
                        "default": "next_quarter"
                    }
                },
                "required": ["ticker"]
            }
        ))
        
        # Data tools (if available)
        if TOOLS_AVAILABLE:
            tools.append(types.Tool(
                name="get_stock_data",
                description="Get basic stock data (price, fundamentals if available)",
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
        
        # Always available tools
        tools.append(types.Tool(
            name="health_check",
            description="Check server status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ))
        
        tools.append(types.Tool(
            name="list_tickers",
            description="List example stock tickers",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ))
        
        tools.append(types.Tool(
            name="simulate_analysis",
            description="Simulate stock analysis with example data",
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
        
        return tools
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle tool execution"""
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        
        try:
            if name == "analyze_stock":
                return await self._analyze_stock_simulated(arguments)
            elif name == "get_stock_data":
                return await self._get_stock_data(arguments)
            elif name == "health_check":
                return await self._health_check(arguments)
            elif name == "list_tickers":
                return await self._list_tickers(arguments)
            elif name == "simulate_analysis":
                return await self._simulate_analysis(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error executing tool {name}: {str(e)}"
            )]
    
    async def _analyze_stock_simulated(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Simulated stock analysis (for testing without agents)"""
        ticker = arguments.get("ticker", "").upper().strip()
        horizon = arguments.get("horizon", "next_quarter")
        
        if not ticker:
            raise ValueError("Ticker symbol is required")
        
        # Simulate analysis
        analysis = {
            "ticker": ticker,
            "horizon": horizon,
            "recommendation": "HOLD",  # Simulated
            "confidence": 65.5,
            "risk_level": "MEDIUM",
            "rationale": f"Simulated analysis for {ticker}. This is a demonstration of the MCP interface. For full analysis, start A2A agents with 'python start_full_system.py'.",
            "timestamp": datetime.now().isoformat(),
            "note": "This is simulated data. Start A2A agents for real analysis."
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(analysis, indent=2)
        )]
    
    async def _get_stock_data(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get basic stock data"""
        ticker = arguments.get("ticker", "").upper().strip()
        
        if not ticker:
            raise ValueError("Ticker symbol is required")
        
        if not TOOLS_AVAILABLE:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "ticker": ticker,
                    "error": "Data tools not available. Check API keys and dependencies.",
                    "timestamp": datetime.now().isoformat()
                }, indent=2)
            )]
        
        try:
            # Try to get real data
            latest_price = get_latest_price(ticker)
            fundamentals = get_fundamentals(ticker)
            
            result = {
                "ticker": ticker,
                "latest_price": latest_price,
                "fundamentals": fundamentals,
                "timestamp": datetime.now().isoformat(),
                "data_source": "polygon.io" if "error" not in latest_price else "simulated"
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
            
        except Exception as e:
            # Fallback to simulated data
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "ticker": ticker,
                    "latest_price": {"close": 150.25, "error": "Simulated data"},
                    "fundamentals": {"market_cap": 2500000000000, "error": "Simulated data"},
                    "timestamp": datetime.now().isoformat(),
                    "note": f"Real data unavailable: {str(e)}"
                }, indent=2)
            )]
    
    async def _health_check(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Check server health"""
        health = {
            "status": "healthy",
            "server": "stock-prediction-simple",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "mcp": "available",
                "tools": "available" if TOOLS_AVAILABLE else "limited",
                "a2a_agents": "not_required",
                "api_keys": "check_env_file"
            },
            "message": "Server is running. For full features, ensure .env has API keys."
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(health, indent=2)
        )]
    
    async def _list_tickers(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """List example tickers"""
        tickers = [
            "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN",
            "META", "NVDA", "JPM", "JNJ", "V",
            "WMT", "PG", "DIS", "NFLX", "BAC"
        ]
        
        result = {
            "available_tickers": tickers,
            "count": len(tickers),
            "timestamp": datetime.now().isoformat(),
            "note": "Example tickers for testing. Most US stocks are supported."
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def _simulate_analysis(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Simulate detailed analysis with example data"""
        ticker = arguments.get("ticker", "").upper().strip()
        
        if not ticker:
            raise ValueError("Ticker symbol is required")
        
        # Example analysis data
        analysis = {
            "ticker": ticker,
            "analysis_date": datetime.now().isoformat(),
            "recommendation": "BUY" if ticker in ["AAPL", "MSFT", "GOOGL"] else "HOLD",
            "confidence_score": 72.5,
            "price_target": 185.50 if ticker == "AAPL" else 155.75,
            "current_price": 150.25,
            "analysis": {
                "fundamental": {
                    "score": 0.7,
                    "summary": "Strong financials, good growth prospects",
                    "metrics": {
                        "pe_ratio": 28.5,
                        "eps_growth": 12.3,
                        "debt_to_equity": 0.35
                    }
                },
                "technical": {
                    "score": 0.6,
                    "summary": "Bullish trend, good momentum",
                    "indicators": {
                        "rsi": 58,
                        "macd": "positive",
                        "trend": "upward"
                    }
                },
                "sentiment": {
                    "score": 0.8,
                    "summary": "Positive news flow, strong investor sentiment",
                    "news_count": 15
                }
            },
            "risk_factors": [
                "Market volatility",
                "Interest rate sensitivity",
                "Competition in sector"
            ],
            "next_earnings_date": "2024-01-25",
            "note": "This is simulated analysis data for demonstration."
        }
        
        # Format for display
        formatted = f"""
📊 SIMULATED STOCK ANALYSIS: {ticker}
========================================
📅 Analysis Date: {analysis['analysis_date']}
🎯 Recommendation: {analysis['recommendation']}
💪 Confidence: {analysis['confidence_score']}%
💰 Price Target: ${analysis['price_target']:.2f}
📈 Current Price: ${analysis['current_price']:.2f}

🔍 ANALYSIS BREAKDOWN:
• Fundamental: {analysis['analysis']['fundamental']['summary']}
• Technical: {analysis['analysis']['technical']['summary']}
• Sentiment: {analysis['analysis']['sentiment']['summary']}

⚠️  RISK FACTORS:
{chr(10).join(f'  • {risk}' for risk in analysis['risk_factors'])}

📅 Next Earnings: {analysis['next_earnings_date']}

💡 Note: {analysis['note']}
========================================
"""
        
        return [types.TextContent(
            type="text",
            text=formatted.strip()
        )]
    
    async def run(self):
        """Run the MCP server"""
        logger.info("🚀 Starting Simple Stock Prediction MCP Server...")
        logger.info("📡 Ready for MCP connections (stdio transport)")
        
        # Run with stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="stock-prediction-simple",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        tools=True,
                        resources=False
                    )
                )
            )


async def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("SIMPLE STOCK PREDICTION MCP SERVER")
    print("=" * 70)
    print("💡 This version works without requiring A2A agents to be running.")
    print("📡 Ready for MCP connections via stdio.")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 70)
    
    server = SimpleStockPredictionMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")