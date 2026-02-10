"""
Industrial Wearable AI — Auth Schemas
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request body."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    """Registration request body."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class ChangePasswordRequest(BaseModel):
    """Change password request body (authenticated user)."""

    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    """User info (for /me endpoint)."""

    id: str
    username: str
