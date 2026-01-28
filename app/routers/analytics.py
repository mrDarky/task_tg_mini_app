from fastapi import APIRouter
from app.services import analytics_service
from app.models import DashboardStats


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats():
    stats = await analytics_service.get_dashboard_stats()
    return stats
