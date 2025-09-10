from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from datetime import datetime, timezone
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    
    expenses: Mapped[list["ExpenseModel"]] = relationship(back_populates="user")

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt_context.hash(password)
    
    @staticmethod
    def verify_password(plain_pass: str, hashed_pass: str) -> bool:
        return bcrypt_context.verify(plain_pass, hashed_pass)