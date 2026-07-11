from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import AccessTokenResponse, LoginRequest, MeResponse, SignupRequest, UpdateMeRequest
from app.auth.security import (
    REFRESH_TOKEN_TYPE,
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config import get_settings
from app.db import get_db
from app.elo.engine import category_ratings, overall_rating, tier_for
from app.elo.constants import CATEGORIES, STARTING_RATING
from app.models import User

router = APIRouter(tags=["auth"])
settings = get_settings()

REFRESH_COOKIE_NAME = "refresh_token"


def _set_refresh_cookie(response: Response, user: User) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=create_refresh_token(user.id),
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/auth",
    )


def _build_me_response(db: Session, user: User) -> MeResponse:
    ratings = category_ratings(db, user.id)
    categories = [
        {
            "category": cat,
            "rating": ratings[cat].rating if cat in ratings else STARTING_RATING,
            "tier": tier_for(ratings[cat].rating if cat in ratings else STARTING_RATING),
            "sessions_count": ratings[cat].sessions_count if cat in ratings else 0,
        }
        for cat in CATEGORIES
    ]
    overall = overall_rating(db, user.id)
    return MeResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        overall_rating=overall,
        overall_tier=tier_for(overall),
        categories=categories,
    )


@router.post("/auth/signup", response_model=AccessTokenResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, response: Response, db: Session = Depends(get_db)) -> AccessTokenResponse:
    if db.query(User).filter(User.email == body.email).one_or_none() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _set_refresh_cookie(response, user)
    return AccessTokenResponse(access_token=create_access_token(user.id))


@router.post("/auth/login", response_model=AccessTokenResponse)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AccessTokenResponse:
    user = db.query(User).filter(User.email == body.email).one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")

    _set_refresh_cookie(response, user)
    return AccessTokenResponse(access_token=create_access_token(user.id))


@router.post("/auth/refresh", response_model=AccessTokenResponse)
def refresh(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
) -> AccessTokenResponse:
    if refresh_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing refresh token")

    try:
        user_id = decode_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    except InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token") from exc

    user = db.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

    # Rotate the refresh token on every use so a stolen cookie has a short shelf life.
    _set_refresh_cookie(response, user)
    return AccessTokenResponse(access_token=create_access_token(user.id))


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/auth")


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeResponse:
    return _build_me_response(db, user)


@router.patch("/me", response_model=MeResponse)
def update_me(
    body: UpdateMeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeResponse:
    user.display_name = body.display_name
    db.commit()
    return _build_me_response(db, user)
