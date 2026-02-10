import traceback
import asyncio
from datetime import datetime
from database.db import db
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class LoggerService:
    """Service for logging application errors and events to database and Telegram"""
    
    @staticmethod
    async def log(level: str, message: str, error: Exception = None, source: str = None):
        """
        Log a message to the database
        
        Args:
            level: Log level (INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            error: Optional exception object
            source: Source of the log (e.g., module name)
        """
        try:
            traceback_text = None
            if error:
                traceback_text = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            
            # Save to database
            await db.execute(
                """INSERT INTO logs (level, message, traceback, source, created_at) 
                   VALUES (?, ?, ?, ?, ?)""",
                (level, message, traceback_text, source, datetime.utcnow())
            )
            
            # Send to Telegram for ERROR and CRITICAL levels
            if level in ['ERROR', 'CRITICAL']:
                asyncio.create_task(LoggerService._send_to_telegram(level, message, traceback_text, source))
        
        except Exception as e:
            # Fallback to standard logging if database logging fails
            logger.error(f"Failed to log to database: {e}")
            logger.error(f"Original log - Level: {level}, Message: {message}")
    
    @staticmethod
    async def _send_to_telegram(level: str, message: str, traceback_text: str = None, source: str = None):
        """Send error notification to Telegram admin users"""
        try:
            if not settings.bot_token or not settings.admin_ids:
                return
            
            from aiogram import Bot
            bot = Bot(token=settings.bot_token)
            
            # Format message
            notification = f"🚨 <b>{level} Alert</b>\n\n"
            notification += f"<b>Message:</b>\n{message}\n\n"
            
            if source:
                notification += f"<b>Source:</b> {source}\n\n"
            
            if traceback_text:
                # Limit traceback length for Telegram (max 4096 chars per message)
                max_traceback_len = 3000
                if len(traceback_text) > max_traceback_len:
                    traceback_text = traceback_text[:max_traceback_len] + "\n... (truncated)"
                notification += f"<b>Traceback:</b>\n<pre>{traceback_text}</pre>"
            
            notification += f"\n<i>Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>"
            
            # Send to all admin users
            for admin_id in settings.admin_ids:
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=notification,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    logger.error(f"Failed to send Telegram notification to admin {admin_id}: {e}")
            
            await bot.session.close()
        
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
    
    @staticmethod
    async def get_logs(offset: int = 0, limit: int = 1000, level: str = None, levels: list = None):
        """
        Retrieve logs from database
        
        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            level: Filter by single log level
            levels: Filter by multiple log levels (takes precedence over level)
        
        Returns:
            List of log records
        """
        try:
            if levels:
                placeholders = ','.join('?' * len(levels))
                query = f"""
                    SELECT id, level, message, traceback, source, created_at 
                    FROM logs 
                    WHERE level IN ({placeholders})
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """
                params = (*levels, limit, offset)
                logs = await db.fetch_all(query, params)
            elif level:
                query = """
                    SELECT id, level, message, traceback, source, created_at 
                    FROM logs 
                    WHERE level = ?
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """
                logs = await db.fetch_all(query, (level, limit, offset))
            else:
                query = """
                    SELECT id, level, message, traceback, source, created_at 
                    FROM logs 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """
                logs = await db.fetch_all(query, (limit, offset))
            
            return [dict(log) for log in logs]
        
        except Exception as e:
            logger.error(f"Failed to retrieve logs: {e}")
            return []
    
    @staticmethod
    async def get_logs_count(level: str = None, levels: list = None):
        """Get total count of logs"""
        try:
            if levels:
                placeholders = ','.join('?' * len(levels))
                query = f"SELECT COUNT(*) as count FROM logs WHERE level IN ({placeholders})"
                result = await db.fetch_one(query, tuple(levels))
            elif level:
                query = "SELECT COUNT(*) as count FROM logs WHERE level = ?"
                result = await db.fetch_one(query, (level,))
            else:
                query = "SELECT COUNT(*) as count FROM logs"
                result = await db.fetch_one(query)
            
            return result['count'] if result else 0
        
        except Exception as e:
            logger.error(f"Failed to get logs count: {e}")
            return 0


# Convenience functions
async def log_info(message: str, source: str = None):
    """Log an info message"""
    await LoggerService.log('INFO', message, source=source)


async def log_warning(message: str, source: str = None):
    """Log a warning message"""
    await LoggerService.log('WARNING', message, source=source)


async def log_error(message: str, error: Exception = None, source: str = None):
    """Log an error message"""
    await LoggerService.log('ERROR', message, error=error, source=source)


async def log_critical(message: str, error: Exception = None, source: str = None):
    """Log a critical error message"""
    await LoggerService.log('CRITICAL', message, error=error, source=source)
