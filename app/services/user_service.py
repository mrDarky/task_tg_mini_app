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


async def get_user_tasks(user_id: int, status: Optional[str] = None) -> List[dict]:
    """Get all tasks for a user, optionally filtered by status"""
    query = """
        SELECT 
            ut.id,
            ut.user_id,
            ut.task_id,
            ut.status,
            ut.completed_at,
            ut.created_at,
            t.title,
            t.description,
            t.type,
            t.url,
            t.reward
        FROM user_tasks ut
        JOIN tasks t ON ut.task_id = t.id
        WHERE ut.user_id = ?
    """
    params = [user_id]
    
    if status:
        query += " AND ut.status = ?"
        params.append(status)
    
    query += " ORDER BY ut.created_at DESC"
    
    rows = await db.fetch_all(query, params)
    return [dict(row) for row in rows]


async def get_user_achievements(user_id: int) -> List[dict]:
    """Get all achievements for a user with their earned status"""
    # First, ensure we have some default achievements
    await ensure_default_achievements()
    
    # Get all achievements with user's earned status
    query = """
        SELECT 
            a.id,
            a.name,
            a.description,
            a.icon,
            a.requirement_type,
            a.requirement_value,
            a.reward_stars,
            CASE WHEN ua.id IS NOT NULL THEN 1 ELSE 0 END as earned,
            ua.earned_at
        FROM achievements a
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
        ORDER BY earned DESC, a.id ASC
    """
    rows = await db.fetch_all(query, (user_id,))
    # Convert earned to boolean for better frontend compatibility
    return [dict(row) | {'earned': bool(row['earned'])} for row in rows]


async def ensure_default_achievements():
    """Ensure default achievements exist in the database"""
    # Check if achievements already exist
    check_query = "SELECT COUNT(*) as count FROM achievements"
    result = await db.fetch_one(check_query)
    
    if result and result['count'] > 0:
        return  # Achievements already exist
    
    # Insert default achievements
    default_achievements = [
        ("First Steps", "Complete your first task", "🌟", "tasks_completed", 1, 10),
        ("Task Master", "Complete 10 tasks", "🏆", "tasks_completed", 10, 50),
        ("Task Legend", "Complete 50 tasks", "👑", "tasks_completed", 50, 200),
        ("Social Butterfly", "Refer 5 friends", "👥", "referrals", 5, 100),
        ("Influencer", "Refer 20 friends", "📢", "referrals", 20, 500),
        ("Star Collector", "Earn 100 stars", "⭐", "stars_earned", 100, 0),
        ("Rich", "Earn 500 stars", "💎", "stars_earned", 500, 0),
        ("Consistent", "Claim daily bonus 7 days in a row", "🔥", "daily_streak", 7, 50),
    ]
    
    query = """
        INSERT INTO achievements (name, description, icon, requirement_type, requirement_value, reward_stars)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    for achievement in default_achievements:
        await db.execute(query, achievement)
