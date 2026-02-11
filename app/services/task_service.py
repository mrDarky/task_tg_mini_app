from database.db import db
from app.models import TaskCreate, TaskUpdate
from typing import Optional, List


async def create_task(task: TaskCreate) -> int:
    query = """
        INSERT INTO tasks (title, description, type, url, reward, status, category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor = await db.execute(query, (
        task.title, task.description, task.type, task.url, 
        task.reward, task.status, task.category_id
    ))
    task_id = cursor.lastrowid
    
    # Create translations if provided
    if task.translations:
        for translation in task.translations:
            await create_task_translation(
                task_id, 
                translation.language_id, 
                translation.title, 
                translation.description
            )
    
    return task_id


async def get_task(task_id: int, include_translations: bool = False) -> Optional[dict]:
    query = "SELECT * FROM tasks WHERE id = ?"
    row = await db.fetch_one(query, (task_id,))
    if not row:
        return None
    
    task = dict(row)
    
    if include_translations:
        task['translations'] = await get_task_translations(task_id)
    
    return task


async def get_tasks(
    search: Optional[str] = None,
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    include_translations: bool = False,
    exclude_completed_by_user: Optional[int] = None
) -> List[dict]:
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    
    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    if task_type:
        query += " AND type = ?"
        params.append(task_type)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)
    
    # Exclude tasks already completed by the user
    if exclude_completed_by_user:
        query += " AND id NOT IN (SELECT task_id FROM user_tasks WHERE user_id = ? AND status = 'completed')"
        params.append(exclude_completed_by_user)
    
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    rows = await db.fetch_all(query, tuple(params))
    tasks = [dict(row) for row in rows]
    
    if include_translations and tasks:
        # Batch fetch all translations to avoid N+1 query
        task_ids = [task['id'] for task in tasks]
        placeholders = ','.join(['?' for _ in task_ids])
        
        trans_rows = await db.fetch_all(
            f"SELECT * FROM task_translations WHERE task_id IN ({placeholders})",
            tuple(task_ids)
        )
        
        # Group translations by task_id
        trans_by_task = {}
        for trans in trans_rows:
            trans_dict = dict(trans)
            task_id = trans_dict['task_id']
            if task_id not in trans_by_task:
                trans_by_task[task_id] = []
            trans_by_task[task_id].append(trans_dict)
        
        # Assign translations to tasks
        for task in tasks:
            task['translations'] = trans_by_task.get(task['id'], [])
    
    return tasks


async def count_tasks(
    search: Optional[str] = None,
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    exclude_completed_by_user: Optional[int] = None
) -> int:
    query = "SELECT COUNT(*) as count FROM tasks WHERE 1=1"
    params = []
    
    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    if task_type:
        query += " AND type = ?"
        params.append(task_type)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)
    
    # Exclude tasks already completed by the user
    if exclude_completed_by_user:
        query += " AND id NOT IN (SELECT task_id FROM user_tasks WHERE user_id = ? AND status = 'completed')"
        params.append(exclude_completed_by_user)
    
    row = await db.fetch_one(query, tuple(params))
    return row['count'] if row else 0


async def update_task(task_id: int, task_update: TaskUpdate) -> bool:
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Extract translations if present
    translations = update_data.pop('translations', None)
    
    if update_data:
        fields = []
        values = []
        for key, value in update_data.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(task_id)
        query = f"UPDATE tasks SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        await db.execute(query, tuple(values))
    
    # Update translations if provided
    if translations is not None:
        for translation in translations:
            await update_task_translation(
                task_id,
                translation['language_id'],
                translation['title'],
                translation.get('description')
            )
    
    return True


async def delete_task(task_id: int) -> bool:
    query = "DELETE FROM tasks WHERE id = ?"
    await db.execute(query, (task_id,))
    return True


async def bulk_update_tasks(task_ids: List[int], update_data: dict) -> bool:
    if not task_ids or not update_data:
        return False
    
    fields = []
    values = []
    for key, value in update_data.items():
        fields.append(f"{key} = ?")
        values.append(value)
    
    placeholders = ','.join(['?' for _ in task_ids])
    values.extend(task_ids)
    query = f"UPDATE tasks SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders})"
    await db.execute(query, tuple(values))
    return True


async def get_available_tasks_for_user(user_id: int) -> List[dict]:
    query = """
        SELECT t.* FROM tasks t
        WHERE t.status = 'active'
        AND NOT EXISTS (
            SELECT 1 FROM user_tasks ut 
            WHERE ut.task_id = t.id AND ut.user_id = ? AND ut.status = 'completed'
        )
        ORDER BY t.created_at DESC
    """
    rows = await db.fetch_all(query, (user_id,))
    return [dict(row) for row in rows]


async def apply_translations_to_tasks(tasks: List[dict], language_code: str) -> List[dict]:
    """Helper function to apply translations to a list of tasks - avoids N+1 queries"""
    if not tasks:
        return tasks
    
    # Get language_id from code
    lang_row = await db.fetch_one("SELECT id FROM languages WHERE code = ?", (language_code,))
    
    if lang_row:
        # Batch fetch all translations at once
        task_ids = [task['id'] for task in tasks]
        placeholders = ','.join(['?' for _ in task_ids])
        
        trans_rows = await db.fetch_all(
            f"SELECT task_id, title, description FROM task_translations WHERE task_id IN ({placeholders}) AND language_id = ?",
            (*task_ids, lang_row['id'])
        )
        
        # Create a map of task_id to translation
        trans_map = {row['task_id']: row for row in trans_rows}
        
        # Apply translations to tasks
        for task in tasks:
            if task['id'] in trans_map:
                trans = trans_map[task['id']]
                task['title'] = trans['title']
                task['description'] = trans['description']
    
    return tasks


async def complete_task(user_id: int, task_id: int) -> bool:
    query = """
        INSERT INTO user_tasks (user_id, task_id, status, completed_at)
        VALUES (?, ?, 'completed', CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, task_id) DO UPDATE SET 
            status = 'completed',
            completed_at = CURRENT_TIMESTAMP
    """
    await db.execute(query, (user_id, task_id))
    
    task = await get_task(task_id)
    if task:
        from app.services.user_service import adjust_user_stars
        await adjust_user_stars(user_id, task['reward'])
    
    return True


async def create_task_translation(task_id: int, language_id: int, title: str, description: Optional[str] = None) -> int:
    """Create a translation for a task"""
    query = """
        INSERT INTO task_translations (task_id, language_id, title, description)
        VALUES (?, ?, ?, ?)
    """
    cursor = await db.execute(query, (task_id, language_id, title, description))
    return cursor.lastrowid


async def update_task_translation(task_id: int, language_id: int, title: str, description: Optional[str] = None) -> bool:
    """Update a translation for a task"""
    query = """
        INSERT INTO task_translations (task_id, language_id, title, description)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(task_id, language_id) DO UPDATE SET
            title = excluded.title,
            description = excluded.description,
            updated_at = CURRENT_TIMESTAMP
    """
    await db.execute(query, (task_id, language_id, title, description))
    return True


async def delete_task_translation(task_id: int, language_id: int) -> bool:
    """Delete a translation for a task"""
    query = "DELETE FROM task_translations WHERE task_id = ? AND language_id = ?"
    await db.execute(query, (task_id, language_id))
    return True


async def get_task_translations(task_id: int) -> List[dict]:
    """Get all translations for a task"""
    query = "SELECT * FROM task_translations WHERE task_id = ?"
    rows = await db.fetch_all(query, (task_id,))
    return [dict(row) for row in rows]


async def get_task_by_language(task_id: int, language_code: str) -> Optional[dict]:
    """Get task with title and description in specific language, fallback to default"""
    task = await get_task(task_id)
    if not task:
        return None
    
    # Get language_id from code
    lang_row = await db.fetch_one("SELECT id FROM languages WHERE code = ?", (language_code,))
    
    if lang_row:
        # Try to get translation
        trans_row = await db.fetch_one(
            "SELECT title, description FROM task_translations WHERE task_id = ? AND language_id = ?",
            (task_id, lang_row['id'])
        )
        if trans_row:
            task['title'] = trans_row['title']
            task['description'] = trans_row['description']
    
    return task


async def get_tasks_by_language(language_code: str, **filters) -> List[dict]:
    """Get all tasks with translations for specific language"""
    tasks = await get_tasks(**filters)
    
    if not tasks:
        return tasks
    
    # Get language_id from code
    lang_row = await db.fetch_one("SELECT id FROM languages WHERE code = ?", (language_code,))
    
    if lang_row:
        # Batch fetch all translations at once to avoid N+1 query
        task_ids = [task['id'] for task in tasks]
        placeholders = ','.join(['?' for _ in task_ids])
        
        trans_rows = await db.fetch_all(
            f"SELECT task_id, title, description FROM task_translations WHERE task_id IN ({placeholders}) AND language_id = ?",
            (*task_ids, lang_row['id'])
        )
        
        # Create a map of task_id to translation
        trans_map = {row['task_id']: row for row in trans_rows}
        
        # Apply translations to tasks
        for task in tasks:
            if task['id'] in trans_map:
                trans = trans_map[task['id']]
                task['title'] = trans['title']
                task['description'] = trans['description']
    
    return tasks
