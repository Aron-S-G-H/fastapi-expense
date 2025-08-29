from sqlalchemy import create_engine, String, Float
from sqlalchemy.orm import sessionmaker,declarative_base, Mapped, mapped_column


SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "expenses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Float)


Base.metadata.create_all(engine)