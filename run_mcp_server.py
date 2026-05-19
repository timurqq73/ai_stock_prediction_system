#!/usr/bin/env python3
"""
Run MCP Server for Stock Prediction System
This script starts the MCP server that provides access to the stock prediction system.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import mcp
        logger.info("✅ MCP package is installed")
    except ImportError:
        logger.error("❌ MCP package not installed")
        logger.info("Installing MCP package...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
            logger.info("✅ MCP package installed successfully")
        except Exception as e:
            logger.error(f"❌ Failed to install MCP: {e}")
            return False
    
    # Check for .env file
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        logger.warning("⚠️  .env file not found. Creating template...")
        try:
            with open(env_file, "w") as f:
                f.write("""# Stock Prediction System - Environment Variables
# Required:
# GOOGLE_API_KEY=your_google_api_key_here
# POLYGON_API_KEY=your_polygon_api_key_here

# Optional but recommended:
# FRED_API_KEY=your_fred_api_key_here
# NEWS_API_KEY=your_news_api_key_here

# MCP Server Configuration
MCP_SERVER_PORT=8007
MCP_SERVER_HOST=0.0.0.0
""")
            logger.info("✅ Created .env template. Please fill in your API keys.")
        except Exception as e:
            logger.error(f"❌ Failed to create .env template: {e}")
    
    return True

async def run_mcp_server():
    """Run the MCP server"""
    try:
        from mcp_server import StockPredictionMCPServer
        
        logger.info("🚀 Initializing Stock Prediction MCP Server...")
        server = StockPredictionMCPServer()
        
        logger.info("✅ MCP Server initialized successfully")
        logger.info("📡 Server is ready to accept connections via MCP protocol")
        logger.info("💡 Use with MCP-compatible clients (Claude Desktop, Cursor, etc.)")
        logger.info("🛑 Press Ctrl+C to stop the server")
        
        await server.run()
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("Make sure you're in the correct directory and dependencies are installed.")
        return 1
    except Exception as e:
        logger.error(f"❌ Error running MCP server: {e}")
        return 1
    
    return 0

def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("STOCK PREDICTION SYSTEM - MCP SERVER")
    print("=" * 70)
    print()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Run the MCP server
    try:
        return asyncio.run(run_mcp_server())
    except KeyboardInterrupt:
        logger.info("\n🛑 MCP Server stopped by user")
        return 0

if __name__ == "__main__":
    sys.exit(main())