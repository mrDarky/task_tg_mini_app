from fastapi import APIRouter, HTTPException, Query, Depends, Request
from app.models import TaskCreate, TaskUpdate
from app.services import task_service
from app.auth import require_auth, get_admin_or_telegram_user
from typing import Optional, List, Dict, Any
from database.db import db


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/", response_model=dict)
async def create_task(task: TaskCreate, username: str = Depends(require_auth)):
    try:
        task_id = await task_service.create_task(task)
        return {"id": task_id, "message": "Task created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}", response_model=dict)
async def get_task(
    task_id: int,
    include_translations: bool = Query(False),
    language_code: Optional[str] = Query(None),
    auth_user: Dict[str, Any] = Depends(get_admin_or_telegram_user)
):
    """
    Get a single task by ID.
    
    Accessible by both admin users (via session) and Telegram Mini App users.
    """
    if language_code:
        task = await task_service.get_task_by_language(task_id, language_code)
    else:
        task = await task_service.get_task(task_id, include_translations=include_translations)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/", response_model=dict)
async def get_tasks(
    search: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_translations: bool = Query(False),
    language_code: Optional[str] = Query(None),
    exclude_completed: bool = Query(False),
    auth_user: Dict[str, Any] = Depends(get_admin_or_telegram_user)
):
    """
    List all available tasks.
    
    Accessible by both admin users (via session) and Telegram Mini App users.
    If exclude_completed=true and user is telegram user, filters out tasks already completed by that user.
    """
    user_id = None
    
    # Get user_id for telegram users to filter completed tasks
    if exclude_completed and auth_user.get('auth_type') == 'telegram':
        user = await db.fetch_one("SELECT id FROM users WHERE telegram_id = ?", (auth_user['telegram_id'],))
        if user:
            user_id = user['id']
    
    if language_code:
        tasks = await task_service.get_tasks_by_language(
            language_code, search=search, task_type=task_type, 
            status=status, category_id=category_id, skip=skip, limit=limit,
            exclude_completed_by_user=user_id
        )
    else:
        tasks = await task_service.get_tasks(
            search, task_type, status, category_id, skip, limit, 
            include_translations=include_translations,
            exclude_completed_by_user=user_id
        )
    
    total = await task_service.count_tasks(search, task_type, status, category_id, exclude_completed_by_user=user_id)
    return {
        "tasks": tasks,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.put("/{task_id}", response_model=dict)
async def update_task(task_id: int, task_update: TaskUpdate, username: str = Depends(require_auth)):
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await task_service.update_task(task_id, task_update)
    return {"message": "Task updated successfully"}


@router.delete("/{task_id}", response_model=dict)
async def delete_task(task_id: int, username: str = Depends(require_auth)):
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await task_service.delete_task(task_id)
    return {"message": "Task deleted successfully"}


@router.post("/bulk-update", response_model=dict)
async def bulk_update_tasks(task_ids: List[int], update_data: dict, username: str = Depends(require_auth)):
    if not task_ids:
        raise HTTPException(status_code=400, detail="No task IDs provided")
    
    await task_service.bulk_update_tasks(task_ids, update_data)
    return {"message": f"Bulk update applied to {len(task_ids)} tasks"}


@router.get("/{task_id}/translations", response_model=dict)
async def get_task_translations(task_id: int, username: str = Depends(require_auth)):
    """Get all translations for a task"""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    translations = await task_service.get_task_translations(task_id)
    return {"translations": translations}


@router.post("/{task_id}/translations", response_model=dict)
async def create_task_translation(
    task_id: int,
    language_id: int,
    title: str,
    description: Optional[str] = None,
    username: str = Depends(require_auth)
):
    """Create or update a translation for a task"""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await task_service.update_task_translation(task_id, language_id, title, description)
    return {"message": "Translation created/updated successfully"}


@router.delete("/{task_id}/translations/{language_id}", response_model=dict)
async def delete_task_translation(task_id: int, language_id: int, username: str = Depends(require_auth)):
    """Delete a translation for a task"""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await task_service.delete_task_translation(task_id, language_id)
    return {"message": "Translation deleted successfully"}

