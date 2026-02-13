"""
Bot Message & Button Constructor

This module provides a centralized way to construct bot messages and buttons
without using states (FSM). It maintains the current structure of the Telegram bot
and includes all messages, buttons, and keyboard layouts.

The constructor provides:
- Message templates with localization support
- Button factory methods
- Keyboard layout builders
- Consistent callback data patterns
- Configurable text and buttons via bot_config.json
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bot.i18n import t
from typing import List, Optional, Dict, Any
import json
from pathlib import Path

# Cache for loaded configuration
_config_cache: Optional[Dict[str, Any]] = None


def load_bot_config() -> Dict[str, Any]:
    """
    Load bot configuration from bot_config.json
    Returns configuration dict with messages, buttons, and language names
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    config_file = Path(__file__).parent / "bot_config.json"
    
    if not config_file.exists():
        # Return empty config if file doesn't exist
        return {"messages": {}, "buttons": {}, "language_names": {}}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            _config_cache = json.load(f)
            return _config_cache
    except Exception as e:
        print(f"Error loading bot config: {e}")
        return {"messages": {}, "buttons": {}, "language_names": {}}


def get_config_text(category: str, key: str, language: str = 'en', **kwargs) -> Optional[str]:
    """
    Get configured text from bot_config.json
    
    Args:
        category: 'messages' or 'buttons'
        key: Configuration key
        language: Language code
        **kwargs: Variables to format in the text
    
    Returns:
        Configured text with variables formatted, or None if not found
    """
    config = load_bot_config()
    
    if category not in config:
        return None
    
    # Try to get text for requested language
    if language in config[category] and key in config[category][language]:
        text = config[category][language][key]
    # Fallback to English
    elif 'en' in config[category] and key in config[category]['en']:
        text = config[category]['en'][key]
    else:
        return None
    
    # Format with variables if provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # If a variable is missing, return text as-is
    
    return text


def reload_bot_config():
    """Clear configuration cache to force reload"""
    global _config_cache
    _config_cache = None


class BotMessageConstructor:
    """
    Centralized message constructor for the Telegram bot.
    Provides methods to build formatted messages with localization support.
    Text can be customized via bot_config.json or falls back to locales/*.json
    """

    @staticmethod
    def welcome_new_user(name: str, stars: int, referral_link: str, language: str = 'en') -> str:
        """Construct welcome message for new users"""
        # Try to get from config first
        config_text = get_config_text('messages', 'welcome_new', language, 
                                      name=name, stars=stars, referral_link=referral_link)
        if config_text:
            return config_text
        # Fallback to translation system
        return t('bot_welcome_new', language, name=name, stars=stars, referral_link=referral_link)

    @staticmethod
    def welcome_back(name: str, stars: int, referral_link: str, language: str = 'en') -> str:
        """Construct welcome back message for returning users"""
        # Try to get from config first
        config_text = get_config_text('messages', 'welcome_back', language,
                                      name=name, stars=stars, referral_link=referral_link)
        if config_text:
            return config_text
        # Fallback to translation system
        return t('bot_welcome_back', language, name=name, stars=stars, referral_link=referral_link)

    @staticmethod
    def welcome_referred(name: str, bonus: int, stars: int, referral_link: str, language: str = 'en') -> str:
        """Construct welcome message for referred users"""
        # Try to get from config first
        config_text = get_config_text('messages', 'welcome_referred', language,
                                      name=name, bonus=bonus, stars=stars, referral_link=referral_link)
        if config_text:
            return config_text
        # Fallback to translation system
        return t('bot_welcome_referred', language, name=name, bonus=bonus, stars=stars, referral_link=referral_link)

    @staticmethod
    def task_categories(language: str = 'en') -> str:
        """Construct task categories message"""
        # Try to get from config first
        config_text = get_config_text('messages', 'task_categories', language)
        if config_text:
            return config_text
        # Fallback to translation system
        return t('bot_task_categories', language)

    @staticmethod
    def profile_message(user_data: Dict[str, Any], stats: Dict[str, Any], language: str = 'en') -> str:
        """Construct user profile message with statistics"""
        username = user_data.get('username', 'N/A')
        stars = user_data.get('stars', 0)
        status = user_data.get('status', 'active')
        created_at = user_data.get('created_at', '')
        
        completed = stats.get('completed', 0)
        referrals = stats.get('referrals', 0)
        achievements = stats.get('achievements', 0)
        
        # Try to get individual profile parts from config
        profile_parts = []
        
        # Title
        title = get_config_text('messages', 'profile_title', language)
        profile_parts.append(title if title else t('bot_profile_title', language))
        profile_parts.append("")
        
        # Username
        username_text = get_config_text('messages', 'profile_username', language, username=username)
        profile_parts.append(username_text if username_text else t('bot_profile_username', language, username=username))
        
        # Stars
        stars_text = get_config_text('messages', 'profile_stars', language, stars=stars)
        profile_parts.append(stars_text if stars_text else t('bot_profile_stars', language, stars=stars))
        
        # Completed
        completed_text = get_config_text('messages', 'profile_completed', language, completed=completed)
        profile_parts.append(completed_text if completed_text else t('bot_profile_completed', language, completed=completed))
        
        # Referrals
        referrals_text = get_config_text('messages', 'profile_referrals', language, referrals=referrals)
        profile_parts.append(referrals_text if referrals_text else t('bot_profile_referrals', language, referrals=referrals))
        
        # Achievements
        achievements_text = get_config_text('messages', 'profile_achievements', language, achievements=achievements)
        profile_parts.append(achievements_text if achievements_text else t('bot_profile_achievements', language, achievements=achievements))
        
        # Status
        status_text = get_config_text('messages', 'profile_status', language, status=status)
        profile_parts.append(status_text if status_text else t('bot_profile_status', language, status=status))
        
        # Member since
        member_since_text = get_config_text('messages', 'profile_member_since', language, date=created_at)
        profile_parts.append(member_since_text if member_since_text else t('bot_profile_member_since', language, date=created_at))
        
        return "\n".join(profile_parts)

    @staticmethod
    def category_tasks_message(category_name: str, task_count: int, language: str = 'en') -> str:
        """Construct category tasks listing message"""
        # Try to get from config first
        config_text = get_config_text('messages', 'category_tasks', language,
                                      category_name=category_name, task_count=task_count)
        if config_text:
            return config_text
        # Fallback to default format
        return f"📋 *{category_name}*\n\nAvailable tasks: {task_count}"

    @staticmethod
    def task_detail_message(task: Dict[str, Any], language: str = 'en') -> str:
        """Construct detailed task information message"""
        title = task.get('title', 'Unknown Task')
        description = task.get('description', 'No description')
        reward = task.get('reward', 0)
        task_type = task.get('type', 'general')
        
        # Try to get from config first
        config_text = get_config_text('messages', 'task_detail', language,
                                      title=title, description=description, 
                                      reward=reward, type=task_type)
        if config_text:
            return config_text
        
        # Fallback to default format
        return (
            f"📝 *{title}*\n\n"
            f"{description}\n\n"
            f"🎯 Type: {task_type}\n"
            f"⭐ Reward: {reward} stars"
        )

    @staticmethod
    def daily_bonus_message(bonus_amount: int, streak: int, language: str = 'en') -> str:
        """Construct daily bonus claim message"""
        # Try to get from config first
        config_text = get_config_text('messages', 'daily_bonus', language,
                                      bonus_amount=bonus_amount, streak=streak)
        if config_text:
            return config_text
        
        # Fallback to default format
        return (
            f"🎁 *Daily Bonus Claimed!*\n\n"
            f"You received {bonus_amount} ⭐\n"
            f"Current streak: {streak} days"
        )

    @staticmethod
    def referral_stats_message(referral_count: int, total_earned: int, language: str = 'en') -> str:
        """Construct referral statistics message"""
        # Try to get from config first
        config_text = get_config_text('messages', 'referral_stats', language,
                                      referral_count=referral_count, total_earned=total_earned)
        if config_text:
            return config_text
        
        # Fallback to default format
        return (
            f"👥 *Referral Statistics*\n\n"
            f"Total referrals: {referral_count}\n"
            f"Total earned: {total_earned} ⭐\n\n"
            f"Invite more friends to earn more stars!"
        )

    @staticmethod
    def settings_message(settings: Dict[str, Any], language: str = 'en') -> str:
        """Construct settings message"""
        notifications = "✅ Enabled" if settings.get('notifications_enabled', True) else "❌ Disabled"
        task_notif = "✅ Enabled" if settings.get('task_notifications', True) else "❌ Disabled"
        reward_notif = "✅ Enabled" if settings.get('reward_notifications', True) else "❌ Disabled"
        current_lang = settings.get('language', 'en')
        
        # Try to get from config first
        config_text = get_config_text('messages', 'settings', language,
                                      language=current_lang.upper(),
                                      notifications=notifications,
                                      task_notif=task_notif,
                                      reward_notif=reward_notif)
        if config_text:
            return config_text
        
        # Fallback to default format
        return (
            f"⚙️ *Settings*\n\n"
            f"🌐 Language: {current_lang.upper()}\n"
            f"🔔 All Notifications: {notifications}\n"
            f"📋 Task Notifications: {task_notif}\n"
            f"🎁 Reward Notifications: {reward_notif}"
        )

    @staticmethod
    def help_message(language: str = 'en') -> str:
        """Construct help message"""
        # Try to get from config first
        config_text = get_config_text('messages', 'help', language)
        if config_text:
            return config_text
        
        # Fallback to default format
        return (
            "ℹ️ *Help & Support*\n\n"
            "Welcome to Task App! Here's how to get started:\n\n"
            "📋 Browse tasks by category\n"
            "✅ Complete tasks to earn stars\n"
            "🎁 Claim daily bonuses\n"
            "👥 Invite friends for referral bonuses\n\n"
            "Need help? Contact support!"
        )

    @staticmethod
    def error_message(error_type: str, language: str = 'en') -> str:
        """Construct error message based on type"""
        # Try to get from config first
        config_key = f'error_{error_type}'
        config_text = get_config_text('messages', config_key, language)
        if config_text:
            return config_text
        
        # Fallback to translation system or default messages
        error_messages = {
            'please_start': t('bot_please_start', language),
            'account_banned': t('bot_account_banned', language),
            'no_categories': t('bot_no_categories', language),
            'generic': "An error occurred. Please try again later."
        }
        return error_messages.get(error_type, error_messages['generic'])


class BotButtonConstructor:
    """
    Centralized button constructor for the Telegram bot.
    Provides methods to build inline keyboard buttons with consistent callback patterns.
    Button text can be customized via bot_config.json or falls back to locales/*.json
    """

    @staticmethod
    def web_app_button(url: str, language: str = 'en') -> InlineKeyboardButton:
        """Create Mini App button"""
        # Try to get from config first
        text = get_config_text('buttons', 'open_app', language)
        if not text:
            text = t('bot_button_open_app', language)
        return InlineKeyboardButton(
            text=text,
            web_app=WebAppInfo(url=url)
        )

    @staticmethod
    def view_tasks_button(language: str = 'en') -> InlineKeyboardButton:
        """Create View Tasks button"""
        text = get_config_text('buttons', 'view_tasks', language)
        if not text:
            text = t('bot_button_view_tasks', language)
        return InlineKeyboardButton(
            text=text,
            callback_data="view_tasks"
        )

    @staticmethod
    def my_profile_button(language: str = 'en') -> InlineKeyboardButton:
        """Create My Profile button"""
        text = get_config_text('buttons', 'my_profile', language)
        if not text:
            text = t('bot_button_my_profile', language)
        return InlineKeyboardButton(
            text=text,
            callback_data="my_profile"
        )

    @staticmethod
    def daily_bonus_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Daily Bonus button"""
        text = get_config_text('buttons', 'daily_bonus', language)
        if not text:
            text = t('bot_button_daily_bonus', language)
        return InlineKeyboardButton(
            text=text,
            callback_data="daily_bonus"
        )

    @staticmethod
    def help_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help button"""
        text = get_config_text('buttons', 'help', language)
        if not text:
            text = t('bot_button_help', language)
        return InlineKeyboardButton(
            text=text,
            callback_data="help"
        )

    @staticmethod
    def settings_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Settings button"""
        text = get_config_text('buttons', 'settings', language)
        if not text:
            text = t('bot_button_settings', language)
        return InlineKeyboardButton(
            text=text,
            callback_data="settings"
        )

    @staticmethod
    def back_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Back button"""
        text = get_config_text('buttons', 'back', language)
        if not text:
            text = t('bot_button_back', language)
        return InlineKeyboardButton(
            text=text,
            callback_data="back_to_menu"
        )

    @staticmethod
    def category_button(category_id: int, category_name: str) -> InlineKeyboardButton:
        """Create category selection button"""
        return InlineKeyboardButton(
            text=f"📁 {category_name}",
            callback_data=f"category_{category_id}"
        )

    @staticmethod
    def task_detail_button(task_id: int, task_title: str) -> InlineKeyboardButton:
        """Create task detail button"""
        return InlineKeyboardButton(
            text=task_title,
            callback_data=f"task_detail_{task_id}"
        )

    @staticmethod
    def complete_task_button(task_id: int, language: str = 'en') -> InlineKeyboardButton:
        """Create complete task button"""
        text = get_config_text('buttons', 'complete_task', language)
        if not text:
            text = "✅ Complete Task"
        return InlineKeyboardButton(
            text=text,
            callback_data=f"complete_{task_id}"
        )

    @staticmethod
    def submit_task_button(task_id: int, language: str = 'en') -> InlineKeyboardButton:
        """Create submit task button"""
        text = get_config_text('buttons', 'submit_task', language)
        if not text:
            text = "📤 Submit Task"
        return InlineKeyboardButton(
            text=text,
            callback_data=f"submit_task_{task_id}"
        )

    @staticmethod
    def view_achievements_button(language: str = 'en') -> InlineKeyboardButton:
        """Create View Achievements button"""
        text = get_config_text('buttons', 'view_achievements', language)
        if not text:
            text = "🏆 View Achievements"
        return InlineKeyboardButton(
            text=text,
            callback_data="view_achievements"
        )

    @staticmethod
    def referral_stats_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Referral Stats button"""
        text = get_config_text('buttons', 'referral_stats', language)
        if not text:
            text = "👥 Referral Stats"
        return InlineKeyboardButton(
            text=text,
            callback_data="referral_stats"
        )

    @staticmethod
    def star_history_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Star History button"""
        text = get_config_text('buttons', 'star_history', language)
        if not text:
            text = "📊 Star History"
        return InlineKeyboardButton(
            text=text,
            callback_data="star_history"
        )

    @staticmethod
    def change_language_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Change Language button"""
        text = get_config_text('buttons', 'change_language', language)
        if not text:
            text = "🌐 Change Language"
        return InlineKeyboardButton(
            text=text,
            callback_data="change_language"
        )

    @staticmethod
    def language_selection_button(lang_code: str, lang_name: str) -> InlineKeyboardButton:
        """Create language selection button"""
        # Try to get language name from config
        config = load_bot_config()
        if 'language_names' in config and lang_code in config['language_names']:
            lang_name = config['language_names'][lang_code]
        return InlineKeyboardButton(
            text=f"{lang_name}",
            callback_data=f"lang_{lang_code}"
        )

    @staticmethod
    def toggle_notifications_button(enabled: bool, language: str = 'en') -> InlineKeyboardButton:
        """Create toggle all notifications button"""
        # Try to get from config first
        key = 'toggle_notifications_on' if enabled else 'toggle_notifications_off'
        text = get_config_text('buttons', key, language)
        if not text:
            status = "✅" if enabled else "❌"
            text = f"{status} All Notifications"
        return InlineKeyboardButton(
            text=text,
            callback_data="toggle_notifications"
        )

    @staticmethod
    def toggle_task_notif_button(enabled: bool, language: str = 'en') -> InlineKeyboardButton:
        """Create toggle task notifications button"""
        # Try to get from config first
        key = 'toggle_task_notif_on' if enabled else 'toggle_task_notif_off'
        text = get_config_text('buttons', key, language)
        if not text:
            status = "✅" if enabled else "❌"
            text = f"{status} Task Notifications"
        return InlineKeyboardButton(
            text=text,
            callback_data="toggle_task_notif"
        )

    @staticmethod
    def toggle_reward_notif_button(enabled: bool, language: str = 'en') -> InlineKeyboardButton:
        """Create toggle reward notifications button"""
        # Try to get from config first
        key = 'toggle_reward_notif_on' if enabled else 'toggle_reward_notif_off'
        text = get_config_text('buttons', key, language)
        if not text:
            status = "✅" if enabled else "❌"
            text = f"{status} Reward Notifications"
        return InlineKeyboardButton(
            text=text,
            callback_data="toggle_reward_notif"
        )

    @staticmethod
    def help_tasks_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help - How to Complete Tasks button"""
        text = get_config_text('buttons', 'help_tasks', language)
        if not text:
            text = "📋 How to Complete Tasks"
        return InlineKeyboardButton(
            text=text,
            callback_data="help_tasks"
        )

    @staticmethod
    def help_stars_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help - About Stars button"""
        text = get_config_text('buttons', 'help_stars', language)
        if not text:
            text = "⭐ About Stars"
        return InlineKeyboardButton(
            text=text,
            callback_data="help_stars"
        )

    @staticmethod
    def help_referrals_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help - Referral System button"""
        text = get_config_text('buttons', 'help_referrals', language)
        if not text:
            text = "👥 Referral System"
        return InlineKeyboardButton(
            text=text,
            callback_data="help_referrals"
        )

    @staticmethod
    def help_support_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help - Support button"""
        text = get_config_text('buttons', 'help_support', language)
        if not text:
            text = "💬 Support"
        return InlineKeyboardButton(
            text=text,
            callback_data="help_support"
        )

    @staticmethod
    def create_ticket_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Create Ticket button"""
        text = get_config_text('buttons', 'create_ticket', language)
        if not text:
            text = "📝 Create Ticket"
        return InlineKeyboardButton(
            text=text,
            callback_data="create_ticket"
        )


class BotKeyboardConstructor:
    """
    Centralized keyboard constructor for the Telegram bot.
    Provides methods to build complete keyboard layouts for different bot screens.
    """

    @staticmethod
    def main_menu_keyboard(web_app_url: str, language: str = 'en') -> InlineKeyboardMarkup:
        """Build main menu keyboard with all primary options"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [BotButtonConstructor.web_app_button(web_app_url, language)],
            [BotButtonConstructor.view_tasks_button(language)],
            [
                BotButtonConstructor.my_profile_button(language),
                BotButtonConstructor.daily_bonus_button(language)
            ],
            [
                BotButtonConstructor.help_button(language),
                BotButtonConstructor.settings_button(language)
            ]
        ])

    @staticmethod
    def categories_keyboard(categories: List[Dict[str, Any]], language: str = 'en') -> InlineKeyboardMarkup:
        """Build categories selection keyboard"""
        buttons = []
        
        for category in categories:
            category_id = category['id']
            category_name = category.get('name', 'Unknown')
            buttons.append([BotButtonConstructor.category_button(category_id, category_name)])
        
        buttons.append([BotButtonConstructor.back_button(language)])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def tasks_list_keyboard(tasks: List[Dict[str, Any]], language: str = 'en') -> InlineKeyboardMarkup:
        """Build tasks list keyboard for a category"""
        buttons = []
        
        for task in tasks:
            task_id = task['id']
            task_title = task.get('title', 'Unknown Task')
            reward = task.get('reward', 0)
            buttons.append([
                BotButtonConstructor.task_detail_button(
                    task_id,
                    f"{task_title} ({reward} ⭐)"
                )
            ])
        
        buttons.append([BotButtonConstructor.back_button(language)])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def task_detail_keyboard(task_id: int, language: str = 'en') -> InlineKeyboardMarkup:
        """Build task detail keyboard with action buttons"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [BotButtonConstructor.complete_task_button(task_id, language)],
            [BotButtonConstructor.back_button(language)]
        ])

    @staticmethod
    def profile_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
        """Build profile keyboard with profile actions"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [BotButtonConstructor.view_achievements_button(language)],
            [BotButtonConstructor.referral_stats_button(language)],
            [BotButtonConstructor.star_history_button(language)],
            [BotButtonConstructor.back_button(language)]
        ])

    @staticmethod
    def settings_keyboard(settings: Dict[str, Any], language: str = 'en') -> InlineKeyboardMarkup:
        """Build settings keyboard with toggles"""
        notifications_enabled = settings.get('notifications_enabled', True)
        task_notif = settings.get('task_notifications', True)
        reward_notif = settings.get('reward_notifications', True)
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [BotButtonConstructor.change_language_button(language)],
            [BotButtonConstructor.toggle_notifications_button(notifications_enabled, language)],
            [BotButtonConstructor.toggle_task_notif_button(task_notif, language)],
            [BotButtonConstructor.toggle_reward_notif_button(reward_notif, language)],
            [BotButtonConstructor.back_button(language)]
        ])

    @staticmethod
    def language_selection_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
        """Build language selection keyboard"""
        languages = [
            ('en', 'English 🇬🇧'),
            ('ru', 'Русский 🇷🇺'),
            ('es', 'Español 🇪🇸')
        ]
        
        buttons = []
        for lang_code, lang_name in languages:
            buttons.append([BotButtonConstructor.language_selection_button(lang_code, lang_name)])
        
        buttons.append([BotButtonConstructor.back_button(language)])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def help_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
        """Build help menu keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [BotButtonConstructor.help_tasks_button(language)],
            [BotButtonConstructor.help_stars_button(language)],
            [BotButtonConstructor.help_referrals_button(language)],
            [BotButtonConstructor.help_support_button(language)],
            [BotButtonConstructor.back_button(language)]
        ])

    @staticmethod
    def back_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
        """Build simple back keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [BotButtonConstructor.back_button(language)]
        ])

    @staticmethod
    def referral_stats_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
        """Build referral stats keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [BotButtonConstructor.back_button(language)]
        ])

    @staticmethod
    def star_history_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
        """Build star history keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [BotButtonConstructor.back_button(language)]
        ])


# Convenience instances for direct usage
messages = BotMessageConstructor()
buttons = BotButtonConstructor()
keyboards = BotKeyboardConstructor()
