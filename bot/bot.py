from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from config.settings import settings
from database.db import db
from app.services import user_service, task_service, category_service
from app.models import UserCreate
from bot.i18n import t
import asyncio
import logging
import hashlib
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot_token)
dp = Dispatcher()

# Default bot username fallback
DEFAULT_BOT_USERNAME = 'TaskAppBot'


def escape_markdown(text: str) -> str:
    """Escape special characters for Markdown formatting"""
    if not text:
        return ''
    # Escape special Markdown characters
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def generate_referral_code(telegram_id: int) -> str:
    """Generate unique referral code for a user"""
    hash_obj = hashlib.md5(f"{telegram_id}_{settings.bot_token[:10]}".encode())
    return hash_obj.hexdigest()[:8].upper()


async def get_user_language(user_id: int) -> str:
    """Get user's language preference from user_settings"""
    user_settings = await db.fetch_one("SELECT language FROM user_settings WHERE user_id = ?", (user_id,))
    return user_settings['language'] if user_settings else 'en'


async def process_referral(new_user_id: int, referral_code: str):
    """Process referral bonus when a new user signs up with a referral code"""
    # Find referrer by referral code
    query = "SELECT id FROM users WHERE referral_code = ?"
    referrer = await db.fetch_one(query, (referral_code,))
    
    if referrer and referrer['id'] != new_user_id:
        # Check if referral already exists
        check_query = "SELECT id FROM referrals WHERE referred_id = ?"
        existing = await db.fetch_one(check_query, (new_user_id,))
        
        if not existing:
            # Create referral record
            await db.execute(
                "INSERT INTO referrals (referrer_id, referred_id, bonus_awarded) VALUES (?, ?, 1)",
                (referrer['id'], new_user_id)
            )
            
            # Award bonus to referrer
            referral_bonus = 50  # 50 stars for successful referral
            await db.execute(
                "UPDATE users SET stars = stars + ? WHERE id = ?",
                (referral_bonus, referrer['id'])
            )
            
            # Log the transaction
            await db.execute(
                """INSERT INTO star_transactions 
                (user_id, amount, type, reference_type, reference_id, description) 
                VALUES (?, ?, 'bonus', 'referral', ?, 'Referral bonus')""",
                (referrer['id'], referral_bonus, new_user_id)
            )
            
            return referrer['id'], referral_bonus
    return None, 0


async def check_bot_is_admin(channel_id: str) -> bool:
    """Check if bot is admin in the specified channel"""
    try:
        # Get bot's member status in the channel
        member = await bot.get_chat_member(channel_id, bot.id)
        # Check if bot is admin or creator
        return member.status in ['administrator', 'creator']
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.warning(f"Could not check bot admin status in channel {channel_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking bot admin status: {e}")
        return False


async def verify_user_channel_membership(user_id: int, channel_id: str) -> bool:
    """Verify if user is a member of the specified channel"""
    try:
        # Get user's member status in the channel
        member = await bot.get_chat_member(channel_id, user_id)
        # User is considered a member if they're not left or kicked
        return member.status in ['member', 'administrator', 'creator']
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.warning(f"Could not verify user {user_id} membership in channel {channel_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error verifying channel membership: {e}")
        return False



@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    # Use bot username from settings, fallback to getting from API
    bot_username = settings.bot_username
    if not bot_username or bot_username == DEFAULT_BOT_USERNAME:
        # Try to get from API if not configured
        try:
            bot_info = await bot.get_me()
            bot_username = bot_info.username if bot_info and bot_info.username else DEFAULT_BOT_USERNAME
        except Exception:
            bot_username = DEFAULT_BOT_USERNAME
    
    bot_username_escaped = escape_markdown(bot_username)
    
    referral_code = None
    # Extract referral code from start command
    if ' ' in message.text:
        referral_code = message.text.split()[1]
    
    # Get user language preference
    user_lang = 'en'
    if user:
        user_lang = await get_user_language(user['id'])
    
    if not user:
        # Generate unique referral code for new user
        user_referral_code = generate_referral_code(message.from_user.id)
        
        user_data = UserCreate(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            referral_code=user_referral_code,
            stars=0,
            status="active",
            role="user"
        )
        user_id = await user_service.create_user(user_data)
        user = await user_service.get_user(user_id)
        
        # Format referral link (escape bot username for markdown)
        referral_link = f"https://t.me/{bot_username_escaped}?start={user_referral_code}"
        
        # Process referral if code was provided
        if referral_code:
            referrer_id, bonus = await process_referral(user_id, referral_code)
            first_name_display = escape_markdown(message.from_user.first_name) if message.from_user.first_name else "there"
            if referrer_id:
                welcome_msg = t('bot_welcome_referred', user_lang,
                    name=first_name_display,
                    bonus=bonus,
                    stars=user['stars'],
                    referral_link=referral_link
                )
            else:
                welcome_msg = t('bot_welcome_new', user_lang,
                    name=first_name_display,
                    stars=user['stars'],
                    referral_link=referral_link
                )
        else:
            first_name_display = escape_markdown(message.from_user.first_name) if message.from_user.first_name else "there"
            welcome_msg = t('bot_welcome_new', user_lang,
                name=first_name_display,
                stars=user['stars'],
                referral_link=referral_link
            )
    else:
        first_name_display = escape_markdown(message.from_user.first_name) if message.from_user.first_name else "there"
        referral_link = f"https://t.me/{bot_username_escaped}?start={user.get('referral_code', '')}"
        welcome_msg = t('bot_welcome_back', user_lang,
            name=first_name_display,
            stars=user['stars'],
            referral_link=referral_link
        )
    
    # Create Mini App button
    web_app_url = f"{settings.web_app_url or 'https://example.com'}/miniapp"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t('bot_button_open_app', user_lang), web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton(text=t('bot_button_view_tasks', user_lang), callback_data="view_tasks")],
        [InlineKeyboardButton(text=t('bot_button_my_profile', user_lang), callback_data="my_profile"),
         InlineKeyboardButton(text=t('bot_button_daily_bonus', user_lang), callback_data="daily_bonus")],
        [InlineKeyboardButton(text=t('bot_button_help', user_lang), callback_data="help"),
         InlineKeyboardButton(text=t('bot_button_settings', user_lang), callback_data="settings")]
    ])
    
    await message.answer(
        welcome_msg,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.message(Command("tasks"))
async def cmd_tasks(message: types.Message):
    """Show tasks organized by categories"""
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    # Get user language
    user_lang = 'en'
    if user:
        user_lang = await get_user_language(user['id'])
    
    if not user:
        await message.answer(t('bot_please_start', user_lang))
        return
    
    if user['status'] == 'banned':
        await message.answer(t('bot_account_banned', user_lang))
        return
    
    # Get all categories
    categories = await db.fetch_all("SELECT * FROM categories WHERE parent_id IS NULL")
    
    if not categories:
        await message.answer(t('bot_no_categories', user_lang))
        return
    
    keyboard_buttons = []
    for category in categories:
        # Get translated name
        category_name = await category_service.get_category_name_by_language(category['id'], user_lang)
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📁 {category_name}", 
                callback_data=f"category_{category['id']}"
            )
        ])
    
    keyboard_buttons.append([InlineKeyboardButton(text=t('bot_button_back', user_lang), callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(
        t('bot_task_categories', user_lang),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    """Show user profile with stats and achievements"""
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    # Get user language
    user_lang = 'en'
    if user:
        user_lang = await get_user_language(user['id'])
    
    if not user:
        await message.answer(t('bot_please_start', user_lang))
        return
    
    # Get user statistics
    completed_query = """
        SELECT COUNT(*) as completed 
        FROM user_tasks 
        WHERE user_id = ? AND status = 'completed'
    """
    completed_result = await db.fetch_one(completed_query, (user['id'],))
    completed_tasks = completed_result['completed'] if completed_result else 0
    
    # Get referral count
    referral_query = "SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ?"
    referral_result = await db.fetch_one(referral_query, (user['id'],))
    referral_count = referral_result['count'] if referral_result else 0
    
    # Get achievements count
    achievements_query = "SELECT COUNT(*) as count FROM user_achievements WHERE user_id = ?"
    achievements_result = await db.fetch_one(achievements_query, (user['id'],))
    achievements_count = achievements_result['count'] if achievements_result else 0
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 View Achievements", callback_data="view_achievements")],
        [InlineKeyboardButton(text="👥 Referral Stats", callback_data="referral_stats")],
        [InlineKeyboardButton(text="📊 Star History", callback_data="star_history")],
        [InlineKeyboardButton(text=t('bot_button_back', user_lang), callback_data="back_to_menu")]
    ])
    
    username_display = escape_markdown(user['username']) if user['username'] else 'N/A'
    
    profile_text = f"{t('bot_profile_title', user_lang)}\n\n"
    profile_text += f"{t('bot_profile_username', user_lang, username=username_display)}\n"
    profile_text += f"{t('bot_profile_stars', user_lang, stars=user['stars'])}\n"
    profile_text += f"{t('bot_profile_completed', user_lang, completed=completed_tasks)}\n"
    profile_text += f"{t('bot_profile_referrals', user_lang, referrals=referral_count)}\n"
    profile_text += f"{t('bot_profile_achievements', user_lang, achievements=achievements_count)}\n"
    profile_text += f"{t('bot_profile_status', user_lang, status=user['status'])}\n"
    profile_text += f"{t('bot_profile_member_since', user_lang, date=user['created_at'][:10])}"
    
    await message.answer(
        profile_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Show comprehensive help information"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 How to Complete Tasks", callback_data="help_tasks")],
        [InlineKeyboardButton(text="⭐ About Stars", callback_data="help_stars")],
        [InlineKeyboardButton(text="👥 Referral System", callback_data="help_referrals")],
        [InlineKeyboardButton(text="💬 Support", callback_data="help_support")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
    ])
    
    await message.answer(
        "ℹ️ *Task App Help Center*\n\n"
        "Welcome to our help center! Choose a topic below to learn more:\n\n"
        "*Available Commands:*\n"
        "/start - Start the bot\n"
        "/tasks - Browse tasks by category\n"
        "/profile - View your profile and stats\n"
        "/help - Show this help message\n"
        "/settings - Manage notification preferences",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    """Show user settings"""
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer("Please start the bot first with /start")
        return
    
    # Get or create user settings
    settings_query = "SELECT * FROM user_settings WHERE user_id = ?"
    user_settings = await db.fetch_one(settings_query, (user['id'],))
    
    if not user_settings:
        # Create default settings
        await db.execute(
            """INSERT INTO user_settings 
            (user_id, language, notifications_enabled, task_notifications, reward_notifications) 
            VALUES (?, 'en', 1, 1, 1)""",
            (user['id'],)
        )
        user_settings = await db.fetch_one(settings_query, (user['id'],))
    
    notif_status = "✅ Enabled" if user_settings['notifications_enabled'] else "❌ Disabled"
    task_notif = "✅ On" if user_settings['task_notifications'] else "❌ Off"
    reward_notif = "✅ On" if user_settings['reward_notifications'] else "❌ Off"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Change Language", callback_data="change_language")],
        [InlineKeyboardButton(
            text=f"🔔 All Notifications: {notif_status}", 
            callback_data="toggle_notifications"
        )],
        [InlineKeyboardButton(
            text=f"📋 Task Alerts: {task_notif}", 
            callback_data="toggle_task_notif"
        )],
        [InlineKeyboardButton(
            text=f"🎁 Reward Alerts: {reward_notif}", 
            callback_data="toggle_reward_notif"
        )],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
    ])
    
    await message.answer(
        "⚙️ *Settings*\n\n"
        f"Language: {user_settings['language'].upper()}\n"
        f"Notifications: {notif_status}\n"
        f"Task Notifications: {task_notif}\n"
        f"Reward Notifications: {reward_notif}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "view_tasks")
async def view_tasks(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot first with /start")
        return
    
    if user['status'] == 'banned':
        await callback.answer("Your account is banned", show_alert=True)
        return
    
    # Get user language
    user_lang = await get_user_language(user['id'])
    
    tasks = await task_service.get_available_tasks_for_user(user['id'])
    
    if not tasks:
        await callback.message.answer("No tasks available at the moment. Check back later!")
        await callback.answer()
        return
    
    # Apply translations to all tasks at once (avoids N+1 query)
    tasks = await task_service.apply_translations_to_tasks(tasks[:5], user_lang)
    
    for task in tasks:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Complete Task", callback_data=f"complete_{task['id']}")],
            [InlineKeyboardButton(text="View", url=task['url'] or "https://example.com")]
        ])
        
        task_type_emoji = {
            'youtube': '🎥',
            'tiktok': '🎵',
            'subscribe': '📢'
        }
        
        title_display = escape_markdown(task['title']) if task['title'] else 'Task'
        description_display = escape_markdown(task['description']) if task['description'] else 'Complete this task to earn stars!'
        
        await callback.message.answer(
            f"{task_type_emoji.get(task['type'], '📋')} {title_display}\n\n"
            f"{description_display}\n\n"
            f"Reward: {task['reward']} ⭐",
            reply_markup=keyboard
        )
    
    await callback.answer()


@dp.callback_query(F.data.startswith("complete_"))
async def complete_task(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot first with /start")
        return
    
    if user['status'] == 'banned':
        await callback.answer("Your account is banned", show_alert=True)
        return
    
    task = await task_service.get_task(task_id)
    
    if not task:
        await callback.answer("Task not found", show_alert=True)
        return
    
    if task['status'] != 'active':
        await callback.answer("This task is no longer active", show_alert=True)
        return
    
    await task_service.complete_task(user['id'], task_id)
    
    updated_user = await user_service.get_user(user['id'])
    
    await callback.message.answer(
        f"✅ Task completed!\n\n"
        f"You earned {task['reward']} ⭐\n"
        f"Total stars: {updated_user['stars']} ⭐"
    )
    await callback.answer("Task completed!", show_alert=True)


@dp.callback_query(F.data == "my_stats")
async def my_stats(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot first with /start")
        return
    
    query = """
        SELECT COUNT(*) as completed 
        FROM user_tasks 
        WHERE user_id = ? AND status = 'completed'
    """
    result = await db.fetch_one(query, (user['id'],))
    completed_tasks = result['completed'] if result else 0
    
    await callback.message.answer(
        f"📊 Your Statistics\n\n"
        f"⭐ Stars: {user['stars']}\n"
        f"✅ Completed Tasks: {completed_tasks}\n"
        f"📌 Status: {user['status']}"
    )
    await callback.answer()


@dp.callback_query(F.data == "help")
async def help_command(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 How to Complete Tasks", callback_data="help_tasks")],
        [InlineKeyboardButton(text="⭐ About Stars", callback_data="help_stars")],
        [InlineKeyboardButton(text="👥 Referral System", callback_data="help_referrals")],
        [InlineKeyboardButton(text="💬 Support", callback_data="help_support")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
    ])
    
    await callback.message.answer(
        "ℹ️ *Task App Help Center*\n\n"
        "Welcome to our help center! Choose a topic below to learn more:\n\n"
        "*Available Commands:*\n"
        "/start - Start the bot\n"
        "/tasks - Browse tasks by category\n"
        "/profile - View your profile and stats\n"
        "/help - Show this help message\n"
        "/settings - Manage notification preferences",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# Category navigation callbacks
@dp.callback_query(F.data.startswith("category_"))
async def show_category_tasks(callback: types.CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user or user['status'] == 'banned':
        await callback.answer("Access denied", show_alert=True)
        return
    
    # Get user language
    user_lang = await get_user_language(user['id'])
    
    # Get category info
    category = await db.fetch_one("SELECT * FROM categories WHERE id = ?", (category_id,))
    if not category:
        await callback.answer("Category not found", show_alert=True)
        return
    
    # Get translated category name
    category_name = await category_service.get_category_name_by_language(category_id, user_lang)
    
    # Get tasks in this category with translations using service function
    tasks = await task_service.get_tasks_by_language(
        user_lang,
        category_id=category_id,
        status='active',
        limit=10
    )
    
    if not tasks:
        await callback.message.answer(f"No tasks available in {category_name} category.")
        await callback.answer()
        return
    
    for task in tasks:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 View Details", callback_data=f"task_detail_{task['id']}")],
            [InlineKeyboardButton(text="✅ Complete", callback_data=f"submit_task_{task['id']}")]
        ])
        
        task_type_emoji = {'youtube': '🎥', 'tiktok': '🎵', 'subscribe': '📢'}
        
        title_display = escape_markdown(task['title']) if task['title'] else 'Task'
        description_display = escape_markdown(task['description']) if task['description'] else 'Complete this task to earn stars!'
        
        await callback.message.answer(
            f"{task_type_emoji.get(task['type'], '📋')} *{title_display}*\n\n"
            f"{description_display}\n\n"
            f"Reward: {task['reward']} ⭐",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    await callback.answer()


@dp.callback_query(F.data.startswith("task_detail_"))
async def show_task_detail(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[2])
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot first with /start")
        return
    
    # Get user language
    user_lang = await get_user_language(user['id'])
    
    # Get task with translation
    task = await task_service.get_task_by_language(task_id, user_lang)
    
    if not task:
        await callback.answer("Task not found", show_alert=True)
        return
    
    # Build keyboard based on task type and verification method
    keyboard_buttons = []
    
    # Add Quick Join button for subscribe tasks
    if task['type'] == 'subscribe' and task['url']:
        keyboard_buttons.append([InlineKeyboardButton(text="⚡ Quick Join", url=task['url'])])
    
    # Add Open Link button for other tasks
    if task['url'] and task['type'] != 'subscribe':
        keyboard_buttons.append([InlineKeyboardButton(text="🔗 Open Link", url=task['url'])])
    
    # Add Submit Completion button
    keyboard_buttons.append([InlineKeyboardButton(text="✅ Submit Completion", callback_data=f"submit_task_{task_id}")])
    
    # Add Back button
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="view_tasks")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    title_display = escape_markdown(task['title']) if task['title'] else 'Task'
    description_display = escape_markdown(task['description']) if task['description'] else 'Complete the task and submit for verification.'
    
    # Customize instructions based on task type and verification method
    verification_info = ""
    if task['type'] == 'subscribe':
        if task.get('verification_method') == 'auto' and task.get('channel_id'):
            verification_info = "\n✓ *Auto-verification enabled* - instant reward!"
        else:
            verification_info = "\n⚠️ *Manual verification required* - submit screenshot"
    
    steps_text = ""
    if task['type'] == 'subscribe':
        steps_text = (
            f"1. Click 'Quick Join' to join the channel\n"
            f"2. Click 'Submit Completion' to verify{verification_info}\n"
            f"3. Receive your reward!"
        )
    else:
        steps_text = (
            f"1. Click 'Open Link' to access the task\n"
            f"2. Complete the required action\n"
            f"3. Take a screenshot (if required)\n"
            f"4. Click 'Submit Completion'"
        )
    
    await callback.message.answer(
        f"📋 *Task Details*\n\n"
        f"*Title:* {title_display}\n"
        f"*Type:* {task['type'].title()}\n"
        f"*Reward:* {task['reward']} ⭐\n\n"
        f"*Instructions:*\n{description_display}\n\n"
        f"*Steps:*\n{steps_text}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("submit_task_"))
async def submit_task(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[2])
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user or user['status'] == 'banned':
        await callback.answer("Access denied", show_alert=True)
        return
    
    task = await task_service.get_task(task_id)
    if not task or task['status'] != 'active':
        await callback.answer("Task not available", show_alert=True)
        return
    
    # Check if task is subscribe type and has channel_id for auto-verification
    if task['type'] == 'subscribe' and task.get('channel_id') and task.get('verification_method') == 'auto':
        # Try bot-based verification
        is_bot_admin = await check_bot_is_admin(task['channel_id'])
        
        if is_bot_admin:
            # Bot is admin, verify user membership
            is_member = await verify_user_channel_membership(callback.from_user.id, task['channel_id'])
            
            if is_member:
                # User is verified as member, complete task automatically
                await task_service.complete_task(user['id'], task_id)
                
                # Update user_task with verification info
                await db.execute(
                    """UPDATE user_tasks 
                    SET verified_at = ?, verification_method = 'auto'
                    WHERE user_id = ? AND task_id = ?""",
                    (datetime.now(timezone.utc).isoformat(), user['id'], task_id)
                )
                
                updated_user = await user_service.get_user(user['id'])
                await callback.message.answer(
                    f"✅ *Task completed!*\n\n"
                    f"✓ Channel membership verified\n"
                    f"You earned {task['reward']} ⭐\n"
                    f"Total stars: {updated_user['stars']} ⭐",
                    parse_mode="Markdown"
                )
                await callback.answer("Verified and completed!", show_alert=True)
                return
            else:
                await callback.message.answer(
                    "❌ *Verification Failed*\n\n"
                    "You haven't joined the channel yet.\n"
                    "Please use the 'Quick Join' button to join the channel first, then try again.",
                    parse_mode="Markdown"
                )
                await callback.answer("Please join the channel first", show_alert=True)
                return
        else:
            # Bot is not admin, fall back to manual verification
            await callback.message.answer(
                "⚠️ *Manual Verification Required*\n\n"
                "Automatic verification is not available.\n"
                "Please send a screenshot showing you've joined the channel.\n"
                "An admin will review your submission.",
                parse_mode="Markdown"
            )
            # Create pending submission
            await db.execute(
                "INSERT OR REPLACE INTO task_submissions (user_id, task_id, status) VALUES (?, ?, 'pending')",
                (user['id'], task_id)
            )
            await callback.answer("Please send a screenshot")
            return
    
    # Check if task requires verification (youtube, tiktok, or subscribe without auto-verification)
    if task['type'] in ['youtube', 'tiktok'] or (task['type'] == 'subscribe' and task.get('verification_method') != 'auto'):
        await callback.message.answer(
            "📸 *Task Submission*\n\n"
            "Please send a screenshot of the completed task.\n"
            "The screenshot will be reviewed by our team.",
            parse_mode="Markdown"
        )
        # Store task_id in user context (simplified version)
        await db.execute(
            "INSERT OR REPLACE INTO task_submissions (user_id, task_id, status) VALUES (?, ?, 'pending')",
            (user['id'], task_id)
        )
        await callback.answer("Please send a screenshot")
    else:
        # Auto-complete for simple tasks
        await task_service.complete_task(user['id'], task_id)
        updated_user = await user_service.get_user(user['id'])
        
        await callback.message.answer(
            f"✅ Task completed!\n\n"
            f"You earned {task['reward']} ⭐\n"
            f"Total stars: {updated_user['stars']} ⭐"
        )
        await callback.answer("Task completed!", show_alert=True)


# Daily bonus callback
@dp.callback_query(F.data == "daily_bonus")
async def claim_daily_bonus(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot first", show_alert=True)
        return
    
    # Check last bonus claim
    last_bonus = await db.fetch_one(
        "SELECT * FROM daily_bonuses WHERE user_id = ? ORDER BY claimed_at DESC LIMIT 1",
        (user['id'],)
    )
    
    can_claim = True
    streak = 1
    
    if last_bonus:
        last_claim_time = datetime.fromisoformat(last_bonus['claimed_at'])
        time_since_claim = datetime.now() - last_claim_time
        
        if time_since_claim < timedelta(hours=24):
            can_claim = False
            hours_left = 24 - int(time_since_claim.total_seconds() / 3600)
            await callback.answer(
                f"You already claimed your daily bonus! Come back in {hours_left} hours.",
                show_alert=True
            )
            return
        elif time_since_claim < timedelta(hours=48):
            # Maintain streak
            streak = last_bonus['streak_count'] + 1
    
    if can_claim:
        bonus_amount = 10 + (streak - 1) * 2  # Base 10 + 2 per streak day
        
        # Award bonus
        await db.execute("UPDATE users SET stars = stars + ? WHERE id = ?", (bonus_amount, user['id']))
        
        # Record bonus
        await db.execute(
            "INSERT INTO daily_bonuses (user_id, bonus_amount, streak_count) VALUES (?, ?, ?)",
            (user['id'], bonus_amount, streak)
        )
        
        # Log transaction
        await db.execute(
            """INSERT INTO star_transactions 
            (user_id, amount, type, description) 
            VALUES (?, ?, 'bonus', ?)""",
            (user['id'], bonus_amount, f'Daily bonus - Day {streak}')
        )
        
        await callback.message.answer(
            f"🎁 *Daily Bonus Claimed!*\n\n"
            f"You received: {bonus_amount} ⭐\n"
            f"Streak: {streak} day(s)\n\n"
            f"Come back tomorrow to maintain your streak!",
            parse_mode="Markdown"
        )
        await callback.answer("Bonus claimed!", show_alert=True)


# Profile callbacks
@dp.callback_query(F.data == "my_profile")
async def show_profile(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot first", show_alert=True)
        return
    
    completed_result = await db.fetch_one(
        "SELECT COUNT(*) as completed FROM user_tasks WHERE user_id = ? AND status = 'completed'",
        (user['id'],)
    )
    completed_tasks = completed_result['completed'] if completed_result else 0
    
    referral_result = await db.fetch_one(
        "SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ?",
        (user['id'],)
    )
    referral_count = referral_result['count'] if referral_result else 0
    
    achievements_result = await db.fetch_one(
        "SELECT COUNT(*) as count FROM user_achievements WHERE user_id = ?",
        (user['id'],)
    )
    achievements_count = achievements_result['count'] if achievements_result else 0
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Achievements", callback_data="view_achievements")],
        [InlineKeyboardButton(text="👥 Referrals", callback_data="referral_stats")],
        [InlineKeyboardButton(text="📊 History", callback_data="star_history")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
    ])
    
    username_display = escape_markdown(user['username']) if user['username'] else 'N/A'
    await callback.message.answer(
        f"👤 *Your Profile*\n\n"
        f"Username: @{username_display}\n"
        f"⭐ Stars: {user['stars']}\n"
        f"✅ Completed: {completed_tasks}\n"
        f"👥 Referrals: {referral_count}\n"
        f"🏆 Achievements: {achievements_count}\n"
        f"📅 Member since: {user['created_at'][:10]}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "referral_stats")
async def show_referral_stats(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot first", show_alert=True)
        return
    
    referrals = await db.fetch_all(
        """SELECT r.*, u.username, u.created_at 
        FROM referrals r
        JOIN users u ON r.referred_id = u.id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at DESC LIMIT 10""",
        (user['id'],)
    )
    
    referral_count = len(referrals)
    total_bonus = referral_count * 50  # 50 stars per referral
    
    referral_list = "\n".join([
        f"• @{ref['username'] or 'User'} - {ref['created_at'][:10]}"
        for ref in referrals[:5]
    ]) if referrals else "No referrals yet"
    
    # Escape bot username for markdown
    bot_username_escaped = escape_markdown(settings.bot_username)
    share_url = f"https://t.me/{bot_username_escaped}?start={user['referral_code']}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Share Referral Link", url=share_url)],
        [InlineKeyboardButton(text="🔙 Back", callback_data="my_profile")]
    ])
    
    await callback.message.answer(
        f"👥 *Referral Statistics*\n\n"
        f"Your referral code: `{user['referral_code']}`\n"
        f"Total referrals: {referral_count}\n"
        f"Bonus earned: {total_bonus} ⭐\n\n"
        f"*Recent Referrals:*\n{referral_list}\n\n"
        f"Share your link to earn 50 ⭐ per friend!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "star_history")
async def show_star_history(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot first", show_alert=True)
        return
    
    transactions = await db.fetch_all(
        """SELECT * FROM star_transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC LIMIT 10""",
        (user['id'],)
    )
    
    if not transactions:
        history_text = "No transactions yet"
    else:
        history_text = "\n".join([
            f"• {'+' if tx['amount'] > 0 else ''}{tx['amount']} ⭐ - {tx['type'].title()} ({tx['created_at'][:10]})"
            for tx in transactions
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data="my_profile")]
    ])
    
    await callback.message.answer(
        f"📊 *Star Transaction History*\n\n"
        f"Current Balance: {user['stars']} ⭐\n\n"
        f"*Recent Transactions:*\n{history_text}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# Settings callbacks
@dp.callback_query(F.data == "settings")
async def show_settings(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot first", show_alert=True)
        return
    
    user_settings = await db.fetch_one("SELECT * FROM user_settings WHERE user_id = ?", (user['id'],))
    
    if not user_settings:
        await db.execute(
            "INSERT INTO user_settings (user_id) VALUES (?)",
            (user['id'],)
        )
        user_settings = await db.fetch_one("SELECT * FROM user_settings WHERE user_id = ?", (user['id'],))
    
    notif_status = "✅" if user_settings['notifications_enabled'] else "❌"
    task_notif = "✅" if user_settings['task_notifications'] else "❌"
    reward_notif = "✅" if user_settings['reward_notifications'] else "❌"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Language", callback_data="change_language")],
        [InlineKeyboardButton(text=f"🔔 Notifications {notif_status}", callback_data="toggle_notifications")],
        [InlineKeyboardButton(text=f"📋 Task Alerts {task_notif}", callback_data="toggle_task_notif")],
        [InlineKeyboardButton(text=f"🎁 Reward Alerts {reward_notif}", callback_data="toggle_reward_notif")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
    ])
    
    await callback.message.answer(
        "⚙️ *Settings*\n\n"
        f"Language: {user_settings['language'].upper()}\n"
        f"Notifications: {notif_status}\n"
        f"Task Notifications: {task_notif}\n"
        f"Reward Notifications: {reward_notif}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "change_language")
async def change_language(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings")]
    ])
    
    await callback.message.answer(
        "🌐 *Select Language*\n\nChoose your preferred language:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if user:
        await db.execute(
            "UPDATE user_settings SET language = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (lang_code, user['id'])
        )
        await callback.answer(f"Language changed to {lang_code.upper()}", show_alert=True)
        await show_settings(callback)


@dp.callback_query(F.data == "toggle_notifications")
async def toggle_notifications(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if user:
        await db.execute(
            """UPDATE user_settings 
            SET notifications_enabled = NOT notifications_enabled, 
                updated_at = CURRENT_TIMESTAMP 
            WHERE user_id = ?""",
            (user['id'],)
        )
        await callback.answer("Notifications toggled")
        await show_settings(callback)


@dp.callback_query(F.data == "toggle_task_notif")
async def toggle_task_notif(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if user:
        await db.execute(
            """UPDATE user_settings 
            SET task_notifications = NOT task_notifications, 
                updated_at = CURRENT_TIMESTAMP 
            WHERE user_id = ?""",
            (user['id'],)
        )
        await callback.answer("Task notifications toggled")
        await show_settings(callback)


@dp.callback_query(F.data == "toggle_reward_notif")
async def toggle_reward_notif(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if user:
        await db.execute(
            """UPDATE user_settings 
            SET reward_notifications = NOT reward_notifications, 
                updated_at = CURRENT_TIMESTAMP 
            WHERE user_id = ?""",
            (user['id'],)
        )
        await callback.answer("Reward notifications toggled")
        await show_settings(callback)


# Help callbacks
@dp.callback_query(F.data == "help_tasks")
async def help_tasks(callback: types.CallbackQuery):
    await callback.message.answer(
        "📋 *How to Complete Tasks*\n\n"
        "1. Browse tasks by category using /tasks\n"
        "2. Click on a task to see full details\n"
        "3. Follow the instructions carefully\n"
        "4. Complete the required action (watch video, subscribe, etc.)\n"
        "5. Submit your completion (screenshot if required)\n"
        "6. Wait for verification (if needed)\n"
        "7. Receive your star reward!\n\n"
        "*Task Types:*\n"
        "🎥 YouTube - Watch videos, subscribe to channels\n"
        "🎵 TikTok - Like videos, follow accounts\n"
        "📢 Subscribe - Join channels, groups, pages",
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "help_stars")
async def help_stars(callback: types.CallbackQuery):
    await callback.message.answer(
        "⭐ *About Stars*\n\n"
        "Stars are the currency in Task App!\n\n"
        "*Ways to Earn Stars:*\n"
        "• Complete tasks (varies by task)\n"
        "• Daily bonus (10+ stars per day)\n"
        "• Refer friends (50 stars per referral)\n"
        "• Achieve milestones (bonus rewards)\n\n"
        "*Using Stars:*\n"
        "• Redeem for rewards\n"
        "• Withdraw to real money\n"
        "• Exchange for gift cards\n"
        "• More options coming soon!",
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "help_referrals")
async def help_referrals(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    referral_code = user['referral_code'] if user else "YOUR_CODE"
    # Escape bot username for markdown
    bot_username_escaped = escape_markdown(settings.bot_username)
    share_url = f"https://t.me/{bot_username_escaped}?start={referral_code}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Share Your Link", url=share_url)],
        [InlineKeyboardButton(text="🔙 Back", callback_data="help")]
    ])
    
    await callback.message.answer(
        "👥 *Referral System*\n\n"
        f"Your referral code: `{referral_code}`\n\n"
        "*How it works:*\n"
        "1. Share your unique referral link\n"
        "2. Friends sign up using your link\n"
        "3. You both get rewarded!\n\n"
        "*Rewards:*\n"
        "• You: 50 ⭐ per successful referral\n"
        "• Friend: Welcome bonus\n\n"
        "*Tips:*\n"
        "• Share on social media\n"
        "• Tell your friends about easy tasks\n"
        "• The more you share, the more you earn!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "help_support")
async def help_support(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Create Support Ticket", callback_data="create_ticket")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="help")]
    ])
    
    await callback.message.answer(
        "💬 *Support*\n\n"
        "Need help? We're here for you!\n\n"
        "*Contact Options:*\n"
        "• Create a support ticket below\n"
        "• Email: support@taskapp.com\n"
        "• Response time: 24-48 hours\n\n"
        "*Common Issues:*\n"
        "• Task not completed? Check requirements\n"
        "• Stars not received? Wait 5-10 minutes\n"
        "• Account issues? Contact support",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "create_ticket")
async def create_ticket_prompt(callback: types.CallbackQuery):
    await callback.message.answer(
        "📝 *Create Support Ticket*\n\n"
        "Please describe your issue in detail.\n"
        "Our support team will respond within 24-48 hours.\n\n"
        "Type your message:",
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please start the bot with /start", show_alert=True)
        return
    
    web_app_url = f"{settings.web_app_url or 'https://example.com'}/miniapp"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Open Mini App", web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton(text="📋 View Tasks", callback_data="view_tasks")],
        [InlineKeyboardButton(text="👤 My Profile", callback_data="my_profile"),
         InlineKeyboardButton(text="🎁 Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton(text="ℹ️ Help", callback_data="help"),
         InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])
    
    await callback.message.answer(
        f"👋 Welcome back, {callback.from_user.first_name}!\n\n"
        f"Your current stars: {user['stars']} ⭐",
        reply_markup=keyboard
    )
    await callback.answer()


# Message handlers for text/photo submissions
@dp.message(F.photo)
async def handle_photo_submission(message: types.Message):
    """Handle screenshot submissions for task verification"""
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer("Please start the bot first with /start")
        return
    
    # Find pending submission
    submission = await db.fetch_one(
        """SELECT * FROM task_submissions 
        WHERE user_id = ? AND status = 'pending' 
        ORDER BY submitted_at DESC LIMIT 1""",
        (user['id'],)
    )
    
    if not submission:
        await message.answer(
            "No pending task submission found. "
            "Please select a task first and click 'Submit Completion'."
        )
        return
    
    # Save photo file_id
    photo_file_id = message.photo[-1].file_id
    await db.execute(
        "UPDATE task_submissions SET file_id = ?, submitted_at = CURRENT_TIMESTAMP WHERE id = ?",
        (photo_file_id, submission['id'])
    )
    
    await message.answer(
        "✅ Screenshot received!\n\n"
        "Your submission is being reviewed by our team.\n"
        "You'll be notified once it's approved (usually within 24 hours)."
    )


@dp.message(F.text)
async def handle_text_message(message: types.Message):
    """Handle text messages for support tickets"""
    # Check if this is a support ticket
    if message.text and len(message.text) > 20:
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        if user:
            # Create support ticket
            await db.execute(
                """INSERT INTO tickets 
                (user_id, subject, message, priority, status) 
                VALUES (?, 'User Support Request', ?, 'medium', 'open')""",
                (user['id'], message.text)
            )
            
            await message.answer(
                "✅ Support ticket created!\n\n"
                "Ticket ID has been generated.\n"
                "Our team will respond within 24-48 hours.\n\n"
                "Thank you for your patience!"
            )
        else:
            await message.answer("Please start the bot first with /start")


@dp.message(Command("help"))
async def cmd_help_duplicate(message: types.Message):
    # This is already handled above, removing duplicate
    pass


async def start_bot():
    await db.connect()
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
