#!/usr/bin/env python3
"""
Run only the Telegram Bot
This script starts only the bot component.
"""
import asyncio
import sys
from bot.bot import start_bot

if __name__ == "__main__":
    print("=" * 60)
    print("    Starting Telegram Bot")
    print("=" * 60)
    print()
    
    # Check if BOT_TOKEN is configured
    try:
        from config.settings import settings
        if not settings.bot_token or settings.bot_token == "your_telegram_bot_token_here":
            print("❌ Error: BOT_TOKEN not configured!")
            print()
            print("Please set BOT_TOKEN in your .env file:")
            print("  1. Copy .env.example to .env")
            print("  2. Get your bot token from @BotFather on Telegram")
            print("  3. Set BOT_TOKEN=your_actual_token in .env")
            print()
            sys.exit(1)
        
        print(f"✅ Bot configured: @{settings.bot_username}")
        print()
        print("Press Ctrl+C to stop the bot")
        print("-" * 60)
        print()
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\n\nBot stopped.")
        sys.exit(0)
