from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdateMeRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CategoryRatingOut(BaseModel):
    category: str
    rating: int
    tier: str
    sessions_count: int


class MeResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    overall_rating: int
    overall_tier: str
    categories: list[CategoryRatingOut]
