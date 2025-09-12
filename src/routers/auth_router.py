import jwt
from datetime import datetime, timezone, timedelta
from src.config import settings
from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from src.dependencies import db_dependency, credential_dependency, locale_dependency
from src.schemas.auth_schema import (
    LoginSchema,
    RegisterSchema,
    RegisterResponseSchema,
    RefreshTokenSchema,
)
from src.models.user_model import UserModel
from jwt.exceptions import DecodeError, InvalidSignatureError


router = APIRouter(prefix="/auth")


def get_current_time():
    return datetime.now(timezone.utc)


def generate_access_token(user_id: int, expire_time: int = 3600) -> str:
    now = get_current_time()
    payload = {
        "type": "access",
        "user_id": user_id,
        "create": now.timestamp(),
        "exp": (now + timedelta(seconds=expire_time)).timestamp(),
    }
    return jwt.encode(
        payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def generate_refresh_token(user_id: int, expire_time: int = 3600 * 24) -> str:
    now = get_current_time()
    payload = {
        "type": "refresh",
        "user_id": user_id,
        "create": now.timestamp(),
        "exp": (now + timedelta(seconds=expire_time)).timestamp(),
    }
    return jwt.encode(
        payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def get_current_user(
    db: db_dependency, credentials: credential_dependency, _: locale_dependency
) -> UserModel:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )
        token_type = payload.get("type", None)
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=_("token type is invalid"),
            )
        user_id = payload.get("user_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=_("token is not correct"),
            )
        now = get_current_time()
        token_exp = payload.get("exp", None)
        if now > datetime.fromtimestamp(token_exp, tz=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=_("token expired")
            )
        user_obj = db.query(UserModel).filter_by(id=user_id).one()
        return user_obj
    except DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"decode error: {e}"
        )
    except InvalidSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"signature error: {e}"
        )


def decode_refresh_token(token) -> int:
    try:
        payload = jwt.decode(
            token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )
        token_type = payload.get("type", None)
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="token type is invalid"
            )
        user_id = payload.get("user_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="token is not correct"
            )
        now = get_current_time()
        token_exp = payload.get("exp", None)
        if now > datetime.fromtimestamp(token_exp, tz=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="token expired"
            )
        return user_id
    except DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"decode error: {e}"
        )
    except InvalidSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"signature error: {e}"
        )


@router.post("/login")
def login(db: db_dependency, _: locale_dependency, data: LoginSchema = Body(...)):
    user_obj = (
        db.query(UserModel).filter(UserModel.username == data.username).one_or_none()
    )
    if user_obj and user_obj.verify_password(data.password, user_obj.hashed_password):
        response = {
            "detail": _("user logged in"),
            "access": generate_access_token(user_obj.id),
            "refresh": generate_refresh_token(user_obj.id),
        }
        return JSONResponse(content=response, status_code=status.HTTP_200_OK)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=_("username or password is wrong")
    )


@router.post(
    "/reister",
    response_model=RegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def register(db: db_dependency, _: locale_dependency, data: RegisterSchema = Body(...)):
    validation = (
        db.query(UserModel).filter(UserModel.username == data.username).one_or_none()
    )
    if validation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_("User already exists")
        )
    new_user = UserModel()
    new_user.username = data.username
    new_user.hashed_password = new_user.hash_password(data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/refresh-token", status_code=status.HTTP_200_OK)
def refresh_token(_: locale_dependency, refresh_token: RefreshTokenSchema = Body(...)):
    try:
        user_id = decode_refresh_token(refresh_token.refresh_token)
    except HTTPException as e:
        return JSONResponse(content={"detail": _(e.detail)}, status_code=e.status_code)
    new_access_token = generate_access_token(user_id=user_id)
    return JSONResponse(content={"access": new_access_token})
