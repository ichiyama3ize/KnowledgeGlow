#!/usr/bin/env python3
"""
Simple HTTP server for KnowledgeGlow Web UI
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "web-ui"}')
            return
        
        # Serve index.html for root path
        if self.path == '/':
            self.path = '/index.html'
        
        return super().do_GET()

def main():
    port = int(os.getenv('WEBUI_PORT', 8000))
    
    # Change to the web-ui directory
    web_ui_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_ui_dir)
    
    with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
        print(f"🌐 Web UI Server starting on port {port}")
        print(f"📁 Serving files from: {web_ui_dir}")
        print(f"🔗 Access the UI at: http://localhost:{port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Web UI Server stopped")

if __name__ == "__main__":
    main()