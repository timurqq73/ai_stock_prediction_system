# MCP Interface for Stock Prediction System

Model Context Protocol (MCP) interface for the multi-agent stock prediction system. This allows the system to be used as a tool by MCP-compatible clients like Claude Desktop, Cursor, and others.

## 📋 Overview

The MCP server provides access to the stock prediction system's capabilities through the Model Context Protocol. It wraps the existing A2A agent architecture and provides tools for stock analysis.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install MCP package
pip install mcp

# Or install from requirements
pip install -r requirements.txt
```

### 2. Configure API Keys

Make sure your `.env` file has the required API keys:

```bash
GOOGLE_API_KEY=your_google_api_key_here
POLYGON_API_KEY=your_polygon_api_key_here
FRED_API_KEY=your_fred_api_key_here  # Optional
NEWS_API_KEY=your_news_api_key_here  # Optional
```

### 3. Start the MCP Server

```bash
# Method 1: Using the run script
python run_mcp_server.py

# Method 2: Direct module execution
python -m mcp_server

# Method 3: With stdio (for MCP clients)
python mcp_server.py
```

## 🔧 Available Tools

The MCP server provides the following tools:

### 1. `analyze_stock`
Complete stock analysis using all 6 AI agents.

**Parameters:**
- `ticker` (required): Stock ticker symbol (e.g., "AAPL", "GOOGL", "TSLA")
- `horizon` (optional): Prediction horizon ("next_week", "next_month", "next_quarter", "next_year")
- `verbose` (optional): Show detailed outputs (true/false)

**Example:**
```json
{
  "ticker": "AAPL",
  "horizon": "next_quarter",
  "verbose": false
}
```

### 2. `get_stock_fundamentals`
Get fundamental financial data for a stock.

**Parameters:**
- `ticker` (required): Stock ticker symbol

### 3. `get_stock_technical`
Get technical analysis data and indicators.

**Parameters:**
- `ticker` (required): Stock ticker symbol
- `days` (optional): Number of days of historical data (default: 365)

### 4. `get_stock_sentiment`
Get news sentiment analysis for a stock.

**Parameters:**
- `ticker` (required): Stock ticker symbol
- `limit` (optional): Maximum number of news articles (default: 10)

### 5. `get_macro_indicators`
Get macroeconomic indicators.

**Parameters:**
- `indicators` (optional): List of indicators to fetch (default: ["GDP", "CPI", "UNRATE", "FEDFUNDS"])

### 6. `health_check`
Check health status of the stock prediction system.

### 7. `list_available_tickers`
List example tickers that can be analyzed.

## 📡 Integration with MCP Clients

### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "stock-prediction": {
      "command": "python",
      "args": ["/path/to/stock-prediction-system/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/stock-prediction-system"
      }
    }
  }
}
```

### Cursor

Add to Cursor's MCP configuration:

```json
{
  "mcpServers": {
    "stock-prediction": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/stock-prediction-system"
    }
  }
}
```

### Kiro

Place the `mcp.json` file in your Kiro configuration directory or update `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "stock-prediction-system": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## 🐳 Docker Integration

### Option 1: Add to existing docker-compose

Add to your `docker-compose.yml`:

```yaml
services:
  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile.system
    env_file:
      - .env
    ports:
      - "8007:8007"
    command: python -m mcp_server
    restart: unless-stopped
```

### Option 2: Standalone Docker

```bash
# Build the image
docker build -t stock-prediction-mcp -f Dockerfile.system .

# Run the MCP server
docker run -p 8007:8007 --env-file .env stock-prediction-mcp python -m mcp_server
```

## 🧪 Testing the MCP Server

### Test with MCP Inspector

```bash
# Install MCP Inspector
pip install mcp-inspector

# Run inspector
python -m mcp.inspector python mcp_server.py
```

### Test with curl (if using HTTP transport)

```bash
# List tools
curl http://localhost:8007/tools

# Call a tool
curl -X POST http://localhost:8007/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "health_check", "arguments": {}}'
```

## 🔍 Resources

The MCP server also provides resources:

1. `stock-prediction://system/info` - System information
2. `stock-prediction://agents/status` - Agents status

## 🚨 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'mcp'"**
   ```bash
   pip install mcp
   ```

2. **"ImportError: cannot import name 'CloudOrchestrator'"**
   Make sure you're running from the project root directory.

3. **API Key Errors**
   Check your `.env` file has valid API keys.

4. **Agents Not Running**
   The MCP server can work without agents, but full analysis requires A2A agents to be running:
   ```bash
   python start_full_system.py
   ```

### Logs

Check the console output for detailed logs. The server logs at INFO level by default.

## 📁 Project Structure

```
AI-agents-Stock-prediction-System/
├── mcp_server.py          # Main MCP server implementation
├── run_mcp_server.py      # Runner script
├── mcp.json              # MCP configuration
├── MCP_README.md         # This file
├── agents/               # Existing A2A agents
├── tools/                # Data fetching tools
└── ...                   # Other project files
```

## 🔄 How It Works

1. MCP client connects to the server via stdio or HTTP
2. Client requests list of available tools
3. Client calls tools with parameters
4. Server executes the request using:
   - Existing `CloudOrchestrator` for full analysis
   - Direct tool calls for individual data
5. Results are returned in structured format

## 📈 Example Usage

```python
# Example MCP client code
import mcp.client

async def analyze_stock():
    async with mcp.client.Client() as client:
        # Connect to server
        await client.connect_to_server(
            command="python",
            args=["mcp_server.py"]
        )
        
        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Analyze a stock
        result = await client.call_tool(
            name="analyze_stock",
            arguments={"ticker": "AAPL", "horizon": "next_quarter"}
        )
        
        print(f"Analysis result: {result}")
```

## 📄 License

MIT License - Same as the main project.

## 👥 Authors

Bogdan Chernykh

## 🧾 Date

May 2026