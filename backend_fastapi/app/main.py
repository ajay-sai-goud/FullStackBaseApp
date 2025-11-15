import uvicorn
from fastapi import FastAPI, Request
from loguru import logger
import time
from fastapi.middleware.cors import CORSMiddleware

from app import core
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.core.lifespan import lifespan
from app.api.router import setup_routes


# Configure logging and tracing before creating the app instance
core.configure_logging()
core.configure_tracing()

app = FastAPI(
    title=core.settings.APP_NAME,
    description="A simple, elegant, and powerful voice AI server designed to be instantly deployable. This server-side application provides a robust foundation for building and scaling voice-based AI solutions, offering a streamlined setup for developers to integrate and manage voice functionalities.",
    version="1.0.0",
    contact={
        "name": "Ajay Sai",
        "url": "https://github.com/Ajay-D-Sai/pipecat-server",
        "email": "ajaysai965@gmail.com",
    },
    openapi_tags=[
        {
            "name": "Pipecat",
            "description": "Endpoints for handling Pipecat voice AI interactions, including session management and real-time communication.",
        }
    ],
    lifespan=lifespan,
    docs_url="/docs_v0",
    redoc_url=None,
    openapi_url="/openapi.json",
)

# ===============================================
# Middleware
# ===============================================
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=core.settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=core.settings.ALLOWED_METHODS,
    allow_headers=core.settings.ALLOWED_HEADERS,
)

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    FastAPI middleware to log incoming requests and extract client IP.
    """
    # Extract client IP from request headers (handles proxies/load balancers)
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.headers.get("x-real-ip") or request.client.host if request.client else None
    
    # Set client IP in context for logging
    from app.core.observability.context import client_ip_context
    client_ip_context.set(client_ip)
    
    start_time = time.time()
    logger.info(f"--> {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}ms"
    
    logger.info(
        f"<-- {request.method} {request.url.path} - "
        f"Completed in {formatted_process_time} "
        f"Status: {response.status_code}"
    )
    
    return response

# ===============================================
# API Routes
# ===============================================
setup_routes(app)

# ===============================================
# Server Runners
# ===============================================
def run_dev_server():
    """
    Run the Uvicorn server for development.
    """
    logger.info("Starting development server... (reload enabled)")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,
    )

def run_prod_server():
    """
    Run the Uvicorn server for production.
    """
    logger.info("Starting production server... (reload disabled, 4 workers)")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4,
        log_config=None,
    )
