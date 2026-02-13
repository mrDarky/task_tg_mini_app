#!/usr/bin/env python3
"""
Initialize Bot States for Bot Constructor

This script populates the bot_states table with all the states that are currently
hardcoded in the bot. This allows the admin panel's bot constructor to display
and manage all bot states.
"""

import asyncio
from database.db import db


async def initialize_states():
    """Initialize bot states in the database"""
    print("Initializing bot states...")
    
    # Check if states already exist
    existing_states = await db.fetch_all("SELECT * FROM bot_states")
    if existing_states:
        print(f"Found {len(existing_states)} existing states.")
        response = input("Do you want to clear existing states and reinitialize? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Initialization cancelled.")
            return
        
        # Clear existing states (cascade will delete buttons too)
        await db.execute("DELETE FROM bot_states")
        print("Cleared existing states.")
    
    states = [
        {
            'state_key': 'start',
            'name': 'Welcome / Start',
            'message_text': '👋 Welcome back, {first_name}!\n\nYour current stars: {stars} ⭐\nYour referral link: {referral_link}',
            'is_start_state': True,
            'buttons': [
                {'text': '🚀 Open Mini App', 'button_type': 'web_app', 'web_app_url': '{web_app_url}', 'row': 0, 'col': 0},
                {'text': '📋 View Tasks', 'button_type': 'callback', 'callback_data': 'view_tasks', 'row': 1, 'col': 0},
                {'text': '👤 My Profile', 'button_type': 'callback', 'callback_data': 'my_profile', 'row': 2, 'col': 0},
                {'text': '🎁 Daily Bonus', 'button_type': 'callback', 'callback_data': 'daily_bonus', 'row': 2, 'col': 1},
                {'text': 'ℹ️ Help', 'button_type': 'callback', 'callback_data': 'help', 'row': 3, 'col': 0},
                {'text': '⚙️ Settings', 'button_type': 'callback', 'callback_data': 'settings', 'row': 3, 'col': 1},
            ]
        },
        {
            'state_key': 'view_tasks',
            'name': 'Task Categories',
            'message_text': '📋 *Task Categories*\n\nChoose a category to view available tasks:',
            'is_start_state': False,
            'buttons': [
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'back_to_menu', 'row': 0, 'col': 0},
            ]
        },
        {
            'state_key': 'my_profile',
            'name': 'User Profile',
            'message_text': '👤 *Your Profile*\n\nUsername: @{username}\n⭐ Stars: {stars}\n✅ Completed Tasks: {completed_tasks}\n👥 Referrals: {referrals}\n🏆 Achievements: {achievements}\n📌 Status: {status}',
            'is_start_state': False,
            'buttons': [
                {'text': '🏆 View Achievements', 'button_type': 'callback', 'callback_data': 'view_achievements', 'row': 0, 'col': 0},
                {'text': '👥 Referral Stats', 'button_type': 'callback', 'callback_data': 'referral_stats', 'row': 1, 'col': 0},
                {'text': '📊 Star History', 'button_type': 'callback', 'callback_data': 'star_history', 'row': 2, 'col': 0},
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'back_to_menu', 'row': 3, 'col': 0},
            ]
        },
        {
            'state_key': 'daily_bonus',
            'name': 'Daily Bonus',
            'message_text': '🎁 *Daily Bonus*\n\nClaim your daily reward and maintain your streak!\n\nStreak: {streak} days\nToday\'s bonus: {bonus_amount} ⭐',
            'is_start_state': False,
            'buttons': [
                {'text': '✅ Claim Bonus', 'button_type': 'callback', 'callback_data': 'claim_daily_bonus', 'row': 0, 'col': 0},
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'back_to_menu', 'row': 1, 'col': 0},
            ]
        },
        {
            'state_key': 'help',
            'name': 'Help Menu',
            'message_text': 'ℹ️ *Help & Information*\n\nSelect a topic to learn more:',
            'is_start_state': False,
            'buttons': [
                {'text': '📋 How to Complete Tasks', 'button_type': 'callback', 'callback_data': 'help_tasks', 'row': 0, 'col': 0},
                {'text': '⭐ About Stars', 'button_type': 'callback', 'callback_data': 'help_stars', 'row': 1, 'col': 0},
                {'text': '👥 Referral System', 'button_type': 'callback', 'callback_data': 'help_referrals', 'row': 2, 'col': 0},
                {'text': '💬 Support', 'button_type': 'callback', 'callback_data': 'help_support', 'row': 3, 'col': 0},
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'back_to_menu', 'row': 4, 'col': 0},
            ]
        },
        {
            'state_key': 'settings',
            'name': 'Settings',
            'message_text': '⚙️ *Settings*\n\nConfigure your preferences:',
            'is_start_state': False,
            'buttons': [
                {'text': '🌐 Change Language', 'button_type': 'callback', 'callback_data': 'change_language', 'row': 0, 'col': 0},
                {'text': '🔔 Notifications', 'button_type': 'callback', 'callback_data': 'toggle_notifications', 'row': 1, 'col': 0},
                {'text': '📋 Task Notifications', 'button_type': 'callback', 'callback_data': 'toggle_task_notif', 'row': 2, 'col': 0},
                {'text': '🎁 Reward Notifications', 'button_type': 'callback', 'callback_data': 'toggle_reward_notif', 'row': 3, 'col': 0},
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'back_to_menu', 'row': 4, 'col': 0},
            ]
        },
        {
            'state_key': 'referral_stats',
            'name': 'Referral Statistics',
            'message_text': '👥 *Referral Statistics*\n\nYour referrals: {referral_count}\nTotal earned from referrals: {total_referral_earnings} ⭐\n\nShare your link to earn more:\n{referral_link}',
            'is_start_state': False,
            'buttons': [
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'my_profile', 'row': 0, 'col': 0},
            ]
        },
        {
            'state_key': 'star_history',
            'name': 'Star History',
            'message_text': '📊 *Star Transaction History*\n\nView your recent star transactions and earnings.',
            'is_start_state': False,
            'buttons': [
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'my_profile', 'row': 0, 'col': 0},
            ]
        },
        {
            'state_key': 'help_tasks',
            'name': 'Help - Tasks',
            'message_text': '📋 *How to Complete Tasks*\n\n1. Browse available tasks in the task categories\n2. Click on a task to view details\n3. Follow the instructions (watch video, subscribe, etc.)\n4. Submit your completion\n5. Wait for verification\n6. Earn stars! ⭐',
            'is_start_state': False,
            'buttons': [
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'help', 'row': 0, 'col': 0},
            ]
        },
        {
            'state_key': 'help_stars',
            'name': 'Help - Stars',
            'message_text': '⭐ *About Stars*\n\nStars are the main currency in our app. You can earn stars by:\n- Completing tasks\n- Daily bonuses\n- Referring friends\n- Achievements\n\nUse stars to unlock premium features!',
            'is_start_state': False,
            'buttons': [
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'help', 'row': 0, 'col': 0},
            ]
        },
        {
            'state_key': 'help_referrals',
            'name': 'Help - Referrals',
            'message_text': '👥 *Referral System*\n\nInvite friends and earn rewards!\n\n- Share your unique referral link\n- When someone joins using your link, you both get stars\n- The more friends you invite, the more you earn\n\nYour referral link: {referral_link}',
            'is_start_state': False,
            'buttons': [
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'help', 'row': 0, 'col': 0},
            ]
        },
        {
            'state_key': 'help_support',
            'name': 'Help - Support',
            'message_text': '💬 *Support*\n\nNeed help? We\'re here for you!\n\nCreate a support ticket and our team will assist you as soon as possible.',
            'is_start_state': False,
            'buttons': [
                {'text': '📝 Create Ticket', 'button_type': 'callback', 'callback_data': 'create_ticket', 'row': 0, 'col': 0},
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'help', 'row': 1, 'col': 0},
            ]
        },
        {
            'state_key': 'change_language',
            'name': 'Language Selection',
            'message_text': '🌐 *Choose your language*\n\nSelect your preferred language:',
            'is_start_state': False,
            'buttons': [
                {'text': '🇬🇧 English', 'button_type': 'callback', 'callback_data': 'lang_en', 'row': 0, 'col': 0},
                {'text': '🇷🇺 Русский', 'button_type': 'callback', 'callback_data': 'lang_ru', 'row': 1, 'col': 0},
                {'text': '🇪🇸 Español', 'button_type': 'callback', 'callback_data': 'lang_es', 'row': 2, 'col': 0},
                {'text': '🔙 Back', 'button_type': 'callback', 'callback_data': 'settings', 'row': 3, 'col': 0},
            ]
        },
    ]
    
    print(f"\nCreating {len(states)} states...")
    
    for state_data in states:
        # Insert state
        cursor = await db.execute(
            """INSERT INTO bot_states 
               (state_key, name, message_text, is_start_state, x_position, y_position) 
               VALUES (?, ?, ?, ?, 0, 0)""",
            (state_data['state_key'], state_data['name'], state_data['message_text'], 
             state_data['is_start_state'])
        )
        
        state_id = cursor.lastrowid
        print(f"  ✓ Created state: {state_data['name']} (ID: {state_id})")
        
        # Insert buttons
        if 'buttons' in state_data:
            for button in state_data['buttons']:
                await db.execute(
                    """INSERT INTO bot_buttons 
                       (state_id, text, button_type, callback_data, url, web_app_url, 
                        target_state_id, row_position, col_position) 
                       VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)""",
                    (state_id, button['text'], button['button_type'], 
                     button.get('callback_data'), button.get('url'), 
                     button.get('web_app_url'), button['row'], button['col'])
                )
            print(f"    ✓ Created {len(state_data['buttons'])} buttons")
    
    print(f"\n✅ Successfully initialized {len(states)} bot states!")
    print("\nYou can now view and manage these states in the admin panel's Bot Constructor.")


async def main():
    """Main function"""
    try:
        await db.connect()
        await initialize_states()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
