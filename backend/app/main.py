from fastapi import FastAPI
from app.routers import auth, orgs, projects, tasks, activity

app = FastAPI()
app.include_router(auth.router, prefix="/auth")
app.include_router(projects.router, prefix="/projects")
app.include_router(tasks.router, prefix="/tasks")
