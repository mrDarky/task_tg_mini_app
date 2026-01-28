from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from database.db import db
from app.routers import users, tasks, categories, analytics, settings, withdrawals, notifications, tickets, moderation, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(
    title="Task App API",
    description="Telegram mini-app tasker with rewards and admin panel",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

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


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})


@app.get("/admin/tasks", response_class=HTMLResponse)
async def admin_tasks(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request})


@app.get("/admin/categories", response_class=HTMLResponse)
async def admin_categories(request: Request):
    return templates.TemplateResponse("categories.html", {"request": request})


@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/admin/reports", response_class=HTMLResponse)
async def admin_reports(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})


@app.get("/admin/withdrawals", response_class=HTMLResponse)
async def admin_withdrawals(request: Request):
    return templates.TemplateResponse("withdrawals.html", {"request": request})


@app.get("/admin/notifications", response_class=HTMLResponse)
async def admin_notifications(request: Request):
    return templates.TemplateResponse("notifications.html", {"request": request})


@app.get("/admin/tickets", response_class=HTMLResponse)
async def admin_tickets(request: Request):
    return templates.TemplateResponse("tickets.html", {"request": request})


@app.get("/admin/moderation", response_class=HTMLResponse)
async def admin_moderation(request: Request):
    return templates.TemplateResponse("moderation.html", {"request": request})


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
