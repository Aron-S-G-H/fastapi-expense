from fastapi import APIRouter, HTTPException, status, Body, Path
from typing import List
from fastapi.responses import JSONResponse
from src.schemas.expense_schema import CreateExpenseSchema, ExpenseSchema, UpdateExpenseSchema
from src.dependencies import db_dependency, user_dependency
from src.models.expense_model import ExpenseModel

router = APIRouter(prefix='/expense')

@router.get("/", response_model=List[ExpenseSchema], status_code=status.HTTP_200_OK)
def get_expenses(db: db_dependency, user: user_dependency):
    expenses = db.query(ExpenseModel).filter_by(user_id=user.id).all()
    return expenses

@router.get("/{expense_id}", response_model=ExpenseSchema, status_code=status.HTTP_200_OK)
def get_expense(db: db_dependency, user: user_dependency, expense_id: int = Path(..., gt=0)):
    expense = db.query(ExpenseModel).filter_by(id=expense_id, user_id=user.id).one_or_none()
    if expense:
        return expense
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

@router.post("/add", response_model=ExpenseSchema, status_code=status.HTTP_201_CREATED)
def create_expense(db: db_dependency, user: user_dependency, data: CreateExpenseSchema = Body(...)):
    new_expense = ExpenseModel(
        description=data.description,
        amount=data.amount,
        user_id=user.id,
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.put("/{expense_id}", response_model=ExpenseSchema, status_code=status.HTTP_200_OK)
def update_expense(db: db_dependency, user: user_dependency, expense_id: int = Path(..., gt=0), data: UpdateExpenseSchema = Body(...)):
    expense = db.query(ExpenseModel).filter_by(id=expense_id, user_id=user.id).one_or_none()
    if expense:
        expense.description = data.description
        expense.amount = data.amount
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)   
def delete_expense(db: db_dependency, user: user_dependency, expense_id: int = Path(..., gt=0)):
    expense = db.query(ExpenseModel).filter_by(id=expense_id).one_or_none()
    if expense:
        db.delete(expense)
        db.commit()
        return JSONResponse({"detail": "item deleted"})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")