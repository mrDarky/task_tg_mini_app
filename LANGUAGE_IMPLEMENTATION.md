# Language and Data Loading Implementation

This document describes the implementation of language translation system and data loading fixes.

## Overview

The implementation addresses four main requirements:
1. **JSON-based translation system** - Translations stored in JSON files with API support
2. **Mini app data loading fixes** - Stars count, bonuses, and referrals now load correctly
3. **Language translations in bot and app** - Consistent translation support across platforms
4. **Referral code display** - Proper referral link format: `https://t.me/botname?start=CODE`

## 1. JSON Translation System

### File Structure

Translation files are stored in the `locales/` directory:
```
locales/
  ├── en.json   # English translations
  ├── ru.json   # Russian translations
  └── es.json   # Spanish translations
```

### JSON Format

Each translation file follows this structure:
```json
{
  "code": "en",
  "name": "English",
  "translations": {
    "nav_home": "Home",
    "nav_tasks": "Tasks",
    "bot_welcome_new": "Welcome to Task App, {name}!",
    ...
  }
}
```

### API Endpoints

#### Get Translation File
```
GET /api/languages/json/{language_code}
```
Returns the complete translation JSON for a language.

#### Import Translation File
```
POST /api/languages/import-file
```
Upload a JSON file to import translations.

#### Export Translation File
```
GET /api/languages/export/{language_code}
```
Download translations as JSON file.

### Admin Panel

The admin panel at `/admin/languages` allows:
- Viewing all languages
- Adding new languages
- Editing language settings
- Importing JSON translation files
- Exporting translations to JSON
- Editing individual translations

## 2. Bot Translation System

### Implementation

The bot uses `bot/i18n.py` for translations:

```python
from bot.i18n import t

# Simple translation
greeting = t('bot_welcome_back', 'en')

# Translation with variables
welcome = t('bot_welcome_new', 'ru', 
    name='John', 
    stars=100, 
    referral_link='https://t.me/bot?start=ABC'
)
```

### Bot Commands

All bot commands now support translations:
- `/start` - Welcome message with referral link
- `/tasks` - Task categories with translated names
- `/profile` - User profile with translated labels

The bot automatically detects user's language preference from `user_settings` table.

## 3. Mini App Translation System

### Loading Translations

The miniapp automatically loads translations from the API:

```javascript
// Translations are loaded automatically on page load
const greeting = window.i18n.t('welcome_back');

// Force reload from API
await window.i18n.loadTranslationsFromAPI('ru');
```

### Language Selection

Users can switch languages using the language selector in the header. The preference is saved to `localStorage`.

## 4. Data Loading Fixes

### Stars Count

The home page now correctly loads and displays:
- Current star balance
- Completed tasks count
- Referral count

### Daily Bonus

New API endpoints:

```
GET /api/users/{user_id}/daily-bonus
```
Returns:
- `can_claim` - Whether bonus can be claimed
- `last_claimed` - Last claim timestamp
- `streak_count` - Current streak days
- `next_bonus_amount` - Stars for next claim

```
POST /api/users/{user_id}/claim-bonus
```
Claims the daily bonus and returns updated info.

### Referrals

New API endpoint:
```
GET /api/users/{user_id}/referrals
```
Returns list of all users referred by this user.

## 5. Referral Code Display

### Format

Referral links are now displayed as:
```
https://t.me/{bot_username}?start={referral_code}
```

### Bot Username

The bot username is fetched from the API:
```
GET /api/settings/public/bot-info
```
Returns:
- `bot_username` - Bot's Telegram username
- `web_app_url` - Mini app URL

### Profile Display

The profile page shows:
- Referral code (alphanumeric)
- Full referral link (clickable)
- Share button with pre-filled message

## Adding New Translations

### 1. Add to JSON Files

Edit the translation JSON files in `locales/`:

```json
{
  "code": "en",
  "name": "English",
  "translations": {
    "new_key": "New translation text",
    "with_variable": "Hello, {name}!"
  }
}
```

### 2. Use in Bot

```python
from bot.i18n import t

message = t('new_key', user_lang)
# With variables
message = t('with_variable', user_lang, name='John')
```

### 3. Use in Mini App

Add `data-i18n` attribute to HTML elements:
```html
<span data-i18n="new_key"></span>
```

Or use in JavaScript:
```javascript
const text = window.i18n.t('new_key');
```

## Testing

To test the translation system:

```bash
# Test translation loading
python3 -c "from bot.i18n import t; print(t('nav_home', 'en'))"

# Test JSON files are valid
python3 -c "import json; json.load(open('locales/en.json'))"

# Run the application
python3 run.py
```

## Configuration

Set the bot username in `.env`:
```
BOT_USERNAME=YourBotName
```

This is used to generate proper referral links.

## Database Schema

New tables and fields used:

### `languages` table
- `id`, `code`, `name`, `is_active`, `is_default`, `created_at`, `updated_at`

### `translations` table
- `id`, `language_id`, `key`, `value`, `category`, `created_at`, `updated_at`

### `user_settings` table
- `user_id`, `language` (user's preferred language)

### `daily_bonuses` table
- `id`, `user_id`, `bonus_amount`, `streak_count`, `claimed_at`

### `referrals` table
- `id`, `referrer_id`, `referred_id`, `bonus_awarded`, `created_at`

## Troubleshooting

### Translations not loading in miniapp
- Check browser console for errors
- Verify API endpoint: `/api/languages/json/en`
- Clear localStorage and reload

### Bot showing English only
- Check `user_settings` table for user's language
- Verify JSON files exist in `locales/` directory
- Check bot logs for loading errors

### Referral link not working
- Verify `BOT_USERNAME` is set in settings
- Check API: `/api/settings/public/bot-info`
- Ensure referral code is generated for user
