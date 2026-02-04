import aiosqlite
from typing import Optional


class Database:
    def __init__(self, db_path: str = "task_app.db"):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.create_tables()
    
    async def disconnect(self):
        if self.connection:
            await self.connection.close()
    
    async def create_tables(self):
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                referral_code TEXT UNIQUE,
                stars INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories (id) ON DELETE CASCADE
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                url TEXT,
                reward INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                category_id INTEGER,
                completion_limit INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                UNIQUE(user_id, task_id)
            )
        """)
        
        # Withdrawals table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                method TEXT,
                details TEXT,
                admin_id INTEGER,
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Notifications table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'general',
                target_type TEXT DEFAULT 'all',
                target_filter TEXT,
                status TEXT DEFAULT 'draft',
                sent_count INTEGER DEFAULT 0,
                opened_count INTEGER DEFAULT 0,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP
            )
        """)
        
        # Support tickets table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'open',
                assigned_to INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Ticket responses table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS ticket_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Moderation logs table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS moderation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                old_value TEXT,
                new_value TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Settings table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Star transactions table (for detailed transaction history)
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS star_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                type TEXT NOT NULL,
                reference_type TEXT,
                reference_id INTEGER,
                description TEXT,
                admin_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Referrals table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER NOT NULL,
                bonus_awarded BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (referred_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(referred_id)
            )
        """)
        
        # Daily bonuses table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS daily_bonuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bonus_amount INTEGER NOT NULL,
                streak_count INTEGER DEFAULT 1,
                claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Achievements table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                requirement_type TEXT NOT NULL,
                requirement_value INTEGER NOT NULL,
                reward_stars INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User achievements table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (achievement_id) REFERENCES achievements (id) ON DELETE CASCADE,
                UNIQUE(user_id, achievement_id)
            )
        """)
        
        # User settings table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                language TEXT DEFAULT 'en',
                notifications_enabled BOOLEAN DEFAULT 1,
                task_notifications BOOLEAN DEFAULT 1,
                reward_notifications BOOLEAN DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Task submissions table (for screenshot verification)
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS task_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                submission_type TEXT DEFAULT 'screenshot',
                file_id TEXT,
                file_path TEXT,
                status TEXT DEFAULT 'pending',
                admin_notes TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        """)
        
        # Languages table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS languages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Translations table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (language_id) REFERENCES languages (id) ON DELETE CASCADE,
                UNIQUE(language_id, key)
            )
        """)
        
        # Admin credentials table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS admin_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.connection.commit()
        
        # Initialize default languages if not exist
        await self._initialize_default_languages()
        
        # Initialize default admin credentials if not exist
        await self._initialize_default_admin()
    
    async def _initialize_default_admin(self):
        """Initialize default admin credentials from settings if they don't exist"""
        from config.settings import settings
        from passlib.context import CryptContext
        
        # Check if admin already exists
        existing = await self.fetch_one("SELECT COUNT(*) as count FROM admin_credentials")
        if existing and existing['count'] > 0:
            return
        
        # Hash the default password using bcrypt
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(settings.admin_password)
        
        # Add default admin
        await self.execute(
            "INSERT INTO admin_credentials (username, password_hash) VALUES (?, ?)",
            (settings.admin_username, password_hash)
        )
    
    async def execute(self, query: str, params: tuple = ()):
        cursor = await self.connection.execute(query, params)
        await self.connection.commit()
        return cursor
    
    async def fetch_one(self, query: str, params: tuple = ()):
        cursor = await self.connection.execute(query, params)
        return await cursor.fetchone()
    
    async def fetch_all(self, query: str, params: tuple = ()):
        cursor = await self.connection.execute(query, params)
        return await cursor.fetchall()
    
    async def _initialize_default_languages(self):
        """Initialize default languages (English and Russian) if they don't exist"""
        # Check if languages already exist
        existing = await self.fetch_one("SELECT COUNT(*) as count FROM languages")
        if existing and existing['count'] > 0:
            return
        
        # Add English (default)
        await self.execute(
            "INSERT INTO languages (code, name, is_active, is_default) VALUES (?, ?, 1, 1)",
            ('en', 'English')
        )
        
        # Add Russian
        await self.execute(
            "INSERT INTO languages (code, name, is_active, is_default) VALUES (?, ?, 1, 0)",
            ('ru', 'Русский')
        )
        
        # Get language IDs
        en_lang = await self.fetch_one("SELECT id FROM languages WHERE code = 'en'")
        ru_lang = await self.fetch_one("SELECT id FROM languages WHERE code = 'ru'")
        
        # Add default translations for English
        default_translations_en = [
            ('welcome_message', 'Welcome to Task App!', 'bot'),
            ('tasks_button', 'Tasks', 'bot'),
            ('profile_button', 'Profile', 'bot'),
            ('help_button', 'Help', 'bot'),
            ('settings_button', 'Settings', 'bot'),
            ('stars_earned', 'Stars earned', 'bot'),
            ('task_completed', 'Task completed!', 'bot'),
            ('daily_bonus', 'Daily Bonus', 'bot'),
            ('referral_bonus', 'Referral Bonus', 'bot'),
            ('admin_panel', 'Admin Panel', 'admin'),
            ('dashboard', 'Dashboard', 'admin'),
            ('users', 'Users', 'admin'),
            ('tasks', 'Tasks', 'admin'),
            ('categories', 'Categories', 'admin'),
            ('languages', 'Languages', 'admin'),
            ('translations', 'Translations', 'admin'),
        ]
        
        for key, value, category in default_translations_en:
            await self.execute(
                "INSERT INTO translations (language_id, key, value, category) VALUES (?, ?, ?, ?)",
                (en_lang['id'], key, value, category)
            )
        
        # Add default translations for Russian
        default_translations_ru = [
            ('welcome_message', 'Добро пожаловать в Task App!', 'bot'),
            ('tasks_button', 'Задания', 'bot'),
            ('profile_button', 'Профиль', 'bot'),
            ('help_button', 'Помощь', 'bot'),
            ('settings_button', 'Настройки', 'bot'),
            ('stars_earned', 'Заработано звезд', 'bot'),
            ('task_completed', 'Задание выполнено!', 'bot'),
            ('daily_bonus', 'Ежедневный бонус', 'bot'),
            ('referral_bonus', 'Реферальный бонус', 'bot'),
            ('admin_panel', 'Панель администратора', 'admin'),
            ('dashboard', 'Панель управления', 'admin'),
            ('users', 'Пользователи', 'admin'),
            ('tasks', 'Задания', 'admin'),
            ('categories', 'Категории', 'admin'),
            ('languages', 'Языки', 'admin'),
            ('translations', 'Переводы', 'admin'),
        ]
        
        for key, value, category in default_translations_ru:
            await self.execute(
                "INSERT INTO translations (language_id, key, value, category) VALUES (?, ?, ?, ?)",
                (ru_lang['id'], key, value, category)
            )


db = Database()
