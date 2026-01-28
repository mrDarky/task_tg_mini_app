from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models import Notification, NotificationCreate
from database.db import db


router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=List[Notification])
async def list_notifications(
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
):
    """List notifications"""
    conditions = []
    params = []
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    offset = (page - 1) * per_page
    params.extend([per_page, offset])
    
    query = f"""
        SELECT * FROM notifications
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """
    
    rows = await db.fetch_all(query, tuple(params))
    return [dict(row) for row in rows]


@router.get("/{notification_id}", response_model=Notification)
async def get_notification(notification_id: int):
    """Get a specific notification"""
    query = "SELECT * FROM notifications WHERE id = ?"
    row = await db.fetch_one(query, (notification_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Notification not found")
    return dict(row)


@router.post("", response_model=Notification)
async def create_notification(notification: NotificationCreate, created_by: int):
    """Create a new notification"""
    query = """
        INSERT INTO notifications 
        (title, message, type, target_type, target_filter, created_by, status)
        VALUES (?, ?, ?, ?, ?, ?, 'draft')
    """
    cursor = await db.execute(
        query,
        (
            notification.title,
            notification.message,
            notification.type,
            notification.target_type,
            notification.target_filter,
            created_by
        )
    )
    notification_id = cursor.lastrowid
    
    # Fetch and return the created notification
    row = await db.fetch_one("SELECT * FROM notifications WHERE id = ?", (notification_id,))
    return dict(row)


@router.post("/{notification_id}/send")
async def send_notification(notification_id: int):
    """Send a notification to users"""
    notification = await db.fetch_one(
        "SELECT * FROM notifications WHERE id = ?",
        (notification_id,)
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Get target users based on target_type
    if notification['target_type'] == 'all':
        users = await db.fetch_all("SELECT id FROM users")
    elif notification['target_type'] == 'active':
        users = await db.fetch_all("SELECT id FROM users WHERE status = 'active'")
    elif notification['target_type'] == 'banned':
        users = await db.fetch_all("SELECT id FROM users WHERE status = 'banned'")
    else:
        users = []
    
    sent_count = len(users)
    
    # Update notification status
    await db.execute(
        """UPDATE notifications 
           SET status = 'sent', sent_count = ?, sent_at = CURRENT_TIMESTAMP 
           WHERE id = ?""",
        (sent_count, notification_id)
    )
    
    return {
        "message": "Notification sent successfully",
        "sent_count": sent_count
    }


@router.delete("/{notification_id}")
async def delete_notification(notification_id: int):
    """Delete a notification"""
    result = await db.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}
