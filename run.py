#!/usr/bin/env python3
"""
Run both FastAPI server and Telegram bot concurrently
"""
import asyncio
import subprocess
import sys
import signal
import os


processes = []


def signal_handler(sig, frame):
    print("\nShutting down services...")
    for proc in processes:
        proc.terminate()
    sys.exit(0)


async def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting Task App services...")
    print("-" * 50)
    
    # Start FastAPI server
    print("Starting FastAPI server on http://localhost:8000")
    fastapi_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes.append(fastapi_proc)
    
    # Wait a bit for FastAPI to start
    await asyncio.sleep(2)
    
    # Check if BOT_TOKEN is set
    from config.settings import settings
    if not settings.bot_token:
        print("\nWARNING: BOT_TOKEN not set. Telegram bot will not start.")
        print("Please set BOT_TOKEN in .env file to use the Telegram bot.")
        print("\nAdmin panel is running at: http://localhost:8000/admin")
    else:
        # Start Telegram bot
        print("Starting Telegram bot...")
        bot_proc = subprocess.Popen(
            [sys.executable, "-m", "bot.bot"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(bot_proc)
    
    print("-" * 50)
    print("\n✅ Services started successfully!")
    print("\nAccess points:")
    print("  - Admin Panel: http://localhost:8000/admin")
    print("  - API Docs: http://localhost:8000/docs")
    print("  - Telegram Bot: Active (if BOT_TOKEN is set)")
    print("\nPress Ctrl+C to stop all services\n")
    
    # Keep the script running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServices stopped.")
