from typing import Optional, List, Dict, Any
from datetime import datetime
from database.db import db


class ActivityService:
    @staticmethod
    async def log_activity(
        ip_address: str,
        endpoint: str,
        method: str,
        status_code: int,
        user_id: Optional[int] = None,
        user_agent: Optional[str] = None,
        action_type: Optional[str] = None,
        details: Optional[str] = None,
        is_suspicious: bool = False
    ):
        """Log an activity to the database"""
        await db.execute(
            """
            INSERT INTO activity_logs 
            (user_id, ip_address, endpoint, method, status_code, user_agent, 
             action_type, details, is_suspicious, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, ip_address, endpoint, method, status_code, user_agent,
             action_type, details, int(is_suspicious), datetime.now())
        )
        
        # Update IP addresses tracking
        await ActivityService._update_ip_tracking(ip_address, is_suspicious)
        
        # Update user-IP mapping if user is identified
        if user_id:
            await ActivityService._update_user_ip_mapping(user_id, ip_address)
    
    @staticmethod
    async def _update_ip_tracking(ip_address: str, is_suspicious: bool):
        """Update or create IP address tracking record"""
        # Check if IP exists
        existing_ip = await db.fetch_one(
            "SELECT id, request_count, suspicious_count FROM ip_addresses WHERE ip_address = ?",
            (ip_address,)
        )
        
        if existing_ip:
            # Update existing IP
            new_request_count = existing_ip['request_count'] + 1
            new_suspicious_count = existing_ip['suspicious_count'] + (1 if is_suspicious else 0)
            await db.execute(
                """
                UPDATE ip_addresses 
                SET last_seen = ?, request_count = ?, suspicious_count = ?
                WHERE ip_address = ?
                """,
                (datetime.now(), new_request_count, new_suspicious_count, ip_address)
            )
        else:
            # Create new IP record
            await db.execute(
                """
                INSERT INTO ip_addresses 
                (ip_address, first_seen, last_seen, request_count, suspicious_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (ip_address, datetime.now(), datetime.now(), 1, 1 if is_suspicious else 0)
            )
    
    @staticmethod
    async def _update_user_ip_mapping(user_id: int, ip_address: str):
        """Update or create user-IP mapping"""
        # Check if mapping exists
        existing_mapping = await db.fetch_one(
            "SELECT id, request_count FROM user_ip_mappings WHERE user_id = ? AND ip_address = ?",
            (user_id, ip_address)
        )
        
        if existing_mapping:
            # Update existing mapping
            new_request_count = existing_mapping['request_count'] + 1
            await db.execute(
                """
                UPDATE user_ip_mappings 
                SET last_seen = ?, request_count = ?
                WHERE user_id = ? AND ip_address = ?
                """,
                (datetime.now(), new_request_count, user_id, ip_address)
            )
        else:
            # Create new mapping
            await db.execute(
                """
                INSERT INTO user_ip_mappings 
                (user_id, ip_address, first_seen, last_seen, request_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, ip_address, datetime.now(), datetime.now(), 1)
            )
    
    @staticmethod
    async def get_activities(
        offset: int = 0,
        limit: int = 50,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        is_suspicious: Optional[bool] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
        status_code: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get activities with filters"""
        query = """
            SELECT 
                al.*,
                u.username,
                u.telegram_id
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if user_id is not None:
            query += " AND al.user_id = ?"
            params.append(user_id)
        
        if ip_address is not None:
            query += " AND al.ip_address = ?"
            params.append(ip_address)
        
        if is_suspicious is not None:
            query += " AND al.is_suspicious = ?"
            params.append(int(is_suspicious))
        
        if start_date is not None:
            query += " AND al.created_at >= ?"
            params.append(start_date)
        
        if end_date is not None:
            query += " AND al.created_at <= ?"
            params.append(end_date)
        
        if search is not None:
            query += " AND (al.endpoint LIKE ? OR al.ip_address LIKE ? OR u.username LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if status_code is not None:
            query += " AND al.status_code = ?"
            params.append(status_code)
        
        query += " ORDER BY al.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        rows = await db.fetch_all(query, tuple(params))
        return [dict(row) for row in rows] if rows else []
    
    @staticmethod
    async def get_activities_count(
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        is_suspicious: Optional[bool] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
        status_code: Optional[int] = None
    ) -> int:
        """Get count of activities with filters"""
        query = """
            SELECT COUNT(*) as count
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if user_id is not None:
            query += " AND al.user_id = ?"
            params.append(user_id)
        
        if ip_address is not None:
            query += " AND al.ip_address = ?"
            params.append(ip_address)
        
        if is_suspicious is not None:
            query += " AND al.is_suspicious = ?"
            params.append(int(is_suspicious))
        
        if start_date is not None:
            query += " AND al.created_at >= ?"
            params.append(start_date)
        
        if end_date is not None:
            query += " AND al.created_at <= ?"
            params.append(end_date)
        
        if search is not None:
            query += " AND (al.endpoint LIKE ? OR al.ip_address LIKE ? OR u.username LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if status_code is not None:
            query += " AND al.status_code = ?"
            params.append(status_code)
        
        result = await db.fetch_one(query, tuple(params))
        return result['count'] if result else 0
    
    @staticmethod
    async def get_ip_addresses(
        offset: int = 0,
        limit: int = 50,
        is_blocked: Optional[bool] = None,
        search: Optional[str] = None,
        min_suspicious_count: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get IP addresses with their stats"""
        query = """
            SELECT 
                ip.*,
                COUNT(DISTINCT uim.user_id) as unique_users,
                GROUP_CONCAT(DISTINCT u.username) as usernames
            FROM ip_addresses ip
            LEFT JOIN user_ip_mappings uim ON ip.ip_address = uim.ip_address
            LEFT JOIN users u ON uim.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if is_blocked is not None:
            query += " AND ip.is_blocked = ?"
            params.append(int(is_blocked))
        
        if search is not None:
            query += " AND ip.ip_address LIKE ?"
            params.append(f"%{search}%")
        
        if min_suspicious_count is not None:
            query += " AND ip.suspicious_count >= ?"
            params.append(min_suspicious_count)
        
        query += """
            GROUP BY ip.id
            ORDER BY ip.last_seen DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        rows = await db.fetch_all(query, tuple(params))
        return [dict(row) for row in rows] if rows else []
    
    @staticmethod
    async def get_ip_addresses_count(
        is_blocked: Optional[bool] = None,
        search: Optional[str] = None,
        min_suspicious_count: Optional[int] = None
    ) -> int:
        """Get count of IP addresses"""
        query = "SELECT COUNT(*) as count FROM ip_addresses WHERE 1=1"
        params = []
        
        if is_blocked is not None:
            query += " AND is_blocked = ?"
            params.append(int(is_blocked))
        
        if search is not None:
            query += " AND ip_address LIKE ?"
            params.append(f"%{search}%")
        
        if min_suspicious_count is not None:
            query += " AND suspicious_count >= ?"
            params.append(min_suspicious_count)
        
        result = await db.fetch_one(query, tuple(params))
        return result['count'] if result else 0
    
    @staticmethod
    async def get_user_ips(user_id: int) -> List[Dict[str, Any]]:
        """Get all IP addresses used by a user"""
        query = """
            SELECT 
                uim.*,
                ip.is_blocked,
                ip.suspicious_count
            FROM user_ip_mappings uim
            LEFT JOIN ip_addresses ip ON uim.ip_address = ip.ip_address
            WHERE uim.user_id = ?
            ORDER BY uim.last_seen DESC
        """
        rows = await db.fetch_all(query, (user_id,))
        return [dict(row) for row in rows] if rows else []
    
    @staticmethod
    async def get_ip_users(ip_address: str) -> List[Dict[str, Any]]:
        """Get all users who used a specific IP"""
        query = """
            SELECT 
                u.id,
                u.username,
                u.telegram_id,
                u.status,
                uim.first_seen,
                uim.last_seen,
                uim.request_count
            FROM user_ip_mappings uim
            JOIN users u ON uim.user_id = u.id
            WHERE uim.ip_address = ?
            ORDER BY uim.last_seen DESC
        """
        rows = await db.fetch_all(query, (ip_address,))
        return [dict(row) for row in rows] if rows else []
    
    @staticmethod
    async def block_ip(ip_address: str, reason: Optional[str] = None):
        """Block an IP address"""
        await db.execute(
            """
            INSERT OR REPLACE INTO ip_addresses 
            (ip_address, is_blocked, block_reason, blocked_at, first_seen, last_seen, request_count, suspicious_count)
            VALUES (
                ?,
                1,
                ?,
                ?,
                COALESCE((SELECT first_seen FROM ip_addresses WHERE ip_address = ?), ?),
                COALESCE((SELECT last_seen FROM ip_addresses WHERE ip_address = ?), ?),
                COALESCE((SELECT request_count FROM ip_addresses WHERE ip_address = ?), 0),
                COALESCE((SELECT suspicious_count FROM ip_addresses WHERE ip_address = ?), 0)
            )
            """,
            (ip_address, reason, datetime.now(), ip_address, datetime.now(),
             ip_address, datetime.now(), ip_address, ip_address)
        )
    
    @staticmethod
    async def unblock_ip(ip_address: str):
        """Unblock an IP address"""
        await db.execute(
            "UPDATE ip_addresses SET is_blocked = 0, block_reason = NULL, blocked_at = NULL WHERE ip_address = ?",
            (ip_address,)
        )
    
    @staticmethod
    async def is_ip_blocked(ip_address: str) -> bool:
        """Check if an IP address is blocked"""
        result = await db.fetch_one(
            "SELECT is_blocked FROM ip_addresses WHERE ip_address = ?",
            (ip_address,)
        )
        return bool(result['is_blocked']) if result else False
    
    @staticmethod
    async def get_ip_details(ip_address: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific IP address"""
        result = await db.fetch_one(
            "SELECT * FROM ip_addresses WHERE ip_address = ?",
            (ip_address,)
        )
        return dict(result) if result else None
