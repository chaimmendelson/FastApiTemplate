# FastAPI Template

A comprehensive FastAPI template with built-in logging, monitoring, middleware, and utility components for rapid API development.

**⚠️ Important**:

- **Fork this repository** before making any changes - do not edit this template directly
- Only edit content in the `app/src` folder. The `app/general` folder contains the core framework and should not be modified

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Git

### Installation

#### For Linux/macOS:

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd FastApiTemplate
   ```

2. **Run the initialization script**

   ```bash
   chmod +x scripts/init.sh
   dos2unix scripts/init.sh
   ./scripts/init.sh
   ```

3. **Activate the virtual environment**

   ```bash
   source .venv/bin/activate
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

#### For Windows:

1. **Clone the repository**

   ```cmd
   git clone <repository-url>
   cd FastApiTemplate
   ```

2. **Run the initialization script**

   ```cmd
   scripts\init.bat
   ```

3. **Activate the virtual environment**

   ```cmd
   .venv\Scripts\activate
   ```

4. **Run the application**
   ```cmd
   python -m app.main
   ```

The application will be available at `http://localhost:8000`

## 📁 Project Structure

```
FastApiTemplate/
├── app/
│   ├── general/           # Core framework (DO NOT MODIFY)
│   │   ├── database/      # Database clients and utilities
│   │   ├── middlewares/   # Request/response middleware
│   │   ├── models/        # Pydantic models
│   │   ├── routes/        # Built-in routes (docs, metrics)
│   │   ├── tasks/         # Background tasks
│   │   └── utils/         # Configuration and logging
│   ├── src/               # Your custom application code
│   ├── static/            # Static files (Swagger UI)
│   └── main.py           # Application entry point
├── scripts/
│   ├── init.sh           # Setup script
│   └── base_requirements.txt
└── README.md
```

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory:

```env
PORT=8000
LOG_LEVEL=INFO
APP_NAME=MyFastAPIApp
PROCESS_TIME_HEADER=X-Process-Time
SWAGGER_STATIC_FILES=/static/swagger
SWAGGER_OPENAPI_JSON_URL=/openapi.json
LOG_REQUEST_EXCLUDE_PATHS=["/health", "/metrics", "/static", "/docs", "/redoc", "/openapi.json", "/.well-known"]
```

## 🛠️ Built-in Features

### 1. **Logging System**

- **Colored console output** with loguru
- **Structured logging** with file, function, and line information
- **Configurable log levels** via environment variables
- **Request/response logging** middleware

### 2. **Monitoring & Metrics**

- **Prometheus metrics** endpoint at `/metrics`
- **Application uptime** tracking
- **Request processing time** headers
- **Custom metrics** support

### 3. **API Documentation**

- **Swagger UI** at `/docs`
- **ReDoc** at `/redoc`
- **OpenAPI JSON** at `/openapi.json`
- **Custom static files** serving

### 4. **Middleware Stack**

- **Request logging** middleware
- **Response time** tracking middleware
- **Exception handling** middleware
- **Customizable** middleware configuration

### 5. **Database & External Services**

- **HTTP client** utilities (`BaseAPI`)
- **FTP client** (`AsyncFTPClient`)
- **Kubernetes client** (`get_dynamic_client`)

### 6. **Background Tasks**

- **Uptime monitoring** task
- **Extensible** task system
- **Async task** management

## 🔌 Database & External Services

### HTTP Client (`BaseAPI`)

```python
from app.general.database.basic_api import BaseAPI

# Create client
api_client = BaseAPI(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"},
    timeout=10.0
)

# Make requests
response = await api_client.get("/users")
response = await api_client.post("/users", json={"name": "John"})
response = await api_client.upload_file_bytes("/upload", "file", "data.txt", file_bytes)
```

### FTP Client (`AsyncFTPClient`)

```python
from app.general.database.ftp_client import AsyncFTPClient

# Create client
ftp_client = await AsyncFTPClient.create(
    host="ftp.example.com",
    user="username",
    password="password",
    port=21,
    base_dir="/uploads"
)

# Operations
await ftp_client.upload("file.txt", content)
content = await ftp_client.download("file.txt")
files = await ftp_client.list()
```

### Kubernetes Client

```python
from app.general.database.kube_client import get_dynamic_client

# Get client (in-cluster or local config)
client = await get_dynamic_client(in_cluster=True)

# Use dynamic client for Kubernetes operations
# (See kubernetes-asyncio documentation for details)
```

## 🎯 Custom Development

**⚠️ Important**:

- **Fork this repository** before making any changes - do not edit this template directly
- Only edit content in the `app/src` folder. The `app/general` folder contains the core framework and should not be modified

### Adding Routes

Create your routes in the `app/src` folder:

```python
# app/src/routes/users.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

class User(BaseModel):
    id: int
    name: str
    email: str

@router.get("/", response_model=list[User])
async def get_users():
    return [{"id": 1, "name": "John", "email": "john@example.com"}]

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    return {"id": user_id, "name": "John", "email": "john@example.com"}
```

### Registering Routes

Update `app/src/__init__.py`:

```python
from fastapi import FastAPI
from .routes import users

async_background_tasks = []

def update_app(app: FastAPI) -> FastAPI:
    app.include_router(users.router)
    return app
```

### Adding Background Tasks

```python
# app/src/tasks/custom_task.py
import asyncio
from loguru import logger

async def custom_background_task():
    while True:
        logger.info("Running custom background task")
        await asyncio.sleep(60)

# Add to app/src/__init__.py
async_background_tasks = [custom_background_task()]
```

### Adding Middleware

```python
# app/src/middlewares/custom_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Your middleware logic here
        response = await call_next(request)
        return response

# Register in app/src/__init__.py
def update_app(app: FastAPI) -> FastAPI:
    app.add_middleware(CustomMiddleware)
    return app
```

## 📊 Monitoring Endpoints

### Health Check

- **GET** `/` - Root endpoint with application info

### Metrics

- **GET** `/metrics` - Prometheus metrics

### Documentation

- **GET** `/docs` - Swagger UI
- **GET** `/redoc` - ReDoc documentation
- **GET** `/openapi.json` - OpenAPI schema

## 🔍 Logging

The application uses structured logging with the following features:

- **Colored output** for different log levels
- **Timestamp** and **log level** information
- **File, function, and line** context
- **Request/response** logging
- **Configurable** log levels

### Log Levels

- `TRACE` - Detailed debugging
- `DEBUG` - Debug information
- `INFO` - General information
- `SUCCESS` - Success messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

## 📦 Dependencies

### Core Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pydantic-settings` - Settings management
- `loguru` - Logging
- `colorama` - Colored output
- `prometheus-client` - Metrics
- `httpx` - HTTP client
- `aioftp` - Async FTP client
- `kubernetes-asyncio` - Kubernetes client

### Development Dependencies

- `python-dotenv` - Environment variables
- `python-multipart` - File uploads
- `uvloop` - Fast event loop
- `httptools` - Fast HTTP parsing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation at `/docs`
- Review the example code in `app/src`

---

**Note**: The `app/general` folder contains the core framework and should not be modified. All custom development should be done in the `app/src` folder.
