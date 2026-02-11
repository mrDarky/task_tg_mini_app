from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from app.models import Withdrawal, WithdrawalCreate, WithdrawalUpdate
from app.telegram_auth import get_telegram_user
from database.db import db


router = APIRouter(prefix="/api/withdrawals", tags=["withdrawals"])


@router.get("", response_model=List[Withdrawal])
async def list_withdrawals(
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20
):
    """List withdrawals with optional filters"""
    conditions = []
    params = []
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    if user_id:
        conditions.append("user_id = ?")
        params.append(user_id)
    
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    offset = (page - 1) * per_page
    params.extend([per_page, offset])
    
    query = f"""
        SELECT * FROM withdrawals
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """
    
    rows = await db.fetch_all(query, tuple(params))
    return [dict(row) for row in rows]


@router.get("/{withdrawal_id}", response_model=Withdrawal)
async def get_withdrawal(withdrawal_id: int):
    """Get a specific withdrawal"""
    query = "SELECT * FROM withdrawals WHERE id = ?"
    row = await db.fetch_one(query, (withdrawal_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    return dict(row)


@router.post("", response_model=Withdrawal)
async def create_withdrawal(
    withdrawal: WithdrawalCreate,
    telegram_user: Dict[str, Any] = Depends(get_telegram_user)
):
    """Create a new withdrawal request"""
    # Check if user has enough stars
    user = await db.fetch_one("SELECT id, stars, telegram_id FROM users WHERE id = ?", (withdrawal.user_id,))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify the authenticated user is creating withdrawal for themselves
    if user['telegram_id'] != telegram_user['telegram_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user['stars'] < withdrawal.amount:
        raise HTTPException(status_code=400, detail="Insufficient stars")
    
    query = """
        INSERT INTO withdrawals (user_id, amount, method, details, status)
        VALUES (?, ?, ?, ?, 'pending')
    """
    cursor = await db.execute(
        query,
        (withdrawal.user_id, withdrawal.amount, withdrawal.method, withdrawal.details)
    )
    withdrawal_id = cursor.lastrowid
    
    # Fetch and return the created withdrawal
    row = await db.fetch_one("SELECT * FROM withdrawals WHERE id = ?", (withdrawal_id,))
    return dict(row)


@router.put("/{withdrawal_id}", response_model=Withdrawal)
async def update_withdrawal(withdrawal_id: int, withdrawal: WithdrawalUpdate, admin_id: int):
    """Update a withdrawal (approve/reject)"""
    # Check if withdrawal exists
    existing = await db.fetch_one("SELECT * FROM withdrawals WHERE id = ?", (withdrawal_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    
    updates = ["admin_id = ?"]
    params = [admin_id]
    
    if withdrawal.status:
        updates.append("status = ?")
        params.append(withdrawal.status)
        
        # If approved, deduct stars from user
        if withdrawal.status == 'approved':
            updates.append("processed_at = CURRENT_TIMESTAMP")
            await db.execute(
                "UPDATE users SET stars = stars - ? WHERE id = ?",
                (existing['amount'], existing['user_id'])
            )
            
            # Create star transaction record
            await db.execute(
                """INSERT INTO star_transactions 
                   (user_id, amount, type, reference_type, reference_id, description, admin_id)
                   VALUES (?, ?, 'spent', 'withdrawal', ?, 'Withdrawal processed', ?)""",
                (existing['user_id'], -existing['amount'], withdrawal_id, admin_id)
            )
    
    if withdrawal.admin_notes:
        updates.append("admin_notes = ?")
        params.append(withdrawal.admin_notes)
    
    params.append(withdrawal_id)
    
    query = f"UPDATE withdrawals SET {', '.join(updates)} WHERE id = ?"
    await db.execute(query, tuple(params))
    
    # Fetch and return updated withdrawal
    row = await db.fetch_one("SELECT * FROM withdrawals WHERE id = ?", (withdrawal_id,))
    return dict(row)


@router.get("/stats/summary")
async def get_withdrawal_stats():
    """Get withdrawal statistics"""
    pending = await db.fetch_one(
        "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM withdrawals WHERE status = 'pending'"
    )
    approved = await db.fetch_one(
        "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM withdrawals WHERE status = 'approved'"
    )
    rejected = await db.fetch_one(
        "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM withdrawals WHERE status = 'rejected'"
    )
    
    return {
        "pending": {"count": pending['count'], "total": pending['total']},
        "approved": {"count": approved['count'], "total": approved['total']},
        "rejected": {"count": rejected['count'], "total": rejected['total']}
    }
