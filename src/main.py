from fastapi import FastAPI
import uvicorn
from src.routers.expense_router import router as expense_router
from src.routers.auth_router import router as auth_router
from src.routers.auth_coockie_router import router as auth_coockie_router

app = FastAPI(title="Expanse Management API", version="1.0.0", debug=True)

app.include_router(expense_router, tags=['Expenses'])
app.include_router(auth_router, tags=['Authentication'])
app.include_router(auth_coockie_router, tags=['Coockie Authentication'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)