#!/usr/bin/env python3
"""
Run only the FastAPI Web App and Admin Panel
This script starts only the web server component.
"""
import sys
import uvicorn
from config.settings import settings

if __name__ == "__main__":
    port = settings.port
    print("=" * 60)
    print("    Starting FastAPI Web App + Admin Panel")
    print("=" * 60)
    print()
    print("📍 Access Points:")
    print(f"   • Mini-App Home:  http://localhost:{port}/miniapp")
    print(f"   • Admin Panel:    http://localhost:{port}/admin")
    print(f"   • API Docs:       http://localhost:{port}/docs")
    print()
    print("💡 Development mode: Auto-reload enabled")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    print()
    
    try:
        # reload=True enables auto-reload for development
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
