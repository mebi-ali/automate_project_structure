# Template for common module files
COMMON_FILES = {
    "base_models.py": '''from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
''',
    
    "config.py": '''from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Project"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
''',
    
    "database.py": '''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
    
    "exceptions.py": '''from fastapi import HTTPException
from typing import Any, Dict, Optional

class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "message": message,
                "details": details or {}
            }
        )

class NotFoundException(BaseAPIException):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=404, message=message, details=details)

class BadRequestException(BaseAPIException):
    def __init__(self, message: str = "Bad request", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=400, message=message, details=details)

class UnauthorizedException(BaseAPIException):
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=401, message=message, details=details)
''',
    
    "router.py": '''from fastapi import APIRouter
from ..usecase1.routers import router as usecase1_router
from ..usecase2.routers import router as usecase2_router
from .config import settings

main_router = APIRouter(prefix=settings.API_V1_STR)

main_router.include_router(
    usecase1_router,
    prefix="/usecase1",
    tags=["usecase1"]
)

main_router.include_router(
    usecase2_router,
    prefix="/usecase2",
    tags=["usecase2"]
)
''',
    
    "utils.py": '''from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy.orm import Query
from fastapi import Query as FastAPIQuery

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime) -> str:
    return dt.isoformat()

def paginate(
    query: Query,
    page: int = FastAPIQuery(1, ge=1),
    page_size: int = FastAPIQuery(10, ge=1, le=100)
) -> Dict[str, Any]:
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }
'''
}

# Template for usecase files
USECASE_FILES = {
    "constants.py": '''# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Cache
CACHE_TTL = 3600  # 1 hour

# Rate Limiting
RATE_LIMIT_CALLS = 100
RATE_LIMIT_PERIOD = 3600  # 1 hour
''',
    
    "dependencies.py": '''from fastapi import Depends, Request
from sqlalchemy.orm import Session
from ..common.database import get_db
from ..common.exceptions import UnauthorizedException

def get_db_session():
    return Depends(get_db)

async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise UnauthorizedException("API key is required")
    # Add your API key validation logic here
    return api_key
''',
    
    "models.py": '''from sqlalchemy import Column, String, Text, Boolean
from ..common.base_models import Base, BaseModel

class Item(BaseModel):
    __tablename__ = "items"
    
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Item {self.name}>"
''',
    
    "schemas.py": '''from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    page: int
    page_size: int
    pages: int
''',
    
    "services.py": '''from sqlalchemy.orm import Session
from . import models, schemas
from ..common.exceptions import NotFoundException
from typing import Optional, List

class ItemService:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, item: schemas.ItemCreate) -> models.Item:
        db_item = models.Item(**item.dict())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    async def get_by_id(self, item_id: int) -> Optional[models.Item]:
        item = self.db.query(models.Item).filter(models.Item.id == item_id).first()
        if not item:
            raise NotFoundException(f"Item with id {item_id} not found")
        return item

    async def get_all(self) -> List[models.Item]:
        return self.db.query(models.Item).filter(models.Item.is_active == True).all()

    async def update(self, item_id: int, item_data: schemas.ItemUpdate) -> models.Item:
        db_item = await self.get_by_id(item_id)
        for field, value in item_data.dict(exclude_unset=True).items():
            setattr(db_item, field, value)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    async def delete(self, item_id: int) -> None:
        db_item = await self.get_by_id(item_id)
        self.db.delete(db_item)
        self.db.commit()
''',
    
    "routers.py": '''from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from . import schemas, services
from .dependencies import get_db_session, verify_api_key
from ..common.utils import paginate
from typing import List

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.ItemResponse,
    status_code=201,
    dependencies=[Depends(verify_api_key)]
)
async def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new item"""
    service = services.ItemService(db)
    return await service.create(item)

@router.get(
    "/",
    response_model=schemas.PaginatedResponse
)
async def list_items(
    db: Session = Depends(get_db_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """List all items with pagination"""
    service = services.ItemService(db)
    query = db.query(services.models.Item)
    return paginate(query, page, page_size)

@router.get(
    "/{item_id}",
    response_model=schemas.ItemResponse
)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db_session)
):
    """Get a specific item by ID"""
    service = services.ItemService(db)
    return await service.get_by_id(item_id)

@router.put(
    "/{item_id}",
    response_model=schemas.ItemResponse,
    dependencies=[Depends(verify_api_key)]
)
async def update_item(
    item_id: int,
    item: schemas.ItemUpdate,
    db: Session = Depends(get_db_session)
):
    """Update an item"""
    service = services.ItemService(db)
    return await service.update(item_id, item)

@router.delete(
    "/{item_id}",
    status_code=204,
    dependencies=[Depends(verify_api_key)]
)
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db_session)
):
    """Delete an item"""
    service = services.ItemService(db)
    await service.delete(item_id)
'''
}

# Template for test files
TEST_FILES = {
    "conftest.py": '''import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.common.database import get_db
from src.common.base_models import Base
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def api_key_headers():
    return {"X-API-Key": "test_api_key"}
'''
}

# Main application template
MAIN_APP_TEMPLATE = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.common.router import main_router
from src.common.config import settings
from src.common.base_models import Base
from src.common.database import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(main_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
'''

# Setup.py template
SETUP_TEMPLATE = '''from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "alembic>=1.11.0",
        "pytest>=7.4.0",
        "httpx>=0.24.0",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "python-multipart>=0.0.6",
        "email-validator>=2.0.0",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pytest-cov>=4.1.0",
            "pre-commit>=3.3.0",
        ]
    },
    python_requires=">=3.9",
)
'''

# Environment file template
ENV_TEMPLATE = '''# Database
DATABASE_URL=sqlite:///./sql_app.db

# Application
DEBUG=True
PROJECT_NAME="FastAPI Project"
API_V1_STR="/api/v1"

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
'''

GITIGNORE_TEMPLATE = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Virtual Environment
venv/
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
'''


README_TEMPLATE = '''# {project_name}

A FastAPI project with clean architecture and best practices.

## Features

- FastAPI framework
- SQLAlchemy ORM
- Pydantic data validation
- JWT Authentication
- Modular structure
- API versioning
- CORS support
- Testing setup
- Environment configuration
- Dependency injection
- Async support
- OpenAPI documentation

## Project Structure

{project_name}/
├── src/
│   ├── common/         # Shared utilities and base classes
│   │   ├── base_models.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   ├── router.py
│   │   └── utils.py
│   ├── usecase1/       # First usecase implementation
│   │   ├── constants.py
│   │   ├── dependencies.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── services.py
│   │   └── routers.py
│   └── usecase2/       # Second usecase implementation
│       ├── constants.py
│       ├── dependencies.py
│       ├── models.py
│       ├── schemas.py
│       ├── services.py
│       └── routers.py
├── tests/              # Test directory
├── main.py            # Application entry point
├── setup.py           # Package setup
├── requirements.txt   # Project dependencies
└── .env              # Environment variables

## Setup

1. Create virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate
    ```

2. Install dependencies:

    ```bash
    pip install -e .
    ```

3. Set up environment variables:

    ```bash
    cp .env.example .env
    # Edit .env with your configurations
    ```

4. Run the application:

    ```bash
    python main.py
    ```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Testing

Run tests with pytest:

    ```bash
    pytest
    ```

Run tests with coverage:

    ```bash
    pytest --cov=src tests/
    coverage report
    coverage html  # Generate HTML report
    ```

## Development

### Project Commands

1. Run development server with auto-reload:

    ```bash
    uvicorn main:app --reload
    ```

2. Run with custom host and port:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8080
    ```

3. Run with workers (production):

    ```bash
    gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
    ```

### Database Operations

    ```bash
    # Generate migration
    alembic revision --autogenerate -m "description"

    # Apply migrations
    alembic upgrade head

    # Rollback migration
    alembic downgrade -1
    ```

### Code Quality

    ```bash
    # Format code
    black src/ tests/

    # Sort imports
    isort src/ tests/

    # Lint code
    flake8 src/ tests/

    # Type checking
    mypy src/
    ```

## Environment Variables

    ```bash
    # Database
    DATABASE_URL=sqlite:///./sql_app.db

    # Application
    DEBUG=True
    PROJECT_NAME="FastAPI Project"
    API_V1_STR="/api/v1"

    # Security
    SECRET_KEY=your-secret-key-here
    ACCESS_TOKEN_EXPIRE_MINUTES=30

    # CORS
    CORS_ORIGINS=http://localhost:3000,http://localhost:8080
    ```

## Dependencies

Main dependencies:
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- Alembic
- Python-jose
- Passlib
- Python-multipart
- Pytest
- HTTPx

Development dependencies:
- Black
- isort
- Flake8
- Mypy
- Pytest-cov

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI Documentation
- SQLAlchemy Documentation
- Pydantic Documentation
- FastAPI Best Practices
'''


