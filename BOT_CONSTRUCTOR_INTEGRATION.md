# Bot Constructor Integration Guide

## Overview

This guide shows how to integrate the Bot Message & Button Constructor into the existing bot code. The constructor is designed to be used alongside existing code without breaking changes.

## Integration Approach

The constructor can be adopted gradually:
1. **Phase 1**: Use constructor for new features
2. **Phase 2**: Optionally refactor existing handlers
3. **Phase 3**: Full adoption (optional)

## Current Bot Structure

The bot currently uses inline definitions for messages and buttons:

```python
# Current approach
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 View Tasks", callback_data="view_tasks")],
    [InlineKeyboardButton(text="👤 My Profile", callback_data="my_profile")],
])

msg = f"👤 *Your Profile*\n\nUsername: @{username}\n⭐ Stars: {stars}"
await message.answer(msg, reply_markup=keyboard, parse_mode="Markdown")
```

## Using the Constructor

With the constructor:

```python
# New approach with constructor
from bot.constructor import messages, keyboards

msg = messages.profile_message(user_data, stats, language=user_lang)
keyboard = keyboards.profile_keyboard(language=user_lang)
await message.answer(msg, reply_markup=keyboard, parse_mode="Markdown")
```

## Example: Refactoring the /start Command

### Before (Current):
```python
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    user_lang = 'en'
    if user:
        user_lang = await get_user_language(user['id'])
    
    if not user:
        user_referral_code = generate_referral_code(message.from_user.id)
        user_data = UserCreate(...)
        user_id = await user_service.create_user(user_data)
        user = await user_service.get_user(user_id)
        
        referral_link = f"https://t.me/{bot_username}?start={user_referral_code}"
        welcome_msg = f"👋 Welcome to Task App!\n\nYour stars: {user['stars']}\nReferral link: {referral_link}"
    else:
        referral_link = f"https://t.me/{bot_username}?start={user.get('referral_code', '')}"
        welcome_msg = f"👋 Welcome back!\n\nYour stars: {user['stars']}"
    
    web_app_url = f"{settings.web_app_url}/miniapp"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Open Mini App", web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton(text="📋 View Tasks", callback_data="view_tasks")],
        [InlineKeyboardButton(text="👤 My Profile", callback_data="my_profile"),
         InlineKeyboardButton(text="🎁 Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton(text="ℹ️ Help", callback_data="help"),
         InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])
    
    await message.answer(welcome_msg, reply_markup=keyboard, parse_mode="Markdown")
```

### After (With Constructor):
```python
from bot.constructor import messages, keyboards

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    user_lang = 'en'
    if user:
        user_lang = await get_user_language(user['id'])
    
    if not user:
        user_referral_code = generate_referral_code(message.from_user.id)
        user_data = UserCreate(...)
        user_id = await user_service.create_user(user_data)
        user = await user_service.get_user(user_id)
        
        referral_link = f"https://t.me/{bot_username}?start={user_referral_code}"
        welcome_msg = messages.welcome_new_user(
            name=message.from_user.first_name,
            stars=user['stars'],
            referral_link=referral_link,
            language=user_lang
        )
    else:
        referral_link = f"https://t.me/{bot_username}?start={user.get('referral_code', '')}"
        welcome_msg = messages.welcome_back(
            name=message.from_user.first_name,
            stars=user['stars'],
            referral_link=referral_link,
            language=user_lang
        )
    
    web_app_url = f"{settings.web_app_url}/miniapp"
    keyboard = keyboards.main_menu_keyboard(web_app_url, language=user_lang)
    
    await message.answer(welcome_msg, reply_markup=keyboard, parse_mode="Markdown")
```

## Example: Refactoring Categories Handler

### Before:
```python
@dp.message(Command("tasks"))
async def cmd_tasks(message: types.Message):
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    user_lang = 'en'
    if user:
        user_lang = await get_user_language(user['id'])
    
    if not user:
        await message.answer("Please start the bot first with /start")
        return
    
    categories = await db.fetch_all("SELECT * FROM categories WHERE parent_id IS NULL")
    
    if not categories:
        await message.answer("No task categories available.")
        return
    
    keyboard_buttons = []
    for category in categories:
        category_name = await category_service.get_category_name_by_language(category['id'], user_lang)
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📁 {category_name}", 
                callback_data=f"category_{category['id']}"
            )
        ])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(
        "📋 *Task Categories*\n\nChoose a category to view available tasks:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
```

### After:
```python
from bot.constructor import messages, keyboards

@dp.message(Command("tasks"))
async def cmd_tasks(message: types.Message):
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    user_lang = 'en'
    if user:
        user_lang = await get_user_language(user['id'])
    
    if not user:
        await message.answer(messages.error_message('please_start', user_lang))
        return
    
    categories = await db.fetch_all("SELECT * FROM categories WHERE parent_id IS NULL")
    
    if not categories:
        await message.answer(messages.error_message('no_categories', user_lang))
        return
    
    # Translate category names
    categories_data = []
    for category in categories:
        category_name = await category_service.get_category_name_by_language(category['id'], user_lang)
        categories_data.append({
            'id': category['id'],
            'name': category_name
        })
    
    msg = messages.task_categories(language=user_lang)
    keyboard = keyboards.categories_keyboard(categories_data, language=user_lang)
    
    await message.answer(msg, reply_markup=keyboard, parse_mode="Markdown")
```

## Example: Refactoring Settings Handler

### Before:
```python
@dp.callback_query(F.data == "settings")
async def show_settings(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    user_lang = await get_user_language(user['id'])
    
    settings = await db.fetch_one("SELECT * FROM user_settings WHERE user_id = ?", (user['id'],))
    
    notifications = "✅ Enabled" if settings['notifications_enabled'] else "❌ Disabled"
    task_notif = "✅ Enabled" if settings['task_notifications'] else "❌ Disabled"
    
    msg = (
        f"⚙️ *Settings*\n\n"
        f"🌐 Language: {user_lang.upper()}\n"
        f"🔔 Notifications: {notifications}\n"
        f"📋 Task Notifications: {task_notif}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Change Language", callback_data="change_language")],
        [InlineKeyboardButton(
            text=f"{'✅' if settings['notifications_enabled'] else '❌'} All Notifications",
            callback_data="toggle_notifications"
        )],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")
```

### After:
```python
from bot.constructor import messages, keyboards

@dp.callback_query(F.data == "settings")
async def show_settings(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    user_lang = await get_user_language(user['id'])
    
    settings_data = await db.fetch_one("SELECT * FROM user_settings WHERE user_id = ?", (user['id'],))
    
    msg = messages.settings_message(settings_data, language=user_lang)
    keyboard = keyboards.settings_keyboard(settings_data, language=user_lang)
    
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")
```

## Benefits of Gradual Adoption

1. **No Breaking Changes**: Existing code continues to work
2. **Gradual Migration**: Refactor handlers one at a time
3. **Immediate Benefits**: New features benefit from constructor immediately
4. **Reduced Code**: Each refactored handler becomes more concise
5. **Better Maintainability**: Centralized message/button management
6. **Consistency**: All new features use the same patterns

## When to Use the Constructor

### Use Constructor For:
✅ New features and handlers  
✅ Complex keyboard layouts  
✅ Multi-language messages  
✅ Reusable message templates  
✅ Consistent UI elements  

### Optional to Refactor:
⚠️ Existing handlers that work fine  
⚠️ Simple one-off messages  
⚠️ Handlers that need custom logic  

## Best Practices

1. **Always import at the top**:
```python
from bot.constructor import messages, buttons, keyboards
```

2. **Always pass language parameter**:
```python
msg = messages.profile_message(user_data, stats, language=user_lang)
```

3. **Use complete keyboards when available**:
```python
# Preferred
keyboard = keyboards.main_menu_keyboard(url, language=user_lang)

# Instead of building manually with buttons
```

4. **Compose custom keyboards with buttons**:
```python
# For custom layouts
custom_kb = InlineKeyboardMarkup(inline_keyboard=[
    [buttons.my_profile_button(user_lang)],
    [buttons.view_tasks_button(user_lang)],
    [buttons.back_button(user_lang)]
])
```

## Summary

The Bot Message & Button Constructor:
- ✅ Works alongside existing code
- ✅ No breaking changes required
- ✅ Can be adopted gradually
- ✅ Reduces code duplication
- ✅ Improves maintainability
- ✅ Provides consistency
- ✅ Supports all languages

You can start using it for new features immediately, and refactor existing handlers at your own pace.
