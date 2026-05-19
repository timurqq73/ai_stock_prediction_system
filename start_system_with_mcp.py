#!/usr/bin/env python3
"""
Start the full system with MCP server
This script starts the main system and the MCP server.
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

def start_system():
    """Start the main stock prediction system"""
    print("🚀 Starting main stock prediction system...")
    
    system_script = Path(__file__).parent / "start_full_system.py"
    if not system_script.exists():
        print(f"❌ System script not found: {system_script}")
        return None
    
    try:
        # Start the system in a subprocess
        proc = subprocess.Popen(
            [sys.executable, str(system_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Start a thread to read output
        def read_output():
            for line in proc.stdout:
                print(f"[SYSTEM] {line}", end='')
        
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        
        print("✅ Main system started")
        return proc
        
    except Exception as e:
        print(f"❌ Failed to start system: {e}")
        return None

def start_mcp_server():
    """Start the MCP server"""
    print("\n🚀 Starting MCP server...")
    
    mcp_script = Path(__file__).parent / "run_mcp_server.py"
    if not mcp_script.exists():
        print(f"❌ MCP script not found: {mcp_script}")
        return None
    
    try:
        # Start the MCP server in a subprocess
        proc = subprocess.Popen(
            [sys.executable, str(mcp_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Start a thread to read output
        def read_output():
            for line in proc.stdout:
                print(f"[MCP] {line}", end='')
        
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        
        print("✅ MCP server started")
        return proc
        
    except Exception as e:
        print(f"❌ Failed to start MCP server: {e}")
        return None

def check_health():
    """Check if services are healthy"""
    import urllib.request
    import urllib.error
    
    print("\n🔍 Checking service health...")
    
    services = [
        ("Backend API", "http://localhost:8000/health"),
        ("Frontend", "http://localhost:3001/"),
        ("Fundamental Agent", "http://localhost:8001/.well-known/agent-card.json"),
        ("Technical Agent", "http://localhost:8002/.well-known/agent-card.json"),
        ("Sentiment Agent", "http://localhost:8003/.well-known/agent-card.json"),
        ("Macro Agent", "http://localhost:8004/.well-known/agent-card.json"),
        ("Regulatory Agent", "http://localhost:8005/.well-known/agent-card.json"),
        ("Predictor Agent", "http://localhost:8006/.well-known/agent-card.json"),
    ]
    
    healthy_count = 0
    for name, url in services:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if 200 <= resp.status < 500:
                    print(f"  ✅ {name}: Healthy")
                    healthy_count += 1
                else:
                    print(f"  ⚠️  {name}: HTTP {resp.status}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
    
    print(f"\n📊 Health summary: {healthy_count}/{len(services)} services healthy")
    
    # Give MCP server time to start
    print("\n⏳ Waiting for MCP server to initialize...")
    time.sleep(3)
    
    return healthy_count >= 3  # At least 3 services should be healthy

def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("STOCK PREDICTION SYSTEM WITH MCP INTERFACE")
    print("=" * 70)
    print()
    
    # Check if we're in the right directory
    if not Path(__file__).parent.exists():
        print("❌ Please run this script from the project root directory")
        return 1
    
    # Start services
    system_proc = start_system()
    if not system_proc:
        return 1
    
    # Wait for system to start
    print("\n⏳ Waiting for system to initialize (10 seconds)...")
    time.sleep(10)
    
    # Check health
    if not check_health():
        print("⚠️  Some services may not be fully healthy, but continuing...")
    
    # Start MCP server
    mcp_proc = start_mcp_server()
    if not mcp_proc:
        print("⚠️  MCP server failed to start, but main system is running")
    
    print("\n" + "=" * 70)
    print("✅ SYSTEM STARTED SUCCESSFULLY")
    print("=" * 70)
    print("\n📡 Available services:")
    print("  • Frontend:      http://localhost:3001")
    print("  • Backend API:   http://localhost:8000")
    print("  • A2A Agents:    http://localhost:8001-8006")
    print("  • MCP Server:    Running on stdio (port 8007 for HTTP if configured)")
    print("\n🔧 MCP Tools available:")
    print("  • analyze_stock           - Complete stock analysis")
    print("  • get_stock_fundamentals  - Fundamental data")
    print("  • get_stock_technical     - Technical analysis")
    print("  • get_stock_sentiment     - News sentiment")
    print("  • get_macro_indicators    - Macroeconomic data")
    print("  • health_check            - System health")
    print("  • list_available_tickers  - Example tickers")
    print("\n🛑 Press Ctrl+C to stop all services")
    print("=" * 70)
    
    try:
        # Keep running until interrupted
        while True:
            # Check if processes are still running
            if system_proc and system_proc.poll() is not None:
                print("\n❌ Main system process terminated")
                break
            
            if mcp_proc and mcp_proc.poll() is not None:
                print("\n❌ MCP server process terminated")
                break
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        
        if system_proc and system_proc.poll() is None:
            system_proc.terminate()
            system_proc.wait(timeout=5)
            print("✅ Main system stopped")
        
        if mcp_proc and mcp_proc.poll() is None:
            mcp_proc.terminate()
            mcp_proc.wait(timeout=5)
            print("✅ MCP server stopped")
        
        print("\n👋 All services stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())