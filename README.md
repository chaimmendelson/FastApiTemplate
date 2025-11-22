# FastAPI Template

A reusable FastAPI application factory packaged for quick reuse. The package exposes a
single public function, `general_create_app`, which returns a fully configured FastAPI
instance with logging, metrics, documentation, and health-check routes ready to go.

## 🚀 Quick Start

### Installation

```bash
pip install horizon-fastapi-template
```

### Usage

Create a new file (for example `main.py`) and bootstrap your API:

```python
from horizon_fastapi_template import general_create_app
from horizon_fastapi_template.utils import settings

app = general_create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
```

Run the application:

```bash
python -m main
```

## 🔧 Configuration

Application behaviour is configured through environment variables using
[`pydantic-settings`](https://docs.pydantic.dev/latest/usage/pydantic_settings/).

| Variable                    | Description                                         | Example                     | Default                                                                                                             |
| --------------------------- | --------------------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `PORT`                      | The port the application will run on.               | `8000`, `8080`              | `8000`                                                                                                              |
| `LOG_LEVEL`                 | Logging level for the application.                  | `INFO`, `DEBUG`, `WARNING`  | `INFO`                                                                                                              |
| `DEBUG`                     | Whether the application should run in debug mode.   | `true` / `false`            | `false`                                                                                                             |
| `RELOAD_INCLUDES`           | List of files or patterns that trigger auto-reload. | `["*.py"]`                  | `[".env"]`                                                                                                          |
| `APP_NAME`                  | The name of the application.                        | `UserService`, `PaymentAPI` | `MyApp`                                                                                                             |
| `PROCESS_TIME_HEADER`       | Response header used to expose processing time.     | `X-Response-Time`           | `X-Process-Time`                                                                                                    |
| `OPENAPI_VERSION`           | OpenAPI version used for Swagger UI.                | `3.0.2`, `3.1.0`            | `3.0.2`                                                                                                             |
| `OPENAPI_JSON_URL`          | URL path for the OpenAPI JSON schema.               | `/api/openapi.json`         | `/openapi.json`                                                                                                     |
| `PROXIED`                   | Whether the API runs behind a reverse proxy.        | `true` / `false`            | `false`                                                                                                             |
| `PROXY_LISTEN_PATH`         | Path prefix used by the proxy.                      | `/proxy`, `/api/proxy`      | `/`                                                                                                                 |
| `SWAGGER_STATIC_FILES`      | Path where Swagger UI static files are served.      | `/static/swagger`           | `/static/swagger`                                                                                                   |
| `SWAGGER_OPENAPI_JSON_URL`  | Path to the OpenAPI JSON used by Swagger.           | `/api/openapi.json`         | `/openapi.json`                                                                                                     |
| `GRAPHIQL_STATIC_FILES`     | Path to GraphiQL (GraphQL UI) static assets.        | `static/graphiql`           | `static/graphiql`                                                                                                   |
| `LOG_REQUEST_EXCLUDE_PATHS` | Paths excluded from request logging.                | `["/health", "/metrics"]`   | `["/health", "/metrics", "/static", "/docs", "/redoc", "/openapi.json", "/.well-known", "/graphql/v.*/playground"]` |
| `PROBE_READINESS_PATH`      | Readiness probe endpoint.                           | `/api/readiness`            | `/readiness`                                                                                                        |
| `PROBE_LIVENESS_PATH`       | Liveness probe endpoint.                            | `/api/liveness`             | `/liveness`                                                                                                         |

Create a `.env` file alongside your application if you need to override defaults:

```env
PORT=8000
LOG_LEVEL=INFO
APP_NAME=MyFastAPIApp
PROCESS_TIME_HEADER=X-Process-Time
SWAGGER_STATIC_FILES=/static/swagger
SWAGGER_OPENAPI_JSON_URL=/openapi.json
LOG_REQUEST_EXCLUDE_PATHS=["/health", "/metrics", "/static", "/docs", "/redoc", "/openapi.json", "/.well-known"]
```

The same settings object is used internally to configure logging, documentation,
and middleware. Although the implementation lives under `fastapi_template._internal`,
those modules are considered private and may change without notice.

## 🧩 Features

* **Logging** – Structured logging powered by `loguru` with an optional request
  logging middleware.
* **Monitoring** – Prometheus-compatible metrics endpoint and uptime background
  task ready to register in your observability stack.
* **Documentation** – Swagger UI and ReDoc served through customisable static
  assets bundled with the package.
* **Middleware** – Request timing, exception handling, and request logging
  middleware that can be toggled through configuration flags.
* **Utilities** – Helper clients for HTTP APIs, Bitbucket API, FTP servers, and Kubernetes
  interactions, plus shared Pydantic models for error responses.

## 📁 Project Structure

```
FastApiTemplate/
├── app/
│   └── main.py               # Example application entrypoint
├── package/
│   └── fastapi_template/
│       ├── __init__.py       # Public package exposing `create_app`
│       ├── utils.py          # Public utility functions and classes
│       ├── _internal/        # Private framework modules
│       └── static/           # Bundled static assets for Swagger UI
├── pyproject.toml            # Packaging metadata
├── requirements.txt         # Pinning dependencies for development
└── README.md
```

## 🛠️ Development

Install dependencies in editable mode when working on the package:

```bash
pip install -e .[dev]
```

Run the example application from the repository root:

```bash
python -m app.main
```

## 📄 License

Distributed under the terms of the MIT license. See the [LICENSE](LICENSE) file
for details.
