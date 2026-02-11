from fastapi import APIRouter, Depends
from app.services import analytics_service
from app.models import DashboardStats, RecentActivity, SystemStatus
from app.auth import require_auth
from database.db import db
from datetime import datetime
from typing import List


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(username: str = Depends(require_auth)):
    stats = await analytics_service.get_dashboard_stats()
    return stats


@router.get("/recent-activity", response_model=List[RecentActivity])
async def get_recent_activity(limit: int = 20, username: str = Depends(require_auth)):
    """Get recent activity feed"""
    activities = []
    
    # Recent user registrations
    users = await db.fetch_all("""
        SELECT id, username, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit // 4,))
    
    for user in users:
        activities.append({
            "id": user['id'],
            "type": "user_registered",
            "description": f"User {user['username'] or user['id']} registered",
            "user_id": user['id'],
            "timestamp": user['created_at']
        })
    
    # Recent task completions
    completions = await db.fetch_all("""
        SELECT ut.id, ut.user_id, ut.created_at, t.title
        FROM user_tasks ut
        JOIN tasks t ON ut.task_id = t.id
        WHERE ut.status = 'completed'
        ORDER BY ut.created_at DESC
        LIMIT ?
    """, (limit // 4,))
    
    for comp in completions:
        activities.append({
            "id": comp['id'],
            "type": "task_completed",
            "description": f"User {comp['user_id']} completed task: {comp['title']}",
            "user_id": comp['user_id'],
            "timestamp": comp['created_at']
        })
    
    # Recent withdrawals
    withdrawals = await db.fetch_all("""
        SELECT id, user_id, amount, status, created_at
        FROM withdrawals
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit // 4,))
    
    for withdrawal in withdrawals:
        activities.append({
            "id": withdrawal['id'],
            "type": "withdrawal_requested",
            "description": f"User {withdrawal['user_id']} requested withdrawal of {withdrawal['amount']} stars",
            "user_id": withdrawal['user_id'],
            "timestamp": withdrawal['created_at']
        })
    
    # Sort all activities by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return activities[:limit]


@router.get("/system-status", response_model=SystemStatus)
async def get_system_status(username: str = Depends(require_auth)):
    """Get system status monitor"""
    # Check database
    db_status = "healthy"
    try:
        await db.fetch_one("SELECT 1")
    except:
        db_status = "error"
    
    # API is healthy if we reach this point
    api_status = "healthy"
    
    return {
        "database": db_status,
        "api": api_status,
        "bot": "unknown",  # Would need bot service integration
        "last_check": datetime.now()
    }
