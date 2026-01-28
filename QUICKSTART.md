# Quick Start Guide

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` file:
```env
BOT_TOKEN=your_telegram_bot_token_here
BOT_USERNAME=your_bot_username
ADMIN_API_KEY=your_admin_api_key_here
DATABASE_URL=sqlite:///./task_app.db
ADMIN_USER_IDS=123456789
WEB_APP_URL=http://localhost:8000
```

### 3. Start Services

**Option A: Run All Services Together (Easiest)**
```bash
python run.py
# Or simply:
./start.sh
```
This starts all three components (Web App, Admin Panel, Bot) in one command with real-time logs.

**Option B: Run Individual Components**
```bash
# Only Web App + Admin Panel
python run_app.py

# Only Telegram Bot
python run_bot.py
```

**Option C: Run Manually in Separate Terminals**
```bash
# Terminal 1 - Start FastAPI Server
python main.py

# Terminal 2 - Start Telegram Bot
python -m bot.bot
```

**Option D: Development Mode (FastAPI only)**
```bash
# Only FastAPI Server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```


## Access Points

- **Admin Panel**: http://localhost:8000/admin
- **Mini-App Home**: http://localhost:8000/miniapp
- **API Docs**: http://localhost:8000/docs
- **Telegram Bot**: Search for your bot in Telegram

## Bot Commands

Users can use these commands in Telegram:

- `/start` - Register and get referral code
- `/tasks` - Browse tasks by category
- `/profile` - View profile and statistics
- `/help` - Get help and support info
- `/settings` - Manage preferences

## Mini-App Pages

Accessible via bot's "Open Mini App" button:

1. **Home** (`/miniapp/home`) - Dashboard with balance and quick tasks
2. **Tasks** (`/miniapp/tasks`) - Browse and filter tasks
3. **Profile** (`/miniapp/profile`) - Stats, achievements, referrals
4. **Rewards** (`/miniapp/rewards`) - Redeem rewards, withdraw
5. **Task Detail** (`/miniapp/task/{id}`) - Complete specific task

## Key Features

### For Users
- ⭐ Earn stars by completing tasks
- 🎁 Daily bonus with streak tracking
- 👥 Referral system (50 stars per friend)
- 🏆 Achievement badges
- 📸 Task verification with screenshots
- 💰 Withdraw stars for rewards

### For Admins
- 👥 User management (ban, adjust stars)
- 📝 Task management (create, edit, delete)
- 📁 Category organization
- 💰 Withdrawal approval
- 🔔 Send notifications
- 🎫 Support ticket handling

## Development

### Project Structure
```
task_tg_mini_app/
├── app/
│   ├── models.py              # Pydantic models
│   ├── routers/               # API endpoints
│   ├── services/              # Business logic
│   ├── templates/             # HTML templates
│   │   ├── miniapp_*.html    # Mini-app pages
│   │   └── *.html            # Admin pages
│   └── static/
│       ├── miniapp/          # Mini-app assets
│       │   ├── css/
│       │   └── js/
│       ├── css/              # Admin CSS
│       └── js/               # Admin JS
├── bot/
│   └── bot.py                # Telegram bot
├── config/
│   └── settings.py           # Configuration
├── database/
│   └── db.py                 # Database layer
└── main.py                   # FastAPI app
```

### Database Tables

**Core Tables:**
- users, tasks, categories, user_tasks

**Feature Tables:**
- referrals, daily_bonuses
- achievements, user_achievements
- user_settings, task_submissions
- star_transactions, withdrawals
- notifications, tickets

### Adding New Features

1. **New Bot Command:**
   - Add handler in `bot/bot.py`
   - Use `@dp.message(Command("name"))`

2. **New Callback Query:**
   - Add handler in `bot/bot.py`
   - Use `@dp.callback_query(F.data == "name")`

3. **New Mini-App Page:**
   - Create HTML in `app/templates/`
   - Add route in `main.py`
   - Create JS in `app/static/miniapp/js/`

4. **New API Endpoint:**
   - Add to appropriate router in `app/routers/`
   - Add service logic in `app/services/`
   - Update models in `app/models.py`

5. **New Database Table:**
   - Add CREATE TABLE in `database/db.py`
   - Add model in `app/models.py`
   - Add service methods

## Testing

### Manual Testing
```bash
# Test FastAPI import
python -c "from main import app; print('OK')"

# Test bot syntax
python -m py_compile bot/bot.py

# Check database tables
sqlite3 task_app.db ".tables"
```

### Security Check
```bash
# Already run - 0 vulnerabilities found
# CodeQL scan completed successfully
```

## Common Issues

### Bot Token Invalid
- Get token from @BotFather on Telegram
- Set BOT_TOKEN in .env file
- Format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### Database Not Created
- Ensure write permissions in project directory
- Database auto-creates on first app start
- Check database/db.py for table creation

### Mini-App Not Loading
- Set WEB_APP_URL in .env
- Ensure FastAPI server is running
- Check browser console for errors

### Import Errors
- Install all dependencies: `pip install -r requirements.txt`
- Activate virtual environment
- Check Python version (3.9+)

## Deployment

See README.md section "Deployment" for production setup including:
- PostgreSQL configuration
- Nginx reverse proxy
- SSL certificates
- Environment variables
- Process managers

## Support

- 📖 Full Documentation: README.md
- 📋 Implementation Details: IMPLEMENTATION_SUMMARY.md
- 🐛 Issues: GitHub Issues
- 💬 Questions: GitHub Discussions

## License

This project is provided as-is for educational and development purposes.
