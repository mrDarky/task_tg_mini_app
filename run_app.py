#!/usr/bin/env python3
"""
Run only the FastAPI Web App and Admin Panel
This script starts only the web server component.
"""
import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("    Starting FastAPI Web App + Admin Panel")
    print("=" * 60)
    print()
    print("📍 Access Points:")
    print("   • Mini-App Home:  http://localhost:8000/miniapp")
    print("   • Admin Panel:    http://localhost:8000/admin")
    print("   • API Docs:       http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    print()
    
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
