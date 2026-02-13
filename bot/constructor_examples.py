"""
Bot Constructor Usage Examples

This file demonstrates how to use the Bot Message & Button Constructor
in various scenarios within the Telegram bot.
"""

from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from bot.constructor import messages, buttons, keyboards


# ==============================================================================
# EXAMPLE 1: Welcome Message with Main Menu
# ==============================================================================

async def example_start_command(message: types.Message, user_data: dict, user_lang: str):
    """
    Example: Send welcome message with main menu keyboard
    """
    # Construct welcome message based on user status
    if user_data.get('is_new_user'):
        welcome_msg = messages.welcome_new_user(
            name=message.from_user.first_name,
            stars=user_data['stars'],
            referral_link=user_data['referral_link'],
            language=user_lang
        )
    else:
        welcome_msg = messages.welcome_back(
            name=message.from_user.first_name,
            stars=user_data['stars'],
            referral_link=user_data['referral_link'],
            language=user_lang
        )
    
    # Build main menu keyboard
    web_app_url = "http://localhost:8000/miniapp"
    keyboard = keyboards.main_menu_keyboard(web_app_url, language=user_lang)
    
    # Send message
    await message.answer(welcome_msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 2: Categories List
# ==============================================================================

async def example_show_categories(callback: types.CallbackQuery, categories_data: list, user_lang: str):
    """
    Example: Display task categories
    """
    # Construct message
    msg = messages.task_categories(language=user_lang)
    
    # Build categories keyboard
    keyboard = keyboards.categories_keyboard(categories_data, language=user_lang)
    
    # Edit message with categories
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 3: Task Detail View
# ==============================================================================

async def example_show_task_detail(callback: types.CallbackQuery, task_data: dict, user_lang: str):
    """
    Example: Display task details with action buttons
    """
    # Construct task detail message
    msg = messages.task_detail_message(task_data, language=user_lang)
    
    # Build task detail keyboard
    keyboard = keyboards.task_detail_keyboard(task_data['id'], language=user_lang)
    
    # Show task details
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 4: Profile Screen
# ==============================================================================

async def example_show_profile(callback: types.CallbackQuery, user_data: dict, stats: dict, user_lang: str):
    """
    Example: Display user profile with statistics
    """
    # Construct profile message
    msg = messages.profile_message(user_data, stats, language=user_lang)
    
    # Build profile keyboard
    keyboard = keyboards.profile_keyboard(language=user_lang)
    
    # Show profile
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 5: Settings Screen with Current State
# ==============================================================================

async def example_show_settings(callback: types.CallbackQuery, current_settings: dict, user_lang: str):
    """
    Example: Display settings with current toggle states
    """
    # Construct settings message
    msg = messages.settings_message(current_settings, language=user_lang)
    
    # Build settings keyboard with current states
    keyboard = keyboards.settings_keyboard(current_settings, language=user_lang)
    
    # Show settings
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 6: Language Selection
# ==============================================================================

async def example_show_language_selection(callback: types.CallbackQuery, user_lang: str):
    """
    Example: Display language selection menu
    """
    # Message for language selection
    msg = "🌐 *Choose your language* / *Выберите язык* / *Elige tu idioma*"
    
    # Build language selection keyboard
    keyboard = keyboards.language_selection_keyboard(language=user_lang)
    
    # Show language options
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 7: Dynamic Task List
# ==============================================================================

async def example_show_category_tasks(callback: types.CallbackQuery, category_id: int, 
                                     category_name: str, tasks: list, user_lang: str):
    """
    Example: Display tasks for a specific category
    """
    # Construct message with task count
    msg = messages.category_tasks_message(category_name, len(tasks), language=user_lang)
    
    # Build dynamic tasks keyboard
    keyboard = keyboards.tasks_list_keyboard(tasks, language=user_lang)
    
    # Show tasks
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 8: Help Menu
# ==============================================================================

async def example_show_help(callback: types.CallbackQuery, user_lang: str):
    """
    Example: Display help menu
    """
    # Construct help message
    msg = messages.help_message(language=user_lang)
    
    # Build help keyboard
    keyboard = keyboards.help_keyboard(language=user_lang)
    
    # Show help
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 9: Error Handling
# ==============================================================================

async def example_handle_error(callback: types.CallbackQuery, error_type: str, user_lang: str):
    """
    Example: Display error message
    """
    # Get error message
    error_msg = messages.error_message(error_type, language=user_lang)
    
    # Simple back keyboard
    keyboard = keyboards.back_keyboard(language=user_lang)
    
    # Show error
    await callback.message.edit_text(error_msg, reply_markup=keyboard)


# ==============================================================================
# EXAMPLE 10: Custom Keyboard Composition
# ==============================================================================

async def example_custom_keyboard(callback: types.CallbackQuery, user_lang: str):
    """
    Example: Build custom keyboard using individual buttons
    """
    from aiogram.types import InlineKeyboardMarkup
    
    # Compose custom keyboard using button constructors
    custom_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: Two buttons side by side
        [
            buttons.my_profile_button(user_lang),
            buttons.daily_bonus_button(user_lang)
        ],
        # Row 2: Single wide button
        [buttons.view_tasks_button(user_lang)],
        # Row 3: Help and settings
        [
            buttons.help_button(user_lang),
            buttons.settings_button(user_lang)
        ],
        # Row 4: Back button
        [buttons.back_button(user_lang)]
    ])
    
    msg = "🎯 *Custom Menu*\n\nChoose an option:"
    await callback.message.edit_text(msg, reply_markup=custom_keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 11: Referral Statistics
# ==============================================================================

async def example_show_referral_stats(callback: types.CallbackQuery, referral_count: int, 
                                     total_earned: int, user_lang: str):
    """
    Example: Display referral statistics
    """
    # Construct referral stats message
    msg = messages.referral_stats_message(referral_count, total_earned, language=user_lang)
    
    # Simple keyboard with back button
    keyboard = keyboards.referral_stats_keyboard(language=user_lang)
    
    # Show stats
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# EXAMPLE 12: Daily Bonus Claim
# ==============================================================================

async def example_claim_daily_bonus(callback: types.CallbackQuery, bonus_amount: int, 
                                   streak: int, user_lang: str):
    """
    Example: Show daily bonus claim result
    """
    # Construct daily bonus message
    msg = messages.daily_bonus_message(bonus_amount, streak, language=user_lang)
    
    # Back keyboard
    keyboard = keyboards.back_keyboard(language=user_lang)
    
    # Show bonus claim result
    await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# COMPLETE HANDLER EXAMPLE
# ==============================================================================

# Below is a complete example showing how to integrate the constructor
# into actual bot handlers

class ExampleBotHandlers:
    """
    Complete example of bot handlers using the constructor
    """
    
    def __init__(self, dp: Dispatcher):
        self.dp = dp
        self.register_handlers()
    
    def register_handlers(self):
        """Register all handlers"""
        # Commands
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_tasks, Command("tasks"))
        self.dp.message.register(self.cmd_profile, Command("profile"))
        
        # Callbacks
        self.dp.callback_query.register(self.show_tasks, F.data == "view_tasks")
        self.dp.callback_query.register(self.show_profile, F.data == "my_profile")
        self.dp.callback_query.register(self.show_settings, F.data == "settings")
        self.dp.callback_query.register(self.back_to_menu, F.data == "back_to_menu")
    
    async def cmd_start(self, message: types.Message):
        """Handle /start command"""
        # Get user data (mock)
        user_data = {
            'telegram_id': message.from_user.id,
            'username': message.from_user.username,
            'stars': 100,
            'referral_link': 'https://t.me/bot?start=ABC123',
            'is_new_user': False
        }
        user_lang = 'en'
        
        # Use constructor
        msg = messages.welcome_back(
            name=message.from_user.first_name,
            stars=user_data['stars'],
            referral_link=user_data['referral_link'],
            language=user_lang
        )
        
        keyboard = keyboards.main_menu_keyboard(
            web_app_url="http://localhost:8000/miniapp",
            language=user_lang
        )
        
        await message.answer(msg, reply_markup=keyboard, parse_mode="Markdown")
    
    async def cmd_tasks(self, message: types.Message):
        """Handle /tasks command"""
        user_lang = 'en'
        categories = [
            {'id': 1, 'name': 'YouTube'},
            {'id': 2, 'name': 'TikTok'},
            {'id': 3, 'name': 'Subscribe'}
        ]
        
        msg = messages.task_categories(language=user_lang)
        keyboard = keyboards.categories_keyboard(categories, language=user_lang)
        
        await message.answer(msg, reply_markup=keyboard, parse_mode="Markdown")
    
    async def cmd_profile(self, message: types.Message):
        """Handle /profile command"""
        user_lang = 'en'
        user_data = {
            'username': message.from_user.username,
            'stars': 150,
            'status': 'active',
            'created_at': '2024-01-15'
        }
        stats = {
            'completed': 10,
            'referrals': 5,
            'achievements': 3
        }
        
        msg = messages.profile_message(user_data, stats, language=user_lang)
        keyboard = keyboards.profile_keyboard(language=user_lang)
        
        await message.answer(msg, reply_markup=keyboard, parse_mode="Markdown")
    
    async def show_tasks(self, callback: types.CallbackQuery):
        """Handle view_tasks callback"""
        user_lang = 'en'
        categories = [
            {'id': 1, 'name': 'YouTube'},
            {'id': 2, 'name': 'TikTok'}
        ]
        
        msg = messages.task_categories(language=user_lang)
        keyboard = keyboards.categories_keyboard(categories, language=user_lang)
        
        await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")
    
    async def show_profile(self, callback: types.CallbackQuery):
        """Handle my_profile callback"""
        user_lang = 'en'
        user_data = {
            'username': callback.from_user.username,
            'stars': 150,
            'status': 'active',
            'created_at': '2024-01-15'
        }
        stats = {
            'completed': 10,
            'referrals': 5,
            'achievements': 3
        }
        
        msg = messages.profile_message(user_data, stats, language=user_lang)
        keyboard = keyboards.profile_keyboard(language=user_lang)
        
        await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")
    
    async def show_settings(self, callback: types.CallbackQuery):
        """Handle settings callback"""
        user_lang = 'en'
        settings = {
            'language': 'en',
            'notifications_enabled': True,
            'task_notifications': True,
            'reward_notifications': False
        }
        
        msg = messages.settings_message(settings, language=user_lang)
        keyboard = keyboards.settings_keyboard(settings, language=user_lang)
        
        await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")
    
    async def back_to_menu(self, callback: types.CallbackQuery):
        """Handle back_to_menu callback"""
        user_lang = 'en'
        
        msg = messages.welcome_back(
            name=callback.from_user.first_name,
            stars=100,
            referral_link='https://t.me/bot?start=ABC',
            language=user_lang
        )
        
        keyboard = keyboards.main_menu_keyboard(
            web_app_url="http://localhost:8000/miniapp",
            language=user_lang
        )
        
        await callback.message.edit_text(msg, reply_markup=keyboard, parse_mode="Markdown")


# ==============================================================================
# NOTES
# ==============================================================================

"""
Key Takeaways:

1. Always use constructor methods instead of creating buttons/keyboards manually
2. Always pass the user's language preference for proper localization
3. Use pre-built keyboard layouts when available (main_menu_keyboard, profile_keyboard, etc.)
4. For custom layouts, compose using individual button constructors
5. Message constructors handle formatting and parameter substitution automatically
6. All callback data follows consistent patterns (view_tasks, category_123, task_detail_456, etc.)
7. No need for FSM states - everything is callback-based navigation

Benefits:
- Centralized UI management
- Easy to maintain and update
- Consistent user experience
- Full localization support
- Type-safe and testable
- Clean, readable code
"""
