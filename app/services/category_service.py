from database.db import db
from app.models import CategoryCreate, CategoryUpdate, CategoryTranslation
from typing import Optional, List


async def create_category(category: CategoryCreate) -> int:
    query = """
        INSERT INTO categories (name, label, parent_id)
        VALUES (?, ?, ?)
    """
    cursor = await db.execute(query, (category.name, category.label, category.parent_id))
    category_id = cursor.lastrowid
    
    # Add translations if provided
    if category.translations:
        for trans in category.translations:
            await db.execute(
                """INSERT INTO category_translations (category_id, language_id, name)
                   VALUES (?, ?, ?)""",
                (category_id, trans.language_id, trans.name)
            )
    
    return category_id


async def get_category(category_id: int, include_translations: bool = False) -> Optional[dict]:
    query = "SELECT * FROM categories WHERE id = ?"
    row = await db.fetch_one(query, (category_id,))
    if not row:
        return None
    
    result = dict(row)
    
    if include_translations:
        trans_query = "SELECT * FROM category_translations WHERE category_id = ?"
        trans_rows = await db.fetch_all(trans_query, (category_id,))
        result['translations'] = [dict(t) for t in trans_rows]
    
    return result


async def get_categories(parent_id: Optional[int] = None, include_translations: bool = False) -> List[dict]:
    if parent_id is None:
        query = "SELECT * FROM categories WHERE parent_id IS NULL ORDER BY name"
        rows = await db.fetch_all(query)
    else:
        query = "SELECT * FROM categories WHERE parent_id = ? ORDER BY name"
        rows = await db.fetch_all(query, (parent_id,))
    
    categories = [dict(row) for row in rows]
    
    if include_translations:
        for cat in categories:
            trans_query = "SELECT * FROM category_translations WHERE category_id = ?"
            trans_rows = await db.fetch_all(trans_query, (cat['id'],))
            cat['translations'] = [dict(t) for t in trans_rows]
    
    return categories


async def get_all_categories(include_translations: bool = False) -> List[dict]:
    query = "SELECT * FROM categories ORDER BY parent_id, name"
    rows = await db.fetch_all(query)
    categories = [dict(row) for row in rows]
    
    if include_translations:
        for cat in categories:
            trans_query = "SELECT * FROM category_translations WHERE category_id = ?"
            trans_rows = await db.fetch_all(trans_query, (cat['id'],))
            cat['translations'] = [dict(t) for t in trans_rows]
    
    return categories


async def get_category_tree(include_translations: bool = False) -> List[dict]:
    categories = await get_all_categories(include_translations)
    
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
    update_data = category_update.model_dump(exclude_unset=True, exclude={'translations'})
    
    updated = False
    
    # Update category base fields
    if update_data:
        fields = []
        values = []
        for key, value in update_data.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(category_id)
        query = f"UPDATE categories SET {', '.join(fields)} WHERE id = ?"
        await db.execute(query, tuple(values))
        updated = True
    
    # Update translations if provided
    if category_update.translations is not None:
        for trans in category_update.translations:
            # Check if translation exists
            existing = await db.fetch_one(
                "SELECT id FROM category_translations WHERE category_id = ? AND language_id = ?",
                (category_id, trans.language_id)
            )
            
            if existing:
                # Update existing translation
                await db.execute(
                    """UPDATE category_translations 
                       SET name = ?, updated_at = CURRENT_TIMESTAMP 
                       WHERE category_id = ? AND language_id = ?""",
                    (trans.name, category_id, trans.language_id)
                )
            else:
                # Insert new translation
                await db.execute(
                    """INSERT INTO category_translations (category_id, language_id, name)
                       VALUES (?, ?, ?)""",
                    (category_id, trans.language_id, trans.name)
                )
        updated = True
    
    return updated


async def delete_category(category_id: int) -> bool:
    query = "DELETE FROM categories WHERE id = ?"
    await db.execute(query, (category_id,))
    return True


async def get_subcategories(parent_id: int, include_translations: bool = False) -> List[dict]:
    query = "SELECT * FROM categories WHERE parent_id = ? ORDER BY name"
    rows = await db.fetch_all(query, (parent_id,))
    categories = [dict(row) for row in rows]
    
    if include_translations:
        for cat in categories:
            trans_query = "SELECT * FROM category_translations WHERE category_id = ?"
            trans_rows = await db.fetch_all(trans_query, (cat['id'],))
            cat['translations'] = [dict(t) for t in trans_rows]
    
    return categories


async def get_category_name_by_language(category_id: int, language_code: str) -> str:
    """Get category name in specific language, fallback to default name"""
    # First get language_id from code
    lang_row = await db.fetch_one("SELECT id FROM languages WHERE code = ?", (language_code,))
    
    if lang_row:
        # Try to get translation
        trans_row = await db.fetch_one(
            "SELECT name FROM category_translations WHERE category_id = ? AND language_id = ?",
            (category_id, lang_row['id'])
        )
        if trans_row:
            return trans_row['name']
    
    # Fallback to default name
    cat_row = await db.fetch_one("SELECT name FROM categories WHERE id = ?", (category_id,))
    return cat_row['name'] if cat_row else "Unknown"

