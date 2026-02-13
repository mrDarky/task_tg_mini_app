#!/usr/bin/env python3
"""
Test script to verify the Bot Constructor module works correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_message_constructors():
    """Test all message constructor methods"""
    from bot.constructor import messages
    
    print("Testing Message Constructors...")
    
    # Test welcome messages
    welcome_new = messages.welcome_new_user("John", 0, "https://t.me/bot?start=ABC", 'en')
    assert "Welcome" in welcome_new
    print("  ✓ welcome_new_user")
    
    welcome_back = messages.welcome_back("John", 100, "https://t.me/bot?start=ABC", 'en')
    assert "Welcome back" in welcome_back
    print("  ✓ welcome_back")
    
    welcome_referred = messages.welcome_referred("John", 50, 50, "https://t.me/bot?start=ABC", 'en')
    assert "referred" in welcome_referred.lower()
    print("  ✓ welcome_referred")
    
    # Test task messages
    task_categories = messages.task_categories('en')
    assert "Task Categories" in task_categories or "categories" in task_categories.lower()
    print("  ✓ task_categories")
    
    # Test profile message
    user_data = {
        'username': 'testuser',
        'stars': 100,
        'status': 'active',
        'created_at': '2024-01-01'
    }
    stats = {
        'completed': 5,
        'referrals': 2,
        'achievements': 3
    }
    profile = messages.profile_message(user_data, stats, 'en')
    assert "Profile" in profile
    print("  ✓ profile_message")
    
    # Test task detail message
    task = {
        'title': 'Watch Video',
        'description': 'Watch a YouTube video',
        'reward': 10,
        'type': 'youtube'
    }
    task_detail = messages.task_detail_message(task, 'en')
    assert "Watch Video" in task_detail
    print("  ✓ task_detail_message")
    
    # Test daily bonus message
    bonus = messages.daily_bonus_message(10, 5, 'en')
    assert "10" in bonus
    print("  ✓ daily_bonus_message")
    
    # Test referral stats message
    referral = messages.referral_stats_message(5, 250, 'en')
    assert "5" in referral
    print("  ✓ referral_stats_message")
    
    # Test settings message
    settings_data = {
        'notifications_enabled': True,
        'task_notifications': True,
        'reward_notifications': False,
        'language': 'en'
    }
    settings_msg = messages.settings_message(settings_data, 'en')
    assert "Settings" in settings_msg
    print("  ✓ settings_message")
    
    # Test help message
    help_msg = messages.help_message('en')
    assert "Help" in help_msg or "help" in help_msg.lower()
    print("  ✓ help_message")
    
    # Test error messages
    error = messages.error_message('please_start', 'en')
    assert len(error) > 0
    print("  ✓ error_message")
    
    print("✅ All message constructors passed!")


def test_button_constructors():
    """Test all button constructor methods"""
    from bot.constructor import buttons
    
    print("\nTesting Button Constructors...")
    
    # Test main buttons
    web_app = buttons.web_app_button("http://localhost:8000/miniapp", 'en')
    assert web_app.web_app is not None
    print("  ✓ web_app_button")
    
    view_tasks = buttons.view_tasks_button('en')
    assert view_tasks.callback_data == "view_tasks"
    print("  ✓ view_tasks_button")
    
    profile = buttons.my_profile_button('en')
    assert profile.callback_data == "my_profile"
    print("  ✓ my_profile_button")
    
    daily_bonus = buttons.daily_bonus_button('en')
    assert daily_bonus.callback_data == "daily_bonus"
    print("  ✓ daily_bonus_button")
    
    help_btn = buttons.help_button('en')
    assert help_btn.callback_data == "help"
    print("  ✓ help_button")
    
    settings = buttons.settings_button('en')
    assert settings.callback_data == "settings"
    print("  ✓ settings_button")
    
    back = buttons.back_button('en')
    assert back.callback_data == "back_to_menu"
    print("  ✓ back_button")
    
    # Test dynamic buttons
    category = buttons.category_button(123, "YouTube")
    assert category.callback_data == "category_123"
    assert "YouTube" in category.text
    print("  ✓ category_button")
    
    task_detail = buttons.task_detail_button(456, "Watch Video")
    assert task_detail.callback_data == "task_detail_456"
    print("  ✓ task_detail_button")
    
    complete = buttons.complete_task_button(789, 'en')
    assert complete.callback_data == "complete_789"
    print("  ✓ complete_task_button")
    
    submit = buttons.submit_task_button(789, 'en')
    assert submit.callback_data == "submit_task_789"
    print("  ✓ submit_task_button")
    
    # Test settings buttons
    achievements = buttons.view_achievements_button('en')
    assert achievements.callback_data == "view_achievements"
    print("  ✓ view_achievements_button")
    
    referral_stats = buttons.referral_stats_button('en')
    assert referral_stats.callback_data == "referral_stats"
    print("  ✓ referral_stats_button")
    
    star_history = buttons.star_history_button('en')
    assert star_history.callback_data == "star_history"
    print("  ✓ star_history_button")
    
    change_lang = buttons.change_language_button('en')
    assert change_lang.callback_data == "change_language"
    print("  ✓ change_language_button")
    
    lang_select = buttons.language_selection_button('ru', 'Русский')
    assert lang_select.callback_data == "lang_ru"
    print("  ✓ language_selection_button")
    
    # Test toggle buttons
    toggle_notif = buttons.toggle_notifications_button(True, 'en')
    assert toggle_notif.callback_data == "toggle_notifications"
    assert "✅" in toggle_notif.text
    print("  ✓ toggle_notifications_button")
    
    toggle_task = buttons.toggle_task_notif_button(False, 'en')
    assert toggle_task.callback_data == "toggle_task_notif"
    assert "❌" in toggle_task.text
    print("  ✓ toggle_task_notif_button")
    
    toggle_reward = buttons.toggle_reward_notif_button(True, 'en')
    assert toggle_reward.callback_data == "toggle_reward_notif"
    print("  ✓ toggle_reward_notif_button")
    
    # Test help buttons
    help_tasks = buttons.help_tasks_button('en')
    assert help_tasks.callback_data == "help_tasks"
    print("  ✓ help_tasks_button")
    
    help_stars = buttons.help_stars_button('en')
    assert help_stars.callback_data == "help_stars"
    print("  ✓ help_stars_button")
    
    help_referrals = buttons.help_referrals_button('en')
    assert help_referrals.callback_data == "help_referrals"
    print("  ✓ help_referrals_button")
    
    help_support = buttons.help_support_button('en')
    assert help_support.callback_data == "help_support"
    print("  ✓ help_support_button")
    
    create_ticket = buttons.create_ticket_button('en')
    assert create_ticket.callback_data == "create_ticket"
    print("  ✓ create_ticket_button")
    
    print("✅ All button constructors passed!")


def test_keyboard_constructors():
    """Test all keyboard constructor methods"""
    from bot.constructor import keyboards
    
    print("\nTesting Keyboard Constructors...")
    
    # Test main menu keyboard
    main_menu = keyboards.main_menu_keyboard("http://localhost:8000/miniapp", 'en')
    assert len(main_menu.inline_keyboard) >= 4
    print("  ✓ main_menu_keyboard")
    
    # Test categories keyboard
    categories = [
        {'id': 1, 'name': 'YouTube'},
        {'id': 2, 'name': 'TikTok'}
    ]
    categories_kb = keyboards.categories_keyboard(categories, 'en')
    assert len(categories_kb.inline_keyboard) == 3  # 2 categories + back button
    print("  ✓ categories_keyboard")
    
    # Test tasks list keyboard
    tasks = [
        {'id': 1, 'title': 'Task 1', 'reward': 10},
        {'id': 2, 'title': 'Task 2', 'reward': 20}
    ]
    tasks_kb = keyboards.tasks_list_keyboard(tasks, 'en')
    assert len(tasks_kb.inline_keyboard) == 3  # 2 tasks + back button
    print("  ✓ tasks_list_keyboard")
    
    # Test task detail keyboard
    task_detail_kb = keyboards.task_detail_keyboard(123, 'en')
    assert len(task_detail_kb.inline_keyboard) >= 2
    # Verify correct task_id is in callback_data
    assert task_detail_kb.inline_keyboard[0][0].callback_data == "complete_123"
    print("  ✓ task_detail_keyboard")
    
    # Test profile keyboard
    profile_kb = keyboards.profile_keyboard('en')
    assert len(profile_kb.inline_keyboard) >= 4
    print("  ✓ profile_keyboard")
    
    # Test settings keyboard
    settings_data = {
        'notifications_enabled': True,
        'task_notifications': True,
        'reward_notifications': False
    }
    settings_kb = keyboards.settings_keyboard(settings_data, 'en')
    assert len(settings_kb.inline_keyboard) >= 5
    print("  ✓ settings_keyboard")
    
    # Test language selection keyboard
    lang_kb = keyboards.language_selection_keyboard('en')
    assert len(lang_kb.inline_keyboard) >= 4  # 3 languages + back
    print("  ✓ language_selection_keyboard")
    
    # Test help keyboard
    help_kb = keyboards.help_keyboard('en')
    assert len(help_kb.inline_keyboard) >= 5
    print("  ✓ help_keyboard")
    
    # Test simple keyboards
    back_kb = keyboards.back_keyboard('en')
    assert len(back_kb.inline_keyboard) == 1
    print("  ✓ back_keyboard")
    
    referral_kb = keyboards.referral_stats_keyboard('en')
    assert len(referral_kb.inline_keyboard) == 1
    print("  ✓ referral_stats_keyboard")
    
    star_kb = keyboards.star_history_keyboard('en')
    assert len(star_kb.inline_keyboard) == 1
    print("  ✓ star_history_keyboard")
    
    print("✅ All keyboard constructors passed!")


def test_multilanguage_support():
    """Test multilanguage support"""
    from bot.constructor import messages, buttons, keyboards
    
    print("\nTesting Multilanguage Support...")
    
    languages = ['en', 'ru', 'es']
    
    for lang in languages:
        # Test message
        msg = messages.welcome_back("Test", 100, "link", lang)
        assert len(msg) > 0
        
        # Test button
        btn = buttons.view_tasks_button(lang)
        assert btn.callback_data == "view_tasks"
        
        # Test keyboard
        kb = keyboards.main_menu_keyboard("http://localhost:8000/miniapp", lang)
        assert len(kb.inline_keyboard) >= 4
        
        print(f"  ✓ {lang} language support")
    
    print("✅ All multilanguage tests passed!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Bot Constructor Module Tests")
    print("=" * 60)
    
    try:
        test_message_constructors()
        test_button_constructors()
        test_keyboard_constructors()
        test_multilanguage_support()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
