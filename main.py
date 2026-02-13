from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from database.db import db
from app.routers import users, tasks, categories, analytics, settings, withdrawals, notifications, tickets, moderation, reports, languages, logs, activity, approvals, bot_constructor
from app.auth import authenticate_user, session_manager, get_current_user, require_auth, update_password, AuthenticationError
from app.services.logger_service import log_error
from app.middleware import ActivityLoggingMiddleware
from pydantic import BaseModel
from config.settings import settings as config_settings
import traceback


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    await db.migrate_schema()
    yield
    await db.disconnect()


app = FastAPI(
    title="Task App API",
    description="Telegram mini-app tasker with rewards and admin panel",
    version="1.0.0",
    lifespan=lifespan
)

# Add activity logging middleware
app.add_middleware(ActivityLoggingMiddleware)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# Exception handler for authentication errors
@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    return RedirectResponse(url="/admin/login", status_code=303)


# Global exception handler for all unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error
    error_message = f"Unhandled exception in {request.method} {request.url.path}"
    await log_error(error_message, error=exc, source=f"{request.method} {request.url.path}")
    
    # Return appropriate response
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. The error has been logged."}
        )
    else:
        # For non-API routes, return a generic error page or redirect
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


# Pydantic models for request validation
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

# Register all routers
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(categories.router)
app.include_router(analytics.router)
app.include_router(settings.router)
app.include_router(withdrawals.router)
app.include_router(notifications.router)
app.include_router(tickets.router)
app.include_router(moderation.router)
app.include_router(reports.router)
app.include_router(languages.router)
app.include_router(logs.router)
app.include_router(activity.router)
app.include_router(approvals.router)
app.include_router(bot_constructor.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/admin")


# Authentication routes
@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    # If already logged in, redirect to dashboard
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/admin", status_code=303)
    
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@app.post("/admin/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if await authenticate_user(username, password):
        # Create session
        session_token = session_manager.create_session(username)
        
        # Redirect to admin dashboard
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(
            key="admin_session",
            value=session_token,
            httponly=True,
            max_age=86400 * 7,  # 7 days
            secure=config_settings.use_secure_cookies,
            samesite="lax"
        )
        return response
    else:
        # Return to login with error
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        }, status_code=401)


@app.get("/admin/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_session")
    return response


@app.post("/admin/change-password")
async def change_password(request: Request, password_data: PasswordChangeRequest, username: str = Depends(require_auth)):
    # Verify current password
    if not await authenticate_user(username, password_data.current_password):
        return JSONResponse(
            status_code=400,
            content={"detail": "Current password is incorrect"}
        )
    
    # Update password
    if await update_password(username, password_data.new_password):
        return {"message": "Password changed successfully"}
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to change password"}
        )


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("users.html", {"request": request, "username": username})


@app.get("/admin/tasks", response_class=HTMLResponse)
async def admin_tasks(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("tasks.html", {"request": request, "username": username})


@app.get("/admin/categories", response_class=HTMLResponse)
async def admin_categories(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("categories.html", {"request": request, "username": username})


@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("settings.html", {"request": request, "username": username})


@app.get("/admin/reports", response_class=HTMLResponse)
async def admin_reports(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("reports.html", {"request": request, "username": username})


@app.get("/admin/withdrawals", response_class=HTMLResponse)
async def admin_withdrawals(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("withdrawals.html", {"request": request, "username": username})


@app.get("/admin/notifications", response_class=HTMLResponse)
async def admin_notifications(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("notifications.html", {"request": request, "username": username})


@app.get("/admin/tickets", response_class=HTMLResponse)
async def admin_tickets(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("tickets.html", {"request": request, "username": username})


@app.get("/admin/moderation", response_class=HTMLResponse)
async def admin_moderation(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("moderation.html", {"request": request, "username": username})


@app.get("/admin/languages", response_class=HTMLResponse)
async def admin_languages(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("languages.html", {"request": request, "username": username})


@app.get("/admin/logs", response_class=HTMLResponse)
async def admin_logs(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("logs.html", {"request": request, "username": username})


@app.get("/admin/activity", response_class=HTMLResponse)
async def admin_activity(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("activity_monitor.html", {"request": request, "username": username})


@app.get("/admin/approvals", response_class=HTMLResponse)
async def admin_approvals(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("approvals.html", {"request": request, "username": username})


@app.get("/admin/translations/{language_id}", response_class=HTMLResponse)
async def admin_translations(request: Request, language_id: int, username: str = Depends(require_auth)):
    return templates.TemplateResponse("translations.html", {"request": request, "language_id": language_id, "username": username})


@app.get("/admin/bot-constructor", response_class=HTMLResponse)
async def admin_bot_constructor(request: Request, username: str = Depends(require_auth)):
    return templates.TemplateResponse("bot_constructor.html", {"request": request, "username": username})


# Mini-app routes
@app.get("/miniapp", response_class=HTMLResponse)
@app.get("/miniapp/home", response_class=HTMLResponse)
async def miniapp_home(request: Request):
    return templates.TemplateResponse("miniapp_home.html", {"request": request})


@app.get("/miniapp/tasks", response_class=HTMLResponse)
async def miniapp_tasks(request: Request):
    return templates.TemplateResponse("miniapp_tasks.html", {"request": request})


@app.get("/miniapp/profile", response_class=HTMLResponse)
async def miniapp_profile(request: Request):
    return templates.TemplateResponse("miniapp_profile.html", {"request": request})


@app.get("/miniapp/rewards", response_class=HTMLResponse)
async def miniapp_rewards(request: Request):
    return templates.TemplateResponse("miniapp_rewards.html", {"request": request})


@app.get("/miniapp/task/{task_id}", response_class=HTMLResponse)
async def miniapp_task_detail(request: Request, task_id: int):
    return templates.TemplateResponse("miniapp_task_detail.html", {"request": request, "task_id": task_id})


@app.get("/miniapp/support", response_class=HTMLResponse)
async def miniapp_support(request: Request):
    return templates.TemplateResponse("miniapp_support.html", {"request": request})


@app.get("/miniapp/ticket-detail", response_class=HTMLResponse)
async def miniapp_ticket_detail(request: Request):
    return templates.TemplateResponse("miniapp_ticket_detail.html", {"request": request})


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config_settings.port)
