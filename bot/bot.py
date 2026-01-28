from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config.settings import settings
from database.db import db
from app.services import user_service, task_service
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot_token)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        user_id = await user_service.create_user({
            "telegram_id": message.from_user.id,
            "username": message.from_user.username,
            "stars": 0,
            "status": "active",
            "role": "user"
        })
        user = await user_service.get_user(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 View Tasks", callback_data="view_tasks")],
        [InlineKeyboardButton(text="⭐ My Stars", callback_data="my_stats")],
        [InlineKeyboardButton(text="ℹ️ Help", callback_data="help")]
    ])
    
    await message.answer(
        f"👋 Welcome to Task App, {message.from_user.first_name}!\n\n"
        f"Complete tasks and earn stars ⭐\n"
        f"Your current stars: {user['stars']}",
        reply_markup=keyboard
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
    
    tasks = await task_service.get_available_tasks_for_user(user['id'])
    
    if not tasks:
        await callback.message.answer("No tasks available at the moment. Check back later!")
        await callback.answer()
        return
    
    for task in tasks[:5]:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Complete Task", callback_data=f"complete_{task['id']}")],
            [InlineKeyboardButton(text="View", url=task['url'] or "https://example.com")]
        ])
        
        task_type_emoji = {
            'youtube': '🎥',
            'tiktok': '🎵',
            'subscribe': '📢'
        }
        
        await callback.message.answer(
            f"{task_type_emoji.get(task['type'], '📋')} {task['title']}\n\n"
            f"{task['description'] or 'Complete this task to earn stars!'}\n\n"
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
    await callback.message.answer(
        "ℹ️ How to use Task App:\n\n"
        "1. View available tasks\n"
        "2. Click on a task to see details\n"
        "3. Complete the task (watch video, subscribe, etc.)\n"
        "4. Click 'Complete Task' button\n"
        "5. Earn stars! ⭐\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )
    await callback.answer()


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "ℹ️ How to use Task App:\n\n"
        "1. View available tasks\n"
        "2. Click on a task to see details\n"
        "3. Complete the task (watch video, subscribe, etc.)\n"
        "4. Click 'Complete Task' button\n"
        "5. Earn stars! ⭐\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )


async def start_bot():
    await db.connect()
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
