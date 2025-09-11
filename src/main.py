from fastapi import FastAPI, Request
import uvicorn
from src.routers.expense_router import router as expense_router
from src.routers.auth_router import router as auth_router
from src.routers.auth_coockie_router import router as auth_coockie_router
from src.routers.test_locale import router as test_locale_router
from src.config import settings


SUPPORTED_LANGS = settings.supported_langs_list
DEFAULT_LANG= settings.DEFAULT_LANG


def _normalize_lang(lang: str | None) -> str:
    if not lang or lang not in SUPPORTED_LANGS:
        return DEFAULT_LANG
    token = lang.split(",")[0].split(";")[0].strip()
    token = token.split("-")[0].lower()
    return token


app = FastAPI(title="Expanse Management API", version="1.0.0", debug=True)


@app.middleware("http")
async def language_middleware(request: Request, call_next):
    lang = request.query_params.get("lang") or request.headers.get("accept-language", DEFAULT_LANG)
    lang = _normalize_lang(lang)
    request.state.lang = lang
    response = await call_next(request)
    return response


app.include_router(expense_router, tags=['Expenses'])
app.include_router(auth_router, tags=['Authentication'])
app.include_router(auth_coockie_router, tags=['Coockie Authentication'])
app.include_router(test_locale_router, tags=['Test Locale'])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)