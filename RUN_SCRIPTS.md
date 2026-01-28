# Run Scripts Documentation

This document describes the various scripts available to run the Task Telegram Mini App components.

## Overview

The application consists of three main components:
1. **FastAPI Web App** - The mini-app interface accessible via browser
2. **Admin Panel** - Web-based administration interface (part of FastAPI)
3. **Telegram Bot** - Bot interface for users on Telegram

## Available Scripts

### 1. `run.py` - Run All Components (Recommended)

**Command:**
```bash
python run.py
```

**What it does:**
- Starts FastAPI server (Web App + Admin Panel) on port 8000
- Starts Telegram Bot (if BOT_TOKEN is configured)
- Shows real-time colored logs from all services
- Monitors process health
- Handles graceful shutdown with Ctrl+C

**Features:**
- ✨ Color-coded output (Green for FastAPI, Yellow for Bot)
- 📊 Real-time log streaming
- 🛡️ Automatic error detection
- 🎯 Clear service status and access points
- ⚡ Fast startup with progress indicators

**Output Example:**
```
============================================================
    TASK APP - Starting All Services
============================================================

📋 Starting components:
   1. FastAPI Web App + Admin Panel
   2. Telegram Bot ✓

[13:00:07] [SETUP] Starting FastAPI server...
[13:00:07] [FastAPI] INFO: Started server process [1234]
[13:00:07] [FastAPI] INFO: Uvicorn running on http://0.0.0.0:8000

============================================================
✅ All Services Started Successfully!
============================================================

📍 Access Points:
   • Mini-App Home:  http://localhost:8000/miniapp
   • Admin Panel:    http://localhost:8000/admin
   • API Docs:       http://localhost:8000/docs
   • Telegram Bot:   Active and polling
```

### 2. `start.sh` - Bash Wrapper Script

**Command:**
```bash
./start.sh
```

**What it does:**
- Shell script wrapper for `run.py`
- Auto-detects Python installation (python3 or python)
- Auto-installs dependencies if missing
- Executes `run.py`

**Use case:** Convenient for users who prefer shell scripts or need auto-dependency installation.

### 3. `run_app.py` - Web App & Admin Panel Only

**Command:**
```bash
python run_app.py
```

**What it does:**
- Starts only the FastAPI server
- No bot component
- Simpler, focused output
- Direct uvicorn execution

**Use case:** When you only need the web interface and admin panel, or when the bot token is not available.

**Access Points:**
- Mini-App: http://localhost:8000/miniapp
- Admin Panel: http://localhost:8000/admin
- API Docs: http://localhost:8000/docs

### 4. `run_bot.py` - Telegram Bot Only

**Command:**
```bash
python run_bot.py
```

**What it does:**
- Starts only the Telegram Bot
- Validates BOT_TOKEN before starting
- Shows clear error messages if token is missing
- No web server

**Use case:** When the web server is running separately (e.g., in production with nginx) and you only need to start the bot.

**Requirements:**
- BOT_TOKEN must be set in .env file
- Web API endpoints should be available (bot depends on the API)

### 5. `main.py` - Direct FastAPI Execution

**Command:**
```bash
python main.py
```

**What it does:**
- Starts FastAPI server directly
- Basic uvicorn configuration
- Standard Python execution

**Use case:** Direct execution without wrapper scripts, or for debugging.

## Configuration

All scripts use settings from the `.env` file:

```env
BOT_TOKEN=your_telegram_bot_token_here
BOT_USERNAME=your_bot_username
ADMIN_API_KEY=your_admin_api_key_here
DATABASE_URL=sqlite:///./task_app.db
ADMIN_USER_IDS=123456789,987654321
WEB_APP_URL=http://localhost:8000
```

## Common Use Cases

### Development
```bash
# Run everything with real-time logs
python run.py
```

### Production (Separate Processes)
```bash
# Terminal 1 - Web Server
python run_app.py

# Terminal 2 - Bot
python run_bot.py
```

### Quick Start
```bash
# Easiest way
./start.sh
```

### Web Interface Only
```bash
# No bot needed
python run_app.py
```

### Bot Development
```bash
# Test bot changes independently
python run_bot.py
```

## Troubleshooting

### "BOT_TOKEN not configured"
- Create `.env` file from `.env.example`
- Get token from @BotFather on Telegram
- Set `BOT_TOKEN=your_actual_token` in `.env`

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`
- Or use `./start.sh` which auto-installs

### Port 8000 already in use
- Stop other services using port 8000
- Or change port in the scripts

### Bot won't start
- Verify BOT_TOKEN is valid
- Check internet connection
- Ensure database is accessible

## Script Comparison

| Script | Web App | Admin Panel | Bot | Auto-Install | Colors | Monitoring |
|--------|---------|-------------|-----|--------------|--------|------------|
| `run.py` | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| `start.sh` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `run_app.py` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `run_bot.py` | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `main.py` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

## Recommendations

- **For beginners:** Use `./start.sh` - it handles everything automatically
- **For development:** Use `python run.py` - best visibility and control
- **For production:** Run components separately with process managers (systemd, supervisor)
- **For testing:** Use individual scripts (`run_app.py`, `run_bot.py`)

## Additional Notes

- All scripts handle Ctrl+C gracefully for clean shutdown
- Logs are written to stdout in real-time
- Process health is monitored automatically in `run.py`
- Scripts are compatible with Python 3.9+
- Database is auto-created on first run
