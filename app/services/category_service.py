from database.db import db
from app.models import CategoryCreate, CategoryUpdate
from typing import Optional, List


async def create_category(category: CategoryCreate) -> int:
    query = """
        INSERT INTO categories (name, parent_id)
        VALUES (?, ?)
    """
    cursor = await db.execute(query, (category.name, category.parent_id))
    return cursor.lastrowid


async def get_category(category_id: int) -> Optional[dict]:
    query = "SELECT * FROM categories WHERE id = ?"
    row = await db.fetch_one(query, (category_id,))
    return dict(row) if row else None


async def get_categories(parent_id: Optional[int] = None) -> List[dict]:
    if parent_id is None:
        query = "SELECT * FROM categories WHERE parent_id IS NULL ORDER BY name"
        rows = await db.fetch_all(query)
    else:
        query = "SELECT * FROM categories WHERE parent_id = ? ORDER BY name"
        rows = await db.fetch_all(query, (parent_id,))
    
    return [dict(row) for row in rows]


async def get_all_categories() -> List[dict]:
    query = "SELECT * FROM categories ORDER BY parent_id, name"
    rows = await db.fetch_all(query)
    return [dict(row) for row in rows]


async def get_category_tree() -> List[dict]:
    categories = await get_all_categories()
    
    category_map = {cat['id']: {**cat, 'children': []} for cat in categories}
    root_categories = []
    
    for category in categories:
        if category['parent_id'] is None:
            root_categories.append(category_map[category['id']])
        else:
            parent = category_map.get(category['parent_id'])
            if parent:
                parent['children'].append(category_map[category['id']])
    
    return root_categories


async def update_category(category_id: int, category_update: CategoryUpdate) -> bool:
    update_data = category_update.model_dump(exclude_unset=True)
    if not update_data:
        return False
    
    fields = []
    values = []
    for key, value in update_data.items():
        fields.append(f"{key} = ?")
        values.append(value)
    
    values.append(category_id)
    query = f"UPDATE categories SET {', '.join(fields)} WHERE id = ?"
    await db.execute(query, tuple(values))
    return True


async def delete_category(category_id: int) -> bool:
    query = "DELETE FROM categories WHERE id = ?"
    await db.execute(query, (category_id,))
    return True


async def get_subcategories(parent_id: int) -> List[dict]:
    query = "SELECT * FROM categories WHERE parent_id = ? ORDER BY name"
    rows = await db.fetch_all(query, (parent_id,))
    return [dict(row) for row in rows]
