from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models import Setting, SettingCreate, SettingUpdate
from database.db import db


router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=List[Setting])
async def list_settings(category: Optional[str] = None):
    """List all settings, optionally filtered by category"""
    if category:
        query = "SELECT * FROM settings WHERE category = ? ORDER BY key"
        rows = await db.fetch_all(query, (category,))
    else:
        query = "SELECT * FROM settings ORDER BY category, key"
        rows = await db.fetch_all(query)
    
    return [dict(row) for row in rows]


@router.get("/{key}", response_model=Setting)
async def get_setting(key: str):
    """Get a specific setting by key"""
    query = "SELECT * FROM settings WHERE key = ?"
    row = await db.fetch_one(query, (key,))
    if not row:
        raise HTTPException(status_code=404, detail="Setting not found")
    return dict(row)


@router.post("", response_model=Setting)
async def create_setting(setting: SettingCreate):
    """Create a new setting"""
    query = """
        INSERT INTO settings (key, value, category, description)
        VALUES (?, ?, ?, ?)
    """
    try:
        cursor = await db.execute(
            query,
            (setting.key, setting.value, setting.category, setting.description)
        )
        setting_id = cursor.lastrowid
        
        # Fetch and return the created setting
        row = await db.fetch_one("SELECT * FROM settings WHERE id = ?", (setting_id,))
        return dict(row)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create setting: {str(e)}")


@router.put("/{key}", response_model=Setting)
async def update_setting(key: str, setting: SettingUpdate):
    """Update an existing setting"""
    # Check if setting exists
    existing = await db.fetch_one("SELECT * FROM settings WHERE key = ?", (key,))
    if not existing:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    # Build update query dynamically
    updates = []
    params = []
    
    if setting.value is not None:
        updates.append("value = ?")
        params.append(setting.value)
    if setting.category is not None:
        updates.append("category = ?")
        params.append(setting.category)
    if setting.description is not None:
        updates.append("description = ?")
        params.append(setting.description)
    
    if not updates:
        return dict(existing)
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(key)
    
    query = f"UPDATE settings SET {', '.join(updates)} WHERE key = ?"
    await db.execute(query, tuple(params))
    
    # Fetch and return updated setting
    row = await db.fetch_one("SELECT * FROM settings WHERE key = ?", (key,))
    return dict(row)


@router.delete("/{key}")
async def delete_setting(key: str):
    """Delete a setting"""
    result = await db.execute("DELETE FROM settings WHERE key = ?", (key,))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"message": "Setting deleted successfully"}
