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
    
    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        banned_users=banned_users,
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        total_categories=total_categories,
        total_stars_distributed=total_stars_distributed,
        total_completions=total_completions
    )
