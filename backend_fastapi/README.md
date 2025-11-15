# FastAPI Production 

This is a production-ready  for creating robust and observable FastAPI applications. It is built with modern, high-performance tooling like `uv` and includes pre-configured, integrated logging and distributed tracing out-of-the-box.

## Core Features

- **High-Speed Tooling**: Uses `uv` for dependency management, virtual environments, and running the server.
- **Structured, Production-Ready Logging**: Configured with `loguru` for clear, colorized, and structured (JSON-optional) logging. It automatically intercepts logs from all standard libraries like Uvicorn.
- **Integrated Distributed Tracing**: Uses **OpenTelemetry** to automatically trace all incoming requests, providing deep insights into application performance.
- **Automatic Log & Trace Correlation**: Every log message is automatically enriched with the `trace_id` and `span_id` of the request that generated it. This allows you to instantly pivot from a specific log entry to the full request trace in an observability platform.
- **Centralized Configuration**: Uses `pydantic-settings` to manage all settings via environment variables, with a clear `.env.example` file.
- **Asynchronous by Default**: All API and service layers are `async`, leveraging the full power of FastAPI.
- **DDD-Aligned Architecture**: Code is organized following Domain-Driven Design principles with domain-based folders and clear layer separation.
- **Domain-Based Organization**: All code (API routes, schemas, services) is organized by domain for better scalability and maintainability.

---

## Observability: Logging & Tracing Explained

This  is built on the principle that good observability is not an afterthought. The logging and tracing systems are designed to work together seamlessly.

### How It Works

1.  **Request Starts**: When a request hits the FastAPI app, the **OpenTelemetry Middleware** intercepts it and starts a new trace with a unique `trace_id`.
2.  **Logs Are Captured**: As your code executes (e.g., in an endpoint like `/api/health`), any call to `logger.info(...)` is processed.
3.  **Context is Injected**: Our custom `loguru` configuration automatically inspects the current OpenTelemetry context, finds the active `trace_id` and `span_id`, and injects them into the log record.
4.  **Unified Output**: The final log message, printed to your console or sent to a logging service, contains these IDs.

This creates a powerful link between your application's two most important observability signals.

**Example Log Output:**
When you call the `/api/health` endpoint, you will see a log message in your console like this:
```
2023-10-27 10:30:00.123 | INFO     | app.api.health.routes:health_check:24 | ip=127.0.0.1 | trace_id=abc123... | span_id=def456... | Health check endpoint was called.
```
You can take that `trace_id`, search for it in a tracing tool like Jaeger, and see the entire request lifecycle.

---

## Getting Started

### Prerequisites

1.  **Install `uv`**:
    If you don't have `uv` installed, follow the official instructions:
    ```sh
    # macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Windows
    irm https://astral.sh/uv/install.ps1 | iex
    ```

### Setup and Running the App

1.  **Create a Virtual Environment**:
    Navigate to the `fastapi` directory and create a virtual environment with `uv`.
    ```sh
    uv venv
    ```

2.  **Activate the Environment**:
    ```sh
    # macOS / Linux
    source .venv/bin/activate

    # Windows
    .venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    Install the project dependencies using `uv`. The `-e .` installs the project in "editable" mode.
    ```sh
    uv pip install -e .
    ```

4.  **Configure Environment**:
    Create a `.env` file with the following variables (optional, defaults are provided):
    ```env
    # Application
    APP_NAME=FastAPI
    LOG_LEVEL=INFO
    LOGURU_JSON_LOGS=false

    # OpenTelemetry (optional)
    OTEL_SERVICE_NAME=fastapi
    OTEL_EXPORTER_OTLP_ENDPOINT=
    OTEL_DEBUG_LOG_SPANS=false

    # CORS Configuration
    ALLOWED_ORIGINS=["http://localhost:3000"]
    ALLOWED_METHODS=["*"]
    ALLOWED_HEADERS=["*"]
    ```

5.  **Run the Application**:
    You now have two scripts to run the server, defined in `pyproject.toml`.

    **For Development (with auto-reload):**
    ```sh
    uv run start_dev
    ```

    **For Production (multi-worker, no auto-reload):**
    ```sh
    uv run start_prod
    ```
    The API will be available at `http://127.0.0.1:8000`.

### API Documentation

The application provides multiple documentation interfaces:

- **Stoplight Elements** (Custom): `http://localhost:8000/docs` - Modern, interactive API documentation with sidebar navigation
- **Swagger UI** (Default): `http://localhost:8000/docs_v0` - Traditional Swagger interface
- **OpenAPI JSON**: `http://localhost:8000/openapi.json` - Raw OpenAPI specification

---

## Project Structure Explained

This  follows **Domain-Driven Design (DDD)** principles with a clean, scalable architecture that separates concerns into distinct layers and organizes code by domain.

```
.
├── app/
│   ├── api/                      # API Layer - Domain-based routing
│   │   ├── health/               # Health domain routes
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── user/                 # User domain routes
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── ui/                   # UI/documentation routes
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── __init__.py           # Main API router combining all domains
│   │
│   ├── schemas/                  # API Layer - Domain-based DTOs
│   │   ├── health/               # Health domain schemas
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   ├── user/                 # User domain schemas
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   └── __init__.py
│   │
│   ├── services/                 # Application Layer - Domain-based services
│   │   ├── health/               # Health domain services
│   │   │   ├── __init__.py
│   │   │   └── service.py
│   │   ├── user/                 # User domain services
│   │   │   ├── __init__.py
│   │   │   └── service.py
│   │   └── __init__.py
│   │
│   ├── utils/                    # Utility Layer - Pure utility functions
│   │   ├── jwt.py                # JWT token utilities
│   │   ├── password.py           # Password hashing utilities
│   │   ├── rsa_keys.py           # RSA key management
│   │   └── formatters.py         # Formatting utilities
│   │
│   ├── core/                     # Core Layer - Configuration & Observability
│   │   ├── config.py             # Application settings and configuration
│   │   ├── observability/       # Observability infrastructure
│   │   │   ├── logging_config.py    # Loguru setup with OpenTelemetry integration
│   │   │   ├── tracing_config.py    # OpenTelemetry tracing setup
│   │   │   ├── tracing_route.py     # Custom API route for trace propagation
│   │   │   └── context.py           # Context variables (e.g., client IP)
│   │   └── __init__.py
│   │
│   ├── utils/                     # Shared utilities
│   │   └── formatters.py
│   │
│   ├── templates/                 # Jinja2 templates
│   │   └── stoplight_elements.html
│   │
│   └── main.py                    # Application entrypoint
├── .env.example
├── pyproject.toml
└── README.md
```

### DDD Architecture Layers:

*   **`app/api/`** - **API Layer**: Handles HTTP routing, request/response validation, and delegates to services. Organized by domain (e.g., `user/`, `health/`). Uses `TracingAPIRoute` for enhanced trace propagation.

*   **`app/schemas/`** - **API Layer (DTOs)**: Pydantic models for request/response validation. Organized by domain. Automatically generates OpenAPI schema.

*   **`app/services/`** - **Application Layer**: Orchestrates business logic and coordinates between domain and infrastructure. Organized by domain. Calls domain functions and uses utilities.

*   **`app/utils/`** - **Utility Layer**: Pure utility functions and helpers (JWT, password hashing, RSA keys, formatters). No business logic.

*   **`app/core/`** - **Core Layer**: 
    *   `config.py`: Application settings and configuration from environment variables.
    *   `observability/`: Logging, tracing, and monitoring infrastructure. Includes:
        *   `logging_config.py`: Loguru setup with OpenTelemetry log correlation
        *   `tracing_config.py`: OpenTelemetry distributed tracing configuration
        *   `tracing_route.py`: Custom API route for W3C Trace Context propagation
        *   `context.py`: Request-scoped context variables (client IP, etc.)

*   **`app/utils/`** - **Shared Utilities**: Generic, stateless utility functions not tied to business logic.

*   **`app/main.py`** - **Application Entrypoint**: Initializes FastAPI app, sets up middleware (CORS, logging, tracing), includes API routers, and defines server runners.

### Domain-Based Organization:

All code is organized by **domain** (e.g., `user`, `health`), making it easy to:
- Add new domains (e.g., `orders`, `products`) by creating new folders
- Maintain domain boundaries and keep related code together
- Scale the application as new features are added
- Follow DDD principles with clear domain separation

### Adding a New Domain:

To add a new domain (e.g., `orders`):

1. **API Routes**: Create `app/api/orders/routes.py` and add router to `app/api/__init__.py`
2. **Schemas**: Create `app/schemas/orders/schemas.py` with request/response models (include validation using Pydantic validators)
3. **Services**: Create `app/services/orders/service.py` with business logic

This structure ensures clean separation of concerns and follows DDD principles.
