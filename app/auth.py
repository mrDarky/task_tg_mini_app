import hashlib
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature
from passlib.context import CryptContext
from config.settings import settings
from database.db import db


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass


class SessionManager:
    def __init__(self, secret_key: str):
        self.serializer = URLSafeTimedSerializer(secret_key)
    
    def create_session(self, username: str) -> str:
        """Create a signed session token"""
        return self.serializer.dumps(username, salt='admin-session')
    
    def verify_session(self, token: str, max_age: int = 86400 * 7) -> Optional[str]:
        """Verify and decode a session token (default: 7 days)"""
        try:
            username = self.serializer.loads(token, salt='admin-session', max_age=max_age)
            return username
        except (BadSignature, Exception):
            return None


session_manager = SessionManager(settings.secret_key)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user with username and password"""
    user = await db.fetch_one(
        "SELECT password_hash FROM admin_credentials WHERE username = ?",
        (username,)
    )
    if not user:
        return False
    
    return verify_password(password, user['password_hash'])


async def get_current_user(request: Request) -> Optional[str]:
    """Get the current logged-in user from session cookie"""
    session_token = request.cookies.get("admin_session")
    if not session_token:
        return None
    
    username = session_manager.verify_session(session_token)
    if not username:
        return None
    
    # Verify user still exists in database
    user = await db.fetch_one(
        "SELECT username FROM admin_credentials WHERE username = ?",
        (username,)
    )
    if not user:
        return None
    
    return username


async def require_auth(request: Request) -> str:
    """Dependency to require authentication for a route"""
    user = await get_current_user(request)
    if not user:
        # Raise custom exception that will be handled by exception handler
        raise AuthenticationError()
    return user


async def update_password(username: str, new_password: str) -> bool:
    """Update user password"""
    password_hash = hash_password(new_password)
    try:
        await db.execute(
            "UPDATE admin_credentials SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE username = ?",
            (password_hash, username)
        )
        return True
    except Exception:
        return False
