from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import TaskApprovalItem, TaskApprovalUpdate
from app.auth import require_auth
from typing import Optional, List
from database.db import db
from datetime import datetime, timezone

router = APIRouter(prefix="/api/approvals", tags=["approvals"], dependencies=[Depends(require_auth)])


@router.get("/", response_model=dict)
async def get_task_approvals(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get list of task submissions for approval/review
    """
    # Build query with joins to get user and task info
    query = """
        SELECT 
            ts.id,
            ts.user_id,
            u.username,
            u.telegram_id,
            ts.task_id,
            t.title as task_title,
            t.type as task_type,
            t.reward as task_reward,
            ts.submission_type,
            ts.file_id,
            ts.file_path,
            ts.status,
            ts.admin_notes,
            ts.submitted_at,
            ts.reviewed_at
        FROM task_submissions ts
        JOIN users u ON ts.user_id = u.id
        JOIN tasks t ON ts.task_id = t.id
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND ts.status = ?"
        params.append(status)
    
    if task_type:
        query += " AND t.type = ?"
        params.append(task_type)
    
    if user_id:
        query += " AND ts.user_id = ?"
        params.append(user_id)
    
    query += " ORDER BY ts.submitted_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    submissions = await db.fetch_all(query, tuple(params))
    
    # Get total count
    count_query = """
        SELECT COUNT(*) as count
        FROM task_submissions ts
        JOIN tasks t ON ts.task_id = t.id
        WHERE 1=1
    """
    count_params = []
    
    if status:
        count_query += " AND ts.status = ?"
        count_params.append(status)
    
    if task_type:
        count_query += " AND t.type = ?"
        count_params.append(task_type)
    
    if user_id:
        count_query += " AND ts.user_id = ?"
        count_params.append(user_id)
    
    total_result = await db.fetch_one(count_query, tuple(count_params))
    total = total_result['count'] if total_result else 0
    
    return {
        "submissions": [dict(s) for s in submissions],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{submission_id}", response_model=dict)
async def get_approval_detail(submission_id: int):
    """
    Get detailed information about a specific submission
    """
    query = """
        SELECT 
            ts.id,
            ts.user_id,
            u.username,
            u.telegram_id,
            ts.task_id,
            t.title as task_title,
            t.type as task_type,
            t.reward as task_reward,
            ts.submission_type,
            ts.file_id,
            ts.file_path,
            ts.status,
            ts.admin_notes,
            ts.submitted_at,
            ts.reviewed_at
        FROM task_submissions ts
        JOIN users u ON ts.user_id = u.id
        JOIN tasks t ON ts.task_id = t.id
        WHERE ts.id = ?
    """
    
    submission = await db.fetch_one(query, (submission_id,))
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return dict(submission)


@router.post("/{submission_id}/approve", response_model=dict)
async def approve_submission(
    submission_id: int,
    approval_data: TaskApprovalUpdate,
    username: str = Depends(require_auth)
):
    """
    Approve or reject a task submission
    """
    # Get admin user
    admin_user = await db.fetch_one("SELECT id FROM users WHERE username = ?", (username,))
    if not admin_user:
        raise HTTPException(status_code=403, detail="Admin user not found")
    
    # Get submission
    submission = await db.fetch_one(
        "SELECT * FROM task_submissions WHERE id = ?",
        (submission_id,)
    )
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission['status'] != 'pending':
        raise HTTPException(status_code=400, detail=f"Submission already {submission['status']}")
    
    # Update submission status
    await db.execute(
        """UPDATE task_submissions 
        SET status = ?, admin_notes = ?, reviewed_at = ?
        WHERE id = ?""",
        (approval_data.status, approval_data.admin_notes, datetime.now(timezone.utc).isoformat(), submission_id)
    )
    
    # If approved, complete the task and award stars
    if approval_data.status == 'approved':
        # Get task details
        task = await db.fetch_one("SELECT * FROM tasks WHERE id = ?", (submission['task_id'],))
        
        if task:
            # Mark task as completed in user_tasks
            now = datetime.now(timezone.utc).isoformat()
            await db.execute(
                """INSERT OR REPLACE INTO user_tasks 
                (user_id, task_id, status, completed_at, verified_at, verification_method)
                VALUES (?, ?, 'completed', ?, ?, 'manual')""",
                (submission['user_id'], submission['task_id'], now, now)
            )
            
            # Award stars
            await db.execute(
                "UPDATE users SET stars = stars + ? WHERE id = ?",
                (task['reward'], submission['user_id'])
            )
            
            # Log transaction
            await db.execute(
                """INSERT INTO star_transactions 
                (user_id, amount, type, reference_type, reference_id, description, admin_id)
                VALUES (?, ?, 'earned', 'task', ?, 'Task completion (manual approval)', ?)""",
                (submission['user_id'], task['reward'], submission['task_id'], admin_user['id'])
            )
    
    # Log moderation action
    await db.execute(
        """INSERT INTO moderation_logs 
        (admin_id, action, entity_type, entity_id, old_value, new_value, notes)
        VALUES (?, ?, 'task_submission', ?, 'pending', ?, ?)""",
        (admin_user['id'], 'approve_submission' if approval_data.status == 'approved' else 'reject_submission',
         submission_id, approval_data.status, approval_data.admin_notes)
    )
    
    return {
        "message": f"Submission {approval_data.status} successfully",
        "submission_id": submission_id,
        "status": approval_data.status
    }


@router.get("/stats/summary", response_model=dict)
async def get_approval_stats():
    """
    Get summary statistics for task approvals
    """
    stats = {}
    
    # Pending submissions count
    pending = await db.fetch_one("SELECT COUNT(*) as count FROM task_submissions WHERE status = 'pending'")
    stats['pending'] = pending['count'] if pending else 0
    
    # Approved today
    approved_today = await db.fetch_one(
        """SELECT COUNT(*) as count FROM task_submissions 
        WHERE status = 'approved' AND DATE(reviewed_at) = DATE('now')"""
    )
    stats['approved_today'] = approved_today['count'] if approved_today else 0
    
    # Rejected today
    rejected_today = await db.fetch_one(
        """SELECT COUNT(*) as count FROM task_submissions 
        WHERE status = 'rejected' AND DATE(reviewed_at) = DATE('now')"""
    )
    stats['rejected_today'] = rejected_today['count'] if rejected_today else 0
    
    # Total processed
    total_processed = await db.fetch_one(
        "SELECT COUNT(*) as count FROM task_submissions WHERE status IN ('approved', 'rejected')"
    )
    stats['total_processed'] = total_processed['count'] if total_processed else 0
    
    return stats
