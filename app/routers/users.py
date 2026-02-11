from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import UserCreate, UserUpdate, User
from app.services import user_service
from app.telegram_auth import get_telegram_user
from typing import Optional, List, Dict, Any


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{user_id}/tasks", response_model=list)
async def fetch_user_tasks(
    user_id: int, 
    status: Optional[str] = Query(None),
    telegram_user: Dict[str, Any] = Depends(get_telegram_user)
):
    """Get all tasks for a user, optionally filtered by status"""
    # Verify the authenticated user is requesting their own data
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user['telegram_id'] != telegram_user['telegram_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        tasks = await user_service.get_user_tasks(user_id, status)
        return tasks
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=dict)
async def create_user(user: UserCreate):
    try:
        user_id = await user_service.create_user(user)
        return {"id": user_id, "message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    telegram_user: Dict[str, Any] = Depends(get_telegram_user)
):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify the authenticated user is requesting their own data
    if user['telegram_id'] != telegram_user['telegram_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return user


@router.get("/", response_model=dict)
async def get_users(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    users = await user_service.get_users(search, status, skip, limit)
    total = await user_service.count_users(search, status)
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.put("/{user_id}", response_model=dict)
async def update_user(user_id: int, user_update: UserUpdate):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_service.update_user(user_id, user_update)
    return {"message": "User updated successfully"}


@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/ban", response_model=dict)
async def ban_user(user_id: int):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_service.ban_user(user_id)
    return {"message": "User banned successfully"}


@router.post("/{user_id}/unban", response_model=dict)
async def unban_user(user_id: int):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_service.unban_user(user_id)
    return {"message": "User unbanned successfully"}


@router.post("/{user_id}/adjust-stars", response_model=dict)
async def adjust_stars(user_id: int, stars_delta: int):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_service.adjust_user_stars(user_id, stars_delta)
    return {"message": f"Stars adjusted by {stars_delta}"}


@router.post("/bulk-update", response_model=dict)
async def bulk_update_users(user_ids: List[int], update_data: dict):
    if not user_ids:
        raise HTTPException(status_code=400, detail="No user IDs provided")
    
    await user_service.bulk_update_users(user_ids, update_data)
    return {"message": f"Bulk update applied to {len(user_ids)} users"}


@router.post("/{user_id}/generate-referral", response_model=dict)
async def generate_referral_code(user_id: int):
    """Generate a referral code for a user who doesn't have one"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If user already has a referral code, return it
    if user.get('referral_code'):
        return {"referral_code": user['referral_code'], "message": "Referral code already exists"}
    
    # Generate new referral code
    referral_code = await user_service.ensure_referral_code(user_id, user['telegram_id'])
    return {"referral_code": referral_code, "message": "Referral code generated successfully"}


@router.get("/{user_id}/referrals", response_model=list)
async def get_user_referrals(
    user_id: int,
    telegram_user: Dict[str, Any] = Depends(get_telegram_user)
):
    """Get all referrals for a user"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify the authenticated user is requesting their own data
    if user['telegram_id'] != telegram_user['telegram_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    referrals = await user_service.get_user_referrals(user_id)
    return referrals


@router.get("/{user_id}/daily-bonus", response_model=dict)
async def get_daily_bonus_status(
    user_id: int,
    telegram_user: Dict[str, Any] = Depends(get_telegram_user)
):
    """Get daily bonus status for a user"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify the authenticated user is requesting their own data
    if user['telegram_id'] != telegram_user['telegram_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    bonus_status = await user_service.get_daily_bonus_status(user_id)
    return bonus_status


@router.post("/{user_id}/claim-bonus", response_model=dict)
async def claim_daily_bonus(
    user_id: int,
    telegram_user: Dict[str, Any] = Depends(get_telegram_user)
):
    """Claim daily bonus for a user"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify the authenticated user is claiming their own bonus
    if user['telegram_id'] != telegram_user['telegram_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await user_service.claim_daily_bonus(user_id)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.get("/{user_id}/achievements", response_model=list)
async def get_user_achievements(
    user_id: int,
    telegram_user: Dict[str, Any] = Depends(get_telegram_user)
):
    """Get all achievements for a user"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify the authenticated user is requesting their own data
    if user['telegram_id'] != telegram_user['telegram_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    achievements = await user_service.get_user_achievements(user_id)
    return achievements
