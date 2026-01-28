#!/usr/bin/env python3
"""
Run both FastAPI server and Telegram bot concurrently
This script manages all three components:
- FastAPI Web App (Mini-App)
- Admin Panel (part of FastAPI)
- Telegram Bot
"""
import asyncio
import subprocess
import sys
import signal
import os
import threading
import time
from datetime import datetime


processes = []
shutdown_event = threading.Event()


def log_prefix(service_name: str, color_code: str = "") -> str:
    """Generate a colored log prefix with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    reset = "\033[0m" if color_code else ""
    return f"{color_code}[{timestamp}] [{service_name}]{reset} "


def stream_output(process, service_name: str, color_code: str):
    """Stream output from a subprocess in real-time"""
    try:
        for line in iter(process.stdout.readline, b''):
            if shutdown_event.is_set():
                break
            if line:
                decoded = line.decode('utf-8').strip()
                if decoded:
                    print(f"{log_prefix(service_name, color_code)}{decoded}")
    except Exception as e:
        if not shutdown_event.is_set():
            print(f"{log_prefix(service_name, color_code)}Error reading output: {e}")


def signal_handler(sig, frame):
    """Handle Ctrl+C and graceful shutdown"""
    print("\n\n" + "=" * 60)
    print("Shutting down all services...")
    print("=" * 60)
    shutdown_event.set()
    
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        except Exception as e:
            print(f"Error terminating process: {e}")
    
    print("\n✅ All services stopped successfully!")
    sys.exit(0)


async def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("    TASK APP - Starting All Services")
    print("=" * 60)
    print()
    
    # Check if BOT_TOKEN is set before starting
    bot_enabled = False
    try:
        from config.settings import settings
        bot_enabled = bool(settings.bot_token and settings.bot_token != "your_telegram_bot_token_here")
    except Exception as e:
        print(f"⚠️  Warning: Could not load settings: {e}")
        print("    Continuing without bot...")
    
    print("📋 Starting components:")
    print(f"   1. FastAPI Web App + Admin Panel")
    print(f"   2. Telegram Bot {'✓' if bot_enabled else '✗ (BOT_TOKEN not configured)'}")
    print()
    print("-" * 60)
    
    # Start FastAPI server
    print(f"{log_prefix('SETUP', '\033[96m')}Starting FastAPI server...")
    fastapi_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1
    )
    processes.append(fastapi_proc)
    
    # Start output streaming thread for FastAPI
    fastapi_thread = threading.Thread(
        target=stream_output,
        args=(fastapi_proc, "FastAPI", "\033[92m"),  # Green
        daemon=True
    )
    fastapi_thread.start()
    
    # Wait for FastAPI to start
    await asyncio.sleep(3)
    
    # Start Telegram bot if token is configured
    if bot_enabled:
        print(f"{log_prefix('SETUP', '\033[96m')}Starting Telegram bot...")
        bot_proc = subprocess.Popen(
            [sys.executable, "-m", "bot.bot"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1
        )
        processes.append(bot_proc)
        
        # Start output streaming thread for bot
        bot_thread = threading.Thread(
            target=stream_output,
            args=(bot_proc, "Bot", "\033[93m"),  # Yellow
            daemon=True
        )
        bot_thread.start()
        
        await asyncio.sleep(2)
    else:
        print(f"{log_prefix('SETUP', '\033[96m')}Skipping bot (BOT_TOKEN not set)")
    
    print()
    print("=" * 60)
    print("✅ All Services Started Successfully!")
    print("=" * 60)
    print()
    print("📍 Access Points:")
    print(f"   • Mini-App Home:  http://localhost:8000/miniapp")
    print(f"   • Admin Panel:    http://localhost:8000/admin")
    print(f"   • API Docs:       http://localhost:8000/docs")
    if bot_enabled:
        print(f"   • Telegram Bot:   Active and polling")
    else:
        print(f"   • Telegram Bot:   Not configured (set BOT_TOKEN in .env)")
    print()
    print("💡 Tip: Set BOT_TOKEN in .env file to enable the Telegram bot")
    print()
    print("Press Ctrl+C to stop all services")
    print("-" * 60)
    print()
    
    # Monitor processes
    try:
        while not shutdown_event.is_set():
            await asyncio.sleep(1)
            
            # Check if any process has died
            for proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  Warning: A service has stopped unexpectedly!")
                    print(f"   Exit code: {proc.returncode}")
                    shutdown_event.set()
                    break
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServices stopped by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
