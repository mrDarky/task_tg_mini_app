from fastapi import APIRouter, HTTPException, Query
from app.models import UserCreate, UserUpdate, User
from app.services import user_service
from typing import Optional, List


router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=dict)
async def create_user(user: UserCreate):
    try:
        user_id = await user_service.create_user(user)
        return {"id": user_id, "message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: int):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
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
