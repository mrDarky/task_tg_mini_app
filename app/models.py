from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class UserBase(BaseModel):
    username: Optional[str] = None
    referral_code: Optional[str] = None
    stars: int = 0
    status: Literal['active', 'banned'] = 'active'
    role: Literal['user', 'admin'] = 'user'


class UserCreate(UserBase):
    telegram_id: int


class UserUpdate(BaseModel):
    username: Optional[str] = None
    referral_code: Optional[str] = None
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
    completion_limit: int = 0


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
    completion_limit: Optional[int] = None


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
    stars_today: int = 0
    stars_week: int = 0
    stars_month: int = 0
    completion_rate: float = 0.0


# Withdrawal models
class WithdrawalBase(BaseModel):
    user_id: int
    amount: int
    method: Optional[str] = None
    details: Optional[str] = None


class WithdrawalCreate(WithdrawalBase):
    pass


class WithdrawalUpdate(BaseModel):
    status: Optional[Literal['pending', 'approved', 'rejected']] = None
    admin_notes: Optional[str] = None


class Withdrawal(WithdrawalBase):
    id: int
    status: Literal['pending', 'approved', 'rejected']
    admin_id: Optional[int] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Notification models
class NotificationBase(BaseModel):
    title: str
    message: str
    type: Literal['general', 'task', 'reward', 'system'] = 'general'
    target_type: Literal['all', 'active', 'banned', 'custom'] = 'all'
    target_filter: Optional[str] = None


class NotificationCreate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: int
    status: Literal['draft', 'sent', 'scheduled']
    sent_count: int = 0
    opened_count: int = 0
    created_by: Optional[int] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ticket models
class TicketBase(BaseModel):
    subject: str
    message: str
    priority: Literal['low', 'medium', 'high', 'urgent'] = 'medium'


class TicketCreate(TicketBase):
    user_id: int


class TicketUpdate(BaseModel):
    status: Optional[Literal['open', 'in_progress', 'resolved', 'closed']] = None
    assigned_to: Optional[int] = None
    priority: Optional[Literal['low', 'medium', 'high', 'urgent']] = None


class Ticket(TicketBase):
    id: int
    user_id: int
    status: Literal['open', 'in_progress', 'resolved', 'closed']
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TicketResponseCreate(BaseModel):
    ticket_id: int
    user_id: int
    message: str
    is_admin: bool = False


class TicketResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Moderation log models
class ModerationLogCreate(BaseModel):
    admin_id: int
    action: str
    entity_type: str
    entity_id: int
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    notes: Optional[str] = None


class ModerationLog(ModerationLogCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Settings models
class SettingBase(BaseModel):
    key: str
    value: str
    category: str = 'general'
    description: Optional[str] = None


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    value: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class Setting(SettingBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Star transaction models
class StarTransactionCreate(BaseModel):
    user_id: int
    amount: int
    type: Literal['earned', 'spent', 'adjusted', 'bonus', 'refund']
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    description: Optional[str] = None
    admin_id: Optional[int] = None


class StarTransaction(StarTransactionCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Enhanced dashboard models
class RecentActivity(BaseModel):
    id: int
    type: str
    description: str
    user_id: Optional[int] = None
    timestamp: datetime


class SystemStatus(BaseModel):
    database: str = 'healthy'
    api: str = 'healthy'
    bot: str = 'unknown'
    last_check: datetime


# Referral models
class ReferralCreate(BaseModel):
    referrer_id: int
    referred_id: int


class Referral(BaseModel):
    id: int
    referrer_id: int
    referred_id: int
    bonus_awarded: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


# Daily bonus models
class DailyBonusCreate(BaseModel):
    user_id: int
    bonus_amount: int
    streak_count: int = 1


class DailyBonus(BaseModel):
    id: int
    user_id: int
    bonus_amount: int
    streak_count: int
    claimed_at: datetime
    
    class Config:
        from_attributes = True


# Achievement models
class AchievementBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    requirement_type: str
    requirement_value: int
    reward_stars: int = 0


class AchievementCreate(AchievementBase):
    pass


class Achievement(AchievementBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserAchievement(BaseModel):
    id: int
    user_id: int
    achievement_id: int
    earned_at: datetime
    
    class Config:
        from_attributes = True


# User settings models
class UserSettingsBase(BaseModel):
    language: str = 'en'
    notifications_enabled: bool = True
    task_notifications: bool = True
    reward_notifications: bool = True


class UserSettingsCreate(UserSettingsBase):
    user_id: int


class UserSettingsUpdate(BaseModel):
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    task_notifications: Optional[bool] = None
    reward_notifications: Optional[bool] = None


class UserSettings(UserSettingsBase):
    id: int
    user_id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Task submission models
class TaskSubmissionCreate(BaseModel):
    user_id: int
    task_id: int
    submission_type: str = 'screenshot'
    file_id: Optional[str] = None
    file_path: Optional[str] = None


class TaskSubmissionUpdate(BaseModel):
    status: Optional[Literal['pending', 'approved', 'rejected']] = None
    admin_notes: Optional[str] = None


class TaskSubmission(BaseModel):
    id: int
    user_id: int
    task_id: int
    submission_type: str
    file_id: Optional[str] = None
    file_path: Optional[str] = None
    status: Literal['pending', 'approved', 'rejected']
    admin_notes: Optional[str] = None
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Language models
class LanguageBase(BaseModel):
    code: str
    name: str
    is_active: bool = True
    is_default: bool = False


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class Language(LanguageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Translation models
class TranslationBase(BaseModel):
    key: str
    value: str
    category: str = 'general'


class TranslationCreate(TranslationBase):
    language_id: int


class TranslationUpdate(BaseModel):
    value: Optional[str] = None
    category: Optional[str] = None


class Translation(TranslationBase):
    id: int
    language_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LanguageExport(BaseModel):
    """Model for exporting language data"""
    code: str
    name: str
    translations: dict[str, str]


class LanguageImport(BaseModel):
    """Model for importing language data"""
    code: str
    name: str
    translations: dict[str, str]
    is_active: bool = True
