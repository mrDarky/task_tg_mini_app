from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from app.models import Ticket, TicketCreate, TicketUpdate, TicketResponse, TicketResponseCreate
from app.telegram_auth import get_telegram_user
from app.auth import require_auth, get_admin_or_telegram_user
from database.db import db


router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("", response_model=List[Ticket])
async def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[int] = None,
    user_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
    auth_user: Dict[str, Any] = Depends(get_admin_or_telegram_user)
):
    """List tickets with optional filters"""
    conditions = []
    params = []
    
    # If Telegram user, enforce ownership - they can only see their own tickets
    if auth_user.get('auth_type') == 'telegram':
        if user_id:
            user = await db.fetch_one("SELECT telegram_id FROM users WHERE id = ?", (user_id,))
            if not user or user['telegram_id'] != auth_user['telegram_id']:
                raise HTTPException(status_code=403, detail="Access denied")
            conditions.append("user_id = ?")
            params.append(user_id)
        else:
            # Telegram users must filter by their own user_id
            user = await db.fetch_one("SELECT id FROM users WHERE telegram_id = ?", (auth_user['telegram_id'],))
            if user:
                conditions.append("user_id = ?")
                params.append(user['id'])
    elif user_id:
        # Admin can filter by any user_id
        conditions.append("user_id = ?")
        params.append(user_id)
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    if priority:
        conditions.append("priority = ?")
        params.append(priority)
    if assigned_to:
        conditions.append("assigned_to = ?")
        params.append(assigned_to)
    
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    offset = (page - 1) * per_page
    params.extend([per_page, offset])
    
    query = f"""
        SELECT * FROM tickets
        {where_clause}
        ORDER BY 
            CASE priority
                WHEN 'urgent' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END,
            created_at DESC
        LIMIT ? OFFSET ?
    """
    
    rows = await db.fetch_all(query, tuple(params))
    return [dict(row) for row in rows]


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: int, auth_user: Dict[str, Any] = Depends(get_admin_or_telegram_user)):
    """Get a specific ticket"""
    query = "SELECT * FROM tickets WHERE id = ?"
    row = await db.fetch_one(query, (ticket_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket = dict(row)
    
    # If Telegram user, enforce ownership - they can only see their own tickets
    if auth_user.get('auth_type') == 'telegram':
        user = await db.fetch_one("SELECT telegram_id FROM users WHERE id = ?", (ticket['user_id'],))
        if not user or user['telegram_id'] != auth_user['telegram_id']:
            raise HTTPException(status_code=403, detail="You don't have permission to view this ticket")
    
    return ticket


@router.post("", response_model=Ticket)
async def create_ticket(
    ticket: TicketCreate,
    telegram_user: Dict[str, Any] = Depends(get_telegram_user)
):
    """Create a new support ticket"""
    # Verify the authenticated user is creating ticket for themselves
    user = await db.fetch_one("SELECT telegram_id FROM users WHERE id = ?", (ticket.user_id,))
    if not user or user['telegram_id'] != telegram_user['telegram_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = """
        INSERT INTO tickets (user_id, subject, message, priority, status)
        VALUES (?, ?, ?, ?, 'open')
    """
    cursor = await db.execute(
        query,
        (ticket.user_id, ticket.subject, ticket.message, ticket.priority)
    )
    ticket_id = cursor.lastrowid
    
    # Fetch and return the created ticket
    row = await db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    return dict(row)


@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(ticket_id: int, ticket: TicketUpdate, username: str = Depends(require_auth)):
    """Update a ticket"""
    # Check if ticket exists
    existing = await db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    updates = ["updated_at = CURRENT_TIMESTAMP"]
    params = []
    
    if ticket.status:
        updates.append("status = ?")
        params.append(ticket.status)
        if ticket.status in ['resolved', 'closed']:
            updates.append("resolved_at = CURRENT_TIMESTAMP")
    
    if ticket.assigned_to is not None:
        updates.append("assigned_to = ?")
        params.append(ticket.assigned_to)
    
    if ticket.priority:
        updates.append("priority = ?")
        params.append(ticket.priority)
    
    params.append(ticket_id)
    
    query = f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?"
    await db.execute(query, tuple(params))
    
    # Fetch and return updated ticket
    row = await db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    return dict(row)


@router.get("/{ticket_id}/responses", response_model=List[TicketResponse])
async def get_ticket_responses(ticket_id: int, auth_user: Dict[str, Any] = Depends(get_admin_or_telegram_user)):
    """Get all responses for a ticket"""
    # Check if ticket exists and user has permission to view it
    ticket = await db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # If Telegram user, enforce ownership
    if auth_user.get('auth_type') == 'telegram':
        user = await db.fetch_one("SELECT telegram_id FROM users WHERE id = ?", (ticket['user_id'],))
        if not user or user['telegram_id'] != auth_user['telegram_id']:
            raise HTTPException(status_code=403, detail="You don't have permission to view this ticket")
    
    query = """
        SELECT * FROM ticket_responses 
        WHERE ticket_id = ? 
        ORDER BY created_at ASC
    """
    rows = await db.fetch_all(query, (ticket_id,))
    return [dict(row) for row in rows]


@router.post("/{ticket_id}/responses", response_model=TicketResponse)
async def create_ticket_response(ticket_id: int, response: TicketResponseCreate, auth_user: Dict[str, Any] = Depends(get_admin_or_telegram_user)):
    """Add a response to a ticket"""
    # Check if ticket exists
    ticket = await db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # If Telegram user, enforce ownership and ensure they can only respond to their own tickets
    if auth_user.get('auth_type') == 'telegram':
        user = await db.fetch_one("SELECT id, telegram_id FROM users WHERE id = ?", (response.user_id,))
        if not user or user['telegram_id'] != auth_user['telegram_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        if ticket['user_id'] != response.user_id:
            raise HTTPException(status_code=403, detail="You don't have permission to respond to this ticket")
    
    query = """
        INSERT INTO ticket_responses (ticket_id, user_id, message, is_admin)
        VALUES (?, ?, ?, ?)
    """
    cursor = await db.execute(
        query,
        (ticket_id, response.user_id, response.message, response.is_admin)
    )
    response_id = cursor.lastrowid
    
    # Update ticket's updated_at
    await db.execute(
        "UPDATE tickets SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (ticket_id,)
    )
    
    # Fetch and return the created response
    row = await db.fetch_one("SELECT * FROM ticket_responses WHERE id = ?", (response_id,))
    return dict(row)


@router.get("/stats/summary")
async def get_ticket_stats(username: str = Depends(require_auth)):
    """Get ticket statistics"""
    stats = {}
    
    for status in ['open', 'in_progress', 'resolved', 'closed']:
        row = await db.fetch_one(
            "SELECT COUNT(*) as count FROM tickets WHERE status = ?",
            (status,)
        )
        stats[status] = row['count']
    
    return stats
