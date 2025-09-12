from fastapi import APIRouter
from src.dependencies import locale_dependency

router = APIRouter(prefix="/test-locale")


@router.get("/hi")
def hi(_: locale_dependency):
    return {"message": _("hi")}


@router.get("/bye")
def bye(_: locale_dependency):
    return {"message": _("bye")}


@router.get("/maktabkhooneh")
def maktabkhooneh(_: locale_dependency):
    return {"message": _("maktabkhooneh")}
