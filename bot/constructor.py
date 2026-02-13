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
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bot.i18n import t
from typing import List, Optional, Dict, Any


class BotMessageConstructor:
    """
    Centralized message constructor for the Telegram bot.
    Provides methods to build formatted messages with localization support.
    """

    @staticmethod
    def welcome_new_user(name: str, stars: int, referral_link: str, language: str = 'en') -> str:
        """Construct welcome message for new users"""
        return t('bot_welcome_new', language, name=name, stars=stars, referral_link=referral_link)

    @staticmethod
    def welcome_back(name: str, stars: int, referral_link: str, language: str = 'en') -> str:
        """Construct welcome back message for returning users"""
        return t('bot_welcome_back', language, name=name, stars=stars, referral_link=referral_link)

    @staticmethod
    def welcome_referred(name: str, bonus: int, stars: int, referral_link: str, language: str = 'en') -> str:
        """Construct welcome message for referred users"""
        return t('bot_welcome_referred', language, name=name, bonus=bonus, stars=stars, referral_link=referral_link)

    @staticmethod
    def task_categories(language: str = 'en') -> str:
        """Construct task categories message"""
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
        
        profile_parts = [
            t('bot_profile_title', language),
            "",
            t('bot_profile_username', language, username=username),
            t('bot_profile_stars', language, stars=stars),
            t('bot_profile_completed', language, completed=completed),
            t('bot_profile_referrals', language, referrals=referrals),
            t('bot_profile_achievements', language, achievements=achievements),
            t('bot_profile_status', language, status=status),
            t('bot_profile_member_since', language, date=created_at)
        ]
        
        return "\n".join(profile_parts)

    @staticmethod
    def category_tasks_message(category_name: str, task_count: int, language: str = 'en') -> str:
        """Construct category tasks listing message"""
        return f"📋 *{category_name}*\n\nAvailable tasks: {task_count}"

    @staticmethod
    def task_detail_message(task: Dict[str, Any], language: str = 'en') -> str:
        """Construct detailed task information message"""
        title = task.get('title', 'Unknown Task')
        description = task.get('description', 'No description')
        reward = task.get('reward', 0)
        task_type = task.get('type', 'general')
        
        return (
            f"📝 *{title}*\n\n"
            f"{description}\n\n"
            f"🎯 Type: {task_type}\n"
            f"⭐ Reward: {reward} stars"
        )

    @staticmethod
    def daily_bonus_message(bonus_amount: int, streak: int, language: str = 'en') -> str:
        """Construct daily bonus claim message"""
        return (
            f"🎁 *Daily Bonus Claimed!*\n\n"
            f"You received {bonus_amount} ⭐\n"
            f"Current streak: {streak} days"
        )

    @staticmethod
    def referral_stats_message(referral_count: int, total_earned: int, language: str = 'en') -> str:
        """Construct referral statistics message"""
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
    """

    @staticmethod
    def web_app_button(url: str, language: str = 'en') -> InlineKeyboardButton:
        """Create Mini App button"""
        return InlineKeyboardButton(
            text=t('bot_button_open_app', language),
            web_app=WebAppInfo(url=url)
        )

    @staticmethod
    def view_tasks_button(language: str = 'en') -> InlineKeyboardButton:
        """Create View Tasks button"""
        return InlineKeyboardButton(
            text=t('bot_button_view_tasks', language),
            callback_data="view_tasks"
        )

    @staticmethod
    def my_profile_button(language: str = 'en') -> InlineKeyboardButton:
        """Create My Profile button"""
        return InlineKeyboardButton(
            text=t('bot_button_my_profile', language),
            callback_data="my_profile"
        )

    @staticmethod
    def daily_bonus_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Daily Bonus button"""
        return InlineKeyboardButton(
            text=t('bot_button_daily_bonus', language),
            callback_data="daily_bonus"
        )

    @staticmethod
    def help_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help button"""
        return InlineKeyboardButton(
            text=t('bot_button_help', language),
            callback_data="help"
        )

    @staticmethod
    def settings_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Settings button"""
        return InlineKeyboardButton(
            text=t('bot_button_settings', language),
            callback_data="settings"
        )

    @staticmethod
    def back_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Back button"""
        return InlineKeyboardButton(
            text=t('bot_button_back', language),
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
        return InlineKeyboardButton(
            text="✅ Complete Task",
            callback_data=f"complete_{task_id}"
        )

    @staticmethod
    def submit_task_button(task_id: int, language: str = 'en') -> InlineKeyboardButton:
        """Create submit task button"""
        return InlineKeyboardButton(
            text="📤 Submit Task",
            callback_data=f"submit_task_{task_id}"
        )

    @staticmethod
    def view_achievements_button(language: str = 'en') -> InlineKeyboardButton:
        """Create View Achievements button"""
        return InlineKeyboardButton(
            text="🏆 View Achievements",
            callback_data="view_achievements"
        )

    @staticmethod
    def referral_stats_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Referral Stats button"""
        return InlineKeyboardButton(
            text="👥 Referral Stats",
            callback_data="referral_stats"
        )

    @staticmethod
    def star_history_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Star History button"""
        return InlineKeyboardButton(
            text="📊 Star History",
            callback_data="star_history"
        )

    @staticmethod
    def change_language_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Change Language button"""
        return InlineKeyboardButton(
            text="🌐 Change Language",
            callback_data="change_language"
        )

    @staticmethod
    def language_selection_button(lang_code: str, lang_name: str) -> InlineKeyboardButton:
        """Create language selection button"""
        return InlineKeyboardButton(
            text=f"{lang_name}",
            callback_data=f"lang_{lang_code}"
        )

    @staticmethod
    def toggle_notifications_button(enabled: bool, language: str = 'en') -> InlineKeyboardButton:
        """Create toggle all notifications button"""
        status = "✅" if enabled else "❌"
        return InlineKeyboardButton(
            text=f"{status} All Notifications",
            callback_data="toggle_notifications"
        )

    @staticmethod
    def toggle_task_notif_button(enabled: bool, language: str = 'en') -> InlineKeyboardButton:
        """Create toggle task notifications button"""
        status = "✅" if enabled else "❌"
        return InlineKeyboardButton(
            text=f"{status} Task Notifications",
            callback_data="toggle_task_notif"
        )

    @staticmethod
    def toggle_reward_notif_button(enabled: bool, language: str = 'en') -> InlineKeyboardButton:
        """Create toggle reward notifications button"""
        status = "✅" if enabled else "❌"
        return InlineKeyboardButton(
            text=f"{status} Reward Notifications",
            callback_data="toggle_reward_notif"
        )

    @staticmethod
    def help_tasks_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help - How to Complete Tasks button"""
        return InlineKeyboardButton(
            text="📋 How to Complete Tasks",
            callback_data="help_tasks"
        )

    @staticmethod
    def help_stars_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help - About Stars button"""
        return InlineKeyboardButton(
            text="⭐ About Stars",
            callback_data="help_stars"
        )

    @staticmethod
    def help_referrals_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help - Referral System button"""
        return InlineKeyboardButton(
            text="👥 Referral System",
            callback_data="help_referrals"
        )

    @staticmethod
    def help_support_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Help - Support button"""
        return InlineKeyboardButton(
            text="💬 Support",
            callback_data="help_support"
        )

    @staticmethod
    def create_ticket_button(language: str = 'en') -> InlineKeyboardButton:
        """Create Create Ticket button"""
        return InlineKeyboardButton(
            text="📝 Create Ticket",
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
