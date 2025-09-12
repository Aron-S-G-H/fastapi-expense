from fastapi import APIRouter, Body, HTTPException, status, Response, Request
from src.dependencies import db_dependency, locale_dependency
from src.schemas.auth_schema import LoginSchema, RegisterResponseSchema, RegisterSchema
from src.models.user_model import UserModel
from src.routers.auth_router import (
    generate_access_token,
    generate_refresh_token,
    decode_refresh_token,
)
from src.config import settings
import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError, ExpiredSignatureError

router = APIRouter(prefix="/auth-coockie")


def get_current_user(
    request: Request, db: db_dependency, _: locale_dependency, response: Response
) -> UserModel:
    access_token = request.cookies.get("access")
    refresh_token = request.cookies.get("refresh")

    user_id = None

    if access_token:
        try:
            payload = jwt.decode(
                access_token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=_("invalid token type"),
                )
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=_("token is not correct"),
                )
        except ExpiredSignatureError:
            access_token = None
        except DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="decode error"
            )
        except InvalidSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="signature error"
            )

    if not access_token and refresh_token:
        try:
            user_id = decode_refresh_token(refresh_token)
            new_access_token = generate_access_token(user_id)
            response.set_cookie(
                key="access",
                value=new_access_token,
                httponly=True,
                secure=True,
                expires=3600,
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=_("invalid refresh token"),
            )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=_("token is not correct")
        )
    user_obj = db.query(UserModel).filter_by(id=user_id).one_or_none()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_("user not found")
        )
    return user_obj


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    response: Response,
    db: db_dependency,
    _: locale_dependency,
    data: LoginSchema = Body(...),
):
    user_obj = (
        db.query(UserModel).filter(UserModel.username == data.username).one_or_none()
    )
    if user_obj and user_obj.verify_password(data.password, user_obj.hashed_password):
        access_token = generate_access_token(user_obj.id)
        refresh_token = generate_refresh_token(user_obj.id)
        response.set_cookie(
            "access", access_token, secure=True, httponly=True, expires=3600
        )
        response.set_cookie(
            "refresh", refresh_token, secure=True, httponly=True, expires=3600 * 24
        )
        return {"detail": _("user logged in")}
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


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response, _: locale_dependency):
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return {"detail": _("logged out successfully")}
