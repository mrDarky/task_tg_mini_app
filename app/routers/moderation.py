from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.models import ModerationLog, ModerationLogCreate
from app.auth import require_auth
from database.db import db


router = APIRouter(prefix="/api/moderation", tags=["moderation"])


@router.get("/logs", response_model=List[ModerationLog])
async def list_moderation_logs(
    admin_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
    username: str = Depends(require_auth)
):
    """List moderation logs with optional filters"""
    conditions = []
    params = []
    
    if admin_id:
        conditions.append("admin_id = ?")
        params.append(admin_id)
    if entity_type:
        conditions.append("entity_type = ?")
        params.append(entity_type)
    if action:
        conditions.append("action = ?")
        params.append(action)
    
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    offset = (page - 1) * per_page
    params.extend([per_page, offset])
    
    query = f"""
        SELECT * FROM moderation_logs
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """
    
    rows = await db.fetch_all(query, tuple(params))
    return [dict(row) for row in rows]


@router.post("/logs", response_model=ModerationLog)
async def create_moderation_log(log: ModerationLogCreate, username: str = Depends(require_auth)):
    """Create a new moderation log entry"""
    query = """
        INSERT INTO moderation_logs 
        (admin_id, action, entity_type, entity_id, old_value, new_value, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor = await db.execute(
        query,
        (
            log.admin_id,
            log.action,
            log.entity_type,
            log.entity_id,
            log.old_value,
            log.new_value,
            log.notes
        )
    )
    log_id = cursor.lastrowid
    
    # Fetch and return the created log
    row = await db.fetch_one("SELECT * FROM moderation_logs WHERE id = ?", (log_id,))
    return dict(row)


@router.get("/logs/{log_id}", response_model=ModerationLog)
async def get_moderation_log(log_id: int, username: str = Depends(require_auth)):
    """Get a specific moderation log"""
    query = "SELECT * FROM moderation_logs WHERE id = ?"
    row = await db.fetch_one(query, (log_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Moderation log not found")
    return dict(row)


@router.get("/stats/summary")
async def get_moderation_stats(username: str = Depends(require_auth)):
    """Get moderation statistics"""
    # Actions by type
    actions = await db.fetch_all("""
        SELECT action, COUNT(*) as count 
        FROM moderation_logs 
        GROUP BY action
        ORDER BY count DESC
    """)
    
    # Recent activity (last 24 hours)
    recent = await db.fetch_one("""
        SELECT COUNT(*) as count 
        FROM moderation_logs 
        WHERE created_at >= datetime('now', '-1 day')
    """)
    
    # Most active admins
    admins = await db.fetch_all("""
        SELECT admin_id, COUNT(*) as action_count 
        FROM moderation_logs 
        GROUP BY admin_id
        ORDER BY action_count DESC
        LIMIT 10
    """)
    
    return {
        "actions_by_type": [{"action": row['action'], "count": row['count']} for row in actions],
        "recent_24h": recent['count'],
        "most_active_admins": [
            {"admin_id": row['admin_id'], "action_count": row['action_count']} 
            for row in admins
        ]
    }
