from pydantic import BaseModel, field_validator, Field


class BaseExpenseSchema(BaseModel):
    description: str = Field(
        ..., min_length=2, max_length=255, pattern=r"^[\u0600-\u06FF\sA-Za-z0-9]+$"
    )
    amount: float = Field(...)

    @field_validator("amount")
    def validator_amount(cls, value):
        if value <= 0:
            raise ValueError("amount must be greater than 0")
        return value


class ExpenseSchema(BaseExpenseSchema):
    id: int = Field(..., gt=0)


class CreateExpenseSchema(BaseExpenseSchema):
    pass


class UpdateExpenseSchema(BaseExpenseSchema):
    pass
