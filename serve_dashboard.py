#!/usr/bin/env python3
"""
Simple HTTP server to serve the Altman Z-Score dashboards.
This resolves CSS loading issues that can occur when opening HTML files directly.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def main():
    # Change to the web directory
    web_dir = Path(__file__).parent / "web"
    
    if not web_dir.exists():
        print(f"❌ Web directory not found: {web_dir}")
        sys.exit(1)
        
    os.chdir(web_dir)
    
    # Find an available port
    port = 8000
    while port < 8010:
        try:
            with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
                print(f"🚀 Starting HTTP server on port {port}")
                print(f"📂 Serving directory: {web_dir}")
                print(f"🌐 Dashboard URL: http://localhost:{port}")
                print("\n📊 Available dashboards:")
                print(f"   • Main Navigator: http://localhost:{port}/index.html")
                print(f"   • Strong Buys: http://localhost:{port}/strong_buys.html")
                print(f"   • Conservative Picks: http://localhost:{port}/conservative_picks.html")
                print(f"   • Dividend Picks: http://localhost:{port}/dividend_picks.html")
                print(f"   • Value Picks: http://localhost:{port}/value_picks.html")
                print(f"   • Growth Picks: http://localhost:{port}/growth_picks.html")
                print(f"   • Aggressive Picks: http://localhost:{port}/aggressive_picks.html")
                print("\n💡 Press Ctrl+C to stop the server")
                
                # Open the main dashboard in browser
                webbrowser.open(f"http://localhost:{port}/index.html")
                
                httpd.serve_forever()
        except OSError:
            port += 1
    
    print("❌ Could not find an available port in range 8000-8009")
    sys.exit(1)

if __name__ == "__main__":
    main()
