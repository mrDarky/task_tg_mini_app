from database.db import db
from app.models import UserCreate, UserUpdate, User
from typing import Optional, List
from datetime import datetime


async def create_user(user: UserCreate) -> int:
    query = """
        INSERT INTO users (telegram_id, username, referral_code, stars, status, role)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor = await db.execute(query, (
        user.telegram_id, user.username, user.referral_code, user.stars, user.status, user.role
    ))
    return cursor.lastrowid


async def get_user(user_id: int) -> Optional[dict]:
    query = "SELECT * FROM users WHERE id = ?"
    row = await db.fetch_one(query, (user_id,))
    return dict(row) if row else None


async def get_user_by_telegram_id(telegram_id: int) -> Optional[dict]:
    query = "SELECT * FROM users WHERE telegram_id = ?"
    row = await db.fetch_one(query, (telegram_id,))
    return dict(row) if row else None


async def get_users(
    search: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    query = """
        SELECT u.*, COALESCE(us.language, 'en') as language
        FROM users u
        LEFT JOIN user_settings us ON u.id = us.user_id
        WHERE 1=1
    """
    params = []
    
    if search:
        query += " AND (u.username LIKE ? OR CAST(u.telegram_id AS TEXT) LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    if status:
        query += " AND u.status = ?"
        params.append(status)
    
    query += " ORDER BY u.id DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    rows = await db.fetch_all(query, tuple(params))
    return [dict(row) for row in rows]


async def count_users(search: Optional[str] = None, status: Optional[str] = None) -> int:
    query = "SELECT COUNT(*) as count FROM users WHERE 1=1"
    params = []
    
    if search:
        query += " AND (username LIKE ? OR CAST(telegram_id AS TEXT) LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    row = await db.fetch_one(query, tuple(params))
    return row['count'] if row else 0


async def update_user(user_id: int, user_update: UserUpdate) -> bool:
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        return False
    
    fields = []
    values = []
    for key, value in update_data.items():
        fields.append(f"{key} = ?")
        values.append(value)
    
    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(query, tuple(values))
    return True


async def delete_user(user_id: int) -> bool:
    query = "DELETE FROM users WHERE id = ?"
    await db.execute(query, (user_id,))
    return True


async def adjust_user_stars(user_id: int, stars_delta: int) -> bool:
    query = "UPDATE users SET stars = stars + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(query, (stars_delta, user_id))
    return True


async def ban_user(user_id: int) -> bool:
    query = "UPDATE users SET status = 'banned', updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(query, (user_id,))
    return True


async def unban_user(user_id: int) -> bool:
    query = "UPDATE users SET status = 'active', updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(query, (user_id,))
    return True


async def bulk_update_users(user_ids: List[int], update_data: dict) -> bool:
    if not user_ids or not update_data:
        return False
    
    fields = []
    values = []
    for key, value in update_data.items():
        fields.append(f"{key} = ?")
        values.append(value)
    
    placeholders = ','.join(['?' for _ in user_ids])
    values.extend(user_ids)
    query = f"UPDATE users SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders})"
    await db.execute(query, tuple(values))
    return True


async def ensure_referral_code(user_id: int, telegram_id: int) -> str:
    """Generate and assign a referral code if user doesn't have one"""
    import hashlib
    
    # Generate referral code
    hash_obj = hashlib.md5(f"{telegram_id}_{datetime.now().timestamp()}".encode())
    referral_code = hash_obj.hexdigest()[:8].upper()
    
    # Update user with referral code
    query = "UPDATE users SET referral_code = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(query, (referral_code, user_id))
    
    return referral_code
