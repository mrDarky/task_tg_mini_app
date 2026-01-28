from database.db import db
from app.models import DashboardStats


async def get_dashboard_stats() -> DashboardStats:
    total_users_row = await db.fetch_one("SELECT COUNT(*) as count FROM users")
    total_users = total_users_row['count'] if total_users_row else 0
    
    active_users_row = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE status = 'active'")
    active_users = active_users_row['count'] if active_users_row else 0
    
    banned_users_row = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE status = 'banned'")
    banned_users = banned_users_row['count'] if banned_users_row else 0
    
    total_tasks_row = await db.fetch_one("SELECT COUNT(*) as count FROM tasks")
    total_tasks = total_tasks_row['count'] if total_tasks_row else 0
    
    active_tasks_row = await db.fetch_one("SELECT COUNT(*) as count FROM tasks WHERE status = 'active'")
    active_tasks = active_tasks_row['count'] if active_tasks_row else 0
    
    total_categories_row = await db.fetch_one("SELECT COUNT(*) as count FROM categories")
    total_categories = total_categories_row['count'] if total_categories_row else 0
    
    total_stars_row = await db.fetch_one("SELECT COALESCE(SUM(stars), 0) as total FROM users")
    total_stars_distributed = total_stars_row['total'] if total_stars_row else 0
    
    total_completions_row = await db.fetch_one("SELECT COUNT(*) as count FROM user_tasks WHERE status = 'completed'")
    total_completions = total_completions_row['count'] if total_completions_row else 0
    
    # Stars distributed today
    stars_today_row = await db.fetch_one("""
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM star_transactions 
        WHERE type = 'earned' AND DATE(created_at) = DATE('now')
    """)
    stars_today = stars_today_row['total'] if stars_today_row else 0
    
    # Stars distributed this week
    stars_week_row = await db.fetch_one("""
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM star_transactions 
        WHERE type = 'earned' AND created_at >= datetime('now', '-7 days')
    """)
    stars_week = stars_week_row['total'] if stars_week_row else 0
    
    # Stars distributed this month
    stars_month_row = await db.fetch_one("""
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM star_transactions 
        WHERE type = 'earned' AND created_at >= datetime('now', '-30 days')
    """)
    stars_month = stars_month_row['total'] if stars_month_row else 0
    
    # Calculate completion rate
    total_user_tasks_row = await db.fetch_one("SELECT COUNT(*) as count FROM user_tasks")
    total_user_tasks = total_user_tasks_row['count'] if total_user_tasks_row else 0
    completion_rate = (total_completions / total_user_tasks * 100) if total_user_tasks > 0 else 0.0
    
    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        banned_users=banned_users,
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        total_categories=total_categories,
        total_stars_distributed=total_stars_distributed,
        total_completions=total_completions,
        stars_today=stars_today,
        stars_week=stars_week,
        stars_month=stars_month,
        completion_rate=round(completion_rate, 2)
    )
