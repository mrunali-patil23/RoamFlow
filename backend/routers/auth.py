"""
Authentication router for FastAPI.
Handles user login, registration, and token management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.auth_service import AuthService
from database import db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Request/Response Models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: str
    updated_at: str

# Authentication endpoints
@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with username and password.
    Returns JWT access token on successful authentication.
    """
    try:
        # Authenticate user
        user = AuthService.authenticate_user(request.username, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        token_data = {"sub": user["id"], "username": user["username"]}
        access_token = AuthService.create_access_token(token_data)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    Returns JWT access token on successful registration.
    """
    try:
        # Register user
        user = AuthService.register_user(request.username, request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Create access token
        token_data = {"sub": user["id"], "username": user["username"]}
        access_token = AuthService.create_access_token(token_data)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated user information.
    Requires valid JWT token in Authorization header.
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Get current user from token
        user = AuthService.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.post("/logout")
async def logout():
    """
    Logout endpoint (token invalidation handled client-side).
    """
    return {"message": "Successfully logged out"}

# Dependency for protected routes
async def get_current_user_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user for protected routes.
    """
    try:
        token = credentials.credentials
        user = AuthService.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication dependency error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )