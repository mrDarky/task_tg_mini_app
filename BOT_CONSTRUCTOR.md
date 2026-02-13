# Bot Message & Button Constructor

## Overview

The Bot Message & Button Constructor is a centralized module that manages all bot messages, buttons, and keyboard layouts for the Telegram bot. It eliminates the need for states (FSM) by providing a clean, organized way to construct bot UI elements.

## Location

- **Module**: `bot/constructor.py`
- **Imports**: Can be imported from `bot.constructor`

## Architecture

The constructor module is organized into three main classes:

### 1. BotMessageConstructor

Provides methods to build formatted messages with localization support.

**Purpose**: Centralize all message templates in one place.

**Features**:
- Localization support through i18n system
- Consistent message formatting
- Parameter substitution for dynamic content

**Example Methods**:
```python
from bot.constructor import messages

# Welcome messages
welcome_msg = messages.welcome_new_user(
    name="John", 
    stars=0, 
    referral_link="https://t.me/bot?start=ABC", 
    language='en'
)

# Profile message
profile_msg = messages.profile_message(
    user_data={'username': 'john', 'stars': 100, ...},
    stats={'completed': 5, 'referrals': 2, ...},
    language='en'
)

# Task detail
task_msg = messages.task_detail_message(
    task={'title': 'Watch Video', 'description': '...', ...},
    language='en'
)
```

### 2. BotButtonConstructor

Provides methods to create individual inline keyboard buttons with consistent callback patterns.

**Purpose**: Standardize button creation and callback data naming.

**Features**:
- Consistent callback data patterns
- Icon support (emojis)
- Localized button text
- Type-safe button creation

**Example Methods**:
```python
from bot.constructor import buttons

# Create individual buttons
view_tasks_btn = buttons.view_tasks_button('en')
profile_btn = buttons.my_profile_button('en')
back_btn = buttons.back_button('en')

# Category button
category_btn = buttons.category_button(
    category_id=1, 
    category_name="YouTube"
)

# Task action buttons
complete_btn = buttons.complete_task_button(task_id=123, language='en')
submit_btn = buttons.submit_task_button(task_id=123, language='en')
```

### 3. BotKeyboardConstructor

Provides methods to build complete keyboard layouts for different bot screens.

**Purpose**: Create consistent keyboard layouts across the bot.

**Features**:
- Pre-built layouts for common screens
- Dynamic keyboard generation based on data
- Consistent button positioning
- Easy to maintain and modify

**Example Methods**:
```python
from bot.constructor import keyboards

# Main menu
main_keyboard = keyboards.main_menu_keyboard(
    web_app_url="http://localhost:8000/miniapp",
    language='en'
)

# Categories list
categories_keyboard = keyboards.categories_keyboard(
    categories=[
        {'id': 1, 'name': 'YouTube'},
        {'id': 2, 'name': 'TikTok'}
    ],
    language='en'
)

# Profile screen
profile_keyboard = keyboards.profile_keyboard(language='en')

# Settings with current state
settings_keyboard = keyboards.settings_keyboard(
    settings={
        'notifications_enabled': True,
        'task_notifications': True,
        'reward_notifications': False
    },
    language='en'
)
```

## Callback Data Patterns

The constructor uses consistent callback data patterns for easy routing:

| Pattern | Description | Example |
|---------|-------------|---------|
| `view_tasks` | Show tasks list | `view_tasks` |
| `my_profile` | Show user profile | `my_profile` |
| `daily_bonus` | Claim daily bonus | `daily_bonus` |
| `help` | Show help menu | `help` |
| `settings` | Show settings | `settings` |
| `back_to_menu` | Return to main menu | `back_to_menu` |
| `category_{id}` | Show category tasks | `category_123` |
| `task_detail_{id}` | Show task details | `task_detail_456` |
| `complete_{id}` | Complete task | `complete_789` |
| `submit_task_{id}` | Submit task proof | `submit_task_789` |
| `lang_{code}` | Change language | `lang_en`, `lang_ru` |
| `toggle_notifications` | Toggle all notifications | `toggle_notifications` |
| `toggle_task_notif` | Toggle task notifications | `toggle_task_notif` |
| `toggle_reward_notif` | Toggle reward notifications | `toggle_reward_notif` |

## Usage in Bot Handlers

### Basic Example

```python
from aiogram import types
from bot.constructor import messages, keyboards

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await get_user(message.from_user.id)
    user_lang = await get_user_language(user['id'])
    
    # Use message constructor
    welcome_msg = messages.welcome_back(
        name=message.from_user.first_name,
        stars=user['stars'],
        referral_link=f"https://t.me/bot?start={user['referral_code']}",
        language=user_lang
    )
    
    # Use keyboard constructor
    keyboard = keyboards.main_menu_keyboard(
        web_app_url=settings.web_app_url + "/miniapp",
        language=user_lang
    )
    
    await message.answer(welcome_msg, reply_markup=keyboard, parse_mode="Markdown")
```

### Advanced Example - Dynamic Content

```python
@dp.callback_query(F.data.startswith("category_"))
async def show_category_tasks(callback: types.CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    user = await get_user(callback.from_user.id)
    user_lang = await get_user_language(user['id'])
    
    # Fetch tasks for category
    tasks = await get_tasks_by_category(category_id)
    
    # Build message
    category = await get_category(category_id)
    msg = messages.category_tasks_message(
        category_name=category['name'],
        task_count=len(tasks),
        language=user_lang
    )
    
    # Build dynamic keyboard
    keyboard = keyboards.tasks_list_keyboard(tasks, language=user_lang)
    
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")
```

## Benefits

1. **Centralization**: All messages and buttons in one place
2. **Consistency**: Uniform formatting and callback patterns
3. **Maintainability**: Easy to update messages and buttons
4. **Localization**: Built-in i18n support
5. **Type Safety**: Clear method signatures
6. **No States**: Simple callback-based navigation
7. **Testability**: Easy to test individual components
8. **Scalability**: Easy to add new buttons and layouts

## Best Practices

### 1. Always Use Constructors

❌ **Don't** create buttons inline:
```python
button = InlineKeyboardButton(text="View Tasks", callback_data="view_tasks")
```

✅ **Do** use the constructor:
```python
button = buttons.view_tasks_button(language='en')
```

### 2. Use Complete Keyboards When Possible

❌ **Don't** build keyboards manually:
```python
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Tasks", callback_data="view_tasks")],
    [InlineKeyboardButton(text="Profile", callback_data="my_profile")]
])
```

✅ **Do** use pre-built keyboards:
```python
keyboard = keyboards.main_menu_keyboard(web_app_url, language='en')
```

### 3. Always Pass Language Parameter

✅ **Always** include language for localization:
```python
msg = messages.help_message(language=user_lang)
button = buttons.help_button(language=user_lang)
keyboard = keyboards.help_keyboard(language=user_lang)
```

### 4. Use Message Constructors for Complex Messages

✅ **Do** use constructors for consistency:
```python
profile_msg = messages.profile_message(user_data, stats, language=user_lang)
```

## Adding New Components

### Adding a New Button

1. Add a static method to `BotButtonConstructor`:
```python
@staticmethod
def my_new_button(language: str = 'en') -> InlineKeyboardButton:
    """Create My New Feature button"""
    return InlineKeyboardButton(
        text=t('bot_button_my_feature', language),
        callback_data="my_feature"
    )
```

2. Add translation to locale files (`locales/en.json`, etc.):
```json
{
  "translations": {
    "bot_button_my_feature": "🎯 My Feature"
  }
}
```

### Adding a New Keyboard Layout

1. Add a static method to `BotKeyboardConstructor`:
```python
@staticmethod
def my_feature_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
    """Build my feature keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [buttons.my_new_button(language)],
        [buttons.back_button(language)]
    ])
```

### Adding a New Message Template

1. Add a static method to `BotMessageConstructor`:
```python
@staticmethod
def my_feature_message(data: Dict[str, Any], language: str = 'en') -> str:
    """Construct my feature message"""
    return f"🎯 *My Feature*\n\nSome content here"
```

## Testing

Test the constructor components:

```python
# Test messages
from bot.constructor import messages

welcome = messages.welcome_new_user("Test", 0, "link", "en")
assert "Welcome" in welcome

# Test buttons
from bot.constructor import buttons

btn = buttons.view_tasks_button('en')
assert btn.callback_data == "view_tasks"

# Test keyboards
from bot.constructor import keyboards

kb = keyboards.main_menu_keyboard("http://localhost:8000/miniapp", 'en')
assert len(kb.inline_keyboard) > 0
```

## Migration Guide

To migrate existing bot code to use the constructor:

### Before:
```python
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 View Tasks", callback_data="view_tasks")],
    [InlineKeyboardButton(text="👤 My Profile", callback_data="my_profile")],
    [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
])

msg = f"👤 *Your Profile*\n\nUsername: @{username}\n⭐ Stars: {stars}"
```

### After:
```python
keyboard = keyboards.profile_keyboard(language=user_lang)
msg = messages.profile_message(user_data, stats, language=user_lang)
```

## Convenience Instances

For quick access, the module provides pre-instantiated objects:

```python
from bot.constructor import messages, buttons, keyboards

# Use directly without instantiating
msg = messages.welcome_new_user(...)
btn = buttons.view_tasks_button(...)
kb = keyboards.main_menu_keyboard(...)
```

## Summary

The Bot Message & Button Constructor provides a clean, maintainable way to manage all bot UI components. It eliminates the complexity of FSM states while maintaining a structured, consistent bot interface. By centralizing messages, buttons, and keyboards, it makes the codebase easier to maintain and extend.
