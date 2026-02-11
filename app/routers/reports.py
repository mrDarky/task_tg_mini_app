from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.auth import require_auth
from database.db import db
from datetime import datetime


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/daily-stats")
async def get_daily_stats(days: int = 30, username: str = Depends(require_auth)):
    """Get daily statistics for the last N days"""
    query = """
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as count
        FROM user_tasks
        WHERE status = 'completed' 
            AND created_at >= datetime('now', '-' || ? || ' days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    """
    rows = await db.fetch_all(query, (days,))
    return [{"date": row['date'], "completions": row['count']} for row in rows]


@router.get("/weekly-stats")
async def get_weekly_stats(weeks: int = 12, username: str = Depends(require_auth)):
    """Get weekly statistics"""
    query = """
        SELECT 
            strftime('%Y-W%W', created_at) as week,
            COUNT(*) as count,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completions
        FROM user_tasks
        WHERE created_at >= datetime('now', '-' || (? * 7) || ' days')
        GROUP BY week
        ORDER BY week DESC
    """
    rows = await db.fetch_all(query, (weeks,))
    return [
        {
            "week": row['week'],
            "total_tasks": row['count'],
            "completions": row['completions']
        } 
        for row in rows
    ]


@router.get("/monthly-stats")
async def get_monthly_stats(months: int = 12, username: str = Depends(require_auth)):
    """Get monthly statistics"""
    query = """
        SELECT 
            strftime('%Y-%m', created_at) as month,
            COUNT(*) as count,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completions
        FROM user_tasks
        WHERE created_at >= datetime('now', '-' || (? * 30) || ' days')
        GROUP BY month
        ORDER BY month DESC
    """
    rows = await db.fetch_all(query, (months,))
    return [
        {
            "month": row['month'],
            "total_tasks": row['count'],
            "completions": row['completions']
        } 
        for row in rows
    ]


@router.get("/user-engagement")
async def get_user_engagement(username: str = Depends(require_auth)):
    """Get user engagement metrics"""
    # Active users by period
    daily_active = await db.fetch_one("""
        SELECT COUNT(DISTINCT user_id) as count
        FROM user_tasks
        WHERE created_at >= datetime('now', '-1 day')
    """)
    
    weekly_active = await db.fetch_one("""
        SELECT COUNT(DISTINCT user_id) as count
        FROM user_tasks
        WHERE created_at >= datetime('now', '-7 days')
    """)
    
    monthly_active = await db.fetch_one("""
        SELECT COUNT(DISTINCT user_id) as count
        FROM user_tasks
        WHERE created_at >= datetime('now', '-30 days')
    """)
    
    # User retention
    total_users = await db.fetch_one("SELECT COUNT(*) as count FROM users")
    
    return {
        "daily_active_users": daily_active['count'],
        "weekly_active_users": weekly_active['count'],
        "monthly_active_users": monthly_active['count'],
        "total_users": total_users['count'],
        "engagement_rate": {
            "daily": round(daily_active['count'] / total_users['count'] * 100, 2) if total_users['count'] > 0 else 0,
            "weekly": round(weekly_active['count'] / total_users['count'] * 100, 2) if total_users['count'] > 0 else 0,
            "monthly": round(monthly_active['count'] / total_users['count'] * 100, 2) if total_users['count'] > 0 else 0
        }
    }


@router.get("/task-completion-heatmap")
async def get_task_completion_heatmap(username: str = Depends(require_auth)):
    """Get task completion data for heatmap visualization"""
    query = """
        SELECT 
            strftime('%w', completed_at) as day_of_week,
            strftime('%H', completed_at) as hour_of_day,
            COUNT(*) as count
        FROM user_tasks
        WHERE status = 'completed'
            AND completed_at IS NOT NULL
            AND completed_at >= datetime('now', '-90 days')
        GROUP BY day_of_week, hour_of_day
        ORDER BY day_of_week, hour_of_day
    """
    rows = await db.fetch_all(query)
    return [
        {
            "day_of_week": int(row['day_of_week']),
            "hour": int(row['hour_of_day']),
            "completions": row['count']
        }
        for row in rows
    ]


@router.get("/reward-trends")
async def get_reward_trends(username: str = Depends(require_auth)):
    """Get reward distribution trends"""
    # Stars distributed over time
    query = """
        SELECT 
            DATE(created_at) as date,
            SUM(amount) as total_stars,
            COUNT(*) as transaction_count
        FROM star_transactions
        WHERE type = 'earned'
            AND created_at >= datetime('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    """
    rows = await db.fetch_all(query)
    
    # Top earning users
    top_earners = await db.fetch_all("""
        SELECT 
            u.id,
            u.username,
            u.stars,
            COUNT(ut.id) as tasks_completed
        FROM users u
        LEFT JOIN user_tasks ut ON u.id = ut.user_id AND ut.status = 'completed'
        GROUP BY u.id
        ORDER BY u.stars DESC
        LIMIT 10
    """)
    
    return {
        "daily_distribution": [
            {
                "date": row['date'],
                "total_stars": row['total_stars'],
                "transaction_count": row['transaction_count']
            }
            for row in rows
        ],
        "top_earners": [
            {
                "user_id": row['id'],
                "username": row['username'] or f"User {row['id']}",
                "total_stars": row['stars'],
                "tasks_completed": row['tasks_completed']
            }
            for row in top_earners
        ]
    }


@router.get("/task-performance")
async def get_task_performance(username: str = Depends(require_auth)):
    """Get performance metrics for each task"""
    query = """
        SELECT 
            t.id,
            t.title,
            t.type,
            t.reward,
            COUNT(ut.id) as attempt_count,
            SUM(CASE WHEN ut.status = 'completed' THEN 1 ELSE 0 END) as completion_count,
            ROUND(
                CAST(SUM(CASE WHEN ut.status = 'completed' THEN 1 ELSE 0 END) AS FLOAT) / 
                CAST(COUNT(ut.id) AS FLOAT) * 100, 
                2
            ) as completion_rate
        FROM tasks t
        LEFT JOIN user_tasks ut ON t.id = ut.task_id
        GROUP BY t.id
        HAVING attempt_count > 0
        ORDER BY completion_rate DESC
    """
    rows = await db.fetch_all(query)
    return [
        {
            "task_id": row['id'],
            "title": row['title'],
            "type": row['type'],
            "reward": row['reward'],
            "attempts": row['attempt_count'],
            "completions": row['completion_count'],
            "completion_rate": row['completion_rate'] or 0
        }
        for row in rows
    ]


@router.get("/category-analytics")
async def get_category_analytics(username: str = Depends(require_auth)):
    """Get analytics for categories"""
    query = """
        SELECT 
            c.id,
            c.name,
            COUNT(DISTINCT t.id) as task_count,
            COUNT(ut.id) as total_attempts,
            SUM(CASE WHEN ut.status = 'completed' THEN 1 ELSE 0 END) as completions
        FROM categories c
        LEFT JOIN tasks t ON c.id = t.category_id
        LEFT JOIN user_tasks ut ON t.id = ut.task_id
        GROUP BY c.id
        ORDER BY completions DESC
    """
    rows = await db.fetch_all(query)
    return [
        {
            "category_id": row['id'],
            "name": row['name'],
            "task_count": row['task_count'],
            "total_attempts": row['total_attempts'],
            "completions": row['completions']
        }
        for row in rows
    ]
