from database.db import db
from app.models import UserCreate, UserUpdate, User
from typing import Optional, List
from datetime import datetime


def parse_iso_datetime(datetime_str: str) -> datetime:
    """Parse ISO datetime string, handling both Z and timezone offsets"""
    if not datetime_str:
        return None
    return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))


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
    
    # Generate referral code using SHA256 for better security
    hash_obj = hashlib.sha256(f"{telegram_id}_{datetime.now().timestamp()}".encode())
    referral_code = hash_obj.hexdigest()[:8].upper()
    
    # Update user with referral code
    query = "UPDATE users SET referral_code = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(query, (referral_code, user_id))
    
    return referral_code


async def get_user_referrals(user_id: int) -> List[dict]:
    """Get all referrals for a user"""
    query = """
        SELECT r.*, u.username, u.telegram_id, u.created_at as referred_at
        FROM referrals r
        JOIN users u ON r.referred_id = u.id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at DESC
    """
    rows = await db.fetch_all(query, (user_id,))
    return [dict(row) for row in rows]


async def get_daily_bonus_status(user_id: int) -> dict:
    """Get daily bonus status for a user"""
    from datetime import datetime, timedelta
    
    # Get the last bonus claim
    query = """
        SELECT * FROM daily_bonuses
        WHERE user_id = ?
        ORDER BY claimed_at DESC
        LIMIT 1
    """
    row = await db.fetch_one(query, (user_id,))
    
    if not row:
        # User has never claimed a bonus
        return {
            'can_claim': True,
            'last_claimed': None,
            'streak_count': 0,
            'next_bonus_amount': 10
        }
    
    last_claimed = parse_iso_datetime(row['claimed_at'])
    now = datetime.now()
    
    # Check if 24 hours have passed since last claim
    time_since_claim = now - last_claimed
    can_claim = time_since_claim.total_seconds() >= 86400  # 24 hours
    
    return {
        'can_claim': can_claim,
        'last_claimed': row['claimed_at'],
        'streak_count': row['streak_count'],
        'next_bonus_amount': 10 + (row['streak_count'] * 2) if can_claim else row['bonus_amount']
    }


async def claim_daily_bonus(user_id: int) -> dict:
    """Claim daily bonus for a user"""
    from datetime import datetime, timedelta
    
    # Check if user can claim
    bonus_status = await get_daily_bonus_status(user_id)
    
    if not bonus_status['can_claim']:
        return {
            'success': False,
            'message': 'Daily bonus already claimed today. Come back tomorrow!'
        }
    
    # Calculate streak
    last_claimed = bonus_status['last_claimed']
    streak_count = bonus_status['streak_count']
    
    if last_claimed:
        last_claimed_dt = parse_iso_datetime(last_claimed)
        time_since = datetime.now() - last_claimed_dt
        
        # If claimed within 48 hours, continue streak, otherwise reset
        if time_since.total_seconds() <= 172800:  # 48 hours
            streak_count += 1
        else:
            streak_count = 1
    else:
        streak_count = 1
    
    # Calculate bonus amount (base 10 + 2 per streak day, max 30)
    bonus_amount = min(10 + ((streak_count - 1) * 2), 30)
    
    # Create bonus record
    query = """
        INSERT INTO daily_bonuses (user_id, bonus_amount, streak_count)
        VALUES (?, ?, ?)
    """
    await db.execute(query, (user_id, bonus_amount, streak_count))
    
    # Award stars to user
    update_query = "UPDATE users SET stars = stars + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(update_query, (bonus_amount, user_id))
    
    # Log the transaction
    log_query = """
        INSERT INTO star_transactions (user_id, amount, type, reference_type, description)
        VALUES (?, ?, 'bonus', 'daily_bonus', ?)
    """
    await db.execute(log_query, (user_id, bonus_amount, f'Daily bonus - Day {streak_count}'))
    
    return {
        'success': True,
        'message': f'Daily bonus claimed! You earned {bonus_amount} stars!',
        'bonus_amount': bonus_amount,
        'streak_count': streak_count,
        'total_stars': (await get_user(user_id))['stars']
    }
