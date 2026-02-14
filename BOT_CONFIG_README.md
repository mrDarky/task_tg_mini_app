# Bot Constructor Configuration Guide

## Overview

The Bot Constructor now supports full customization of all text, buttons, and UI elements through a JSON configuration file (`bot/bot_config.json`). This allows you to modify all bot messages and button labels without changing code, with full support for multiple languages.

## Features

✅ **Configurable Messages** - Customize all bot messages (welcome, profile, tasks, etc.)  
✅ **Configurable Buttons** - Customize all button labels  
✅ **Multi-Language Support** - Different text for English, Russian, and Spanish  
✅ **Backward Compatible** - Falls back to existing translations if config not found  
✅ **Template Variables** - Use `{variable}` syntax for dynamic content  
✅ **Easy to Extend** - Add new languages or messages easily  

## Configuration File Location

```
bot/bot_config.json
```

## File Structure

```json
{
  "version": "1.0",
  "description": "Bot Constructor Configuration",
  
  "messages": {
    "en": { /* English messages */ },
    "ru": { /* Russian messages */ },
    "es": { /* Spanish messages */ }
  },
  
  "buttons": {
    "en": { /* English button labels */ },
    "ru": { /* Russian button labels */ },
    "es": { /* Spanish button labels */ }
  },
  
  "language_names": {
    "en": "English 🇬🇧",
    "ru": "Русский 🇷🇺",
    "es": "Español 🇪🇸"
  }
}
```

## How It Works

### Priority System

1. **Config File** - First checks `bot/bot_config.json`
2. **Translation System** - Falls back to `locales/*.json` if config not found
3. **Default Text** - Uses hardcoded defaults as last resort

### Language Fallback

If a message is not found in the requested language, it automatically falls back to English:

```
Requested: ru → Not found → Falls back to: en → Not found → Returns: None
```

## Customizing Messages

### Available Message Keys

| Key | Description | Variables |
|-----|-------------|-----------|
| `welcome_new` | Welcome message for new users | `{name}`, `{stars}`, `{referral_link}` |
| `welcome_back` | Welcome back message | `{name}`, `{stars}`, `{referral_link}` |
| `welcome_referred` | Welcome for referred users | `{name}`, `{bonus}`, `{stars}`, `{referral_link}` |
| `task_categories` | Task categories header | None |
| `category_tasks` | Category tasks list | `{category_name}`, `{task_count}` |
| `task_detail` | Task detail view | `{title}`, `{description}`, `{type}`, `{reward}` |
| `daily_bonus` | Daily bonus claimed | `{bonus_amount}`, `{streak}` |
| `referral_stats` | Referral statistics | `{referral_count}`, `{total_earned}` |
| `help` | Help message | None |
| `profile_title` | Profile header | None |
| `profile_username` | Profile username | `{username}` |
| `profile_stars` | Profile stars | `{stars}` |
| `profile_completed` | Profile completed tasks | `{completed}` |
| `profile_referrals` | Profile referrals | `{referrals}` |
| `profile_achievements` | Profile achievements | `{achievements}` |
| `profile_status` | Profile status | `{status}` |
| `profile_member_since` | Profile member since | `{date}` |
| `settings` | Settings view | `{lang}`, `{notifications}`, `{task_notif}`, `{reward_notif}` |
| `error_please_start` | Please start error | None |
| `error_account_banned` | Account banned error | None |
| `error_no_categories` | No categories error | None |
| `error_generic` | Generic error | None |

### Example: Customizing Welcome Message

```json
{
  "messages": {
    "en": {
      "welcome_new": "🎉 Hello {name}! Welcome aboard!\n\nYou have {stars} stars.\nShare your link: {referral_link}"
    },
    "ru": {
      "welcome_new": "🎉 Привет {name}! Добро пожаловать!\n\nУ вас {stars} звёзд.\nПоделитесь ссылкой: {referral_link}"
    }
  }
}
```

## Customizing Buttons

### Available Button Keys

| Key | Description | Used For |
|-----|-------------|----------|
| `open_app` | Open Mini App button | Main menu |
| `view_tasks` | View Tasks button | Main menu |
| `my_profile` | My Profile button | Main menu |
| `daily_bonus` | Daily Bonus button | Main menu |
| `help` | Help button | Main menu |
| `settings` | Settings button | Main menu |
| `back` | Back button | Navigation |
| `complete_task` | Complete Task button | Task actions |
| `submit_task` | Submit Task button | Task actions |
| `view_achievements` | View Achievements button | Profile |
| `referral_stats` | Referral Stats button | Profile |
| `star_history` | Star History button | Profile |
| `change_language` | Change Language button | Settings |
| `toggle_notifications_on` | All Notifications ON | Settings |
| `toggle_notifications_off` | All Notifications OFF | Settings |
| `toggle_task_notif_on` | Task Notifications ON | Settings |
| `toggle_task_notif_off` | Task Notifications OFF | Settings |
| `toggle_reward_notif_on` | Reward Notifications ON | Settings |
| `toggle_reward_notif_off` | Reward Notifications OFF | Settings |
| `help_tasks` | How to Complete Tasks | Help menu |
| `help_stars` | About Stars | Help menu |
| `help_referrals` | Referral System | Help menu |
| `help_support` | Support | Help menu |
| `create_ticket` | Create Ticket | Support |

### Example: Customizing Button Labels

```json
{
  "buttons": {
    "en": {
      "view_tasks": "📋 Browse Tasks",
      "my_profile": "👤 Profile",
      "daily_bonus": "🎁 Get Bonus"
    },
    "ru": {
      "view_tasks": "📋 Обзор заданий",
      "my_profile": "👤 Профиль",
      "daily_bonus": "🎁 Получить бонус"
    }
  }
}
```

## Adding a New Language

To add support for a new language (e.g., French):

1. Add language code to `language_names`:
```json
"language_names": {
  "fr": "Français 🇫🇷"
}
```

2. Add French translations to `messages`:
```json
"messages": {
  "fr": {
    "welcome_new": "👋 Bienvenue à Task App, {name}!...",
    "welcome_back": "👋 Bon retour, {name}!...",
    // ... add all message keys
  }
}
```

3. Add French button labels to `buttons`:
```json
"buttons": {
  "fr": {
    "open_app": "🚀 Ouvrir l'App",
    "view_tasks": "📋 Voir les Tâches",
    // ... add all button keys
  }
}
```

## Using the Configuration

### In Code

The configuration is loaded automatically. No code changes needed!

```python
from bot.constructor import messages, buttons, keyboards

# Messages automatically use config
msg = messages.welcome_back("John", 100, "link", language='en')

# Buttons automatically use config
btn = buttons.view_tasks_button(language='en')

# Keyboards automatically use config
keyboard = keyboards.main_menu_keyboard(url, language='en')
```

### Reloading Configuration

If you modify `bot_config.json` while the bot is running:

```python
from bot.constructor import reload_bot_config

# Clear cache and reload configuration
reload_bot_config()
```

## Important Notes

### Variable Names

⚠️ **Important**: Some variable names are reserved and should not be used in templates:
- Avoid using `language` as a variable name (use `lang` instead)
- Variables must match the function parameters exactly

### Template Syntax

Use Python's `str.format()` syntax:
- Variables: `{variable_name}`
- No default values or formatting in config
- Missing variables are silently ignored

### Validation

Always validate your JSON:
```bash
python -c "import json; json.load(open('bot/bot_config.json'))"
```

## Testing

Run the test suite to verify your configuration:

```bash
python test_constructor.py
```

Expected output:
```
✅ All message constructors passed!
✅ All button constructors passed!
✅ All keyboard constructors passed!
✅ All multilanguage tests passed!
✅ ALL TESTS PASSED!
```

## Troubleshooting

### Config Not Loading

1. Check file location: `bot/bot_config.json`
2. Validate JSON syntax
3. Check file permissions

### Variables Not Replaced

1. Verify variable names match exactly (case-sensitive)
2. Check for typos in `{variable_name}`
3. Ensure variables are passed to the function

### Wrong Language Displayed

1. Check language code is correct (`en`, `ru`, `es`)
2. Verify language exists in config
3. Remember: Falls back to English if language not found

## Best Practices

1. **Keep Consistent**: Use the same emoji and formatting across languages
2. **Test All Languages**: Verify each language displays correctly
3. **Backup Before Changes**: Keep a copy of working config
4. **Use Version Control**: Track changes to configuration
5. **Document Custom Keys**: Add comments about custom additions

## Example: Complete Custom Configuration

```json
{
  "version": "1.0",
  "description": "My Custom Bot Config",
  
  "messages": {
    "en": {
      "welcome_new": "🌟 Welcome {name}! 🌟\n\nYou're awesome!\nStars: {stars}\nReferral: {referral_link}",
      "welcome_back": "👋 Hey {name}! Good to see you!\n\nStars: {stars}\nLink: {referral_link}"
    }
  },
  
  "buttons": {
    "en": {
      "open_app": "🚀 Launch App",
      "view_tasks": "📝 Tasks",
      "my_profile": "😊 My Profile"
    }
  },
  
  "language_names": {
    "en": "English 🇬🇧"
  }
}
```

## Summary

The Bot Constructor configuration system provides:

- ✅ Full customization without code changes
- ✅ Multi-language support (EN, RU, ES)
- ✅ Backward compatibility with existing system
- ✅ Easy to extend and maintain
- ✅ Template-based dynamic content
- ✅ Automatic fallback system

For questions or issues, refer to the main documentation or open an issue on GitHub.
