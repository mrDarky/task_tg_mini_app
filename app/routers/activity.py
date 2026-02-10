from fastapi import APIRouter, Query, Depends
from typing import Optional
from app.services.activity_service import ActivityService
from app.auth import require_auth
from datetime import datetime

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("/logs")
async def get_activity_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    user_id: Optional[int] = Query(None),
    ip_address: Optional[str] = Query(None),
    is_suspicious: Optional[bool] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    status_code: Optional[int] = Query(None),
    username: str = Depends(require_auth)
):
    """
    Get activity logs with optional filters
    
    Args:
        offset: Number of records to skip
        limit: Maximum number of records to return
        user_id: Filter by user ID
        ip_address: Filter by IP address
        is_suspicious: Filter by suspicious flag
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        search: Search in endpoint, IP, or username
        status_code: Filter by HTTP status code
    """
    activities = await ActivityService.get_activities(
        offset=offset,
        limit=limit,
        user_id=user_id,
        ip_address=ip_address,
        is_suspicious=is_suspicious,
        start_date=start_date,
        end_date=end_date,
        search=search,
        status_code=status_code
    )
    
    total = await ActivityService.get_activities_count(
        user_id=user_id,
        ip_address=ip_address,
        is_suspicious=is_suspicious,
        start_date=start_date,
        end_date=end_date,
        search=search,
        status_code=status_code
    )
    
    return {
        "activities": activities,
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.get("/logs/suspicious")
async def get_suspicious_activities(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    username: str = Depends(require_auth)
):
    """Get only suspicious activities (404s, 500s, etc.)"""
    activities = await ActivityService.get_activities(
        offset=offset,
        limit=limit,
        is_suspicious=True
    )
    
    total = await ActivityService.get_activities_count(is_suspicious=True)
    
    return {
        "activities": activities,
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.get("/logs/user/{user_id}")
async def get_user_activities(
    user_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    username: str = Depends(require_auth)
):
    """Get all activities for a specific user"""
    activities = await ActivityService.get_activities(
        offset=offset,
        limit=limit,
        user_id=user_id
    )
    
    total = await ActivityService.get_activities_count(user_id=user_id)
    
    # Also get all IPs used by this user
    user_ips = await ActivityService.get_user_ips(user_id)
    
    return {
        "activities": activities,
        "total": total,
        "offset": offset,
        "limit": limit,
        "user_ips": user_ips
    }


@router.get("/logs/ip/{ip_address}")
async def get_ip_activities(
    ip_address: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    username: str = Depends(require_auth)
):
    """Get all activities for a specific IP address"""
    activities = await ActivityService.get_activities(
        offset=offset,
        limit=limit,
        ip_address=ip_address
    )
    
    total = await ActivityService.get_activities_count(ip_address=ip_address)
    
    # Also get all users who used this IP
    ip_users = await ActivityService.get_ip_users(ip_address)
    
    # Get IP details
    ip_details = await ActivityService.get_ip_details(ip_address)
    
    return {
        "activities": activities,
        "total": total,
        "offset": offset,
        "limit": limit,
        "ip_users": ip_users,
        "ip_details": ip_details
    }


@router.get("/ip-addresses")
async def get_ip_addresses(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    is_blocked: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    min_suspicious_count: Optional[int] = Query(None),
    username: str = Depends(require_auth)
):
    """
    Get IP addresses with their stats
    
    Args:
        offset: Number of records to skip
        limit: Maximum number of records to return
        is_blocked: Filter by blocked status
        search: Search by IP address
        min_suspicious_count: Filter by minimum suspicious activity count
    """
    ip_addresses = await ActivityService.get_ip_addresses(
        offset=offset,
        limit=limit,
        is_blocked=is_blocked,
        search=search,
        min_suspicious_count=min_suspicious_count
    )
    
    total = await ActivityService.get_ip_addresses_count(
        is_blocked=is_blocked,
        search=search,
        min_suspicious_count=min_suspicious_count
    )
    
    return {
        "ip_addresses": ip_addresses,
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.post("/ip-addresses/{ip_address}/block")
async def block_ip_address(
    ip_address: str,
    reason: Optional[str] = Query(None),
    username: str = Depends(require_auth)
):
    """Block an IP address"""
    await ActivityService.block_ip(ip_address, reason)
    return {"message": f"IP address {ip_address} has been blocked"}


@router.post("/ip-addresses/{ip_address}/unblock")
async def unblock_ip_address(
    ip_address: str,
    username: str = Depends(require_auth)
):
    """Unblock an IP address"""
    await ActivityService.unblock_ip(ip_address)
    return {"message": f"IP address {ip_address} has been unblocked"}


@router.get("/ip-addresses/{ip_address}")
async def get_ip_address_details(
    ip_address: str,
    username: str = Depends(require_auth)
):
    """Get detailed information about a specific IP address"""
    ip_details = await ActivityService.get_ip_details(ip_address)
    ip_users = await ActivityService.get_ip_users(ip_address)
    
    return {
        "ip_details": ip_details,
        "users": ip_users
    }
