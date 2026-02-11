"""
Telegram Web App Authentication Module

This module provides authentication for Telegram Mini App users by validating
the initData sent from the Telegram Web App. This ensures that only legitimate
Telegram users who opened the app through Telegram can access the API.

Based on Telegram's Web App authentication documentation:
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from urllib.parse import parse_qsl
from fastapi import HTTPException, Header, status, Request
from config.settings import settings
from database.db import db


async def set_user_id_in_request_state(request: Request, telegram_id: Optional[int]) -> None:
    """
    Helper function to look up user by telegram_id and set request.state.user_id.
    This allows the activity logging middleware to link IP addresses to users.
    
    Args:
        request: FastAPI request object
        telegram_id: Telegram user ID (can be None)
    """
    if not telegram_id:
        return
    
    try:
        user = await db.fetch_one(
            "SELECT id FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        if user:
            request.state.user_id = user['id']
    except Exception as e:
        # If database query fails, silently continue without setting user_id
        # This ensures authentication doesn't break if IP tracking has issues
        # In production, you might want to log this error
        import logging
        logging.debug(f"Failed to set user_id in request state: {e}")
        pass


def validate_telegram_init_data(init_data: str) -> Dict[str, Any]:
    """
    Validate Telegram Web App initData and extract user information.
    
    Args:
        init_data: The initData string from Telegram Web App
        
    Returns:
        Dictionary containing validated user data
        
    Raises:
        HTTPException: If validation fails
    """
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Telegram authentication data"
        )
    
    # Parse the init_data string
    try:
        parsed_data = dict(parse_qsl(init_data))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication data format"
        )
    
    # Extract hash and create data_check_string
    received_hash = parsed_data.get('hash')
    if not received_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing hash in Telegram authentication data"
        )
    
    # Remove hash from data for verification
    data_to_check = {k: v for k, v in parsed_data.items() if k != 'hash'}
    
    # Create data_check_string: sorted key=value pairs joined by newline
    data_check_string = '\n'.join(
        f"{k}={v}" for k, v in sorted(data_to_check.items())
    )
    
    # Compute the secret key: HMAC-SHA256(bot_token, "WebAppData")
    secret_key = hmac.new(
        key="WebAppData".encode(),
        msg=settings.bot_token.encode(),
        digestmod=hashlib.sha256
    ).digest()
    
    # Compute the hash: HMAC-SHA256(secret_key, data_check_string)
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Verify the hash
    if not hmac.compare_digest(computed_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication data"
        )
    
    # Parse user data from the validated init_data
    user_data = {}
    if 'user' in parsed_data:
        try:
            user_data = json.loads(parsed_data['user'])
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user data in Telegram authentication"
            )
    
    # Check auth_date to prevent replay attacks (recommended)
    # Telegram recommends checking if auth_date is not too old
    if 'auth_date' in parsed_data:
        try:
            import time
            auth_date = int(parsed_data['auth_date'])
            current_time = int(time.time())
            # Reject if auth_date is older than 24 hours (86400 seconds)
            if current_time - auth_date > 86400:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication data expired. Please reload the app."
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid auth_date in Telegram authentication"
            )
    
    return {
        'telegram_id': user_data.get('id'),
        'username': user_data.get('username'),
        'first_name': user_data.get('first_name'),
        'last_name': user_data.get('last_name'),
        'language_code': user_data.get('language_code'),
        'is_premium': user_data.get('is_premium', False),
        'auth_date': parsed_data.get('auth_date'),
        'raw_data': parsed_data
    }


async def get_telegram_user(
    request: Request,
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data")
) -> Dict[str, Any]:
    """
    FastAPI dependency to validate Telegram Web App user.
    
    This dependency can be used in route handlers to ensure the request
    comes from a legitimate Telegram user.
    
    Args:
        request: FastAPI request object
        x_telegram_init_data: The initData from Telegram Web App sent in header
        
    Returns:
        Dictionary containing validated user data
        
    Raises:
        HTTPException: If validation fails
    """
    if not settings.bot_token:
        # If bot token is not configured, we're in development mode
        # Allow requests but log a warning
        import logging
        logging.warning("BOT_TOKEN not configured. Telegram authentication is disabled.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram authentication is not configured"
        )
    
    if not x_telegram_init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram authentication required. Please access this API through the Telegram Mini App."
        )
    
    telegram_user = validate_telegram_init_data(x_telegram_init_data)
    
    # Set user_id in request state for activity logging
    await set_user_id_in_request_state(request, telegram_user.get('telegram_id'))
    
    return telegram_user


async def get_telegram_user_optional(
    request: Request,
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data")
) -> Optional[Dict[str, Any]]:
    """
    Optional FastAPI dependency to validate Telegram Web App user.
    
    Similar to get_telegram_user but returns None instead of raising exception
    if authentication data is missing. This is useful for endpoints that can
    work both with and without authentication.
    
    Args:
        request: FastAPI request object
        x_telegram_init_data: The initData from Telegram Web App sent in header
        
    Returns:
        Dictionary containing validated user data or None if not authenticated
    """
    if not x_telegram_init_data:
        return None
    
    if not settings.bot_token:
        return None
    
    try:
        telegram_user = validate_telegram_init_data(x_telegram_init_data)
        
        # Set user_id in request state for activity logging
        await set_user_id_in_request_state(request, telegram_user.get('telegram_id'))
        
        return telegram_user
    except HTTPException:
        return None
