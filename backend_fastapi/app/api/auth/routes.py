"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, status
from loguru import logger

from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth.interfaces import IAuthService
from app.core.dependencies import get_auth_service

router = APIRouter(tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def login(
    login_data: LoginRequest,
    auth_service: IAuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Authenticate user and return JWT token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access token on successful authentication.
    """
    logger.info(f"Login request for email: {login_data.email}")
    result = await auth_service.authenticate_user(login_data.email, login_data.password)
    return TokenResponse(**result)

