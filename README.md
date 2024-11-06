# SkyDrive's Backend

A modern Python REST API using FastAPI and Supabase for authentication and database operations.

## Project Structure

```
.
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── .env                     # Environment variables (not in version control)
├── .gitignore              # Git ignore file
└── app/                    # Main application package
    ├── __init__.py
    ├── main.py            # FastAPI application and routing setup
    ├── config.py          # Configuration management
    ├── auth.py            # Authentication utilities
    ├── models/            # Database models
    │   ├── __init__.py
    │   └── base.py
    ├── schemas/           # Pydantic schemas for request/response
    │   ├── __init__.py
    │   └── base.py
    ├── api/              # API endpoints
    │   ├── __init__.py
    │   └── v1/
    │       ├── __init__.py
    │       ├── deps.py   # Dependencies (auth, database)
    │       └── endpoints/
    │           ├── __init__.py
    │           └── auth.py
    └── db/              # Database configuration
        ├── __init__.py
        └── client.py    # Supabase client setup
```

## Prerequisites

- Python 3.8+
- [Supabase](https://supabase.com) account and project

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Copy `.env.example` to `.env` and update with your Supabase credentials:
   ```env
   SUPABASE_URL=your-supabase-project-url
   SUPABASE_KEY=your-supabase-anon-key
   SUPABASE_SECRET_KEY=your-supabase-service-role-key
   API_V1_PREFIX=/api/v1
   PROJECT_NAME=FastAPI Supabase Project
   BACKEND_CORS_ORIGINS=["http://localhost:8000"]
   ```

5. **Start development server**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   The API will be available at `http://localhost:8000`
   
   Interactive API documentation (Swagger UI) will be at `http://localhost:8000/docs`

## API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/signup` - Create new user account
- `POST /api/v1/auth/login` - Login with email and password
- `POST /api/v1/auth/logout` - Logout current user

### Protected Routes

- `GET /protected` - Example protected route (requires authentication)

## Testing

### Using Postman

1. Import the provided Postman collection from `postman/collection.json`
2. Import the environment variables from `postman/environment.json`
3. Select the "FastAPI Supabase Local" environment
4. Start testing the endpoints

## Development Guidelines

### Adding New Endpoints

1. Create a new file in `app/api/v1/endpoints/`
2. Define your router and endpoints
3. Import and include the router in `app/main.py`

Example:
```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from ....auth import get_current_user

router = APIRouter()

@router.get("/users/me")
async def get_my_profile(user = Depends(get_current_user)):
    return {"user": user}
```

### Working with Supabase

The Supabase client is available through dependency injection:

```python
from fastapi import Depends
from ..deps import get_db

@router.get("/items")
async def get_items(db = Depends(get_db)):
    return db.from_("items").select("*").execute()
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
