from fastapi import APIRouter, HTTPException, Query, Depends, Request
from app.models import CategoryCreate, CategoryUpdate
from app.services import category_service
from app.auth import require_auth, get_admin_or_telegram_user
from typing import Optional, Dict, Any


router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.post("/", response_model=dict)
async def create_category(category: CategoryCreate, username: str = Depends(require_auth)):
    try:
        category_id = await category_service.create_category(category)
        return {"id": category_id, "message": "Category created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{category_id}", response_model=dict)
async def get_category(category_id: int, include_translations: bool = Query(default=False), username: str = Depends(require_auth)):
    category = await category_service.get_category(category_id, include_translations)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/", response_model=dict)
async def get_categories(
    parent_id: Optional[int] = None, 
    include_translations: bool = Query(default=False),
    auth_user: Dict[str, Any] = Depends(get_admin_or_telegram_user)
):
    """
    List all categories.
    
    Accessible by both admin users (via session) and Telegram Mini App users.
    """
    categories = await category_service.get_categories(parent_id, include_translations)
    return {"categories": categories}


@router.get("/tree/all", response_model=dict)
async def get_category_tree(include_translations: bool = Query(default=False), username: str = Depends(require_auth)):
    tree = await category_service.get_category_tree(include_translations)
    return {"tree": tree}


@router.put("/{category_id}", response_model=dict)
async def update_category(category_id: int, category_update: CategoryUpdate, username: str = Depends(require_auth)):
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await category_service.update_category(category_id, category_update)
    return {"message": "Category updated successfully"}


@router.delete("/{category_id}", response_model=dict)
async def delete_category(category_id: int, username: str = Depends(require_auth)):
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await category_service.delete_category(category_id)
    return {"message": "Category deleted successfully"}

