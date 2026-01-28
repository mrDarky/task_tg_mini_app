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
    return cursor.lastrowid


async def get_task(task_id: int) -> Optional[dict]:
    query = "SELECT * FROM tasks WHERE id = ?"
    row = await db.fetch_one(query, (task_id,))
    return dict(row) if row else None


async def get_tasks(
    search: Optional[str] = None,
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
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
    
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    rows = await db.fetch_all(query, tuple(params))
    return [dict(row) for row in rows]


async def count_tasks(
    search: Optional[str] = None,
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    category_id: Optional[int] = None
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
    
    row = await db.fetch_one(query, tuple(params))
    return row['count'] if row else 0


async def update_task(task_id: int, task_update: TaskUpdate) -> bool:
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        return False
    
    fields = []
    values = []
    for key, value in update_data.items():
        fields.append(f"{key} = ?")
        values.append(value)
    
    values.append(task_id)
    query = f"UPDATE tasks SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(query, tuple(values))
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
