from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
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
