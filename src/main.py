from fastapi import FastAPI, HTTPException, status, Body, Path
from fastapi.responses import JSONResponse
from schema import CreateExpenseSchema, ExpenseSchema, UpdateExpenseSchema
import uvicorn

app = FastAPI(title="Expanse Management API", version="1.0.0")

expenses = [
    {"id": 1, "description": "خرید لپ‌تاپ", "amount": 35000.50},
    {"id": 2, "description": "پرداخت قبض اینترنت", "amount": 400.00},
    {"id": 3, "description": "خرید موس", "amount": 150.75},
]

current_id = max(expenses, key=lambda x: x["id"])["id"]

@app.get("/expenses", response_model=list[ExpenseSchema])
def get_expenses():
    return JSONResponse(content=expenses, status_code=status.HTTP_200_OK)

@app.get("/expenses/{expense_id}", response_model=ExpenseSchema)
def get_expense(expense_id: int = Path(..., gt=0)):
    for item in expenses:
        if item['id'] == expense_id:
            return JSONResponse(content=item, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

@app.post("/expenses", response_model=ExpenseSchema)
def create_expense(request: CreateExpenseSchema = Body(...)):
    global current_id
    current_id += 1
    expenses.append({"id": current_id, "description": request.description, "amount": request.amount})
    return JSONResponse(content=expenses[-1], status_code=status.HTTP_201_CREATED)

@app.put("/expenses/{expense_id}", response_model=ExpenseSchema)
def update_expense(expense_id: int = Path(..., gt=0), request: UpdateExpenseSchema = Body(...)):
    for item in expenses:
        if item['id'] == expense_id:
            item['description'] = request.description
            item['amount'] = request.amount
            return JSONResponse(content=item, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

@app.delete("/expenses/{expense_id}")   
def delete_expense(expense_id: int = Path(..., gt=0)):
    for item in expenses:
        if item['id'] == expense_id:
            expenses.remove(item)
            return JSONResponse(content={"detail": "Expense deleted successfully"}, status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)