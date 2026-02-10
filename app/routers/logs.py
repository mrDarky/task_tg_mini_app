from fastapi import APIRouter, Query, Depends
from typing import Optional
from app.services.logger_service import LoggerService
from app.auth import require_auth

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("/")
async def get_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    level: Optional[str] = Query(None),
    username: str = Depends(require_auth)
):
    """
    Get logs with pagination
    
    Args:
        offset: Number of records to skip
        limit: Maximum number of records to return (max 1000)
        level: Optional filter by log level (e.g., 'ERROR')
    """
    logs = await LoggerService.get_logs(offset=offset, limit=limit, level=level)
    total = await LoggerService.get_logs_count(level=level)
    
    return {
        "logs": logs,
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.get("/errors")
async def get_error_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    username: str = Depends(require_auth)
):
    """Get only error logs (ERROR and CRITICAL levels)"""
    # Get both ERROR and CRITICAL logs in a single query
    logs = await LoggerService.get_logs(offset=offset, limit=limit, levels=['ERROR', 'CRITICAL'])
    total = await LoggerService.get_logs_count(levels=['ERROR', 'CRITICAL'])
    
    return {
        "logs": logs,
        "total": total,
        "offset": offset,
        "limit": limit
    }
