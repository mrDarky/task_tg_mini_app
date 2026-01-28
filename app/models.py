from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class UserBase(BaseModel):
    username: Optional[str] = None
    stars: int = 0
    status: Literal['active', 'banned'] = 'active'
    role: Literal['user', 'admin'] = 'user'


class UserCreate(UserBase):
    telegram_id: int


class UserUpdate(BaseModel):
    username: Optional[str] = None
    stars: Optional[int] = None
    status: Optional[Literal['active', 'banned']] = None
    role: Optional[Literal['user', 'admin']] = None


class User(UserBase):
    id: int
    telegram_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: Literal['youtube', 'tiktok', 'subscribe']
    url: Optional[str] = None
    reward: int = 0
    status: Literal['active', 'inactive', 'completed'] = 'active'
    category_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[Literal['youtube', 'tiktok', 'subscribe']] = None
    url: Optional[str] = None
    reward: Optional[int] = None
    status: Optional[Literal['active', 'inactive', 'completed']] = None
    category_id: Optional[int] = None


class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserTaskBase(BaseModel):
    user_id: int
    task_id: int
    status: Literal['pending', 'completed', 'rejected'] = 'pending'


class UserTaskCreate(UserTaskBase):
    pass


class UserTask(UserTaskBase):
    id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    banned_users: int
    total_tasks: int
    active_tasks: int
    total_categories: int
    total_stars_distributed: int
    total_completions: int
