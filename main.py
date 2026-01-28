from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from database.db import db
from app.routers import users, tasks, categories, analytics


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

app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(categories.router)
app.include_router(analytics.router)


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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
