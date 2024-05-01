import uvicorn
from fastapi import FastAPI, Depends, status, HTTPException
from app.user.router import router as user_router
from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.events import permission_role_creation
from app.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.utils import AuthUtils
from app.database import db
from app.tasks.router import router as tasks_router

app = FastAPI(lifespan=permission_role_creation)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(router=admin_router, prefix="/admin", tags=["admin utils"])


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        ssl_keyfile=settings.rsa.private_key_path,
        ssl_certfile=settings.rsa.certificate,
    )
