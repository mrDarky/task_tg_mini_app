# Bot States Initialization

This document explains how to initialize bot states in the database for the Bot Constructor feature.

## Overview

The bot has several hardcoded conversation flows (states) that users interact with when using the Telegram bot. The Bot Constructor in the admin panel allows you to visually manage these states, but they need to be initialized in the database first.

## What Gets Initialized

The initialization script creates 13 bot states with their corresponding buttons:

1. **Welcome / Start** (start state) - Main menu with app access and navigation
2. **Task Categories** - Browse available task categories
3. **User Profile** - View user statistics and achievements
4. **Daily Bonus** - Claim daily rewards
5. **Help Menu** - Access help topics
6. **Settings** - Configure preferences
7. **Referral Statistics** - View referral earnings
8. **Star History** - Transaction history
9. **Help - Tasks** - How to complete tasks
10. **Help - Stars** - Information about stars
11. **Help - Referrals** - Referral system explanation
12. **Help - Support** - Create support tickets
13. **Language Selection** - Choose language preference

Each state includes:
- State key (unique identifier)
- Display name
- Message text with variable placeholders
- Associated buttons with proper positioning
- Start state designation (for /start command)

## How to Initialize

### First Time Setup

Run the initialization script:

```bash
python3 initialize_bot_states.py
```

The script will:
1. Check if states already exist
2. Create all 13 bot states
3. Create buttons for each state
4. Display progress and confirmation

### Re-initialization

If you need to reset the states to defaults:

```bash
python3 initialize_bot_states.py
```

When prompted, type `yes` to clear existing states and reinitialize.

### Automatic Initialization

To skip the prompt (useful for automated deployments):

```bash
echo "yes" | python3 initialize_bot_states.py
```

## Verifying the States

After initialization, you can verify the states in two ways:

### 1. Admin Panel (Recommended)
1. Open the admin panel: `http://localhost:8000/admin`
2. Navigate to **Bot Constructor**
3. You should see all 13 states listed
4. Click on any state to view/edit its details and buttons

### 2. Database Query
```python
python3 -c "
import asyncio
from database.db import db

async def check():
    await db.connect()
    states = await db.fetch_all('SELECT * FROM bot_states')
    print(f'Total states: {len(states)}')
    await db.disconnect()

asyncio.run(check())
"
```

## Available Variables

The following variables can be used in message texts and will be replaced with actual user data:

- `{username}` - User's Telegram username
- `{first_name}` - User's first name
- `{stars}` or `{stars_count}` - User's star balance
- `{referral_code}` - User's unique referral code
- `{referral_link}` - Full referral link
- `{completed_tasks}` - Number of completed tasks
- `{telegram_id}` - User's Telegram ID
- `{web_app_url}` - Mini app URL (for web app buttons)

## Important Notes

1. **Start State**: Only one state should be marked as the start state. This is the state shown when users type `/start` in the bot.

2. **State Keys**: Must be unique and match the callback_data used in the bot code.

3. **Button Types**: 
   - `callback` - Navigate between states or trigger actions
   - `url` - Open external links
   - `web_app` - Open Telegram Web App

4. **Production**: Run this script during initial deployment or when resetting states to defaults.

## Troubleshooting

### "No module named 'aiosqlite'" error
Install dependencies first:
```bash
pip3 install -r requirements.txt
```

### States not appearing in admin panel
1. Verify the web app is running
2. Check you're logged into the admin panel
3. Refresh the page
4. Check browser console for errors

### Need to add more states
Edit the `initialize_bot_states.py` script and add new state definitions to the `states` list, then re-run the script.

## Related Files

- `initialize_bot_states.py` - The initialization script
- `database/db.py` - Database schema definitions
- `app/routers/bot_constructor.py` - Bot Constructor API endpoints
- `app/templates/bot_constructor.html` - Bot Constructor UI
- `bot/bot.py` - Bot handlers that use these states
