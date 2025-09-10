from fastapi import Depends, Request, Response
from src.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.models.user_model import UserModel
from src.config import settings

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
credential_dependency = Annotated[HTTPAuthorizationCredentials, Depends(security)]

if settings.AUTH_MODE == 'Bearer':
    def user_dependency_func(db: db_dependency, credentials: credential_dependency) -> UserModel:
        from src.routers.auth_router import get_current_user
        return get_current_user(db, credentials)
elif settings.AUTH_MODE == 'Coockie':
    def user_dependency_func(request: Request, response: Response, db: db_dependency) -> UserModel:
        from src.routers.auth_coockie_router import get_current_user
        return get_current_user(request, db, response)
else:
    raise Exception({"message": "Invalid Auth mode"})


user_dependency = Annotated[UserModel, Depends(user_dependency_func)]