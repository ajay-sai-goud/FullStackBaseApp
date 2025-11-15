"""UI and documentation API endpoints."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.core.observability import TracingAPIRoute

# Setup templates directory
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter(route_class=TracingAPIRoute)


@router.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_docs(request: Request):
    """Serve Stoplight Elements API documentation."""
    return templates.TemplateResponse("stoplight_elements.html", {"request": request})

