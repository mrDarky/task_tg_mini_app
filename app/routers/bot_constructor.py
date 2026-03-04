from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from database.db import db
from app.auth import require_auth
from datetime import datetime, timezone

router = APIRouter(prefix="/api/bot-constructor", tags=["bot-constructor"])


class BotButtonCreate(BaseModel):
    text: str
    button_type: str = "callback"
    callback_data: Optional[str] = None
    url: Optional[str] = None
    web_app_url: Optional[str] = None
    target_state_id: Optional[int] = None
    row_position: int = 0
    col_position: int = 0


class BotButtonUpdate(BaseModel):
    text: Optional[str] = None
    button_type: Optional[str] = None
    callback_data: Optional[str] = None
    url: Optional[str] = None
    web_app_url: Optional[str] = None
    target_state_id: Optional[int] = None
    row_position: Optional[int] = None
    col_position: Optional[int] = None


class BotStateCreate(BaseModel):
    state_key: str
    name: str
    message_text: str
    is_start_state: bool = False
    x_position: int = 0
    y_position: int = 0


class BotStateUpdate(BaseModel):
    state_key: Optional[str] = None
    name: Optional[str] = None
    message_text: Optional[str] = None
    is_start_state: Optional[bool] = None
    x_position: Optional[int] = None
    y_position: Optional[int] = None


class StateTranslationsUpdate(BaseModel):
    translations: Dict[str, str]  # {language_code: message_text}


class ButtonTranslationsUpdate(BaseModel):
    translations: Dict[str, str]  # {language_code: text}


class AutoTranslateRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str


@router.post("/auto-translate")
async def auto_translate(data: AutoTranslateRequest, username: str = Depends(require_auth)):
    """Translate text using Google Translate free API, preserving {variable} placeholders"""
    import re
    import urllib.request
    import urllib.parse
    import json
    import asyncio

    text = data.text
    source_lang = data.source_lang.strip()
    target_lang = data.target_lang.strip()

    if not text.strip():
        return {"translated": ""}

    if source_lang == target_lang:
        return {"translated": text}

    # Extract {variable} placeholders and replace with safe tokens
    placeholders = re.findall(r'\{[^}]+\}', text)
    protected_text = text
    for i, ph in enumerate(placeholders):
        protected_text = protected_text.replace(ph, f'__PH{i}__', 1)

    def do_translate(src: str, tgt: str, q: str) -> str:
        url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl={urllib.parse.quote(src)}"
            f"&tl={urllib.parse.quote(tgt)}&dt=t&q={urllib.parse.quote(q)}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return "".join(seg[0] for seg in result[0] if seg[0])

    try:
        loop = asyncio.get_running_loop()
        translated = await loop.run_in_executor(None, do_translate, source_lang, target_lang, protected_text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Translation failed: {str(e)}")

    # Restore {variable} placeholders (handle spaces Google may insert around tokens)
    for i, ph in enumerate(placeholders):
        token = f'__PH{i}__'
        translated = re.sub(r'\s*' + re.escape(token) + r'\s*', ph, translated)

    return {"translated": translated}


@router.get("/states")
async def get_all_states(username: str = Depends(require_auth)):
    """Get all bot states with their buttons"""
    states = await db.fetch_all("""
        SELECT * FROM bot_states 
        ORDER BY is_start_state DESC, created_at ASC
    """)
    
    result = []
    for state in states:
        buttons = await db.fetch_all(
            """SELECT * FROM bot_buttons 
               WHERE state_id = ? 
               ORDER BY row_position, col_position""",
            (state['id'],)
        )
        
        result.append({
            'id': state['id'],
            'state_key': state['state_key'],
            'name': state['name'],
            'message_text': state['message_text'],
            'is_start_state': bool(state['is_start_state']),
            'x_position': state['x_position'],
            'y_position': state['y_position'],
            'buttons': [dict(btn) for btn in buttons]
        })
    
    return result


@router.get("/states/{state_id}")
async def get_state(state_id: int, username: str = Depends(require_auth)):
    """Get a specific bot state with its buttons"""
    state = await db.fetch_one("SELECT * FROM bot_states WHERE id = ?", (state_id,))
    
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    buttons = await db.fetch_all(
        """SELECT * FROM bot_buttons 
           WHERE state_id = ? 
           ORDER BY row_position, col_position""",
        (state_id,)
    )
    
    return {
        'id': state['id'],
        'state_key': state['state_key'],
        'name': state['name'],
        'message_text': state['message_text'],
        'is_start_state': bool(state['is_start_state']),
        'x_position': state['x_position'],
        'y_position': state['y_position'],
        'buttons': [dict(btn) for btn in buttons]
    }


@router.post("/states")
async def create_state(state: BotStateCreate, username: str = Depends(require_auth)):
    """Create a new bot state"""
    try:
        # If this is marked as start state, unmark all others
        if state.is_start_state:
            await db.execute("UPDATE bot_states SET is_start_state = 0")
        
        cursor = await db.execute(
            """INSERT INTO bot_states 
               (state_key, name, message_text, is_start_state, x_position, y_position) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (state.state_key, state.name, state.message_text, 
             state.is_start_state, state.x_position, state.y_position)
        )
        
        state_id = cursor.lastrowid
        return await get_state(state_id, username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/states/{state_id}")
async def update_state(
    state_id: int, 
    state: BotStateUpdate, 
    username: str = Depends(require_auth)
):
    """Update a bot state"""
    existing = await db.fetch_one("SELECT * FROM bot_states WHERE id = ?", (state_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="State not found")
    
    # If this is marked as start state, unmark all others
    if state.is_start_state:
        await db.execute("UPDATE bot_states SET is_start_state = 0")
    
    # Build update query dynamically
    # Note: Column names are hardcoded and never derived from user input
    updates = []
    params = []
    
    if state.state_key is not None:
        updates.append("state_key = ?")
        params.append(state.state_key)
    if state.name is not None:
        updates.append("name = ?")
        params.append(state.name)
    if state.message_text is not None:
        updates.append("message_text = ?")
        params.append(state.message_text)
    if state.is_start_state is not None:
        updates.append("is_start_state = ?")
        params.append(state.is_start_state)
    if state.x_position is not None:
        updates.append("x_position = ?")
        params.append(state.x_position)
    if state.y_position is not None:
        updates.append("y_position = ?")
        params.append(state.y_position)
    
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())
        params.append(state_id)
        
        await db.execute(
            f"UPDATE bot_states SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
    
    return await get_state(state_id, username)


@router.delete("/states/{state_id}")
async def delete_state(state_id: int, username: str = Depends(require_auth)):
    """Delete a bot state"""
    existing = await db.fetch_one("SELECT * FROM bot_states WHERE id = ?", (state_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="State not found")
    
    await db.execute("DELETE FROM bot_states WHERE id = ?", (state_id,))
    return {"message": "State deleted successfully"}


@router.post("/states/{state_id}/buttons")
async def create_button(
    state_id: int, 
    button: BotButtonCreate, 
    username: str = Depends(require_auth)
):
    """Create a new button for a state"""
    state = await db.fetch_one("SELECT * FROM bot_states WHERE id = ?", (state_id,))
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    cursor = await db.execute(
        """INSERT INTO bot_buttons 
           (state_id, text, button_type, callback_data, url, web_app_url, 
            target_state_id, row_position, col_position) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (state_id, button.text, button.button_type, button.callback_data,
         button.url, button.web_app_url, button.target_state_id,
         button.row_position, button.col_position)
    )
    
    button_id = cursor.lastrowid
    new_button = await db.fetch_one("SELECT * FROM bot_buttons WHERE id = ?", (button_id,))
    return dict(new_button)


@router.put("/buttons/{button_id}")
async def update_button(
    button_id: int, 
    button: BotButtonUpdate, 
    username: str = Depends(require_auth)
):
    """Update a button"""
    existing = await db.fetch_one("SELECT * FROM bot_buttons WHERE id = ?", (button_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Button not found")
    
    # Build update query dynamically
    # Note: Column names are hardcoded and never derived from user input
    updates = []
    params = []
    
    if button.text is not None:
        updates.append("text = ?")
        params.append(button.text)
    if button.button_type is not None:
        updates.append("button_type = ?")
        params.append(button.button_type)
    if button.callback_data is not None:
        updates.append("callback_data = ?")
        params.append(button.callback_data)
    if button.url is not None:
        updates.append("url = ?")
        params.append(button.url)
    if button.web_app_url is not None:
        updates.append("web_app_url = ?")
        params.append(button.web_app_url)
    if button.target_state_id is not None:
        updates.append("target_state_id = ?")
        params.append(button.target_state_id)
    if button.row_position is not None:
        updates.append("row_position = ?")
        params.append(button.row_position)
    if button.col_position is not None:
        updates.append("col_position = ?")
        params.append(button.col_position)
    
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())
        params.append(button_id)
        
        await db.execute(
            f"UPDATE bot_buttons SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
    
    updated_button = await db.fetch_one("SELECT * FROM bot_buttons WHERE id = ?", (button_id,))
    return dict(updated_button)


@router.delete("/buttons/{button_id}")
async def delete_button(button_id: int, username: str = Depends(require_auth)):
    """Delete a button"""
    existing = await db.fetch_one("SELECT * FROM bot_buttons WHERE id = ?", (button_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Button not found")
    
    await db.execute("DELETE FROM bot_buttons WHERE id = ?", (button_id,))
    return {"message": "Button deleted successfully"}


@router.get("/states/{state_id}/translations")
async def get_state_translations(state_id: int, username: str = Depends(require_auth)):
    """Get per-language message text translations for a state"""
    state = await db.fetch_one("SELECT id FROM bot_states WHERE id = ?", (state_id,))
    if not state:
        raise HTTPException(status_code=404, detail="State not found")

    rows = await db.fetch_all(
        "SELECT language_code, message_text FROM bot_state_translations WHERE state_id = ?",
        (state_id,)
    )
    return {row['language_code']: row['message_text'] for row in rows}


@router.put("/states/{state_id}/translations")
async def update_state_translations(
    state_id: int,
    data: StateTranslationsUpdate,
    username: str = Depends(require_auth)
):
    """Save per-language message text translations for a state"""
    state = await db.fetch_one("SELECT id FROM bot_states WHERE id = ?", (state_id,))
    if not state:
        raise HTTPException(status_code=404, detail="State not found")

    for lang_code, message_text in data.translations.items():
        await db.execute(
            """INSERT INTO bot_state_translations (state_id, language_code, message_text)
               VALUES (?, ?, ?)
               ON CONFLICT(state_id, language_code) DO UPDATE SET
               message_text = excluded.message_text,
               updated_at = CURRENT_TIMESTAMP""",
            (state_id, lang_code, message_text)
        )

    return {"message": "State translations saved successfully"}


@router.get("/buttons/{button_id}/translations")
async def get_button_translations(button_id: int, username: str = Depends(require_auth)):
    """Get per-language text translations for a button"""
    button = await db.fetch_one("SELECT id FROM bot_buttons WHERE id = ?", (button_id,))
    if not button:
        raise HTTPException(status_code=404, detail="Button not found")

    rows = await db.fetch_all(
        "SELECT language_code, text FROM bot_button_translations WHERE button_id = ?",
        (button_id,)
    )
    return {row['language_code']: row['text'] for row in rows}


@router.put("/buttons/{button_id}/translations")
async def update_button_translations(
    button_id: int,
    data: ButtonTranslationsUpdate,
    username: str = Depends(require_auth)
):
    """Save per-language text translations for a button"""
    button = await db.fetch_one("SELECT id FROM bot_buttons WHERE id = ?", (button_id,))
    if not button:
        raise HTTPException(status_code=404, detail="Button not found")

    for lang_code, text in data.translations.items():
        await db.execute(
            """INSERT INTO bot_button_translations (button_id, language_code, text)
               VALUES (?, ?, ?)
               ON CONFLICT(button_id, language_code) DO UPDATE SET
               text = excluded.text,
               updated_at = CURRENT_TIMESTAMP""",
            (button_id, lang_code, text)
        )

    return {"message": "Button translations saved successfully"}


@router.get("/variables")
async def get_available_variables(username: str = Depends(require_auth)):
    """Get list of available variables that can be used in messages"""
    return {
        "variables": [
            {
                "key": "{username}",
                "description": "User's username"
            },
            {
                "key": "{first_name}",
                "description": "User's first name"
            },
            {
                "key": "{stars_count}",
                "description": "User's star balance"
            },
            {
                "key": "{stars}",
                "description": "User's star balance (alias)"
            },
            {
                "key": "{referral_code}",
                "description": "User's referral code"
            },
            {
                "key": "{referral_link}",
                "description": "User's referral link"
            },
            {
                "key": "{completed_tasks}",
                "description": "Number of completed tasks"
            },
            {
                "key": "{telegram_id}",
                "description": "User's Telegram ID"
            }
        ]
    }


def get_default_states_data():
    """Get the default bot states structure"""
    return [
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


@router.get("/default-states")
async def get_default_states(username: str = Depends(require_auth)):
    """Get default bot states structure for preview"""
    states = get_default_states_data()
    return {
        "states": states,
        "total_states": len(states),
        "total_buttons": sum(len(s.get('buttons', [])) for s in states)
    }


@router.post("/generate-default-states")
async def generate_default_states(username: str = Depends(require_auth)):
    """Generate default bot states in the database"""
    try:
        # Check if states already exist
        existing_states = await db.fetch_all("SELECT * FROM bot_states")
        
        # Clear existing states if any (cascade will delete buttons too)
        if existing_states:
            await db.execute("DELETE FROM bot_states")
        
        # Get default states
        states = get_default_states_data()
        created_states = []
        
        # Create each state
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
            
            # Insert buttons
            buttons = []
            if 'buttons' in state_data:
                for button in state_data['buttons']:
                    btn_cursor = await db.execute(
                        """INSERT INTO bot_buttons 
                           (state_id, text, button_type, callback_data, url, web_app_url, 
                            target_state_id, row_position, col_position) 
                           VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)""",
                        (state_id, button['text'], button['button_type'], 
                         button.get('callback_data'), button.get('url'), 
                         button.get('web_app_url'), button['row'], button['col'])
                    )
                    buttons.append({
                        'id': btn_cursor.lastrowid,
                        'text': button['text'],
                        'button_type': button['button_type']
                    })
            
            created_states.append({
                'id': state_id,
                'name': state_data['name'],
                'state_key': state_data['state_key'],
                'button_count': len(buttons)
            })
        
        return {
            "message": "Default states generated successfully",
            "states_created": len(created_states),
            "states": created_states
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating states: {str(e)}")


@router.post("/apply-to-bot")
async def apply_to_bot(username: str = Depends(require_auth)):
    """
    Apply constructor changes to the bot.
    Reads all states from the database and persists them into bot_config.json
    so that the running bot picks up the updated messages and keyboard layouts.
    Also clears the in-memory config cache so changes are visible immediately.
    """
    try:
        from bot.constructor import reload_bot_config
        import json
        from pathlib import Path

        # Fetch all states with buttons
        states = await db.fetch_all(
            "SELECT * FROM bot_states ORDER BY is_start_state DESC, created_at ASC"
        )

        states_config: dict = {}
        for state in states:
            buttons = await db.fetch_all(
                "SELECT * FROM bot_buttons WHERE state_id = ? ORDER BY row_position, col_position",
                (state['id'],)
            )
            states_config[state['state_key']] = {
                'message_text': state['message_text'],
                'buttons': [dict(btn) for btn in buttons]
            }

        # Load existing config and update the 'states' section
        config_file = Path(__file__).parent.parent.parent / "bot" / "bot_config.json"
        existing_config: dict = {}
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
            except Exception:
                existing_config = {}

        existing_config['states'] = states_config

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)

        # Clear in-memory cache so bot picks up new config immediately
        reload_bot_config()

        return {
            "message": "Changes applied to bot successfully",
            "states_updated": len(states_config)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying changes: {str(e)}")
