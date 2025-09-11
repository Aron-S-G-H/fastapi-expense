from fastapi import Depends, Request, Response
from src.database import SessionLocal
from typing import Annotated, Callable
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.models.user_model import UserModel
from src.config import settings
import os
import gettext

security = HTTPBearer()
SUPPORTED_LANGS = settings.supported_langs_list
DEFAULT_LANG= settings.DEFAULT_LANG
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOCALES_DIR = os.path.join(BASE_DIR, "locales")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
credential_dependency = Annotated[HTTPAuthorizationCredentials, Depends(security)]


def get_translator(request: Request) -> Callable[[str], str]:
    lang = getattr(request.state, "lang", DEFAULT_LANG)
    try:
        trans = gettext.translation("messages", localedir=LOCALES_DIR, languages=[lang])
        _ = trans.gettext
    except FileNotFoundError:
        trans = gettext.translation("messages", localedir=LOCALES_DIR, languages=[DEFAULT_LANG])
        _ = trans.gettext
    return _


locale_dependency = Annotated[Callable[[str], str], Depends(get_translator)]

if settings.AUTH_MODE == 'Bearer':
    def user_dependency_func(db: db_dependency, credentials: credential_dependency, locale: locale_dependency) -> UserModel:
        from src.routers.auth_router import get_current_user
        return get_current_user(db, credentials, locale)
elif settings.AUTH_MODE == 'Coockie':
    def user_dependency_func(request: Request, response: Response, db: db_dependency, locale: locale_dependency) -> UserModel:
        from src.routers.auth_coockie_router import get_current_user
        return get_current_user(request, db, locale, response)
else:
    raise Exception({"message": "Invalid Auth mode"})


user_dependency = Annotated[UserModel, Depends(user_dependency_func)]