from faker import Faker
from fastapi import Depends
from fastapi.testclient import TestClient
from src.database import create_engine, sessionmaker, Base
from src.dependencies import get_db
from sqlalchemy import StaticPool
from src.models.user_model import UserModel
from src.models.expense_model import ExpenseModel
from src.routers.auth_router import generate_access_token
import pytest
from src.main import app

faker = Faker()
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="package")
def get_test_db():
    db = TestSesionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def override_dependencies(get_test_db):
    app.dependency_overrides[get_db] = lambda : get_test_db
    yield
    app.dependency_overrides.clear()



@pytest.fixture(scope="session",autouse=True)
def tear_up_and_down_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    
    
@pytest.fixture(scope="package")
def anon_client():
    client = TestClient(app)
    yield client
    
@pytest.fixture(scope="package",autouse=True)
def generate_mock_data(get_test_db):
    user = UserModel(username="testuser")
    user.hashed_password = user.hash_password("12345678")
    get_test_db.add(user)
    get_test_db.commit()
    get_test_db.refresh(user)

    expenses_list = []
    for _ in range(3):
        expenses_list.append(
            ExpenseModel(
                user_id=user.id,
                description=faker.pystr(min_chars=5, max_chars=50), 
                amount = faker.pyfloat(left_digits=3, right_digits=2, positive=True)
            )
        )
    get_test_db.add_all(expenses_list)
    get_test_db.commit()

@pytest.fixture(scope="package")
def auth_client(get_test_db):
    client = TestClient(app)
    user = get_test_db.query(UserModel).filter_by(username="testuser").one()
    access_token = generate_access_token(user.id)
    client.headers.update({"Authorization":f"Bearer {access_token}"})
    yield client
    
@pytest.fixture(scope="function")
def random_expense(get_test_db):
    user = get_test_db.query(UserModel).filter_by(username="testuser").one()
    expense = get_test_db.query(ExpenseModel).filter_by(user_id=user.id).first()
    return expense